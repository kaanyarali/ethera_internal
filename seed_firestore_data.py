"""
Seed data script for Ethera Jewelry - Firestore version
Run this script to populate Firestore with sample materials, purchases, and products.

Usage:
    python seed_firestore_data.py
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK (same as app/database.py)
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    try:
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("FIREBASE_PROJECT_ID")
        
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            if project_id:
                firebase_admin.initialize_app(cred, {'projectId': project_id})
            else:
                firebase_admin.initialize_app(cred)
        else:
            if project_id:
                firebase_admin.initialize_app(options={'projectId': project_id})
            else:
                firebase_admin.initialize_app()
        print("✓ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing Firebase: {e}")
        sys.exit(1)

# Get Firestore client
db = firestore.client()
print("✓ Firestore client initialized\n")


def clear_existing_data():
    """Clear all existing data (optional - comment out if you want to keep existing data)"""
    print("Clearing existing data...")
    
    # Clear products and related data
    products = db.collection("products").stream()
    for product in products:
        product_id = product.id
        
        # Delete BOM lines
        bom_lines = db.collection("product_bom").where("product_id", "==", product_id).stream()
        for bom in bom_lines:
            bom.reference.delete()
        
        # Delete product images
        images = db.collection("product_images").where("product_id", "==", product_id).stream()
        for image in images:
            image.reference.delete()
        
        # Delete product
        product.reference.delete()
    
    # Clear purchases
    purchases = db.collection("purchases").stream()
    for purchase in purchases:
        purchase.reference.delete()
    
    # Clear materials
    materials = db.collection("materials").stream()
    for material in materials:
        material.reference.delete()
    
    print("✓ Existing data cleared\n")


def create_materials():
    """Create sample materials"""
    print("Creating materials...")
    
    materials_data = [
        {
            "type": "GEMSTONE",
            "name": "Round Diamond",
            "unit": "ct",
            "notes": "High quality round cut diamonds, D-F color, VS1-VVS2 clarity",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "GEMSTONE",
            "name": "Emerald",
            "unit": "ct",
            "notes": "Natural emeralds, medium to high quality",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "GEMSTONE",
            "name": "Sapphire",
            "unit": "ct",
            "notes": "Blue sapphires, various sizes",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "GEMSTONE",
            "name": "Ruby",
            "unit": "ct",
            "notes": "Natural rubies, premium quality",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "METAL",
            "name": "14K Yellow Gold",
            "unit": "gram",
            "notes": "14 karat yellow gold wire and sheet",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "METAL",
            "name": "18K White Gold",
            "unit": "gram",
            "notes": "18 karat white gold for premium pieces",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "METAL",
            "name": "Sterling Silver",
            "unit": "gram",
            "notes": "925 sterling silver sheet and wire",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "METAL",
            "name": "Platinum",
            "unit": "gram",
            "notes": "Pure platinum for high-end jewelry",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "OTHER",
            "name": "Silver Chain",
            "unit": "piece",
            "notes": "18 inch sterling silver chain",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "OTHER",
            "name": "Gold Chain",
            "unit": "piece",
            "notes": "16-20 inch 14K gold chains",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "type": "OTHER",
            "name": "Pearl",
            "unit": "piece",
            "notes": "Freshwater pearls, various sizes",
            "created_at": firestore.SERVER_TIMESTAMP
        },
    ]
    
    material_refs = {}
    for material_data in materials_data:
        doc_ref = db.collection("materials").document()
        doc_ref.set(material_data)
        material_refs[material_data["name"]] = doc_ref.id
        print(f"  ✓ Created: {material_data['name']} ({material_data['type']})")
    
    print(f"✓ Created {len(materials_data)} materials\n")
    return material_refs


def create_purchases(material_refs):
    """Create sample purchases"""
    print("Creating purchases...")
    
    purchases_data = [
        {
            "material_id": material_refs["Round Diamond"],
            "supplier_name": "Gemstone Wholesale Co.",
            "purchase_date": datetime.now() - timedelta(days=60),
            "qty_purchased": 10.0,
            "qty_remaining": 6.5,
            "unit_cost": 2500.00,
            "currency": "USD",
            "notes": "Premium quality diamonds, D-F color",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Round Diamond"],
            "supplier_name": "Diamond Direct",
            "purchase_date": datetime.now() - timedelta(days=30),
            "qty_purchased": 5.0,
            "qty_remaining": 3.0,
            "unit_cost": 2800.00,
            "currency": "USD",
            "notes": "High-end diamonds",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Emerald"],
            "supplier_name": "Gemstone Wholesale Co.",
            "purchase_date": datetime.now() - timedelta(days=45),
            "qty_purchased": 8.0,
            "qty_remaining": 5.5,
            "unit_cost": 450.00,
            "currency": "USD",
            "notes": "Natural emeralds",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Sapphire"],
            "supplier_name": "Gemstone Wholesale Co.",
            "purchase_date": datetime.now() - timedelta(days=20),
            "qty_purchased": 12.0,
            "qty_remaining": 9.0,
            "unit_cost": 320.00,
            "currency": "USD",
            "notes": "Blue sapphires",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Ruby"],
            "supplier_name": "Precious Stones Ltd.",
            "purchase_date": datetime.now() - timedelta(days=15),
            "qty_purchased": 6.0,
            "qty_remaining": 4.0,
            "unit_cost": 850.00,
            "currency": "USD",
            "notes": "Premium rubies",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["14K Yellow Gold"],
            "supplier_name": "Metal Supply Inc.",
            "purchase_date": datetime.now() - timedelta(days=40),
            "qty_purchased": 200.0,
            "qty_remaining": 150.0,
            "unit_cost": 45.50,
            "currency": "USD",
            "notes": "14K yellow gold",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["14K Yellow Gold"],
            "supplier_name": "Metal Supply Inc.",
            "purchase_date": datetime.now() - timedelta(days=10),
            "qty_purchased": 100.0,
            "qty_remaining": 95.0,
            "unit_cost": 46.00,
            "currency": "USD",
            "notes": "14K yellow gold - recent purchase",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["18K White Gold"],
            "supplier_name": "Premium Metals Co.",
            "purchase_date": datetime.now() - timedelta(days=25),
            "qty_purchased": 150.0,
            "qty_remaining": 120.0,
            "unit_cost": 58.00,
            "currency": "USD",
            "notes": "18K white gold",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Sterling Silver"],
            "supplier_name": "Metal Supply Inc.",
            "purchase_date": datetime.now() - timedelta(days=35),
            "qty_purchased": 500.0,
            "qty_remaining": 400.0,
            "unit_cost": 0.85,
            "currency": "USD",
            "notes": "Sterling silver sheet and wire",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Platinum"],
            "supplier_name": "Premium Metals Co.",
            "purchase_date": datetime.now() - timedelta(days=50),
            "qty_purchased": 80.0,
            "qty_remaining": 60.0,
            "unit_cost": 32.50,
            "currency": "USD",
            "notes": "Pure platinum",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Silver Chain"],
            "supplier_name": "Chain Manufacturing Ltd.",
            "purchase_date": datetime.now() - timedelta(days=20),
            "qty_purchased": 50.0,
            "qty_remaining": 40.0,
            "unit_cost": 12.00,
            "currency": "USD",
            "notes": "18 inch chains",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Gold Chain"],
            "supplier_name": "Chain Manufacturing Ltd.",
            "purchase_date": datetime.now() - timedelta(days=15),
            "qty_purchased": 30.0,
            "qty_remaining": 25.0,
            "unit_cost": 85.00,
            "currency": "USD",
            "notes": "14K gold chains",
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "material_id": material_refs["Pearl"],
            "supplier_name": "Pearl Importers",
            "purchase_date": datetime.now() - timedelta(days=30),
            "qty_purchased": 100.0,
            "qty_remaining": 75.0,
            "unit_cost": 15.00,
            "currency": "USD",
            "notes": "Freshwater pearls",
            "created_at": firestore.SERVER_TIMESTAMP
        },
    ]
    
    purchase_refs = {}
    for idx, purchase_data in enumerate(purchases_data):
        doc_ref = db.collection("purchases").document()
        doc_ref.set(purchase_data)
        purchase_refs[f"purchase_{idx}"] = doc_ref.id
        material_name = [k for k, v in material_refs.items() if v == purchase_data["material_id"]][0]
        print(f"  ✓ Created: {purchase_data['supplier_name']} - {material_name} ({purchase_data['qty_purchased']} {purchase_data.get('currency', 'USD')})")
    
    print(f"✓ Created {len(purchases_data)} purchases\n")
    return purchase_refs, purchases_data


def create_products(material_refs, purchase_refs, purchases_data):
    """Create sample products"""
    print("Creating products...")
    
    # Map purchase indices to material names for easier lookup
    purchase_to_material = {}
    for idx, purchase_data in enumerate(purchases_data):
        material_id = purchase_data["material_id"]
        material_name = [k for k, v in material_refs.items() if v == material_id][0]
        purchase_to_material[f"purchase_{idx}"] = material_name
    
    products_data = [
        {
            "sku": "RING-001",
            "name": "Diamond Engagement Ring",
            "description": "Beautiful engagement ring with round diamond center stone and 14K yellow gold band",
            "collection_name": "Classic Collection",
            "product_type": "RING",
            "count": 1,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "RING-002",
            "name": "Emerald and Diamond Ring",
            "description": "Elegant ring featuring emerald center stone with diamond accents, set in 18K white gold",
            "collection_name": "Classic Collection",
            "product_type": "RING",
            "count": 2,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "NECK-001",
            "name": "Sapphire Pendant Necklace",
            "description": "Stunning blue sapphire pendant on 18 inch silver chain",
            "collection_name": "Spring Collection",
            "product_type": "NECKLACE",
            "count": 3,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "NECK-002",
            "name": "Pearl Strand Necklace",
            "description": "Classic freshwater pearl strand necklace, 18 inches",
            "collection_name": "Classic Collection",
            "product_type": "NECKLACE",
            "count": 1,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "EARR-001",
            "name": "Diamond Stud Earrings",
            "description": "Timeless diamond stud earrings in 14K yellow gold",
            "collection_name": "Classic Collection",
            "product_type": "EARRING",
            "count": 2,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "EARR-002",
            "name": "Ruby Drop Earrings",
            "description": "Elegant ruby drop earrings with diamond accents, 18K white gold",
            "collection_name": "Luxury Collection",
            "product_type": "EARRING",
            "count": 1,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "BRAC-001",
            "name": "Gold Chain Bracelet",
            "description": "Delicate 14K gold chain bracelet, adjustable length",
            "collection_name": "Spring Collection",
            "product_type": "BRACELET",
            "count": 4,
            "created_at": firestore.SERVER_TIMESTAMP
        },
        {
            "sku": "BRAC-002",
            "name": "Platinum Tennis Bracelet",
            "description": "Luxurious platinum tennis bracelet with round diamonds",
            "collection_name": "Luxury Collection",
            "product_type": "BRACELET",
            "count": 1,
            "created_at": firestore.SERVER_TIMESTAMP
        },
    ]
    
    product_refs = {}
    for product_data in products_data:
        doc_ref = db.collection("products").document()
        doc_ref.set(product_data)
        product_refs[product_data["sku"]] = doc_ref.id
        print(f"  ✓ Created: {product_data['name']} ({product_data['sku']})")
    
    print(f"✓ Created {len(products_data)} products\n")
    return product_refs


def create_bom_lines(product_refs, material_refs, purchase_refs, purchases_data):
    """Create BOM lines linking products to materials and purchases"""
    print("Creating BOM lines...")
    
    # Helper to find purchase ID for a material
    def find_purchase_for_material(material_name):
        for idx, purchase_data in enumerate(purchases_data):
            material_id = purchase_data["material_id"]
            if material_refs.get(material_name) == material_id:
                return purchase_refs.get(f"purchase_{idx}")
        return None
    
    bom_data = [
        # Diamond Engagement Ring
        {
            "product_id": product_refs["RING-001"],
            "material_id": material_refs["Round Diamond"],
            "purchase_id": find_purchase_for_material("Round Diamond"),
            "qty_required": 1.5,
            "unit": "ct",
            "note": "Center stone"
        },
        {
            "product_id": product_refs["RING-001"],
            "material_id": material_refs["14K Yellow Gold"],
            "purchase_id": find_purchase_for_material("14K Yellow Gold"),
            "qty_required": 3.5,
            "unit": "gram",
            "note": "Band"
        },
        # Emerald and Diamond Ring
        {
            "product_id": product_refs["RING-002"],
            "material_id": material_refs["Emerald"],
            "purchase_id": find_purchase_for_material("Emerald"),
            "qty_required": 2.0,
            "unit": "ct",
            "note": "Center stone"
        },
        {
            "product_id": product_refs["RING-002"],
            "material_id": material_refs["Round Diamond"],
            "purchase_id": find_purchase_for_material("Round Diamond"),
            "qty_required": 0.5,
            "unit": "ct",
            "note": "Accent stones"
        },
        {
            "product_id": product_refs["RING-002"],
            "material_id": material_refs["18K White Gold"],
            "purchase_id": find_purchase_for_material("18K White Gold"),
            "qty_required": 4.0,
            "unit": "gram",
            "note": "Setting"
        },
        # Sapphire Pendant Necklace
        {
            "product_id": product_refs["NECK-001"],
            "material_id": material_refs["Sapphire"],
            "purchase_id": find_purchase_for_material("Sapphire"),
            "qty_required": 3.0,
            "unit": "ct",
            "note": "Pendant stone"
        },
        {
            "product_id": product_refs["NECK-001"],
            "material_id": material_refs["Silver Chain"],
            "purchase_id": find_purchase_for_material("Silver Chain"),
            "qty_required": 1.0,
            "unit": "piece",
            "note": "Chain"
        },
        # Pearl Strand Necklace
        {
            "product_id": product_refs["NECK-002"],
            "material_id": material_refs["Pearl"],
            "purchase_id": find_purchase_for_material("Pearl"),
            "qty_required": 45.0,
            "unit": "piece",
            "note": "Pearls"
        },
        {
            "product_id": product_refs["NECK-002"],
            "material_id": material_refs["Sterling Silver"],
            "purchase_id": find_purchase_for_material("Sterling Silver"),
            "qty_required": 2.0,
            "unit": "gram",
            "note": "Clasp and findings"
        },
        # Diamond Stud Earrings
        {
            "product_id": product_refs["EARR-001"],
            "material_id": material_refs["Round Diamond"],
            "purchase_id": find_purchase_for_material("Round Diamond"),
            "qty_required": 1.0,
            "unit": "ct",
            "note": "Total for pair"
        },
        {
            "product_id": product_refs["EARR-001"],
            "material_id": material_refs["14K Yellow Gold"],
            "purchase_id": find_purchase_for_material("14K Yellow Gold"),
            "qty_required": 2.0,
            "unit": "gram",
            "note": "Settings"
        },
        # Ruby Drop Earrings
        {
            "product_id": product_refs["EARR-002"],
            "material_id": material_refs["Ruby"],
            "purchase_id": find_purchase_for_material("Ruby"),
            "qty_required": 2.5,
            "unit": "ct",
            "note": "Drop stones"
        },
        {
            "product_id": product_refs["EARR-002"],
            "material_id": material_refs["Round Diamond"],
            "purchase_id": find_purchase_for_material("Round Diamond"),
            "qty_required": 0.3,
            "unit": "ct",
            "note": "Accent diamonds"
        },
        {
            "product_id": product_refs["EARR-002"],
            "material_id": material_refs["18K White Gold"],
            "purchase_id": find_purchase_for_material("18K White Gold"),
            "qty_required": 3.0,
            "unit": "gram",
            "note": "Settings"
        },
        # Gold Chain Bracelet
        {
            "product_id": product_refs["BRAC-001"],
            "material_id": material_refs["Gold Chain"],
            "purchase_id": find_purchase_for_material("Gold Chain"),
            "qty_required": 1.0,
            "unit": "piece",
            "note": "Chain"
        },
        # Platinum Tennis Bracelet
        {
            "product_id": product_refs["BRAC-002"],
            "material_id": material_refs["Round Diamond"],
            "purchase_id": find_purchase_for_material("Round Diamond"),
            "qty_required": 5.0,
            "unit": "ct",
            "note": "Total diamonds"
        },
        {
            "product_id": product_refs["BRAC-002"],
            "material_id": material_refs["Platinum"],
            "purchase_id": find_purchase_for_material("Platinum"),
            "qty_required": 12.0,
            "unit": "gram",
            "note": "Bracelet body"
        },
    ]
    
    for bom_data_item in bom_data:
        doc_ref = db.collection("product_bom").document()
        doc_ref.set(bom_data_item)
    
    print(f"✓ Created {len(bom_data)} BOM lines\n")


def main():
    """Main function to seed Firestore with mock data"""
    print("=" * 60)
    print("Ethera Jewelry - Firestore Seed Data Script")
    print("=" * 60)
    print()
    
    # Ask user if they want to clear existing data
    response = input("Do you want to clear existing data? (yes/no): ").strip().lower()
    if response in ['yes', 'y']:
        clear_existing_data()
    else:
        print("Keeping existing data...\n")
    
    try:
        # Create materials
        material_refs = create_materials()
        
        # Create purchases
        purchase_refs, purchases_data = create_purchases(material_refs)
        
        # Create products
        product_refs = create_products(material_refs, purchase_refs, purchases_data)
        
        # Create BOM lines
        create_bom_lines(product_refs, material_refs, purchase_refs, purchases_data)
        
        # Summary
        print("=" * 60)
        print("✓ Seed data created successfully!")
        print("=" * 60)
        
        # Count created items
        materials_count = len(list(db.collection("materials").stream()))
        purchases_count = len(list(db.collection("purchases").stream()))
        products_count = len(list(db.collection("products").stream()))
        bom_count = len(list(db.collection("product_bom").stream()))
        
        print(f"  - {materials_count} materials")
        print(f"  - {purchases_count} purchases")
        print(f"  - {products_count} products")
        print(f"  - {bom_count} BOM lines")
        print()
        
    except Exception as e:
        print(f"\n✗ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
