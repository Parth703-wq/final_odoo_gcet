'use client';

import { useState, useEffect } from 'react';
import { ordersApi } from '@/lib/api/endpoints';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function MyOrdersPage() {
    const { user } = useAuth();
    const [orders, setOrders] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const data = await ordersApi.list();
            setOrders(Array.isArray(data) ? data : []);
        } catch (error) {
            toast.error('Failed to load orders');
            setOrders([]);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        const colors: Record<string, string> = {
            'draft': 'bg-gray-100 text-gray-800',
            'quotation': 'bg-yellow-100 text-yellow-800',
            'confirmed': 'bg-blue-100 text-blue-800',
            'picked_up': 'bg-purple-100 text-purple-800',
            'active': 'bg-green-100 text-green-800',
            'returned': 'bg-indigo-100 text-indigo-800',
            'completed': 'bg-gray-100 text-gray-800',
            'cancelled': 'bg-red-100 text-red-800',
        };
        return colors[status?.toLowerCase()] || 'bg-gray-100 text-gray-800';
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
                        <h1 className="text-2xl font-bold text-gray-900">My Orders</h1>
                        <div className="flex gap-4">
                            <Link href="/browse" className="text-blue-600 hover:underline">
                                Browse Products
                            </Link>
                            <button
                                onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
                                className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium text-sm"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {orders.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">No orders yet</h2>
                        <p className="text-gray-600 mb-6">Start browsing to place your first order</p>
                        <Link
                            href="/browse"
                            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700"
                        >
                            Browse Products
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {orders.map((order) => (
                            <div key={order.id} className="bg-white rounded-lg shadow-sm p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="font-semibold text-lg text-gray-900">
                                            Order #{order.order_number || order.orderNumber || order.id}
                                        </h3>
                                        <p className="text-sm text-gray-500">
                                            {order.created_at ? new Date(order.created_at).toLocaleDateString() : 'N/A'}
                                        </p>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                                        {order.status?.replace('_', ' ') || 'Unknown'}
                                    </span>
                                </div>

                                <div className="border-t pt-4">
                                    <div className="space-y-2 mb-4">
                                        {(order.items || []).map((item: any) => (
                                            <div key={item.id} className="flex justify-between text-sm">
                                                <span className="text-gray-600">
                                                    {item.product_name || item.productName || 'Product'} x{item.quantity}
                                                </span>
                                                <span className="font-medium">₹{item.line_total || item.lineTotal || 0}</span>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="flex justify-between items-center border-t pt-4">
                                        <div>
                                            <span className="text-gray-600">Total: </span>
                                            <span className="text-xl font-bold text-gray-900">₹{order.total_amount || order.totalAmount || 0}</span>
                                        </div>
                                        <Link
                                            href={`/orders/${order.id}`}
                                            className="text-blue-600 hover:text-blue-700 font-medium"
                                        >
                                            View Details →
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
