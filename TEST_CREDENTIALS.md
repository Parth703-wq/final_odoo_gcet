# Test Account Credentials

## Login at: http://localhost:3000/login

---

## 🔐 Test Accounts

### Administrator Account
- **Email:** `admin@rental.com`
- **Password:** `Admin@123`
- **Access:** Full system control

**What You Can Do:**
- View system-wide statistics
- Manage all users (activate/deactivate)
- Configure system settings
- Create discount coupons
- View all orders and products
- Access admin dashboard at `/admin/dashboard`

---

### Vendor Account
- **Email:** `vendor@rental.com`
- **Password:** `Vendor@123`
- **Company:** Tech Rentals Pvt Ltd
- **Access:** Product & order management

**What You Can Do:**
- Add, edit, delete products
- View vendor-specific orders
- Mark products as picked up/returned
- View revenue statistics
- Export reports
- Access vendor dashboard at `/vendor/dashboard`

---

### Customer Account
- **Email:** `customer@rental.com`
- **Password:** `Customer@123`
- **Access:** Browse & rent products

**What You Can Do:**
- Browse product catalog
- Filter products by category
- Add products to cart
- Checkout and pay (Razorpay test mode)
- View order history
- Track order status
- Browse products at `/browse`

---

## 🧪 Testing Flow

### 1. Test as Customer
1. Login with `customer@rental.com / Customer@123`
2. Browse products at http://localhost:3000/browse
3. Click on any product to view details
4. Select rental dates and quantity
5. Add to cart
6. View cart and proceed to checkout
7. Complete payment (Razorpay test mode)
8. View your orders

### 2. Test as Vendor  
1. Login with `vendor@rental.com / Vendor@123`
2. View dashboard statistics
3. Add new products (click "Add New Product")
4. View and manage orders
5. Mark orders as picked up/returned

### 3. Test as Admin
1. Login with `admin@rental.com / Admin@123`
2. View system-wide statistics
3. Manage users (click on users table)
4. Activat/deactivate user accounts
5. Configure system settings

---

## 📝 Notes

- **Backend:** Running on http://localhost:8000
- **Frontend:** Running on http://localhost:3000
- **API Docs:** http://localhost:8000/docs

**Note:** Since no products have been added yet, you'll need to login as vendor first and create some products to test the full customer flow.

---

## 🚀 Quick Start

1. **Backend** - Already running on port 8000
2. **Frontend** - Already running on port 3000
3. **Test Accounts** - Created and ready to use!

Just open http://localhost:3000/login and start testing!
