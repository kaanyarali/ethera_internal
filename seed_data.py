"""
Seed data script for Ethera Jewelry MVP
Run this after setting up the database to populate with sample data.
"""
from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app.models import Base, Material, Purchase, Product, ProductBOM, MaterialType

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Clear existing data (optional - comment out if you want to keep existing data)
    db.query(ProductBOM).delete()
    db.query(Product).delete()
    db.query(Purchase).delete()
    db.query(Material).delete()
    db.commit()
    
    # Create Materials
    diamond = Material(
        type=MaterialType.GEMSTONE,
        name="Round Diamond",
        unit="ct",
        notes="High quality round cut diamonds",
        attributes_json={"shape": "round", "color": "D-F", "clarity": "VS1-VVS2"}
    )
    db.add(diamond)
    
    gold = Material(
        type=MaterialType.METAL,
        name="14K Yellow Gold",
        unit="gram",
        notes="14 karat yellow gold wire and sheet"
    )
    db.add(gold)
    
    silver = Material(
        type=MaterialType.METAL,
        name="Sterling Silver",
        unit="gram",
        notes="925 sterling silver"
    )
    db.add(silver)
    
    chain = Material(
        type=MaterialType.OTHER,
        name="Silver Chain",
        unit="piece",
        notes="18 inch sterling silver chain"
    )
    db.add(chain)
    
    db.commit()
    db.refresh(diamond)
    db.refresh(gold)
    db.refresh(silver)
    db.refresh(chain)
    
    # Create Purchases
    purchase1 = Purchase(
        material_id=diamond.id,
        supplier_name="Gemstone Wholesale Co.",
        purchase_date=datetime.now() - timedelta(days=30),
        qty_purchased=5.0,
        qty_remaining=3.5,
        unit_cost=2500.00,
        currency="USD",
        notes="Premium quality diamonds"
    )
    db.add(purchase1)
    
    purchase2 = Purchase(
        material_id=gold.id,
        supplier_name="Metal Supply Inc.",
        purchase_date=datetime.now() - timedelta(days=15),
        qty_purchased=100.0,
        qty_remaining=75.0,
        unit_cost=45.50,
        currency="USD",
        notes="14K yellow gold"
    )
    db.add(purchase2)
    
    purchase3 = Purchase(
        material_id=silver.id,
        supplier_name="Metal Supply Inc.",
        purchase_date=datetime.now() - timedelta(days=10),
        qty_purchased=200.0,
        qty_remaining=180.0,
        unit_cost=0.85,
        currency="USD",
        notes="Sterling silver sheet and wire"
    )
    db.add(purchase3)
    
    purchase4 = Purchase(
        material_id=chain.id,
        supplier_name="Chain Manufacturing Ltd.",
        purchase_date=datetime.now() - timedelta(days=5),
        qty_purchased=20.0,
        qty_remaining=18.0,
        unit_cost=12.00,
        currency="USD",
        notes="18 inch chains"
    )
    db.add(purchase4)
    
    db.commit()
    
    # Create Product
    product = Product(
        sku="RING-001",
        name="Diamond Engagement Ring",
        description="Beautiful engagement ring with round diamond center stone and 14K yellow gold band",
        image_url=None,
        created_at=datetime.now()
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Create BOM lines for the product
    bom1 = ProductBOM(
        product_id=product.id,
        material_id=diamond.id,
        qty_required=1.0,
        unit="ct",
        note="Center stone"
    )
    db.add(bom1)
    
    bom2 = ProductBOM(
        product_id=product.id,
        material_id=gold.id,
        qty_required=3.5,
        unit="gram",
        note="Band weight"
    )
    db.add(bom2)
    
    bom3 = ProductBOM(
        product_id=product.id,
        material_id=chain.id,
        qty_required=1.0,
        unit="piece",
        note="Necklace chain (if used as pendant)"
    )
    db.add(bom3)
    
    db.commit()
    
    print("✓ Seed data created successfully!")
    print(f"  - {db.query(Material).count()} materials")
    print(f"  - {db.query(Purchase).count()} purchases")
    print(f"  - {db.query(Product).count()} products")
    print(f"  - {db.query(ProductBOM).count()} BOM lines")
    
except Exception as e:
    db.rollback()
    print(f"Error creating seed data: {e}")
    raise
finally:
    db.close()
