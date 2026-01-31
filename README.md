# 🏪 Rental Management System

A comprehensive multi-vendor rental management platform built with **FastAPI** (Backend) and **Next.js** (Frontend).

## 🚀 Features

### For Customers
- Browse and search rental products
- Check real-time availability
- Add to cart and checkout
- Track orders and rentals
- View invoices and payment history

### For Vendors
- Product management (CRUD)
- Inventory tracking
- Order management
- Revenue analytics
- Category-based product organization

### For Admins
- User management (activate/deactivate)
- Platform analytics and reports
- Coupon management
- System settings
- Export orders/invoices to CSV

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 18, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.10+, SQLAlchemy |
| **Database** | MySQL |
| **Authentication** | JWT (JSON Web Tokens) |

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Config, security, database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── main.py                  # FastAPI app entry
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── app/                     # Next.js pages (App Router)
│   ├── components/              # React components
│   ├── contexts/                # Auth context
│   ├── lib/api/                 # API client
│   └── types/                   # TypeScript types
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL Server

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure database
# Edit .env file with your MySQL credentials

# Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🔗 Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## 👤 Default Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@rental.com | Admin@123 |
| Vendor | vendor@rental.com | Vendor@123 |
| Customer | customer@rental.com | Customer@123 |

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/signup/customer` - Customer signup
- `POST /api/v1/auth/signup/vendor` - Vendor signup
- `GET /api/v1/auth/me` - Get current user

### Products
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product
- `POST /api/v1/products` - Create product (Vendor)
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Orders
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders/cart/add` - Add to cart
- `POST /api/v1/orders/{id}/confirm` - Confirm order

### Admin
- `GET /api/v1/admin/users` - List users
- `POST /api/v1/admin/users/{id}/toggle-status` - Toggle user status

## 🔒 Reservation System

The platform includes a reservation system to prevent double-booking:

1. **Add to Cart** → Checks availability
2. **Confirm Order** → Creates reservation (blocks stock)
3. **Pickup** → Stock marked as "with customer"
4. **Return** → Reservation released, stock freed
5. **Cancel** → Reservation released

## 📝 License

MIT License

## 👨‍💻 Author

Built for GCET Hackathon 2026
