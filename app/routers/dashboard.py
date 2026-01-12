from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from firebase_admin import firestore
from datetime import datetime
from app.database import get_db
from app.jinja_templates import templates
from app.firestore_models import document_to_dict
import json
from collections import defaultdict


def get_fallback_exchange_rate(base_currency: str, target_currency: str) -> float:
    """
    Get fallback exchange rate without API calls.
    Returns: rate
    """
    if base_currency == target_currency:
        return 1.0
    
    default_rates = {
        "USD": {"TRY": 30.0},
        "EUR": {"TRY": 33.0},
        "GBP": {"TRY": 38.0},
        "JPY": {"TRY": 0.20},
        "CNY": {"TRY": 4.2},
        "INR": {"TRY": 0.36},
        "CAD": {"TRY": 22.0},
        "AUD": {"TRY": 20.0},
        "CHF": {"TRY": 34.0},
        "SGD": {"TRY": 22.0},
    }
    return default_rates.get(base_currency, {}).get(target_currency, 1.0)

html_router = APIRouter()


@html_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db = Depends(get_db)):
    # Products over time
    products_ref = db.collection("products")
    product_docs = products_ref.order_by("created_at").stream()
    products = []
    for doc in product_docs:
        product = document_to_dict(doc)
        if product:
            products.append(product)
    
    if products:
        product_dates = []
        for p in products:
            created_at = p.get("created_at")
            if created_at:
                if isinstance(created_at, datetime):
                    product_dates.append(created_at.date())
                else:
                    # Try to parse if it's a string
                    try:
                        product_dates.append(datetime.fromisoformat(str(created_at)).date())
                    except:
                        pass
        
        product_counts = {}
        for date in product_dates:
            product_counts[date] = product_counts.get(date, 0) + 1
        
        sorted_dates = sorted(product_counts.keys())
        products_over_time = {
            "labels": [d.strftime("%Y-%m-%d") for d in sorted_dates],
            "data": [product_counts[d] for d in sorted_dates]
        }
    else:
        products_over_time = {"labels": [], "data": []}
    
    # Materials by type
    materials_ref = db.collection("materials")
    material_docs = materials_ref.stream()
    materials = []
    for doc in material_docs:
        material = document_to_dict(doc)
        if material:
            materials.append(material)
    
    if materials:
        material_types = {}
        for material in materials:
            mat_type = material.get("type", "OTHER")
            material_types[mat_type] = material_types.get(mat_type, 0) + 1
        
        materials_by_type = {
            "labels": list(material_types.keys()),
            "data": list(material_types.values())
        }
    else:
        materials_by_type = {"labels": [], "data": []}
    
    # Purchases over time
    purchases_ref = db.collection("purchases")
    purchase_docs = purchases_ref.order_by("purchase_date").stream()
    purchases = []
    for doc in purchase_docs:
        purchase = document_to_dict(doc)
        if purchase:
            purchases.append(purchase)
    
    if purchases:
        purchase_dates = []
        for p in purchases:
            purchase_date = p.get("purchase_date")
            if purchase_date:
                if isinstance(purchase_date, datetime):
                    purchase_dates.append(purchase_date.date())
                else:
                    try:
                        purchase_dates.append(datetime.fromisoformat(str(purchase_date)).date())
                    except:
                        pass
        
        purchase_counts = {}
        for date in purchase_dates:
            purchase_counts[date] = purchase_counts.get(date, 0) + 1
        
        sorted_purchase_dates = sorted(purchase_counts.keys())
        purchases_over_time = {
            "labels": [d.strftime("%Y-%m-%d") for d in sorted_purchase_dates],
            "data": [purchase_counts[d] for d in sorted_purchase_dates]
        }
    else:
        purchases_over_time = {"labels": [], "data": []}
    
    # Spending over time
    if purchases:
        spending_by_date = {}
        for purchase in purchases:
            purchase_date = purchase.get("purchase_date")
            if purchase_date:
                if isinstance(purchase_date, datetime):
                    date = purchase_date.date()
                else:
                    try:
                        date = datetime.fromisoformat(str(purchase_date)).date()
                    except:
                        continue
                
                spending = float(purchase.get("qty_purchased", 0) * purchase.get("unit_cost", 0))
                if date not in spending_by_date:
                    spending_by_date[date] = 0.0
                spending_by_date[date] += spending
        
        sorted_spending_dates = sorted(spending_by_date.keys())
        spending_over_time = {
            "labels": [d.strftime("%Y-%m-%d") for d in sorted_spending_dates],
            "data": [spending_by_date[d] for d in sorted_spending_dates]
        }
    else:
        spending_over_time = {"labels": [], "data": []}
    
    # Total inventory value by currency
    if purchases:
        inventory_by_currency = defaultdict(float)
        for purchase in purchases:
            currency = purchase.get("currency", "USD")
            qty_remaining = purchase.get("qty_remaining", 0)
            unit_cost = purchase.get("unit_cost", 0)
            inventory_by_currency[currency] += float(qty_remaining * unit_cost)
        
        currencies = list(inventory_by_currency.keys())
        values = [inventory_by_currency[c] for c in currencies]
        inventory_value = {"labels": currencies, "data": values}
    else:
        inventory_value = {"labels": [], "data": []}
    
    # Top materials by purchase quantity
    if purchases:
        material_qty_map = defaultdict(float)
        material_name_map = {}
        
        for purchase in purchases:
            material_id = purchase.get("material_id")
            if material_id:
                material_doc = db.collection("materials").document(material_id).get()
                if material_doc.exists:
                    material = document_to_dict(material_doc)
                    if material:
                        material_name = material.get("name", "Unknown")
                        material_name_map[material_id] = material_name
                        qty = purchase.get("qty_purchased", 0)
                        material_qty_map[material_id] += float(qty)
        
        # Sort by quantity and take top 10
        sorted_materials = sorted(material_qty_map.items(), key=lambda x: x[1], reverse=True)[:10]
        material_names = [material_name_map.get(mid, "Unknown") for mid, _ in sorted_materials]
        material_qtys = [qty for _, qty in sorted_materials]
        top_materials_data = {"labels": material_names, "data": material_qtys}
    else:
        top_materials_data = {"labels": [], "data": []}
    
    # Products by total count
    if products:
        product_count_map = {}
        for product in products:
            product_name = product.get("name", "Unknown")
            count = product.get("count", 1)
            product_count_map[product_name] = product_count_map.get(product_name, 0) + count
        
        # Sort by count and take top 10
        sorted_products = sorted(product_count_map.items(), key=lambda x: x[1], reverse=True)[:10]
        product_names = [name for name, _ in sorted_products]
        product_counts_list = [count for _, count in sorted_products]
        products_by_count = {"labels": product_names, "data": product_counts_list}
    else:
        products_by_count = {"labels": [], "data": []}
    
    # Statistics
    total_products = len(products)
    total_materials = len(materials)
    total_purchases = len(purchases)
    total_products_count = sum(p.get("count", 1) for p in products)
    
    # Calculate spending by currency (sum of all purchases across all materials: qty_purchased * unit_cost)
    spending_by_currency_dict = {}
    if purchases:
        for purchase in purchases:
            currency = purchase.get("currency", "USD")
            spending = float(purchase.get("qty_purchased", 0) * purchase.get("unit_cost", 0))
            spending_by_currency_dict[currency] = spending_by_currency_dict.get(currency, 0.0) + spending
    
    # Calculate total spending in TRY by converting each purchase using fallback exchange rates
    total_spending_try = 0.0
    exchange_rate_info = []  # Track which rates were used
    
    for purchase in purchases:
        purchase_amount = float(purchase.get("qty_purchased", 0) * purchase.get("unit_cost", 0))
        purchase_currency = purchase.get("currency", "USD")
        
        if purchase_currency == "TRY":
            total_spending_try += purchase_amount
        else:
            # Get fallback exchange rate (no API calls)
            rate = get_fallback_exchange_rate(purchase_currency, "TRY")
            converted_amount = purchase_amount * rate
            total_spending_try += converted_amount
            
            # Track exchange rate info (only add unique currency combinations)
            rate_key = purchase_currency
            if not any(r.get('key') == rate_key for r in exchange_rate_info):
                exchange_rate_info.append({
                    'key': rate_key,
                    'currency': purchase_currency,
                    'rate': rate
                })
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "products_over_time": json.dumps(products_over_time),
            "materials_by_type": json.dumps(materials_by_type),
            "purchases_over_time": json.dumps(purchases_over_time),
            "spending_over_time": json.dumps(spending_over_time),
            "inventory_value": json.dumps(inventory_value),
            "top_materials": json.dumps(top_materials_data),
            "products_by_count": json.dumps(products_by_count),
            "total_products": total_products,
            "total_materials": total_materials,
            "total_purchases": total_purchases,
            "total_products_count": int(total_products_count),
            "spending_by_currency": spending_by_currency_dict,
            "total_spending_try": total_spending_try,
            "exchange_rate_info": exchange_rate_info
        }
    )
