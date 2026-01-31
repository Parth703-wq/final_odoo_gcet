'use client';

import { useState, useEffect } from 'react';
import { dashboardApi, adminApi } from '@/lib/api/endpoints';
import { ProtectedRoute, useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types';
import Link from 'next/link';
import toast from 'react-hot-toast';

function AdminDashboardContent() {
    const { logout, user } = useAuth();
    const [stats, setStats] = useState<any>(null);
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsData, usersData] = await Promise.all([
                dashboardApi.getAdminStats(),
                adminApi.listUsers(),
            ]);
            const usersList = Array.isArray(usersData) ? usersData : [];
            const s = statsData as any;
            // If stats don't have totalUsers, calculate from usersList
            const finalStats = {
                ...statsData,
                total_users: s?.total_users || s?.totalUsers || usersList.length,
                totalUsers: s?.total_users || s?.totalUsers || usersList.length,
            };
            setStats(finalStats);
            setUsers(usersList.slice(0, 5)); // Show first 5 users
        } catch (error) {
            console.error('Dashboard error:', error);
            setStats({});
            setUsers([]);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleUserStatus = async (userId: number, currentStatus: boolean) => {
        try {
            await adminApi.toggleUserStatus(userId, !currentStatus);
            toast.success('User status updated');
            fetchData();
        } catch (error) {
            toast.error('Failed to update user status');
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
                        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                        <div className="flex gap-4 items-center">
                            <Link
                                href="/admin/users"
                                className="text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Manage Users
                            </Link>
                            <Link
                                href="/admin/settings"
                                className="text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Settings
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
                    {/* Total Revenue */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Revenue</h3>
                        <p className="text-3xl font-bold text-blue-600">
                            ₹{(stats?.total_revenue || stats?.totalRevenue || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Users</h3>
                        <p className="text-3xl font-bold text-green-600">
                            {(stats?.total_users || stats?.totalUsers || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Active Rentals</h3>
                        <p className="text-3xl font-bold text-purple-600">
                            {(stats?.active_rentals || stats?.activeRentals || 0).toLocaleString()}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Orders</h3>
                        <p className="text-3xl font-bold text-orange-600">
                            {(stats?.total_orders || stats?.totalOrders || 0).toLocaleString()}
                        </p>
                    </div>
                </div>

                {/* Recent Users */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold text-gray-900">Recent Users</h2>
                        <Link href="/admin/users" className="text-blue-600 hover:underline text-sm">
                            View All
                        </Link>
                    </div>
                    {users.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No users found</p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left py-3 px-4 font-medium text-gray-700">Name</th>
                                        <th className="text-left py-3 px-4 font-medium text-gray-700">Email</th>
                                        <th className="text-left py-3 px-4 font-medium text-gray-700">Role</th>
                                        <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                                        <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map((u) => (
                                        <tr key={u.id} className="border-b hover:bg-gray-50">
                                            <td className="py-3 px-4">
                                                {u.first_name} {u.last_name}
                                            </td>
                                            <td className="py-3 px-4">{u.email}</td>
                                            <td className="py-3 px-4">
                                                <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                    {u.role}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <span
                                                    className={`px-2 py-1 rounded-full text-xs font-medium ${u.is_active
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-red-100 text-red-800'
                                                        }`}
                                                >
                                                    {u.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <button
                                                    onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                                                >
                                                    {u.is_active ? 'Deactivate' : 'Activate'}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Link
                        href="/admin/users"
                        className="bg-blue-600 text-white rounded-lg p-6 hover:bg-blue-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">👥</div>
                        <h3 className="font-semibold">Manage Users</h3>
                    </Link>
                    <Link
                        href="/admin/settings"
                        className="bg-green-600 text-white rounded-lg p-6 hover:bg-green-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">⚙️</div>
                        <h3 className="font-semibold">Settings</h3>
                    </Link>
                    <Link
                        href="/admin/coupons"
                        className="bg-purple-600 text-white rounded-lg p-6 hover:bg-purple-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">🎟️</div>
                        <h3 className="font-semibold">Manage Coupons</h3>
                    </Link>
                    <Link
                        href="/admin/reports"
                        className="bg-orange-600 text-white rounded-lg p-6 hover:bg-orange-700 transition text-center"
                    >
                        <div className="text-4xl mb-2">📊</div>
                        <h3 className="font-semibold">View Reports</h3>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function AdminDashboard() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
            <AdminDashboardContent />
        </ProtectedRoute>
    );
}
