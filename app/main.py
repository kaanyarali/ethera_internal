from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.routers import materials, purchases, products, cost, dashboard
from app.jinja_templates import templates

app = FastAPI(title="Ethera Jewelry")

# Include routers
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["purchases"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cost.router, prefix="/api", tags=["cost"])

# Include HTML routers
app.include_router(materials.html_router, tags=["materials-html"])
app.include_router(purchases.html_router, tags=["purchases-html"])
app.include_router(products.html_router, tags=["products-html"])
app.include_router(dashboard.html_router, tags=["dashboard-html"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
