import api from './client';
import {
    LoginRequest,
    SignupRequest,
    AuthResponse,
    User,
    Product,
    Order,
    Invoice,
    Payment,
    DashboardStats,
    CartItem,
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
    Coupon,
    CompanySettings,
    Category,
} from '@/types';

// ======================
// Authentication API
// ======================

export const authApi = {
    login: async (data: LoginRequest): Promise<AuthResponse> => {
        const response = await api.post('/auth/login', {
            email: data.email,
            password: data.password
        });
        return response.data;
    },

    signupCustomer: async (data: SignupRequest): Promise<AuthResponse> => {
        const response = await api.post('/auth/signup/customer', data);
        return response.data;
    },

    signupVendor: async (data: SignupRequest): Promise<AuthResponse> => {
        const response = await api.post('/auth/signup/vendor', data);
        return response.data;
    },

    getMe: async (): Promise<User> => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    forgotPassword: async (email: string): Promise<{ message: string }> => {
        const response = await api.post('/auth/forgot-password', { email });
        return response.data;
    },

    resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
        const response = await api.post('/auth/reset-password', { token, new_password: newPassword });
        return response.data;
    },

    changePassword: async (currentPassword: string, newPassword: string): Promise<{ message: string }> => {
        const response = await api.post('/auth/change-password', {
            current_password: currentPassword,
            new_password: newPassword,
        });
        return response.data;
    },

    updateProfile: async (data: Partial<User>): Promise<User> => {
        const response = await api.put('/auth/me', data);
        return response.data;
    },
};

// ======================
// Products API
// ======================

export const productsApi = {
    list: async (params?: any): Promise<Product[]> => {
        try {
            const response = await api.get('/products', { params });
            // API returns { items: [...], total, page, per_page, pages }
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch products:', error);
            return [];
        }
    },

    getById: async (id: number): Promise<Product> => {
        const response = await api.get(`/products/${id}`);
        return response.data;
    },

    create: async (data: any): Promise<Product> => {
        const response = await api.post('/products', data);
        return response.data;
    },

    update: async (id: number, data: any): Promise<Product> => {
        const response = await api.put(`/products/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/products/${id}`);
    },

    checkAvailability: async (data: AvailabilityCheckRequest): Promise<AvailabilityCheckResponse> => {
        const response = await api.post('/products/check-availability', data);
        return response.data;
    },

    getVendorProducts: async (): Promise<Product[]> => {
        try {
            const response = await api.get('/products/vendor');
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch vendor products:', error);
            return [];
        }
    },

    togglePublish: async (id: number): Promise<Product> => {
        const response = await api.post(`/products/${id}/toggle-publish`);
        return response.data;
    },
};

// ======================
// Categories API - Backend route is /products/categories
// ======================

export const categoriesApi = {
    list: async (): Promise<Category[]> => {
        try {
            const response = await api.get('/products/categories');
            return Array.isArray(response.data) ? response.data : [];
        } catch (error) {
            console.error('Failed to fetch categories:', error);
            return [];
        }
    },

    create: async (data: { name: string; description?: string; parent_id?: number }): Promise<Category> => {
        const response = await api.post('/products/categories', data);
        return response.data;
    },
};

// ======================
// Orders API
// ======================

export const ordersApi = {
    getCart: async (): Promise<any> => {
        try {
            const response = await api.get('/orders/cart');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch cart:', error);
            return { order: null, item_count: 0, subtotal: 0, tax_amount: 0, total_amount: 0 };
        }
    },

    addToCart: async (item: CartItem): Promise<any> => {
        const response = await api.post('/orders/cart/add', item);
        return response.data;
    },

    removeFromCart: async (itemId: number): Promise<any> => {
        const response = await api.delete(`/orders/cart/item/${itemId}`);
        return response.data;
    },

    createOrder: async (data?: any): Promise<Order> => {
        const response = await api.post('/orders', data || {});
        return response.data;
    },

    list: async (params?: any): Promise<Order[]> => {
        try {
            const response = await api.get('/orders', { params });
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch orders:', error);
            return [];
        }
    },

    getById: async (id: number): Promise<Order> => {
        const response = await api.get(`/orders/${id}`);
        return response.data;
    },

    confirmOrder: async (id: number, data: any): Promise<Order> => {
        const response = await api.post(`/orders/${id}/confirm`, data);
        return response.data;
    },

    markPickup: async (id: number, data: { picked_up_by: string; notes?: string }): Promise<Order> => {
        const response = await api.post(`/orders/${id}/pickup`, data);
        return response.data;
    },

    markReturn: async (id: number, data: any): Promise<Order> => {
        const response = await api.post(`/orders/${id}/return`, data);
        return response.data;
    },

    cancelOrder: async (id: number): Promise<Order> => {
        const response = await api.post(`/orders/${id}/cancel`);
        return response.data;
    },

    getPendingPickups: async (): Promise<Order[]> => {
        try {
            const response = await api.get('/orders/vendor/pending-pickups');
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch pending pickups:', error);
            return [];
        }
    },

    getUpcomingReturns: async (): Promise<Order[]> => {
        try {
            const response = await api.get('/orders/vendor/upcoming-returns');
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch upcoming returns:', error);
            return [];
        }
    },

    getOverdueOrders: async (): Promise<Order[]> => {
        try {
            const response = await api.get('/orders/vendor/overdue');
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch overdue orders:', error);
            return [];
        }
    },
};

