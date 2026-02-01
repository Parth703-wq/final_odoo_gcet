// TypeScript type definitions for the Rental Management System

// ======================
// User Types
// ======================

export enum UserRole {
    CUSTOMER = "customer",
    VENDOR = "vendor",
    ADMIN = "admin"
}

export interface User {
    id: number;
    email: string;
    first_name: string;  // Backend uses snake_case
    last_name: string;
    phone?: string;
    company_name?: string;
    company_logo?: string;
    gstin?: string;
    address_line1?: string;
    address_line2?: string;
    city?: string;
    state?: string;
    country?: string;
    zip_code?: string;
    role: UserRole;
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
}

// ======================
// Auth Types
// ======================

export interface LoginRequest {
    email: string;
    password: string;
}

export interface SignupRequest {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    role?: UserRole;
    coupon_code?: string;

    // Vendor fields
    company_name?: string;
    gstin?: string;
    address_line1?: string;
    city?: string;
    state?: string;
    zip_code?: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

// ======================
// Product Types
// ======================

export interface Product {
    id: number;
    vendorId: number;
    name: string;
    description: string;
    sku: string;
    categoryId: number | null;

    // Pricing
    costPrice: number;
    salesPrice: number;
    hourlyRate: number | null;
    dailyRate: number;
    weeklyRate: number | null;
    monthlyRate: number | null;
    securityDeposit: number;

    // Inventory
    quantityOnHand: number;
    availableQuantity?: number;

    // Attributes
    brand: string | null;
    color: string | null;

    // Images
    images: string[];

    // Status
    isPublished: boolean;

    // Relationships
    category?: Category;
    vendor?: User;
    variants?: ProductVariant[];
    attributes?: ProductAttribute[];

    createdAt: string;
    updatedAt: string;
}

export interface ProductVariant {
    id: number;
    productId: number;
    variantName: string;
    sku: string;
    quantityOnHand: number;
    priceDifference: number;
    attributes: Record<string, any>;
}

export interface Category {
    id: number;
    name: string;
    description: string | null;
    parentId: number | null;
}

export interface ProductAttribute {
    id: number;
    productId: number;
    attributeName: string;
    attributeValue: string;
}

// ======================
// Order Types
// ======================

export enum OrderStatus {
    DRAFT = "draft",
    QUOTATION = "quotation",
    CONFIRMED = "confirmed",
    PICKED_UP = "picked_up",
    ACTIVE = "active",
    RETURNED = "returned",
    COMPLETED = "completed",
    CANCELLED = "cancelled"
}

export enum DeliveryMethod {
    PICKUP = "pickup",
    DELIVERY = "delivery"
}

export interface Order {
    id: number;
    order_number: string;
    customer_id: number;
    vendor_id: number;

    // Status
    status: OrderStatus;

    // Period
    rental_start_date: string;
    rental_end_date: string;
    rental_period?: string;

    // Amounts
    subtotal: number;
    tax_amount: number;
    security_deposit: number;
    discount_amount: number;
    total_amount: number;

    // Delivery
    delivery_method: string; // Adjusted to string to matches backend
    delivery_address: string | null;
    billing_address: string | null;

    // Items
    items: OrderItem[];

    // Relationships
    customer?: User;
    vendor?: User;
    invoice?: Invoice;

    created_at: string;
    updated_at: string;
}

export interface OrderItem {
    id: number;
    order_id: number;
    product_id: number;
    variant_id: number | null;

    product_name: string;
    product_sku?: string;
    quantity: number;

    unit_price: number;
    line_total: number;
    tax_amount: number;

    // Period
    rental_start_date: string;
    rental_end_date: string;

