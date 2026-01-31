# Rental Management System - Backend API

Production-ready FastAPI backend for a comprehensive Rental Management System.

## Features

- **Multi-vendor Architecture**: Support for multiple vendors managing their products
- **Complete Rental Lifecycle**: Quotation → Sale Order → Invoice → Pickup → Return
- **Stock Management**: Reservation system prevents double-booking
- **Payment Integration**: Razorpay payment gateway with partial payment support
- **GST Compliance**: Automatic GST calculation and invoicing
- **Role-based Access Control**: Customer, Vendor, and Admin roles
- **Authentication**: JWT-based authentication with password reset
- **Email Notifications**: Google OAuth integration for emails
- **Reports & Export**: Dashboard with CSV export functionality

## Tech Stack

- **Framework**: FastAPI 0.110+
- **Database**: MySQL (via XAMPP) + SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) + bcrypt
- **Payment**: Razorpay
- **Email**: Google OAuth + aiosmtplib
- **Validation**: Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/    # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── products.py      # Product CRUD
│   │   ├── orders.py        # Order & cart management
│   │   ├── invoices.py      # Invoicing & payments
│   │   ├── dashboard.py     # Analytics & reports
│   │   └── admin.py         # Admin & settings
│   ├── core/                # Core functionality
│   │   ├── config.py        # Settings management
│   │   ├── database.py      # DB connection
│   │   └── security.py      # JWT & RBAC
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── alembic/                 # Database migrations
├── .env                     # Environment variables
├── main.py                  # Application entry point
└── requirements.txt         # Dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- XAMPP (MySQL running on port 3306)
- MySQL database: `rental_management_db`

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Copy `.env.example` to `.env` (if exists) or use the existing `.env`
   - Update database credentials if needed
   - Add your Razorpay API keys
   - Add Google OAuth credentials

3. **Create database tables**:
   ```bash
   # Option 1: Using Alembic (recommended for production)
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   
   # Option 2: Direct creation (for development)
   # Tables will be auto-created on first run via main.py
   ```

4. **Run the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API documentation**:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Environment Variables

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=rental_management_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Razorpay
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup/customer` - Customer registration
- `POST /api/v1/auth/signup/vendor` - Vendor registration
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Reset password with token
- `GET /api/v1/auth/me` - Get current user

### Products
- `GET /api/v1/products` - List products (public)
- `GET /api/v1/products/vendor` - Vendor's products
- `POST /api/v1/products` - Create product (vendor)
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/check-availability` - Check availability

### Orders
- `GET /api/v1/orders/cart` - Get cart
- `POST /api/v1/orders/cart/add` - Add to cart
- `POST /api/v1/orders` - Create order
- `POST /api/v1/orders/{id}/confirm` - Confirm order
- `POST /api/v1/orders/{id}/pickup` - Mark as picked up
- `POST /api/v1/orders/{id}/return` - Mark as returned
- `GET /api/v1/orders/vendor/pending-pickups` - Pending pickups
- `GET /api/v1/orders/vendor/overdue` - Overdue returns

### Invoices & Payments
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices` - List invoices
- `POST /api/v1/invoices/payments/create-order` - Create Razorpay order
- `POST /api/v1/invoices/payments/verify` - Verify payment
- `POST /api/v1/invoices/payments/cash` - Record cash payment

### Dashboard
- `GET /api/v1/dashboard/admin` - Admin dashboard stats
- `GET /api/v1/dashboard/vendor` - Vendor dashboard stats
- `GET /api/v1/dashboard/revenue-chart` - Revenue chart data
- `GET /api/v1/dashboard/top-products` - Most rented products
- `GET /api/v1/dashboard/export/orders` - Export orders CSV
- `GET /api/v1/dashboard/export/invoices` - Export invoices CSV

### Admin
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users/{id}/toggle-status` - Activate/deactivate user
- `GET /api/v1/admin/settings` - Get company settings
- `PUT /api/v1/admin/settings` - Update settings
- `GET /api/v1/admin/coupons` - List coupons
- `POST /api/v1/admin/coupons` - Create coupon

## Key Features

### Reservation System
Prevents double-booking by creating reservations when orders are confirmed. Tracks stock status throughout the rental lifecycle.

### Multi-vendor Support
Products belong to specific vendors. Orders are automatically split by vendor. Each vendor has their own dashboard.

### Complete Rental Flow
1. **Quotation**: Customer adds items to cart
2. **Sale Order**: Customer confirms order (creates reservations)
3. **Invoice**: Auto-generated with GST calculation
4. **Payment**: Razorpay or cash, supports partial payments
5. **Pickup**: Vendor confirms product pickup
6. **Active**: Product with customer
7. **Return**: Vendor confirms return, calculates late fees
8. **Completed**: Order closed

### Late Fee Calculation
Automatic late fee calculation based on:
- Fixed fee per day
- Percentage of rental amount per day
- Configurable in company settings

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

Start the server and access the interactive API docs at `/api/docs` to test endpoints.

## Production Deployment

1. Set `DEBUG=False` in config
2. Use production WSGI server (gunicorn)
3. Set up proper MySQL credentials
4. Configure SSL certificates
5. Set strong SECRET_KEY
6. Enable CORS only for your frontend domain
7. Set up proper logging
8. Use environment-specific .env files

## License

Proprietary - Rental Management System
