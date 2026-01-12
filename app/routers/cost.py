from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from datetime import datetime
import httpx
from app.database import get_db
from app import schemas
from app.firestore_models import document_to_dict

router = APIRouter()


async def get_exchange_rate(base_currency: str, target_currency: str, date: datetime) -> tuple[float, bool]:
    """
    Get exchange rate for a given date.
    Tries multiple free APIs for historical rates.
    Returns: (rate, is_from_api) tuple
    """
    if base_currency == target_currency:
        return (1.0, True)
    
    date_str = date.strftime('%Y-%m-%d')
    
    # Try exchangerate-api.com (free tier, no API key needed for basic usage)
    try:
        url = f"https://api.exchangerate-api.com/v4/historical/{base_currency}/{date_str}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "rates" in data and target_currency in data["rates"]:
                    rate = float(data["rates"][target_currency])
                    print(f"✓ Fetched rate from exchangerate-api.com: 1 {base_currency} = {rate} {target_currency} (date: {date_str})")
                    return (rate, True)
    except Exception as e:
        print(f"⚠ exchangerate-api.com failed: {e}")
    
    # Try exchangerate.host as backup
    try:
        url = f"https://api.exchangerate.host/{date_str}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params={
                "base": base_currency,
                "symbols": target_currency
            })
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "rates" in data:
                    rates = data["rates"]
                    if target_currency in rates:
                        rate = float(rates[target_currency])
                        print(f"✓ Fetched rate from exchangerate.host: 1 {base_currency} = {rate} {target_currency} (date: {date_str})")
                        return (rate, True)
    except Exception as e:
        print(f"⚠ exchangerate.host failed: {e}")
    
    # Try fixer.io free endpoint (no API key needed for limited usage)
    try:
        url = f"https://api.fixer.io/{date_str}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params={
                "base": base_currency,
                "symbols": target_currency
            })
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "rates" in data:
                    rates = data["rates"]
                    if target_currency in rates:
                        rate = float(rates[target_currency])
                        print(f"✓ Fetched rate from fixer.io: 1 {base_currency} = {rate} {target_currency} (date: {date_str})")
                        return (rate, True)
    except Exception as e:
        print(f"⚠ fixer.io failed: {e}")
    
    # All APIs failed - use fallback
    print(f"⚠ All APIs failed for {base_currency} to {target_currency} on {date_str}. Using fallback rate.")
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
    fallback_rate = default_rates.get(base_currency, {}).get(target_currency, 1.0)
    return (fallback_rate, False)


@router.get("/products/{product_id}/cost-estimate", response_model=schemas.CostEstimate)
async def get_cost_estimate(product_id: str, db = Depends(get_db)):
    # Get product
    product_doc = db.collection("products").document(product_id).get()
    if not product_doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")
    product = document_to_dict(product_doc)
    
    # Get BOM lines
    bom_ref = db.collection("product_bom")
    bom_docs = bom_ref.where("product_id", "==", product_id).stream()
    bom_lines = []
    for bom_doc in bom_docs:
        bom = document_to_dict(bom_doc)
        if bom:
            bom_lines.append(bom)
    
    material_breakdown = []
    currency_totals_dict = {}  # Dictionary to track totals per currency
    has_missing_costs = False
    
    for bom_line in bom_lines:
        # Get purchase specified in the BOM line
        purchase_id = bom_line.get("purchase_id")
        purchase = None
        if purchase_id:
            purchase_doc = db.collection("purchases").document(purchase_id).get()
            if purchase_doc.exists:
                purchase = document_to_dict(purchase_doc)
        
        if purchase:
            unit_cost = purchase.get("unit_cost")
            currency = purchase.get("currency")
            total_cost_for_line = bom_line.get("qty_required", 0) * unit_cost
            
            # Calculate total cost in TRY based on purchase date
            total_cost_try = None
            if currency == "TRY":
                total_cost_try = total_cost_for_line
            else:
                # Get exchange rate for the purchase date
                purchase_date = purchase.get("purchase_date")
                if purchase_date:
                    # Convert Firestore timestamp to datetime if needed
                    if not isinstance(purchase_date, datetime):
                        # Assume it's already a datetime or handle conversion
                        purchase_date = purchase_date
                    rate, is_from_api = await get_exchange_rate(currency, "TRY", purchase_date)
                    total_cost_try = total_cost_for_line * rate
            
            # Add to currency total
            if currency not in currency_totals_dict:
                currency_totals_dict[currency] = 0.0
            currency_totals_dict[currency] += total_cost_for_line
            
            has_cost = True
            warning = None
        else:
            unit_cost = None
            total_cost_for_line = None
            total_cost_try = None
            currency = None
            has_cost = False
            has_missing_costs = True
            warning = "No purchase specified for this material"
        
        # Get material name
        material_id = bom_line.get("material_id")
        material_name = "Unknown"
        if material_id:
            material_doc = db.collection("materials").document(material_id).get()
            if material_doc.exists:
                material = document_to_dict(material_doc)
                material_name = material.get("name", "Unknown") if material else "Unknown"
        
        material_breakdown.append(
            schemas.MaterialCostBreakdown(
                material_id=material_id,
                material_name=material_name,
                qty_required=bom_line.get("qty_required", 0),
                unit=bom_line.get("unit", ""),
                unit_cost=unit_cost,
                currency=currency,
                total_cost=total_cost_for_line,
                total_cost_try=total_cost_try,
                has_cost=has_cost,
                warning=warning
            )
        )
    
    # Convert currency totals dictionary to list
    currency_totals = [
        schemas.CurrencyTotal(currency=curr, total=total)
        for curr, total in sorted(currency_totals_dict.items())
    ]
    
    # Calculate total in Turkish Lira by summing individual material costs in TRY
    # (each material uses its own purchase date for conversion)
    total_try = 0.0
    exchange_rates = []
    seen_rates = {}  # Track unique exchange rates used
    
    # Track exchange rates while processing BOM lines (before summing)
    for bom_line in bom_lines:
        purchase_id = bom_line.get("purchase_id")
        if purchase_id:
            purchase_doc = db.collection("purchases").document(purchase_id).get()
            if purchase_doc.exists:
                purchase = document_to_dict(purchase_doc)
                if purchase and purchase.get("currency") != "TRY":
                    purchase_date = purchase.get("purchase_date")
                    if purchase_date:
                        if not isinstance(purchase_date, datetime):
                            purchase_date = purchase_date
                        date_str = purchase_date.strftime('%Y-%m-%d') if hasattr(purchase_date, 'strftime') else str(purchase_date)
                        rate_key = f"{purchase.get('currency')}_{date_str}"
                        
                        if rate_key not in seen_rates:
                            rate, is_from_api = await get_exchange_rate(purchase.get("currency"), "TRY", purchase_date)
                            seen_rates[rate_key] = True
                            exchange_rates.append(
                                schemas.ExchangeRateInfo(
                                    from_currency=purchase.get("currency"),
                                    to_currency="TRY",
                                    rate=rate,
                                    date=date_str,
                                    is_from_api=is_from_api
                                )
                            )
    
    # Sum up all TRY costs from material breakdown
    for breakdown in material_breakdown:
        if breakdown.total_cost_try is not None:
            total_try += breakdown.total_cost_try
    
    return schemas.CostEstimate(
        product_id=product_id,
        product_name=product.get("name", "Unknown"),
        material_breakdown=material_breakdown,
        currency_totals=currency_totals,
        total_try=total_try if total_try > 0 else None,
        exchange_rates=exchange_rates,
        has_missing_costs=has_missing_costs
    )