    product?: Product;
}

// ======================
// Invoice Types
// ======================

export enum InvoiceStatus {
    DRAFT = "draft",
    POSTED = "posted",
    PARTIALLY_PAID = "partially_paid",
    PAID = "paid",
    CANCELLED = "cancelled"
}

export enum PaymentMethod {
    RAZORPAY = "razorpay",
    CARD = "card",
    UPI = "upi",
    NETBANKING = "netbanking",
    CASH = "cash"
}

export interface Invoice {
    id: number;
    invoice_number: string;
    order_id: number;
    vendor_id: number;
    customer_id: number;

    // Status
    status: InvoiceStatus;

    // Amounts
    subtotal: number;
    tax_rate: number;
    cgst: number;
    sgst: number;
    igst: number;
    tax_amount: number;

    discount_amount: number;
    security_deposit: number;
    delivery_charges: number;
    late_fees: number;

    total_amount: number;
    amount_paid: number;
    amount_due: number;

    // Info
    vendor_company_name?: string;
    vendor_gstin?: string;
    customer_name?: string;
    customer_gstin?: string;
    billing_address?: string;
    delivery_address?: string;
    notes?: string;
    terms_conditions?: string;

    // Dates
    invoice_date: string;
    due_date: string;
    rental_start_date: string;
    rental_end_date: string;

    // Items & Payments
    items: InvoiceItem[];
    payments: Payment[];
    customer?: User;

    created_at: string;
}

export interface InvoiceItem {
    id: number;
    invoice_id: number;
    product_name: string;
    product_sku?: string;
    description?: string;
    quantity: number;
    unit: string;
    unit_price: number;
    tax_rate: number;
    tax_amount: number;
    line_total: number;
    rental_start_date?: string;
    rental_end_date?: string;
}

export interface Payment {
    id: number;
    paymentNumber: string;
    invoiceId: number;
    amount: number;
    paymentMethod: PaymentMethod;
    status: string;

    // Razorpay
    razorpayOrderId: string | null;
    razorpayPaymentId: string | null;

    paymentDate: string | null;
    createdAt: string;
}

// ======================
// Dashboard Types
// ======================

export interface DashboardStats {
    totalRevenue: number;
    activeRentals: number;
    pendingPickups: number;
    overdueReturns: number;

    // Admin specific
    totalUsers?: number;
    totalVendors?: number;
    totalProducts?: number;
    totalOrders?: number;
}

export interface RevenueChartData {
    labels: string[];
    data: number[];
}

export interface TopProduct {
    productId: number;
    productName: string;
    rentalCount: number;
    totalRevenue: number;
}

// ======================
// API Response Types
// ======================

export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

export interface ErrorResponse {
    detail: string;
}

// ======================
// Form Types
// ======================

export interface AvailabilityCheckRequest {
    productId: number;
    variantId?: number;
    startDate: string;
    endDate: string;
    quantity: number;
}

export interface AvailabilityCheckResponse {
    available: boolean;
    availableQuantity: number;
    conflicts?: any[];
}

export interface CartItem {
    product_id: number;
    variant_id?: number | null;
    quantity: number;
    rental_start_date: string;
    rental_end_date: string;
    rental_period_type: string;
}

export interface CheckoutRequest {
    deliveryMethod: DeliveryMethod;
    deliveryAddress?: string;
    billingAddress?: string;
    notes?: string;
}

// ======================
// Settings Types
// ======================

export interface CompanySettings {
    id: number;
    companyName: string;
    logo: string | null;
    address: string | null;
    city: string | null;
    state: string | null;
    pincode: string | null;
    phone: string | null;
    email: string | null;
    gstin: string | null;
    gstRate: number;
    lateFeePerDay: number;
    lateFeePercentage: number;
}

export interface Coupon {
    id: number;
    code: string;
    description?: string;
    discount_type: "percentage" | "fixed";
    discount_value: number;
    max_discount?: number;
    min_order_value: number;
    usage_limit?: number;
    per_user_limit: number;
    usage_count: number;
    valid_from?: string;
    valid_until?: string;
    is_active: boolean;
    created_at: string;
}
