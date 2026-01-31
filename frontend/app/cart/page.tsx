'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ordersApi } from '@/lib/api/endpoints';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { formatErrorMessage } from '@/lib/utils/errors';

interface CartResponse {
    order: any | null;
    item_count: number;
    subtotal: number;
    tax_amount: number;
    total_amount: number;
}

export default function CartPage() {
    const { user } = useAuth();
    const router = useRouter();
    const [cart, setCart] = useState<CartResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            router.push('/login');
            return;
        }
        fetchCart();
    }, [user]);

    const fetchCart = async () => {
        try {
            const data = await ordersApi.getCart();
            setCart(data);
        } catch (error) {
            console.error('Failed to load cart');
            setCart({ order: null, item_count: 0, subtotal: 0, tax_amount: 0, total_amount: 0 });
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveItem = async (itemId: number) => {
        try {
            await ordersApi.removeFromCart(itemId);
            toast.success('Item removed from cart');
            fetchCart();
        } catch (error) {
            toast.error('Failed to remove item');
        }
    };

    const handleCheckout = async () => {
        if (!cart?.order || !cart.order.items || cart.order.items.length === 0) {
            toast.error('Cart is empty');
            return;
        }

        try {
            router.push('/checkout/' + cart.order.id);
        } catch (error: any) {
            toast.error(formatErrorMessage(error));
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    const order = cart?.order;
    const items = order?.items || [];

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Shopping Cart</h1>
                        <Link href="/browse" className="text-blue-600 hover:underline">
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {items.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
                        <p className="text-gray-600 mb-6">Add some products to get started</p>
                        <Link
                            href="/browse"
                            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700"
                        >
                            Browse Products
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Cart Items */}
                        <div className="lg:col-span-2 space-y-4">
                            {items.map((item: any) => (
                                <div key={item.id} className="bg-white rounded-lg shadow-sm p-6">
                                    <div className="flex justify-between">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-gray-900 text-lg">
                                                {item.product_name || item.productName || 'Product'}
                                            </h3>
                                            <p className="text-sm text-gray-500 mt-1">
                                                {item.rental_start_date ? new Date(item.rental_start_date).toLocaleDateString() : 'N/A'} - {item.rental_end_date ? new Date(item.rental_end_date).toLocaleDateString() : 'N/A'}
                                            </p>
                                            <div className="mt-3">
                                                <span className="text-gray-600">Quantity: {item.quantity}</span>
                                                <span className="mx-4">•</span>
                                                <span className="text-gray-600">₹{item.unit_price || item.unitPrice || 0}/day</span>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-2xl font-bold text-gray-900">₹{item.line_total || item.lineTotal || 0}</div>
                                            <button
                                                onClick={() => handleRemoveItem(item.id)}
                                                className="mt-2 text-sm text-red-600 hover:text-red-700"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Order Summary */}
                        <div>
                            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
                                <div className="space-y-3 mb-6">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Subtotal</span>
                                        <span className="font-medium">₹{cart?.subtotal || order?.subtotal || 0}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Tax</span>
                                        <span className="font-medium">₹{cart?.tax_amount || order?.tax_amount || 0}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Security Deposit</span>
                                        <span className="font-medium">₹{order?.deposit_amount || 0}</span>
                                    </div>
                                    <div className="border-t pt-3">
                                        <div className="flex justify-between">
                                            <span className="font-semibold text-gray-900">Total</span>
                                            <span className="text-2xl font-bold text-blue-600">₹{cart?.total_amount || order?.total_amount || 0}</span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={handleCheckout}
                                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                                >
                                    Proceed to Checkout
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
