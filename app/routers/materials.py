from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from firebase_admin import firestore
from app.database import get_db
from app import schemas, models
from app.jinja_templates import templates
from app.firestore_models import document_to_dict, datetime_to_timestamp
from datetime import datetime

router = APIRouter()
html_router = APIRouter()


@router.get("/", response_model=list[schemas.Material])
def get_materials(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    materials_ref = db.collection("materials")
    docs = materials_ref.order_by("name").offset(skip).limit(limit).stream()
    materials = []
    for doc in docs:
        material = document_to_dict(doc)
        if material:
            materials.append(material)
    return materials


@router.get("/{material_id}", response_model=schemas.Material)
def get_material(material_id: str, db = Depends(get_db)):
    doc = db.collection("materials").document(material_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Material not found")
    return document_to_dict(doc)


@router.post("/", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db = Depends(get_db)):
    doc_ref = db.collection("materials").document()
    # Convert to dict and ensure type is a string
    data = material.model_dump()
    # Explicitly convert type enum to string value
    if hasattr(material, 'type') and material.type:
        data["type"] = material.type.value if isinstance(material.type, models.MaterialType) else str(material.type)
    elif "type" in data:
        if isinstance(data["type"], models.MaterialType):
            data["type"] = data["type"].value
        elif data["type"] is not None:
            data["type"] = str(data["type"])
    data["created_at"] = firestore.SERVER_TIMESTAMP
    doc_ref.set(data)
    doc = doc_ref.get()
    return document_to_dict(doc)


@router.put("/{material_id}", response_model=schemas.Material)
def update_material(material_id: str, material: schemas.MaterialUpdate, db = Depends(get_db)):
    doc_ref = db.collection("materials").document(material_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Use model_dump with mode='python' to get enum values as strings
    update_data = material.model_dump(exclude_unset=True, mode='python')
    # Ensure type is stored as string value (not enum object)
    if "type" in update_data:
        if isinstance(update_data["type"], models.MaterialType):
            update_data["type"] = update_data["type"].value
        elif not isinstance(update_data["type"], str):
            # Fallback: convert to string
            update_data["type"] = str(update_data["type"])
    if update_data:
        doc_ref.update(update_data)
    
    updated_doc = doc_ref.get()
    return document_to_dict(updated_doc)


@router.get("/{material_id}/purchases", response_model=list[schemas.Purchase])
def get_material_purchases(material_id: str, db = Depends(get_db)):
    purchases_ref = db.collection("purchases")
    docs = purchases_ref.where("material_id", "==", material_id).order_by("purchase_date", direction=firestore.Query.DESCENDING).stream()
    purchases = []
    for doc in docs:
        purchase = document_to_dict(doc)
        if purchase:
            purchases.append(purchase)
    return purchases


@router.delete("/{material_id}")
def delete_material(material_id: str, db = Depends(get_db)):
    doc_ref = db.collection("materials").document(material_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Delete all BOM lines that reference this material
    bom_lines = db.collection("product_bom").where("material_id", "==", material_id).stream()
    for bom_line in bom_lines:
        bom_line.reference.delete()
    
    # Delete all purchases that reference this material
    purchases = db.collection("purchases").where("material_id", "==", material_id).stream()
    for purchase in purchases:
        purchase.reference.delete()
    
    # Now delete the material
    doc_ref.delete()
    return {"message": "Material deleted"}


# HTML routes
@html_router.get("/materials", response_class=HTMLResponse)
async def materials_page(request: Request, db = Depends(get_db)):
    materials_ref = db.collection("materials")
    docs = materials_ref.order_by("name").stream()
    materials = []
    for doc in docs:
        material = document_to_dict(doc)
        if material:
            # Ensure type field exists (default to empty string if missing)
            if "type" not in material:
                material["type"] = ""
            materials.append(material)
    return templates.TemplateResponse("materials.html", {"request": request, "materials": materials})


@html_router.get("/materials/new", response_class=HTMLResponse)
async def new_material_page(request: Request):
    return templates.TemplateResponse("material_form.html", {"request": request, "material": None})


@html_router.get("/materials/{material_id}/edit", response_class=HTMLResponse)
async def edit_material_page(request: Request, material_id: str, db = Depends(get_db)):
    doc = db.collection("materials").document(material_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Material not found")
    material = document_to_dict(doc)
    return templates.TemplateResponse("material_form.html", {"request": request, "material": material})


@html_router.post("/materials", response_class=HTMLResponse)
async def create_material_form(
    request: Request,
    type: str = Form(...),
    name: str = Form(...),
    unit: str = Form(...),
    notes: str = Form(None),
    db = Depends(get_db)
):
    # Convert string to MaterialType enum
    try:
        material_type = models.MaterialType(type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {type}")
    
    material = schemas.MaterialCreate(
        type=material_type,
        name=name,
        unit=unit,
        notes=notes
    )
    create_material(material, db)
    return RedirectResponse(url="/materials", status_code=303)


@html_router.post("/materials/{material_id}", response_class=HTMLResponse)
async def update_material_form(
    request: Request,
    material_id: str,
    type: str = Form(None),
    name: str = Form(None),
    unit: str = Form(None),
    notes: str = Form(None),
    db = Depends(get_db)
):
    update_data = {}
    if type:
        # Convert string to MaterialType enum
        try:
            update_data["type"] = models.MaterialType(type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid material type: {type}")
    if name:
        update_data["name"] = name
    if unit:
        update_data["unit"] = unit
    if notes is not None:
        update_data["notes"] = notes
    
    material = schemas.MaterialUpdate(**update_data)
    update_material(material_id, material, db)
    return RedirectResponse(url="/materials", status_code=303)


@html_router.post("/materials/{material_id}/delete", response_class=HTMLResponse)
async def delete_material_form(request: Request, material_id: str, db = Depends(get_db)):
    delete_material(material_id, db)
    return RedirectResponse(url="/materials", status_code=303)
