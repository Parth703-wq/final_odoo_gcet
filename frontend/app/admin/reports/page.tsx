'use client';

import { useState, useEffect } from 'react';
import { adminApi, productsApi, ordersApi } from '@/lib/api/endpoints';
import { UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function ReportsContent() {
    const [exporting, setExporting] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalUsers: 0,
        customers: 0,
        vendors: 0,
        admins: 0,
        totalProducts: 0,
        activeProducts: 0,
        totalOrders: 0,
        pendingOrders: 0,
        completedOrders: 0,
    });

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const [usersRes, productsRes, ordersRes] = await Promise.all([
                adminApi.listUsers(),
                productsApi.list(),
                ordersApi.list(),
            ]);

            // Extract items from paginated responses
            const usersList = usersRes?.items || (Array.isArray(usersRes) ? usersRes : []);
            const productsList = productsRes?.items || (Array.isArray(productsRes) ? productsRes : []);
            const ordersList = ordersRes?.items || (Array.isArray(ordersRes) ? ordersRes : []);

            console.log('Fetched data:', { usersList, productsList, ordersList });

            setStats({
                totalUsers: usersList.length,
                customers: usersList.filter((u: any) => u.role === 'customer').length,
                vendors: usersList.filter((u: any) => u.role === 'vendor').length,
                admins: usersList.filter((u: any) => u.role === 'admin').length,
                totalProducts: productsList.length,
                activeProducts: productsList.filter((p: any) => p.is_published || p.isPublished).length,
                totalOrders: ordersList.length,
                pendingOrders: ordersList.filter((o: any) => o.status === 'pending' || o.status === 'quotation' || o.status === 'cart').length,
                completedOrders: ordersList.filter((o: any) => o.status === 'completed' || o.status === 'returned').length,
            });
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async (type: 'orders' | 'invoices') => {
        setExporting(type);
        try {
            const data = type === 'orders'
                ? await adminApi.exportOrders()
                : await adminApi.exportInvoices();

            // Create CSV download
            const blob = new Blob([data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            toast.success(`${type} exported successfully`);
        } catch (error) {
            toast.error(`Failed to export ${type}`);
        } finally {
            setExporting(null);
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
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">📊 Reports & Analytics</h1>
                        <Link
                            href="/admin/dashboard"
                            className="text-blue-600 hover:text-blue-700 font-medium"
                        >
                            ← Back to Dashboard
                        </Link>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Overview Section */}
                <div className="mb-8">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">📈 Platform Overview</h2>

                    {/* Users Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-blue-100 text-sm">Total Users</p>
                                    <p className="text-4xl font-bold">{stats.totalUsers}</p>
                                </div>
                                <div className="text-5xl opacity-50">👥</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-green-100 text-sm">Customers</p>
                                    <p className="text-4xl font-bold">{stats.customers}</p>
                                </div>
                                <div className="text-5xl opacity-50">🛒</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-purple-100 text-sm">Vendors</p>
                                    <p className="text-4xl font-bold">{stats.vendors}</p>
                                </div>
                                <div className="text-5xl opacity-50">🏪</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-orange-100 text-sm">Admins</p>
                                    <p className="text-4xl font-bold">{stats.admins}</p>
                                </div>
                                <div className="text-5xl opacity-50">👨‍💼</div>
                            </div>
                        </div>
                    </div>

                    {/* Products & Orders Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white rounded-xl p-6 shadow-md border-l-4 border-blue-500">
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
                                    📦
                                </div>
                                <div>
                                    <p className="text-gray-500 text-sm">Total Products</p>
                                    <p className="text-3xl font-bold text-gray-800">{stats.totalProducts}</p>
                                    <p className="text-sm text-green-600">{stats.activeProducts} active</p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-white rounded-xl p-6 shadow-md border-l-4 border-green-500">
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center text-2xl">
                                    🛍️
                                </div>
                                <div>
                                    <p className="text-gray-500 text-sm">Total Orders</p>
                                    <p className="text-3xl font-bold text-gray-800">{stats.totalOrders}</p>
                                    <p className="text-sm text-orange-600">{stats.pendingOrders} pending</p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-white rounded-xl p-6 shadow-md border-l-4 border-purple-500">
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 bg-purple-100 rounded-full flex items-center justify-center text-2xl">
                                    ✅
                                </div>
                                <div>
                                    <p className="text-gray-500 text-sm">Completed Orders</p>
                                    <p className="text-3xl font-bold text-gray-800">{stats.completedOrders}</p>
                                    <p className="text-sm text-blue-600">
                                        {stats.totalOrders > 0
                                            ? Math.round((stats.completedOrders / stats.totalOrders) * 100)
                                            : 0}% completion rate
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Export Reports Section */}
                <div className="mb-8">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">📥 Export Reports</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Orders Export */}
                        <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
                                    📋
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800">Orders Report</h3>
                                    <p className="text-sm text-gray-500">Export complete order data</p>
                                </div>
                            </div>
                            <p className="text-gray-600 mb-4">
                                Export all order data including customer information, dates, amounts, and statuses.
                            </p>
                            <button
                                onClick={() => handleExport('orders')}
                                disabled={exporting === 'orders'}
                                className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 font-medium shadow-md"
                            >
                                {exporting === 'orders' ? '⏳ Exporting...' : '📥 Export Orders CSV'}
                            </button>
                        </div>

                        {/* Invoices Export */}
                        <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
                                    🧾
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800">Invoices Report</h3>
                                    <p className="text-sm text-gray-500">Export financial data</p>
                                </div>
                            </div>
                            <p className="text-gray-600 mb-4">
                                Export all invoice data including payments, taxes, and billing information.
                            </p>
                            <button
                                onClick={() => handleExport('invoices')}
                                disabled={exporting === 'invoices'}
                                className="w-full px-4 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 font-medium shadow-md"
                            >
                                {exporting === 'invoices' ? '⏳ Exporting...' : '📥 Export Invoices CSV'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Info Section */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center gap-2">
                        <span>💡</span> About Reports
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">📊</span>
                            <div>
                                <p className="font-medium text-blue-900">CSV Format</p>
                                <p className="text-sm text-blue-700">Compatible with Excel, Google Sheets</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">⏱️</span>
                            <div>
                                <p className="font-medium text-blue-900">Real-time Data</p>
                                <p className="text-sm text-blue-700">Current as of export time</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">🔒</span>
                            <div>
                                <p className="font-medium text-blue-900">Complete History</p>
                                <p className="text-sm text-blue-700">All vendors, all time</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function Reports() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
            <ReportsContent />
        </ProtectedRoute>
    );
}
