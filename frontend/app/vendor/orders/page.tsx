'use client';

import { useState, useEffect } from 'react';
import { ordersApi } from '@/lib/api/endpoints';
import { Order, UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function VendorOrdersContent() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchOrders();
    }, [filter]);

    const fetchOrders = async () => {
        try {
            const response = await ordersApi.list({ vendor: true });
            setOrders(Array.isArray(response) ? response : (response as any)?.items || []);
        } catch (error) {
            toast.error('Failed to load orders');
        } finally {
            setLoading(false);
        }
    };

    const handleMarkPickup = async (orderId: number) => {
        try {
            await ordersApi.markPickup(orderId, { picked_up_by: 'Customer', notes: '' });
            toast.success('Order marked as picked up');
            fetchOrders();
        } catch (error) {
            toast.error('Failed to update order');
        }
    };

    const handleMarkReturn = async (orderId: number) => {
        try {
            await ordersApi.markReturn(orderId, { returned_by: 'Customer', condition: 'good', notes: '' });
            toast.success('Order marked as returned');
            fetchOrders();
        } catch (error) {
            toast.error('Failed to update order');
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
                        <h1 className="text-2xl font-bold text-gray-900">My Orders</h1>
                        <Link
                            href="/vendor/dashboard"
                            className="text-blue-600 hover:text-blue-700 font-medium"
                        >
                            ← Dashboard
                        </Link>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {orders.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                                        <div className="text-4xl mb-2">📋</div>
                                        <p>No orders yet</p>
                                    </td>
                                </tr>
                            ) : (
                                orders.map((order) => (
                                    <tr key={order.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">
                                            {order.orderNumber}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {order.customer?.first_name} {order.customer?.last_name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {new Date(order.startDate).toLocaleDateString()} - {new Date(order.endDate).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap font-bold text-blue-600">
                                            ₹{order.totalAmount.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${order.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
                                                    order.status === 'picked_up' ? 'bg-green-100 text-green-800' :
                                                        order.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                                                            'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {order.status.replace('_', ' ').toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {order.status === 'confirmed' && (
                                                <button
                                                    onClick={() => handleMarkPickup(order.id)}
                                                    className="text-blue-600 hover:text-blue-900 mr-2"
                                                >
                                                    Mark Pickup
                                                </button>
                                            )}
                                            {order.status === 'picked_up' && (
                                                <button
                                                    onClick={() => handleMarkReturn(order.id)}
                                                    className="text-green-600 hover:text-green-900"
                                                >
                                                    Mark Return
                                                </button>
                                            )}
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

export default function VendorOrders() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR, UserRole.ADMIN]}>
            <VendorOrdersContent />
        </ProtectedRoute>
    );
}
