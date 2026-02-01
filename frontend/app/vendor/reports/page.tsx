'use client';

import { useState, useEffect } from 'react';
import { dashboardApi } from '@/lib/api/endpoints';
import { ProtectedRoute, useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { TrendingUp, Package, IndianRupee, Download, BarChart2, PieChart as PieChartIcon, Calendar, ArrowUpRight } from 'lucide-react';

/**
 * Enhanced Bar Chart with Gradients and Tooltips
 */
function EnhancedBarChart({ data }: { data: any[] }) {
    if (!data || data.length === 0) {
        return (
            <div className="h-64 flex flex-col items-center justify-center text-gray-400 bg-gray-50/50 rounded-xl border border-dashed border-gray-200">
                <BarChart2 className="w-8 h-8 mb-2 opacity-20" />
                <p className="text-sm">No revenue data for this period</p>
            </div>
        );
    }

    const maxVal = Math.max(...data.map(d => d.revenue || 0), 0);
    const hasData = maxVal > 0;
    const displayMax = hasData ? maxVal : 1000; // Default scale if zero

    return (
        <div className="relative pt-8">
            {/* Y-Axis Label */}
            <div className="absolute top-0 left-0 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                Revenue (₹)
            </div>

            <div className="h-64 flex items-end gap-1.5 px-2 relative group/chart">
                {/* Horizontal Grid Lines */}
                {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
                    <div
                        key={tick}
                        className="absolute left-0 right-0 border-t border-gray-100 pointer-events-none"
                        style={{ bottom: `${tick * 100}%` }}
                    >
                        {tick > 0 && (
                            <span className="absolute -top-2 -left-1 text-[8px] text-gray-300">
                                {Math.round(tick * displayMax)}
                            </span>
                        )}
                    </div>
                ))}

                {data.map((item, id) => {
                    const height = hasData ? ((item.revenue || 0) / displayMax) * 100 : 2; // Minimal height for zero data
                    return (
                        <div key={id} className="flex-1 flex flex-col items-center group relative h-full justify-end">
                            <div
                                className={`w-full rounded-t-lg transition-all duration-500 ease-out cursor-pointer ${item.revenue > 0
                                    ? 'bg-gradient-to-t from-blue-600 to-blue-400 group-hover:from-blue-500 group-hover:to-blue-300'
                                    : 'bg-gray-100 hover:bg-gray-200'
                                    }`}
                                style={{ height: `${height}%` }}
                            >
                                {/* Tooltip */}
                                <div className="opacity-0 group-hover:opacity-100 absolute -top-12 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[10px] py-1.5 px-3 rounded-lg shadow-xl z-20 whitespace-nowrap transition-opacity pointer-events-none">
                                    <div className="font-bold">₹{(item.revenue || 0).toLocaleString()}</div>
                                    <div className="text-[8px] text-gray-400">{item.date}</div>
                                    {/* Arrow */}
                                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-x-4 border-x-transparent border-t-4 border-t-gray-900"></div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
            {!hasData && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <p className="text-xs text-gray-400 font-medium bg-white/80 px-4 py-2 rounded-full shadow-sm border border-gray-100">
                        Waiting for first rental revenue...
                    </p>
                </div>
            )}
        </div>
    );
}

/**
 * Enhanced Pie Chart with Premium Styling
 */
function EnhancedPieChart({ data }: { data: any[] }) {
    if (!data || data.length === 0) {
        return (
            <div className="h-64 flex flex-col items-center justify-center text-gray-400 bg-gray-50/50 rounded-xl border border-dashed border-gray-200">
                <PieChartIcon className="w-8 h-8 mb-2 opacity-20" />
                <p className="text-sm">No rental history to analyze</p>
            </div>
        );
    }

    const total = data.reduce((acc, curr) => acc + (curr.rental_count || 0), 0);
    const hasData = total > 0;

    let currentAngle = 0;
    const colors = [
        '#3B82F6', // Blue
        '#10B981', // Emerald
        '#F59E0B', // Amber
        '#EF4444', // Red
        '#8B5CF6', // Violet
        '#EC4899', // Pink
    ];

    if (!hasData) {
        return (
            <div className="h-64 flex items-center justify-center text-gray-400">
                No rental counts recorded yet.
            </div>
        );
    }

    return (
        <div className="flex flex-col xl:flex-row items-center gap-12 py-6 px-4">
            <div className="relative w-56 h-56 group">
                <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90 filter drop-shadow-lg">
                    {data.map((item, idx) => {
                        const value = item.rental_count || 0;
                        const percentage = (value / total) * 100;

                        // Handle 100% case explicitly as SVG arcs fail with identical start/end points
                        if (percentage >= 99.9) {
                            return (
                                <circle
                                    key={idx}
                                    cx="50"
                                    cy="50"
                                    r="48"
                                    fill={colors[idx % colors.length]}
                                    className="transition-all duration-300 hover:scale-[1.05] origin-center cursor-pointer stroke-white stroke-[0.8]"
                                >
                                    <title>{item.product_name}: {value} rentals (100%)</title>
                                </circle>
                            );
                        }

                        const largeArc = percentage > 50 ? 1 : 0;
                        const startX = 50 + 48 * Math.cos((2 * Math.PI * currentAngle) / 100);
                        const startY = 50 + 48 * Math.sin((2 * Math.PI * currentAngle) / 100);

                        currentAngle += percentage;

                        const endX = 50 + 48 * Math.cos((2 * Math.PI * currentAngle) / 100);
                        const endY = 50 + 48 * Math.sin((2 * Math.PI * currentAngle) / 100);

                        return (
                            <path
                                key={idx}
                                d={`M 50 50 L ${startX} ${startY} A 48 48 0 ${largeArc} 1 ${endX} ${endY} Z`}
                                fill={colors[idx % colors.length]}
                                className="transition-all duration-300 hover:scale-[1.05] origin-center cursor-pointer stroke-white stroke-[0.8]"
                            >
                                <title>{item.product_name}: {value} rentals ({Math.round(percentage)}%)</title>
                            </path>
                        );
                    })}
                </svg>
            </div>

            <div className="flex-1 w-full space-y-3">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Distribution</h4>
                {data.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="flex items-center group/item p-2 rounded-lg hover:bg-gray-50 transition">
                        <div className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ backgroundColor: colors[idx % colors.length] }}></div>
                        <div className="ml-3 flex-1 min-w-0">
                            <div className="text-xs font-bold text-gray-700 truncate">{item.product_name}</div>
                            <div className="w-full bg-gray-100 h-1 rounded-full mt-1.5 overflow-hidden">
                                <div
                                    className="h-full rounded-full transition-all duration-1000"
                                    style={{
                                        width: `${(item.rental_count / total) * 100}%`,
                                        backgroundColor: colors[idx % colors.length]
                                    }}
                                ></div>
                            </div>
                        </div>
                        <div className="ml-4 text-right">
                            <div className="text-xs font-black text-gray-900">{item.rental_count}</div>
                            <div className="text-[10px] text-gray-400">{Math.round((item.rental_count / total) * 100)}%</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function VendorReportsContent() {
    const { user } = useAuth();
    const [revenueData, setRevenueData] = useState<any[]>([]);
    const [topProducts, setTopProducts] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(30);

    useEffect(() => {
        fetchData();
    }, [days]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statsData, revenueRes, topProductsRes] = await Promise.all([
                dashboardApi.getVendorStats(),
                dashboardApi.getRevenueChart(days),
                dashboardApi.getTopProducts(10)
            ]);

            console.log('Dynamic Stats:', statsData);
            console.log('Dynamic Revenue:', revenueRes);
            console.log('Dynamic Products:', topProductsRes);

            setStats(statsData);
            setRevenueData(revenueRes || []);
            setTopProducts(topProductsRes || []);
        } catch (error) {
            console.error('Dynamic Reports error:', error);
            toast.error('Failed to update dynamic reports');
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async (type: 'orders' | 'invoices') => {
        const loadingToast = toast.loading(`Preparing ${type} export...`);
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
            const token = localStorage.getItem('access_token');

            const response = await fetch(`${baseUrl}/dashboard/export/${type}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) throw new Error('Security check or export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `vendor_${type}_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success(`${type.toUpperCase()} downloaded`, { id: loadingToast });
        } catch (error) {
            toast.error(`Export error: ${error instanceof Error ? error.message : 'Unknown'}`, { id: loadingToast });
        }
    };

    if (loading && !stats) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-blue-600 animate-pulse" />
                    </div>
                </div>
                <p className="mt-4 text-gray-500 font-medium animate-pulse">Analyzing dynamic data...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#F8FAFC]">
            {/* Nav Header */}
            <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-30">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
                                <TrendingUp className="w-5 h-5" />
                            </div>
                            <div>
                                <h1 className="text-lg font-black text-gray-900 leading-none">Dynamic Analytics</h1>
                                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Real-time Performance</p>
                            </div>
                        </div>
                        <div className="flex gap-4 items-center">
                            <Link
                                href="/vendor/dashboard"
                                className="px-4 py-2 text-gray-500 hover:text-blue-600 font-bold text-xs transition-colors"
                            >
                                BACK TO DASHBOARD
                            </Link>
                            <div className="h-6 w-px bg-gray-100"></div>
                            <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 font-bold text-xs">
                                    {(user?.first_name || 'V')[0]}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Summary Panel */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 relative overflow-hidden group">
                        <div className="absolute -right-4 -bottom-4 opacity-5 transform group-hover:scale-110 transition-transform">
                            <IndianRupee className="w-24 h-24 text-blue-600" />
                        </div>
                        <div className="flex items-center gap-4 relative z-10">
                            <div className="p-3 bg-blue-50 rounded-xl">
                                <IndianRupee className="text-blue-600 w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Revenue</p>
                                <p className="text-2xl font-black text-gray-900">₹{(stats?.total_revenue || 0).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 relative overflow-hidden group">
                        <div className="absolute -right-4 -bottom-4 opacity-5 transform group-hover:scale-110 transition-transform">
                            <Package className="w-24 h-24 text-emerald-600" />
                        </div>
                        <div className="flex items-center gap-4 relative z-10">
                            <div className="p-3 bg-emerald-50 rounded-xl">
                                <Package className="text-emerald-600 w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Actives</p>
                                <p className="text-2xl font-black text-gray-900">{(stats?.active_rentals || 0).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 relative overflow-hidden group">
                        <div className="absolute -right-4 -bottom-4 opacity-5 transform group-hover:scale-110 transition-transform">
                            <BarChart2 className="w-24 h-24 text-purple-600" />
                        </div>
                        <div className="flex items-center gap-4 relative z-10">
                            <div className="p-3 bg-purple-50 rounded-xl">
                                <BarChart2 className="text-purple-600 w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Rentals</p>
                                <p className="text-2xl font-black text-gray-900">{(stats?.total_orders || 0).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-10">
                    {/* Revenue Advanced Chart */}
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
                        <div className="p-8 border-b border-gray-50 flex justify-between items-center">
                            <div>
                                <h2 className="text-xl font-black text-gray-900 flex items-center gap-2">
                                    Revenue Stream
                                    <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">LIVE</span>
                                </h2>
                                <p className="text-xs text-gray-400 mt-1">Daily income trends across your inventory</p>
                            </div>
                            <div className="flex bg-gray-50 p-1 rounded-xl">
                                {[7, 30, 90].map(v => (
                                    <button
                                        key={v}
                                        onClick={() => setDays(v)}
                                        className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition ${days === v ? 'bg-white shadow-sm text-blue-600' : 'text-gray-400 hover:text-gray-600'
                                            }`}
                                    >
                                        {v}D
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="p-8 flex-1">
                            <EnhancedBarChart data={revenueData} />
                            <div className="flex justify-between mt-6 text-[10px] font-bold text-gray-300 px-2 uppercase tracking-tighter">
                                <span>{revenueData[0]?.date || 'Oldest'}</span>
                                <span>{revenueData[Math.floor(revenueData.length / 2)]?.date || 'Mid'}</span>
                                <span>{revenueData[revenueData.length - 1]?.date || 'Recent'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Inventory Popularity Chart */}
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 flex flex-col">
                        <div className="p-8 border-b border-gray-50">
                            <h2 className="text-xl font-black text-gray-900">Product Popularity</h2>
                            <p className="text-xs text-gray-400 mt-1">Which items are moving fastest</p>
                        </div>
                        <div className="p-8 flex-1 flex flex-col justify-center">
                            <EnhancedPieChart data={topProducts} />
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    {/* Performance Table */}
                    <div className="lg:col-span-2 bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                        <div className="p-8 border-b border-gray-50 bg-gray-50/50">
                            <h2 className="text-xl font-black text-gray-900">Performance Metrics</h2>
                            <p className="text-xs text-gray-400 mt-1">Detailed product-level analytics</p>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-[#F8FAFC] text-gray-400 text-[10px] uppercase font-black tracking-widest">
                                    <tr>
                                        <th className="px-8 py-5">Product Details</th>
                                        <th className="px-8 py-5 text-center">Rental Count</th>
                                        <th className="px-8 py-5 text-right">Yield</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {topProducts.map((p, idx) => (
                                        <tr key={idx} className="hover:bg-blue-50/30 transition group">
                                            <td className="px-8 py-5">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 font-bold text-xs uppercase group-hover:bg-white transition shadow-sm">
                                                        {p.product_name?.substring(0, 2) || 'PR'}
                                                    </div>
                                                    <div>
                                                        <div className="text-sm font-black text-gray-900 group-hover:text-blue-600 transition">{p.product_name}</div>
                                                        <div className="text-[10px] text-gray-400 font-medium">ID: #{p.product_id}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-8 py-5 text-center">
                                                <span className="inline-flex items-center justify-center px-3 py-1 bg-gray-100 rounded-full text-xs font-black text-gray-600">
                                                    {p.rental_count}
                                                </span>
                                            </td>
                                            <td className="px-8 py-5 text-right">
                                                <div className="text-sm font-black text-blue-600">₹{(p.revenue || 0).toLocaleString()}</div>
                                                <div className="text-[10px] text-emerald-500 font-bold flex items-center justify-end gap-0.5">
                                                    Profit <ArrowUpRight className="w-2 h-2" />
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    {topProducts.length === 0 && (
                                        <tr>
                                            <td colSpan={3} className="px-8 py-16 text-center">
                                                <div className="flex flex-col items-center">
                                                    <Package className="w-12 h-12 text-gray-100 mb-2" />
                                                    <p className="text-sm text-gray-400 font-bold">No product status to report</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Reports Container */}
                    <div className="flex flex-col gap-6">
                        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
                            <h2 className="text-lg font-black text-gray-900 mb-6 flex items-center justify-between">
                                Raw Data Export
                                <Download className="w-4 h-4 text-blue-500" />
                            </h2>
                            <div className="space-y-4">
                                <button
                                    onClick={() => handleExport('orders')}
                                    className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-blue-50 rounded-2xl transition group border border-transparent hover:border-blue-100"
                                >
                                    <div className="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-blue-600 group-hover:scale-110 transition">
                                        <Calendar className="w-5 h-5" />
                                    </div>
                                    <div className="text-left">
                                        <div className="text-xs font-black text-gray-700">Order Logs</div>
                                        <div className="text-[10px] text-gray-400 font-bold">FULL HISTORY .CSV</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleExport('invoices')}
                                    className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-emerald-50 rounded-2xl transition group border border-transparent hover:border-emerald-100"
                                >
                                    <div className="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-emerald-600 group-hover:scale-110 transition">
                                        <IndianRupee className="w-5 h-5" />
                                    </div>
                                    <div className="text-left">
                                        <div className="text-xs font-black text-gray-700">Invoice Registry</div>
                                        <div className="text-[10px] text-gray-400 font-bold">SUMMARY DATA .CSV</div>
                                    </div>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}

export default function VendorReports() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR]}>
            <VendorReportsContent />
        </ProtectedRoute>
    );
}
