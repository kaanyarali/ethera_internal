# Ethera Jewelry MVP

A small internal MVP for tracking jewelry products, materials, and calculating item costs.

## Features

- **Materials Management**: Track gemstones, metals, and other materials with attributes
- **Purchase Tracking**: Record inventory purchases with supplier information and costs
- **Product Management**: Create and manage jewelry products with SKUs
- **Bill of Materials (BOM)**: Define material requirements for each product
- **Cost Estimation**: Automatically calculate product costs based on latest purchase prices

## Tech Stack

- Python 3.11
- FastAPI
- Firestore (Google Cloud Firestore)
- Firebase Storage (for product images)
- Jinja2 templates for HTML UI

## Setup

### 1. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Firebase

1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Enable Firebase Storage
4. Download your service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the JSON file
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
   ```
6. Set Firebase Storage bucket name (optional, for image uploads):
   ```bash
   export FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
   ```

### 4. (Optional) Seed Sample Data

```bash
python seed_data.py
```

This will create:
- Sample materials (diamond, gold, silver, chain)
- Sample purchases with pricing
- One sample product with BOM

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## Usage

### Pages

- `/` - Home page with quick links
- `/materials` - List and manage materials
- `/materials/new` - Add new material
- `/materials/{id}/edit` - Edit material
- `/purchases` - List and manage purchases
- `/purchases/new` - Add new purchase
- `/products` - List and manage products
- `/products/new` - Add new product
- `/products/{id}` - View product details, BOM, and cost estimate
- `/products/{id}/edit` - Edit product

### API Endpoints

All API endpoints are prefixed with `/api`:

- `GET /api/materials` - List materials
- `POST /api/materials` - Create material
- `GET /api/materials/{id}` - Get material
- `PUT /api/materials/{id}` - Update material
- `DELETE /api/materials/{id}` - Delete material

- `GET /api/purchases` - List purchases
- `POST /api/purchases` - Create purchase
- `GET /api/purchases/{id}` - Get purchase
- `PUT /api/purchases/{id}` - Update purchase
- `DELETE /api/purchases/{id}` - Delete purchase

- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/products/{id}/bom` - Get product BOM
- `POST /api/products/{id}/bom` - Add BOM line
- `DELETE /api/products/bom/{bom_id}` - Delete BOM line

- `GET /api/products/{id}/cost-estimate` - Get cost estimate for product

### Cost Calculation

The cost estimation works by:
1. Finding all BOM lines for a product
2. For each material, finding the most recent purchase (by purchase_date)
3. Calculating: `qty_required × latest_unit_cost`
4. Summing all material costs for total product cost

If a material has no purchase records, it will show a warning and exclude it from the total.

## Database

The application uses **Firestore** (Google Cloud Firestore), a NoSQL document database. 

### Firestore Collections

- `materials` - Material definitions
- `purchases` - Purchase/inventory records
- `products` - Product definitions
- `product_bom` - Bill of Materials lines
- `product_images` - Product image references

### Local Development

For local development, you need:
1. A Firebase project
2. Service account credentials (set `GOOGLE_APPLICATION_CREDENTIALS` environment variable)
3. Firestore and Storage enabled in your Firebase project

### Cloud Deployment

For Cloud Run deployment:
- Uses default application credentials (no service account file needed)
- Set `FIREBASE_STORAGE_BUCKET` environment variable for image storage

## Future Enhancements

- Material consumption tracking (actual inventory deduction)
- Enhanced supplier management
- Production orders/work orders
- Advanced reporting and analytics
- Real-time updates with Firestore listeners

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and routes
│   ├── database.py          # Firestore client initialization
│   ├── models.py            # MaterialType enum
│   ├── schemas.py           # Pydantic schemas
│   ├── firestore_models.py  # Firestore helper functions
│   ├── storage.py           # Firebase Storage client
│   ├── jinja_templates.py   # Jinja2 template setup
│   ├── routers/             # API and HTML routers
│   │   ├── materials.py
│   │   ├── purchases.py
│   │   ├── products.py
│   │   ├── cost.py
│   │   └── dashboard.py
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── materials.html
│       ├── material_form.html
│       ├── purchases.html
│       ├── purchase_form.html
│       ├── products.html
│       ├── product_form.html
│       ├── product_detail.html
│       └── dashboard.html
├── requirements.txt
├── seed_data.py
└── README.md
```
