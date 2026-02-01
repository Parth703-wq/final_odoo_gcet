'use client';

import { useState, useEffect } from 'react';
import { ordersApi } from '@/lib/api/endpoints';
import { Order, UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { reviewsApi } from '@/lib/api/endpoints';
import { Star, MessageSquare, XCircle } from 'lucide-react';

function VendorOrdersContent() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [selectedOrderReviews, setSelectedOrderReviews] = useState<any[]>([]);
    const [isReviewOpen, setIsReviewOpen] = useState(false);
    const [viewingOrderNum, setViewingOrderNum] = useState<string | null>(null);

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
            const updatedOrder = await ordersApi.markPickup(orderId, { picked_up_by: 'Customer', notes: 'Marked on-time' });
            toast.success('Order marked as picked up');
            // Optimistically update the local state for better responsiveness
            setOrders(prev => prev.map(o => o.id === orderId ? updatedOrder : o));
        } catch (error) {
            toast.error('Failed to update order');
            fetchOrders(); // Fallback to full refresh on error
        }
    };

    const handleMarkReturn = async (orderId: number) => {
        try {
            const updatedOrder = await ordersApi.markReturn(orderId, { returned_by: 'Customer', condition: 'good', notes: '' });
            toast.success('Order marked as returned');
            // Optimistically update the local state
            setOrders(prev => prev.map(o => o.id === orderId ? updatedOrder : o));
        } catch (error) {
            toast.error('Failed to update order');
            fetchOrders(); // Fallback
        }
    };

    const handleViewFeedback = async (orderId: number, orderNum: string) => {
        try {
            const reviews = await reviewsApi.getOrderReviews(orderId);
            setSelectedOrderReviews(reviews.items || []);
            setViewingOrderNum(orderNum);
            setIsReviewOpen(true);
        } catch (error) {
            toast.error('Failed to load feedback');
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
                                            {order.order_number || order.id}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {order.customer?.first_name} {order.customer?.last_name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {new Date(order.rental_start_date).toLocaleDateString()} - {new Date(order.rental_end_date).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap font-bold text-blue-600">
                                            ₹{(order.total_amount || 0).toLocaleString()}
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
                                                    className="text-green-600 hover:text-green-900 font-bold text-[10px] uppercase tracking-wider block"
                                                >
                                                    Mark Return
                                                </button>
                                            )}
                                            {(order.status === 'picked_up' || order.status === 'active' || order.status === 'returned' || order.status === 'completed') && (
                                                <button
                                                    onClick={() => handleViewFeedback(order.id, order.order_number || order.id.toString())}
                                                    className="text-blue-600 hover:text-blue-900 border-2 border-blue-50 px-2 py-0.5 rounded-lg flex items-center gap-1 mt-2 font-bold text-[10px] uppercase tracking-wider transition hover:bg-blue-50 w-fit"
                                                >
                                                    <MessageSquare className="w-3 h-3" /> Feedback
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

            {/* View Feedback Modal */}
            {isReviewOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="bg-indigo-600 p-8 text-white relative">
                            <button
                                onClick={() => setIsReviewOpen(false)}
                                className="absolute top-4 right-4 text-white/50 hover:text-white"
                            >
                                <XCircle className="w-6 h-6" />
                            </button>
                            <h2 className="text-2xl font-black">Customer Feedback</h2>
                            <p className="text-indigo-100 text-sm mt-1">Order #{viewingOrderNum}</p>
                        </div>

                        <div className="p-8 space-y-6 max-h-[60vh] overflow-y-auto">
                            {selectedOrderReviews.length === 0 ? (
                                <div className="text-center py-8">
                                    <MessageSquare className="w-12 h-12 text-gray-100 mx-auto mb-2" />
                                    <p className="text-gray-400 font-bold uppercase text-xs tracking-widest">No feedback left yet</p>
                                </div>
                            ) : (
                                selectedOrderReviews.map((review, idx) => (
                                    <div key={idx} className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <div className="font-bold text-gray-900">{review.customer_name}</div>
                                                <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
                                                    {new Date(review.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                            <div className="flex">
                                                {[1, 2, 3, 4, 5].map((star) => (
                                                    <Star
                                                        key={star}
                                                        className={`w-4 h-4 ${star <= review.rating ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                        <p className="text-gray-600 text-sm italic">"{review.comment}"</p>
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="p-6 bg-gray-50 border-t border-gray-100 flex justify-end">
                            <button
                                onClick={() => setIsReviewOpen(false)}
                                className="px-6 py-2 border-2 border-gray-200 text-gray-500 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-gray-100 transition"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
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
