'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { productsApi } from '@/lib/api/endpoints';
import { Product, UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function EditProductContent() {
    const router = useRouter();
    const params = useParams();
    const productId = params.id as string;

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        sku: '',
        dailyRate: '',
        weeklyRate: '',
        monthlyRate: '',
        securityDeposit: '',
        quantityOnHand: '',
        brand: '',
        color: '',
    });

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                const product: Product = await productsApi.getById(parseInt(productId));
                setFormData({
                    name: product.name,
                    description: product.description,
                    sku: product.sku,
                    dailyRate: product.dailyRate?.toString() || '',
                    weeklyRate: product.weeklyRate?.toString() || '',
                    monthlyRate: product.monthlyRate?.toString() || '',
                    securityDeposit: product.securityDeposit?.toString() || '',
                    quantityOnHand: product.quantityOnHand?.toString() || '',
                    brand: product.brand || '',
                    color: product.color || '',
                });
            } catch (error: any) {
                toast.error('Failed to load product');
                router.push('/vendor/products');
            } finally {
                setLoading(false);
            }
        };

        if (productId) {
            fetchProduct();
        }
    }, [productId, router]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const productFormData = new FormData();
            productFormData.append('name', formData.name);
            productFormData.append('description', formData.description);
            productFormData.append('sku', formData.sku);
            productFormData.append('daily_rate', formData.dailyRate);
            productFormData.append('weekly_rate', formData.weeklyRate || '0');
            productFormData.append('monthly_rate', formData.monthlyRate || '0');
            productFormData.append('security_deposit', formData.securityDeposit);
            productFormData.append('quantity_on_hand', formData.quantityOnHand);
            productFormData.append('brand', formData.brand || '');
            productFormData.append('color', formData.color || '');

            await productsApi.update(parseInt(productId), productFormData);
            toast.success('Product updated successfully!');
            router.push('/vendor/products');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update product');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Edit Product</h1>
                        <Link
                            href="/vendor/products"
                            className="text-blue-600 hover:text-blue-700 font-medium"
                        >
                            ← Back to Products
                        </Link>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <form onSubmit={handleSubmit} className="bg-white shadow-sm rounded-lg p-6 space-y-6">
                    {/* Basic Info */}
                    <div>
                        <h2 className="text-lg font-bold mb-4">Basic Information</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Product Name *
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Description *
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    required
                                    rows={4}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    SKU *
                                </label>
                                <input
                                    type="text"
                                    name="sku"
                                    value={formData.sku}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Quantity Available *
                                </label>
                                <input
                                    type="number"
                                    name="quantityOnHand"
                                    value={formData.quantityOnHand}
                                    onChange={handleChange}
                                    required
                                    min="1"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Brand
                                </label>
                                <input
                                    type="text"
                                    name="brand"
                                    value={formData.brand}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Color
                                </label>
                                <input
                                    type="text"
                                    name="color"
                                    value={formData.color}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Pricing */}
                    <div className="border-t pt-6">
                        <h2 className="text-lg font-bold mb-4">Pricing</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Daily Rate (₹) *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="dailyRate"
                                    value={formData.dailyRate}
                                    onChange={handleChange}
                                    required
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Weekly Rate (₹)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="weeklyRate"
                                    value={formData.weeklyRate}
                                    onChange={handleChange}
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Monthly Rate (₹)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="monthlyRate"
                                    value={formData.monthlyRate}
                                    onChange={handleChange}
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Security Deposit (₹) *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="securityDeposit"
                                    value={formData.securityDeposit}
                                    onChange={handleChange}
                                    required
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Submit */}
                    <div className="flex justify-end space-x-4 pt-4 border-t">
                        <Link
                            href="/vendor/products"
                            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </Link>
                        <button
                            type="submit"
                            disabled={submitting}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            {submitting ? 'Updating...' : 'Update Product'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function EditProduct() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR, UserRole.ADMIN]}>
            <EditProductContent />
        </ProtectedRoute>
    );
}
