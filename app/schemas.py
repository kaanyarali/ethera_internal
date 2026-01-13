from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.models import MaterialType, ProductType


# Material schemas
class MaterialBase(BaseModel):
    type: MaterialType
    name: str
    unit: str
    notes: Optional[str] = None
    attributes_json: Optional[Dict[str, Any]] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    type: Optional[MaterialType] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    attributes_json: Optional[Dict[str, Any]] = None


class Material(MaterialBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase schemas
class PurchaseBase(BaseModel):
    material_id: str
    supplier_name: str
    purchase_date: datetime
    qty_purchased: float
    qty_remaining: Optional[float] = None
    unit_cost: float
    currency: str = "USD"
    notes: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    pass


class PurchaseUpdate(BaseModel):
    material_id: Optional[str] = None
    supplier_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    qty_purchased: Optional[float] = None
    qty_remaining: Optional[float] = None
    unit_cost: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None


class Purchase(PurchaseBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    count: int = 1
    collection_name: Optional[str] = None
    product_type: Optional[ProductType] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    count: Optional[int] = None
    collection_name: Optional[str] = None
    product_type: Optional[ProductType] = None


class Product(ProductBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ProductImage schemas
class ProductImageBase(BaseModel):
    image_url: str
    order: int = 0


class ProductImageCreate(ProductImageBase):
    product_id: str


class ProductImage(ProductImageBase):
    id: str
    product_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class BulkCountUpdate(BaseModel):
    product_id: str
    count: int


class BulkCountUpdateRequest(BaseModel):
    updates: list[BulkCountUpdate]


# ProductBOM schemas
class ProductBOMBase(BaseModel):
    product_id: str
    material_id: str
    purchase_id: str
    qty_required: float
    unit: str
    note: Optional[str] = None


class ProductBOMCreate(ProductBOMBase):
    pass


class ProductBOMUpdate(BaseModel):
    product_id: Optional[str] = None
    material_id: Optional[str] = None
    purchase_id: Optional[str] = None
    qty_required: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None


class ProductBOM(ProductBOMBase):
    id: str

    class Config:
        from_attributes = True


# Cost estimate schemas
class MaterialCostBreakdown(BaseModel):
    material_id: str
    material_name: str
    qty_required: float
    unit: str
    unit_cost: Optional[float]
    currency: Optional[str]
    total_cost: Optional[float]
    total_cost_try: Optional[float] = None  # Total cost in TRY based on purchase date
    has_cost: bool
    warning: Optional[str] = None


class CurrencyTotal(BaseModel):
    currency: str
    total: float


class ExchangeRateInfo(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    date: str
    is_from_api: bool = True


class CostEstimate(BaseModel):
    product_id: str
    product_name: str
    material_breakdown: list[MaterialCostBreakdown]
    currency_totals: list[CurrencyTotal]
    total_try: Optional[float] = None
    exchange_rates: list[ExchangeRateInfo] = []
    has_missing_costs: bool
