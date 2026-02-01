import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to add the JWT token to headers
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const authApi = {
    login: async (data: any) => {
        const response = await api.post('/auth/login', data);
        return response.data;
    },
    signupCustomer: async (data: any) => {
        const response = await api.post('/auth/signup/customer', data);
        return response.data;
    },
    signupVendor: async (data: any) => {
        const response = await api.post('/auth/signup/vendor', data);
        return response.data;
    },
    getMe: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },
};

export const productsApi = {
    list: async (params?: any) => {
        const response = await api.get('/products', { params });
        return response.data;
    },
    getById: async (id: number) => {
        const response = await api.get(`/products/${id}`);
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post('/products', data);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put(`/products/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/products/${id}`);
        return response.data;
    },
    getVendorProducts: async (params?: any) => {
        const response = await api.get('/products/vendor', { params });
        return response.data;
    },
    togglePublish: async (id: number) => {
        const response = await api.post(`/products/${id}/toggle-publish`);
        return response.data;
    },
    checkAvailability: async (data: any) => {
        const response = await api.post('/products/check-availability', data);
        return response.data;
    },
};

export const categoriesApi = {
    list: async () => {
        const response = await api.get('/products/categories');
        return response.data;
    },
};

export const ordersApi = {
    list: async (params?: any) => {
        const response = await api.get('/orders', { params });
        return response.data;
    },
    getById: async (id: number) => {
        const response = await api.get(`/orders/${id}`);
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post('/orders', data);
        return response.data;
    },
    getCart: async () => {
        const response = await api.get('/orders/cart');
        return response.data;
    },
    addToCart: async (data: any) => {
        const response = await api.post('/orders/cart/add', data);
        return response.data;
    },
    removeFromCart: async (itemId: number) => {
        const response = await api.delete(`/orders/cart/item/${itemId}`);
        return response.data;
    },
    confirmOrder: async (id: number, data: any) => {
        const response = await api.post(`/orders/${id}/confirm`, data);
        return response.data;
    },
    markPickup: async (id: number, data: any) => {
        const response = await api.post(`/orders/${id}/pickup`, data);
        return response.data;
    },
    markReturn: async (id: number, data: any) => {
        const response = await api.post(`/orders/${id}/return`, data);
        return response.data;
    },
    cancelOrder: async (id: number, notes?: string) => {
        const response = await api.post(`/orders/${id}/cancel`, { notes });
        return response.data;
    },
    getPendingPickups: async () => {
        const response = await api.get('/orders/vendor/pending-pickups');
        return response.data;
    },
    getUpcomingReturns: async (days: number = 7) => {
        const response = await api.get('/orders/vendor/upcoming-returns', { params: { days } });
        return response.data;
    },
    getOverdue: async () => {
        const response = await api.get('/orders/vendor/overdue');
        return response.data;
    }
};

export const invoicesApi = {
    list: async (params?: any) => {
        const response = await api.get('/invoices', { params });
        return response.data;
    },
    getById: async (id: number) => {
        const response = await api.get(`/invoices/${id}`);
        return response.data;
    },
    get: async (id: number) => {
        const response = await api.get(`/invoices/${id}`);
        return response.data;
    },
    post: async (id: number) => {
        const response = await api.post(`/invoices/${id}/post`);
        return response.data;
    },
    pay: async (id: number, data: any) => {
        const response = await api.post(`/invoices/${id}/pay`, data);
        return response.data;
    },
};

export const dashboardApi = {
    getVendorStats: async () => {
        const response = await api.get('/dashboard/vendor');
        return response.data;
    },
    getAdminStats: async () => {
        const response = await api.get('/dashboard/admin');
        return response.data;
    },
    getRevenueChart: async (days: number = 30) => {
        const response = await api.get('/dashboard/revenue-chart', { params: { days } });
        return response.data;
    },
    getTopProducts: async (limit: number = 10) => {
        const response = await api.get('/dashboard/top-products', { params: { limit } });
        return response.data;
    },
    getVendorPerformance: async (limit: number = 10) => {
        const response = await api.get('/dashboard/vendor-performance', { params: { limit } });
        return response.data;
    },
};

export const adminApi = {
    listUsers: async (params?: any) => {
        const response = await api.get('/admin/users', { params });
        return response.data;
    },
    listVendors: async () => {
        const response = await api.get('/admin/vendors');
        return response.data;
    },
    toggleUserStatus: async (userId: number, status: boolean) => {
        const response = await api.post(`/admin/users/${userId}/toggle-status`, null, {
            params: { is_active: status }
        });
        return response.data;
    },
    // Coupons
    listCoupons: async () => {
        const response = await api.get('/admin/coupons');
        return response.data;
    },
    createCoupon: async (data: any) => {
        const response = await api.post('/admin/coupons', data);
        return response.data;
    },
    deleteCoupon: async (id: number) => {
        const response = await api.delete(`/admin/coupons/${id}`);
        return response.data;
    },
    // Export Reports
    exportOrders: async () => {
        const response = await api.get('/admin/export/orders', { responseType: 'text' });
        return response.data;
    },
    exportInvoices: async () => {
        const response = await api.get('/admin/export/invoices', { responseType: 'text' });
        return response.data;
    },
};

export const reviewsApi = {
    createReview: async (data: { product_id: number, order_id: number, rating: number, comment?: string }) => {
        const response = await api.post('/reviews', data);
        return response.data;
    },
    getProductReviews: async (productId: number) => {
        const response = await api.get(`/reviews/product/${productId}`);
        return response.data;
    },
    getOrderReviews: async (orderId: number) => {
        const response = await api.get(`/reviews/order/${orderId}`);
        return response.data;
    }
};

export const complaintsApi = {
    create: async (data: { order_id: number, product_id: number, subject: string, description: string }) => {
        const response = await api.post('/complaints', data);
        return response.data;
    },
    list: async () => {
        const response = await api.get('/complaints');
        return response.data;
    },
    update: async (id: number, data: { status?: string, admin_notes?: string }) => {
        const response = await api.patch(`/complaints/${id}`, data);
        return response.data;
    }
};

export const paymentsApi = {
    createRazorpayOrder: async (data: { amount: number, order_id?: number, invoice_id?: number }) => {
        const response = await api.post('/payments/razorpay/order', data);
        return response.data;
    },
    verifyPayment: async (data: { razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string }) => {
        const response = await api.post('/payments/razorpay/verify', data);
        return response.data;
    },
    getMyPayments: async () => {
        const response = await api.get('/payments/my-payments');
        return response.data;
    }
};

export default {
    auth: authApi,
    products: productsApi,
    categories: categoriesApi,
    orders: ordersApi,
    invoices: invoicesApi,
    dashboard: dashboardApi,
    admin: adminApi,
    reviews: reviewsApi,
    complaints: complaintsApi,
    payments: paymentsApi,
};
