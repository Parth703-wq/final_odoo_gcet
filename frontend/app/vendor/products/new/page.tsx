'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { productsApi, categoriesApi } from '@/lib/api/endpoints';
import { UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function NewProductContent() {
    const router = useRouter();
    const [submitting, setSubmitting] = useState(false);
    const [categories, setCategories] = useState<any[]>([]);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        sku: '',
        category_id: '',
        rental_price_daily: '',
        rental_price_weekly: '',
        rental_price_monthly: '',
        security_deposit: '',
        quantity_on_hand: '',
        brand: '',
        color: '',
    });

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const data = await categoriesApi.list();
            setCategories(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Failed to load categories', error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const productData = {
                name: formData.name,
                description: formData.description,
                sku: formData.sku,
                category_id: formData.category_id ? parseInt(formData.category_id) : null,
                rental_price_daily: parseFloat(formData.rental_price_daily) || 0,
                rental_price_weekly: parseFloat(formData.rental_price_weekly) || 0,
                rental_price_monthly: parseFloat(formData.rental_price_monthly) || 0,
                security_deposit: parseFloat(formData.security_deposit) || 0,
                quantity_on_hand: parseInt(formData.quantity_on_hand) || 1,
                brand: formData.brand || '',
                color: formData.color || '',
                is_published: true,
                is_rentable: true,
            };

            await productsApi.create(productData);
            toast.success('Product created successfully!');
            router.push('/vendor/products');
        } catch (error: any) {
            console.error('Create product error:', error);
            toast.error(error.response?.data?.detail || 'Failed to create product');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Add New Product</h1>
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
                        <h2 className="text-lg font-bold text-blue-600 mb-4">Basic Information</h2>
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
                                    placeholder="e.g., PS5 Gaming Console"
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
                                    placeholder="Describe your product..."
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
                                    placeholder="PS5-001"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Category *
                                </label>
                                <select
                                    name="category_id"
                                    value={formData.category_id}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Select Category</option>
                                    {categories.map((cat) => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Quantity Available *
                                </label>
                                <input
                                    type="number"
                                    name="quantity_on_hand"
                                    value={formData.quantity_on_hand}
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
                                    placeholder="Sony"
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
                                    placeholder="Black"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Pricing */}
                    <div className="border-t pt-6">
                        <h2 className="text-lg font-bold text-green-600 mb-4">Rental Pricing (₹)</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Daily Rate (₹) *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="rental_price_daily"
                                    value={formData.rental_price_daily}
                                    onChange={handleChange}
                                    required
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Weekly Rate (₹)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="rental_price_weekly"
                                    value={formData.rental_price_weekly}
                                    onChange={handleChange}
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="3000"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Monthly Rate (₹)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="rental_price_monthly"
                                    value={formData.rental_price_monthly}
                                    onChange={handleChange}
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="10000"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Security Deposit (₹) *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="security_deposit"
                                    value={formData.security_deposit}
                                    onChange={handleChange}
                                    required
                                    min="0"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="5000"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Submit */}
                    <div className="border-t pt-6 flex gap-4">
                        <button
                            type="submit"
                            disabled={submitting}
                            className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                        >
                            {submitting ? 'Creating...' : 'Create Product'}
                        </button>
                        <Link
                            href="/vendor/products"
                            className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function NewProduct() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR, UserRole.ADMIN]}>
            <NewProductContent />
        </ProtectedRoute>
    );
}
