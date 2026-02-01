'use client';

import { useState, useEffect } from 'react';
import { dashboardApi, ordersApi } from '@/lib/api/endpoints';
import { ProtectedRoute, useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types';
import Link from 'next/link';
import toast from 'react-hot-toast';

function VendorDashboardContent() {
    const { logout, user } = useAuth();
    const [stats, setStats] = useState<any>(null);
    const [pendingPickups, setPendingPickups] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsData, pickupsData] = await Promise.all([
                dashboardApi.getVendorStats(),
                ordersApi.getPendingPickups(),
            ]);
            setStats(statsData);
            setPendingPickups(pickupsData?.items || (Array.isArray(pickupsData) ? pickupsData : []));
        } catch (error) {
            console.error('Dashboard error:', error);
            setStats({});
            setPendingPickups([]);
        } finally {
            setLoading(false);
        }
    };

    const handleMarkPickup = async (orderId: number) => {
        try {
            await ordersApi.markPickup(orderId, { picked_up_by: 'Customer', notes: 'Direct from dashboard' });
            toast.success('Order marked as picked up');
            // Remove from the list after marking as picked up
            setPendingPickups(prev => prev.filter(o => o.id !== orderId));
            // Also update stats if possible (decrement pending pickups)
            if (stats) {
                setStats({
                    ...stats,
                    pending_pickups: (stats.pending_pickups || 1) - 1,
                    active_rentals: (stats.active_rentals || 0) + 1
                });
            }
        } catch (error) {
            toast.error('Failed to mark pickup');
            fetchData();
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
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Vendor Dashboard</h1>
                        <div className="flex gap-4 items-center">
                            <Link
                                href="/vendor/products"
                                className="text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Manage Products
                            </Link>
                            <Link
                                href="/vendor/orders"
                                className="text-blue-600 hover:text-blue-700 font-medium"
                            >
                                View Orders
                            </Link>
                            <span className="text-gray-600 text-sm">
                                {user?.first_name} {user?.last_name}
                            </span>
                            <button
                                onClick={logout}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Revenue</h3>
                        <p className="text-3xl font-bold text-blue-600">
                            ₹{(stats?.total_revenue || stats?.totalRevenue || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Active Rentals</h3>
                        <p className="text-3xl font-bold text-green-600">
                            {(stats?.active_rentals || stats?.activeRentals || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Pending Pickups</h3>
                        <p className="text-3xl font-bold text-purple-600">
                            {(stats?.pending_pickups || stats?.pendingPickups || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Overdue Returns</h3>
                        <p className="text-3xl font-bold text-orange-600">
                            {(stats?.overdue_returns || stats?.overdueReturns || 0).toLocaleString()}
                        </p>
                    </div>
                </div>

                {/* Pending Pickups */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold text-gray-900">Pending Pickups</h2>
                        <Link href="/vendor/orders" className="text-blue-600 hover:underline text-sm">
                            View All
                        </Link>
                    </div>
                    {pendingPickups.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No pending pickups</p>
                    ) : (
                        <div className="space-y-4">
                            {pendingPickups.slice(0, 5).map((order) => (
                                <div key={order.id} className="flex justify-between items-center border-b pb-4">
                                    <div>
                                        <h3 className="font-medium text-gray-900">
                                            Order #{order.order_number || order.orderNumber || order.id}
                                        </h3>
                                        <p className="text-sm text-gray-500">
                                            Pickup: {order.rental_start_date ? new Date(order.rental_start_date).toLocaleDateString() : 'N/A'}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => handleMarkPickup(order.id)}
                                        className="text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg text-sm font-medium transition"
                                    >
                                        Mark Pickup
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                    <Link
                        href="/vendor/products/new"
                        className="bg-blue-600 text-white rounded-lg p-6 hover:bg-blue-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">+</div>
                        <h3 className="font-semibold">Add New Product</h3>
                    </Link>
                    <Link
                        href="/vendor/orders"
                        className="bg-green-600 text-white rounded-lg p-6 hover:bg-green-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">📦</div>
                        <h3 className="font-semibold">Manage Orders</h3>
                    </Link>
                    <Link
                        href="/vendor/reports"
                        className="bg-purple-600 text-white rounded-lg p-6 hover:bg-purple-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">📊</div>
                        <h3 className="font-semibold">View Reports</h3>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function VendorDashboard() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR]}>
            <VendorDashboardContent />
        </ProtectedRoute>
    );
}
