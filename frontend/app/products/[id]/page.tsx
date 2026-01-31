'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { productsApi, ordersApi } from '@/lib/api/endpoints';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { formatErrorMessage } from '@/lib/utils/errors';

export default function ProductDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const [product, setProduct] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [addingToCart, setAddingToCart] = useState(false);

    const [formData, setFormData] = useState({
        quantity: 1,
        startDate: '',
        endDate: '',
        rentalPeriod: 'daily',
    });

    useEffect(() => {
        fetchProduct();
    }, [params.id]);

    const fetchProduct = async () => {
        try {
            const data = await productsApi.getById(Number(params.id));
            setProduct(data);
        } catch (error) {
            toast.error('Failed to load product');
        } finally {
            setLoading(false);
        }
    };

    const handleAddToCart = async () => {
        if (!user) {
            toast.error('Please login to add items to cart');
            router.push('/login');
            return;
        }

        if (!formData.startDate || !formData.endDate) {
            toast.error('Please select rental dates');
            return;
        }

        setAddingToCart(true);
        try {
            await ordersApi.addToCart({
                product_id: product.id,
                quantity: formData.quantity,
                rental_start_date: formData.startDate,
                rental_end_date: formData.endDate,
                rental_period_type: formData.rentalPeriod,
            });
            toast.success('Added to cart!');
            router.push('/cart');
        } catch (error: any) {
            toast.error(formatErrorMessage(error));
        } finally {
            setAddingToCart(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!product) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Product not found</h2>
                    <Link href="/browse" className="text-blue-600 hover:underline">
                        Browse Products
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <Link href="/browse" className="text-blue-600 hover:underline">
                        ← Back to Browse
                    </Link>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
                        {/* Product Image */}
                        <div>
                            <div className="aspect-square bg-gray-200 rounded-lg overflow-hidden">
                                {product.image_url ? (
                                    <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="w-full h-full object-cover"
                                    />
                                ) : product.gallery_images && product.gallery_images.length > 0 ? (
                                    <img
                                        src={product.gallery_images[0]}
                                        alt={product.name}
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <div className="flex items-center justify-center h-full text-gray-400">
                                        No Image
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Product Info */}
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
                            <p className="text-gray-600 mb-6">{product.description}</p>

                            {/* Pricing */}
                            <div className="bg-blue-50 rounded-lg p-4 mb-6">
                                <h3 className="font-semibold text-gray-900 mb-2">Rental Pricing</h3>
                                <div className="grid grid-cols-2 gap-2">
                                    {product.rental_price_daily > 0 && (
                                        <div>
                                            <span className="text-2xl font-bold text-blue-600">₹{product.rental_price_daily}</span>
                                            <span className="text-sm text-gray-600">/day</span>
                                        </div>
                                    )}
                                    {product.rental_price_weekly > 0 && (
                                        <div>
                                            <span className="text-xl font-bold text-blue-600">₹{product.rental_price_weekly}</span>
                                            <span className="text-sm text-gray-600">/week</span>
                                        </div>
                                    )}
                                    {product.rental_price_monthly > 0 && (
                                        <div>
                                            <span className="text-xl font-bold text-blue-600">₹{product.rental_price_monthly}</span>
                                            <span className="text-sm text-gray-600">/month</span>
                                        </div>
                                    )}
                                </div>
                                <div className="mt-2 text-sm text-gray-600">
                                    Security Deposit: ₹{product.security_deposit || 0}
                                </div>
                            </div>

                            {/* Rental Form */}
                            <div className="space-y-4 mb-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Quantity
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        max={product.quantity_on_hand || 1}
                                        value={formData.quantity}
                                        onChange={(e) => setFormData({ ...formData, quantity: Number(e.target.value) })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    />
                                    <p className="text-sm text-gray-500 mt-1">{product.quantity_on_hand || 0} available</p>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Start Date
                                        </label>
                                        <input
                                            type="date"
                                            value={formData.startDate}
                                            onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                                            min={new Date().toISOString().split('T')[0]}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            End Date
                                        </label>
                                        <input
                                            type="date"
                                            value={formData.endDate}
                                            onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                                            min={formData.startDate || new Date().toISOString().split('T')[0]}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Rental Period
                                    </label>
                                    <select
                                        value={formData.rentalPeriod}
                                        onChange={(e) => setFormData({ ...formData, rentalPeriod: e.target.value })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="daily">Daily</option>
                                        <option value="weekly">Weekly</option>
                                        <option value="monthly">Monthly</option>
                                    </select>
                                </div>
                            </div>

                            {/* Add to Cart Button */}
                            <button
                                onClick={handleAddToCart}
                                disabled={addingToCart}
                                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
                            >
                                {addingToCart ? 'Adding to Cart...' : 'Add to Cart'}
                            </button>

                            {/* Product Details */}
                            <div className="mt-8 border-t pt-6">
                                <h3 className="font-semibold text-gray-900 mb-3">Product Details</h3>
                                <dl className="space-y-2">
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">SKU:</dt>
                                        <dd className="font-medium">{product.sku}</dd>
                                    </div>
                                    {product.brand && (
                                        <div className="flex justify-between">
                                            <dt className="text-gray-600">Brand:</dt>
                                            <dd className="font-medium">{product.brand}</dd>
                                        </div>
                                    )}
                                    {product.color && (
                                        <div className="flex justify-between">
                                            <dt className="text-gray-600">Color:</dt>
                                            <dd className="font-medium">{product.color}</dd>
                                        </div>
                                    )}
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