// ======================
// Invoices API
// ======================

export const invoicesApi = {
    create: async (orderId: number): Promise<Invoice> => {
        const response = await api.post('/invoices', { order_id: orderId });
        return response.data;
    },

    list: async (params?: any): Promise<Invoice[]> => {
        try {
            const response = await api.get('/invoices', { params });
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch invoices:', error);
            return [];
        }
    },

    getById: async (id: number): Promise<Invoice> => {
        const response = await api.get(`/invoices/${id}`);
        return response.data;
    },

    post: async (id: number): Promise<Invoice> => {
        const response = await api.post(`/invoices/${id}/post`);
        return response.data;
    },

    createRazorpayOrder: async (data: { invoice_id: number; amount: number }): Promise<any> => {
        const response = await api.post('/invoices/payments/create-order', data);
        return response.data;
    },

    verifyPayment: async (data: {
        razorpay_order_id: string;
        razorpay_payment_id: string;
        razorpay_signature: string;
        invoice_id: number;
    }): Promise<Payment> => {
        const response = await api.post('/invoices/payments/verify', data);
        return response.data;
    },

    recordCashPayment: async (data: { invoice_id: number; amount: number; notes?: string }): Promise<Payment> => {
        const response = await api.post('/invoices/payments/cash', data);
        return response.data;
    },
};

// ======================
// Dashboard API
// ======================

export const dashboardApi = {
    getAdminStats: async (): Promise<DashboardStats> => {
        try {
            const response = await api.get('/dashboard/admin');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch admin stats:', error);
            return {
                totalRevenue: 0,
                totalOrders: 0,
                activeRentals: 0,
                pendingPickups: 0,
                totalUsers: 0,
                totalProducts: 0,
                overdueReturns: 0,
            };
        }
    },

    getVendorStats: async (): Promise<DashboardStats> => {
        try {
            const response = await api.get('/dashboard/vendor');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch vendor stats:', error);
            return {
                totalRevenue: 0,
                totalOrders: 0,
                activeRentals: 0,
                pendingPickups: 0,
                totalUsers: 0,
                totalProducts: 0,
                overdueReturns: 0,
            };
        }
    },

    getRevenueChart: async (days: number = 30): Promise<any> => {
        try {
            const response = await api.get('/dashboard/revenue-chart', { params: { days } });
            return response.data;
        } catch (error) {
            console.error('Failed to fetch revenue chart:', error);
            return [];
        }
    },

    getTopProducts: async (limit: number = 10): Promise<any> => {
        try {
            const response = await api.get('/dashboard/top-products', { params: { limit } });
            return response.data;
        } catch (error) {
            console.error('Failed to fetch top products:', error);
            return [];
        }
    },

    exportOrders: async (params?: any): Promise<Blob> => {
        const response = await api.get('/dashboard/export/orders', {
            params,
            responseType: 'blob',
        });
        return response.data;
    },

    exportInvoices: async (params?: any): Promise<Blob> => {
        const response = await api.get('/dashboard/export/invoices', {
            params,
            responseType: 'blob',
        });
        return response.data;
    },
};

// =======================
// Admin API
// ======================

export const adminApi = {
    listUsers: async (params?: any): Promise<User[]> => {
        try {
            const response = await api.get('/admin/users', { params });
            if (response.data && response.data.items) {
                return response.data.items;
            }
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch users:', error);
            return [];
        }
    },

    toggleUserStatus: async (userId: number, isActive: boolean): Promise<User> => {
        const response = await api.post(`/admin/users/${userId}/toggle-status`, null, {
            params: { is_active: isActive }
        });
        return response.data;
    },

    getSettings: async (): Promise<CompanySettings | null> => {
        try {
            const response = await api.get('/admin/settings');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch settings:', error);
            return null;
        }
    },

    updateSettings: async (data: Partial<CompanySettings>): Promise<CompanySettings> => {
        const response = await api.put('/admin/settings', data);
        return response.data;
    },

    listCoupons: async (): Promise<Coupon[]> => {
        try {
            const response = await api.get('/admin/coupons');
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch coupons:', error);
            return [];
        }
    },

    createCoupon: async (data: Partial<Coupon>): Promise<Coupon> => {
        const response = await api.post('/admin/coupons', data);
        return response.data;
    },

    deleteCoupon: async (id: number): Promise<void> => {
        await api.delete(`/admin/coupons/${id}`);
    },

    validateCoupon: async (code: string, orderAmount: number): Promise<{ valid: boolean; discount_amount?: number }> => {
        const response = await api.post('/admin/coupons/validate', { code, order_amount: orderAmount });
        return response.data;
    },

    exportOrders: async (): Promise<string> => {
        const response = await api.get('/dashboard/export/orders', {
            responseType: 'text',
        });
        return response.data;
    },

    exportInvoices: async (): Promise<string> => {
        const response = await api.get('/dashboard/export/invoices', {
            responseType: 'text',
        });
        return response.data;
    },
};

// Export all APIs
export default {
    auth: authApi,
    products: productsApi,
    categories: categoriesApi,
    orders: ordersApi,
    invoices: invoicesApi,
    dashboard: dashboardApi,
    admin: adminApi,
};
