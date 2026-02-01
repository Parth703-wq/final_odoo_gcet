'use client';

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api/endpoints';
import { Coupon, UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function CouponsContent() {
    const [coupons, setCoupons] = useState<Coupon[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState<Partial<Coupon>>({
        code: '',
        description: '',
        discount_type: 'percentage',
        discount_value: 0,
        min_order_value: 0,
        usage_limit: undefined,
        valid_from: new Date().toISOString().split('T')[0],
        valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        is_active: true
    });

    useEffect(() => {
        fetchCoupons();
    }, []);

    const fetchCoupons = async () => {
        try {
            const data = await adminApi.listCoupons();
            setCoupons(Array.isArray(data) ? data : []);
        } catch (error) {
            toast.error('Failed to load coupons');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? (value === '' ? undefined : parseFloat(value)) : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Format dates as ISO datetime strings for backend
            const payload = {
                code: formData.code,
                description: formData.description || '',
                discount_type: formData.discount_type,
                discount_value: Number(formData.discount_value) || 0,
                min_order_value: Number(formData.min_order_value) || 0,
                usage_limit: formData.usage_limit ? Number(formData.usage_limit) : null,
                per_user_limit: 1,
                valid_from: formData.valid_from ? new Date(formData.valid_from).toISOString() : null,
                valid_until: formData.valid_until ? new Date(formData.valid_until).toISOString() : null,
                is_active: formData.is_active ?? true,
            };
            console.log('Creating coupon with payload:', JSON.stringify(payload, null, 2));
            const result = await adminApi.createCoupon(payload);
            console.log('Coupon created:', result);
            toast.success('Coupon created successfully');
            setShowForm(false);
            setFormData({
                code: '',
                description: '',
                discount_type: 'percentage',
                discount_value: 0,
                min_order_value: 0,
                usage_limit: undefined,
                valid_from: new Date().toISOString().split('T')[0],
                valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                is_active: true
            });
            fetchCoupons();
        } catch (error: any) {
            console.error('Coupon creation error - Full error:', error);
            console.error('Coupon creation error - Response:', error.response);
            console.error('Coupon creation error - Data:', error.response?.data);
            console.error('Coupon creation error - Status:', error.response?.status);
            toast.error(error.response?.data?.detail || error.message || 'Failed to create coupon');
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this coupon?')) return;
        try {
            await adminApi.deleteCoupon(id);
            toast.success('Coupon deleted successfully');
            fetchCoupons();
        } catch (error) {
            toast.error('Failed to delete coupon');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Coupon Management</h1>
                        <div className="flex gap-4">
                            <button
                                onClick={() => setShowForm(!showForm)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                {showForm ? 'Cancel' : '+ New Coupon'}
                            </button>
                            <Link
                                href="/admin/dashboard"
                                className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
                            >
                                ← Dashboard
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {showForm && (
                    <form onSubmit={handleSubmit} className="bg-white shadow-sm rounded-lg p-6 mb-6">
                        <h2 className="text-xl font-bold mb-4">Create New Coupon</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Coupon Code *</label>
                                <input
                                    type="text"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    placeholder="SAVE20"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Discount Type *</label>
                                <select
                                    name="discount_type"
                                    value={formData.discount_type}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="percentage">Percentage</option>
                                    <option value="fixed">Fixed Amount</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Discount Value * ({formData.discount_type === 'percentage' ? '%' : '₹'})
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="discount_value"
                                    value={formData.discount_value}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Min Order Value (₹)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="min_order_value"
                                    value={formData.min_order_value || ''}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Max Usage Count (Optional)</label>
                                <input
                                    type="number"
                                    name="usage_limit"
                                    value={formData.usage_limit || ''}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Valid From *</label>
                                <input
                                    type="date"
                                    name="valid_from"
                                    value={formData.valid_from}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Valid Until *</label>
                                <input
                                    type="date"
                                    name="valid_until"
                                    value={formData.valid_until}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        </div>
                        <div className="mt-4 flex justify-end">
                            <button
                                type="submit"
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Create Coupon
                            </button>
                        </div>
                    </form>
                )}

                <div className="bg-white shadow-sm rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discount</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min Order</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valid Until</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {coupons.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                                        <div className="text-4xl mb-2">🎟️</div>
                                        <p>No coupons yet. Create one!</p>
                                    </td>
                                </tr>
                            ) : (
                                coupons.map((coupon) => (
                                    <tr key={coupon.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap font-mono font-bold text-blue-600">
                                            {coupon.code}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {coupon.discount_type === 'percentage' ? `${coupon.discount_value}%` : `₹${coupon.discount_value}`}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {coupon.min_order_value ? `₹${coupon.min_order_value}` : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {coupon.usage_count} / {coupon.usage_limit || '∞'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {coupon.valid_until ? new Date(coupon.valid_until).toLocaleDateString() : '∞'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${coupon.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {coupon.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <button
                                                onClick={() => handleDelete(coupon.id)}
                                                className="text-red-600 hover:text-red-900"
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default function Coupons() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
            <CouponsContent />
        </ProtectedRoute>
    );
}
