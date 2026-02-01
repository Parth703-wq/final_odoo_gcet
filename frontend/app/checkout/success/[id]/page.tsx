'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ordersApi } from '@/lib/api/endpoints';
import { Order } from '@/types';
import Link from 'next/link';
import { CheckCircle, ArrowRight, Download, FileText, ShoppingBag } from 'lucide-react';

export default function PaymentSuccessPage() {
    const params = useParams();
    const router = useRouter();
    const [order, setOrder] = useState<Order | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (params.id) {
            fetchOrder();
        }
    }, [params.id]);

    const fetchOrder = async () => {
        try {
            const data = await ordersApi.getById(Number(params.id));
            setOrder(data);
        } catch (error) {
            console.error('Error fetching order:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-white">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 text-center border border-gray-100 animate-in fade-in zoom-in duration-500">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 text-green-600 shadow-inner">
                    <CheckCircle className="w-12 h-12" />
                </div>

                <h1 className="text-3xl font-black text-gray-900 mb-2">Payment Successful!</h1>
                <p className="text-gray-500 mb-8 font-medium">Your order #{order?.order_number || order?.id} has been confirmed and is being processed.</p>

                <div className="bg-gray-50 rounded-2xl p-6 mb-8 text-left border border-gray-100">
                    <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-200/50">
                        <span className="text-sm text-gray-400 font-bold uppercase tracking-widest">Amount Paid</span>
                        <span className="text-xl font-black text-green-600">₹{order?.total_amount}</span>
                    </div>
                    <div className="space-y-3">
                        {order?.items?.slice(0, 3).map((item, idx) => (
                            <div key={idx} className="flex justify-between text-sm">
                                <span className="text-gray-600 truncate mr-4">{item.product_name} x{item.quantity}</span>
                                <span className="text-gray-400 font-bold">₹{item.line_total}</span>
                            </div>
                        ))}
                        {order?.items && order.items.length > 3 && (
                            <p className="text-xs text-gray-400 italic">+{order.items.length - 3} more items</p>
                        )}
                    </div>
                </div>

                <div className="space-y-4">
                    {order?.invoice?.id ? (
                        <Link
                            href={`/invoices/${order.invoice.id}`}
                            className="w-full h-14 bg-indigo-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-indigo-700 transition shadow-lg shadow-indigo-100"
                        >
                            View & Download Invoice <Download className="w-4 h-4" />
                        </Link>
                    ) : (
                        <Link
                            href={`/orders/${order?.id}`}
                            className="w-full h-14 bg-indigo-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-indigo-700 transition shadow-lg shadow-indigo-100"
                        >
                            View Order Details <FileText className="w-4 h-4" />
                        </Link>
                    )}

                    <Link
                        href="/browse"
                        className="w-full h-14 bg-white text-gray-900 border-2 border-gray-100 rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-gray-50 transition"
                    >
                        Continue Shopping <ShoppingBag className="w-4 h-4" />
                    </Link>
                </div>

                <p className="mt-8 text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                    Redirecting to orders in 10 seconds...
                </p>
            </div>
        </div>
    );
}
