'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ordersApi, reviewsApi, complaintsApi, invoicesApi } from '@/lib/api/endpoints';
import { Order, OrderStatus } from '@/types';
import toast from 'react-hot-toast';
import Link from 'next/link';
import {
    Calendar,
    MapPin,
    Package,
    Clock,
    CheckCircle2,
    XCircle,
    ArrowLeft,
    FileText,
    CreditCard,
    Star,
    MessageSquare,
    Send,
    AlertCircle,
    ShieldAlert,
    Download
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

export default function OrderDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();

    const [order, setOrder] = useState<Order | null>(null);
    const [orderInvoice, setOrderInvoice] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState<{ productId: number, productName: string } | null>(null);
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [submittingReview, setSubmittingReview] = useState(false);
    const [existingReviews, setExistingReviews] = useState<any[]>([]);

    // Complaint States
    const [isComplaintModalOpen, setIsComplaintModalOpen] = useState(false);
    const [complaintSubject, setComplaintSubject] = useState('');
    const [complaintDescription, setComplaintDescription] = useState('');
    const [submittingComplaint, setSubmittingComplaint] = useState(false);

    useEffect(() => {
        if (params.id) {
            fetchOrder(Number(params.id));
        }
    }, [params.id]);

    useEffect(() => {
        if (order && !orderInvoice && (order.status === 'sale_order' || order.status === OrderStatus.CONFIRMED)) {
            fetchInvoiceForOrder(order.id);
        }
    }, [order, orderInvoice]);

    const fetchOrder = async (id: number) => {
        try {
            setLoading(true);
            const data = await ordersApi.getById(id);
            setOrder(data);
            if (data.invoice) {
                setOrderInvoice(data.invoice);
            }

            // Also fetch existing reviews for this order
            const reviews = await reviewsApi.getOrderReviews(id);
            setExistingReviews(reviews.items || []);
        } catch (error) {
            console.error('Failed to fetch order:', error);
            toast.error('Failed to load order details');
        } finally {
            setLoading(false);
        }
    };

    const fetchInvoiceForOrder = async (orderId: number) => {
        try {
            const invoices = await invoicesApi.list({ order_id: orderId });
            if (invoices.items && invoices.items.length > 0) {
                setOrderInvoice(invoices.items[0]);
            }
        } catch (error) {
            console.error('Failed to fetch invoice:', error);
        }
    };

    const handleOpenReview = (productId: number, productName: string) => {
        setSelectedItem({ productId, productName });
        setIsReviewModalOpen(true);
        setRating(5);
        setComment('');
    };

    const handleReviewSubmit = async () => {
        if (!selectedItem || !order) return;

        try {
            setSubmittingReview(true);
            await reviewsApi.createReview({
                product_id: selectedItem.productId,
                order_id: order.id,
                rating,
                comment
            });
            toast.success('Thank you for your feedback!');
            setIsReviewModalOpen(false);

            // Refresh reviews
            const reviews = await reviewsApi.getOrderReviews(order.id);
            setExistingReviews(reviews.items || []);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to submit review');
        } finally {
            setSubmittingReview(false);
        }
    };

    const handleOpenComplaint = (productId: number, productName: string) => {
        setSelectedItem({ productId, productName });
        setIsComplaintModalOpen(true);
        setComplaintSubject('');
        setComplaintDescription('');
    };

    const handleComplaintSubmit = async () => {
        if (!selectedItem || !order || !complaintSubject || !complaintDescription) {
            toast.error('Please fill in all fields');
            return;
        }

        try {
            setSubmittingComplaint(true);
            await complaintsApi.create({
                order_id: order.id,
                product_id: selectedItem.productId,
                subject: complaintSubject,
                description: complaintDescription
            });
            toast.success('Your complaint has been submitted to Admin. We will look into it.');
            setIsComplaintModalOpen(false);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to submit complaint');
        } finally {
            setSubmittingComplaint(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
                <h1 className="text-2xl font-bold text-gray-800 mb-4">Order not found</h1>
                <Link href="/orders" className="text-indigo-600 hover:underline flex items-center gap-2">
                    <ArrowLeft className="w-4 h-4" /> Back to My Orders
                </Link>
            </div>
        );
    }

    const getStatusInfo = (status: string) => {
        const statuses: Record<string, { label: string, color: string, icon: any }> = {
            'draft': { label: 'Draft', color: 'bg-gray-100 text-gray-800', icon: Clock },
            'quotation': { label: 'Quotation', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
            'sale_order': { label: 'Confirmed', color: 'bg-blue-100 text-blue-800', icon: CheckCircle2 },
            'confirmed': { label: 'Confirmed', color: 'bg-blue-100 text-blue-800', icon: CheckCircle2 },
            'picked_up': { label: 'Picked Up', color: 'bg-purple-100 text-purple-800', icon: Package },
            'returned': { label: 'Returned', color: 'bg-indigo-100 text-indigo-800', icon: CheckCircle2 },
            'cancelled': { label: 'Cancelled', color: 'bg-red-100 text-red-800', icon: XCircle },
        };
        return statuses[status.toLowerCase()] || { label: status, color: 'bg-gray-100 text-gray-800', icon: Clock };
    };

    const statusInfo = getStatusInfo(order.status);

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                <div className="mb-8 flex items-center justify-between">
                    <Link href="/orders" className="text-gray-600 hover:text-gray-900 flex items-center gap-2 transition">
                        <ArrowLeft className="w-4 h-4" /> Back to Orders
                    </Link>
                    <div className="flex gap-3">
                        {orderInvoice && (
                            <button
                                onClick={() => router.push(`/invoices/${orderInvoice.id}?download=true`)}
                                className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition flex items-center gap-2 font-medium shadow-sm"
                            >
                                <Download className="w-4 h-4" /> Download Invoice
                            </button>
                        )}
                        {orderInvoice && (
                            <Link
                                href={`/invoices/${orderInvoice.id}`}
                                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 font-medium"
                            >
                                <FileText className="w-4 h-4" /> View Invoice
                            </Link>
                        )}
                        {order.status === OrderStatus.QUOTATION && (
                            <Link
                                href={`/checkout/${order.id}`}
                                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center gap-2 font-medium"
                            >
                                <CreditCard className="w-4 h-4" /> Checkout & Pay
                            </Link>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                    {/* Header */}
                    <div className="p-8 border-b border-gray-100 bg-white">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div>
                                <h1 className="text-3xl font-extrabold text-gray-900 mb-2">
                                    Order #{order.order_number || order.id}
                                </h1>
                                <p className="text-gray-500 flex items-center gap-2">
                                    Placed on {new Date(order.created_at || '').toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })}
                                </p>
                            </div>
                            <div className={`flex items-center gap-2 px-4 py-2 rounded-full font-semibold ${statusInfo.color}`}>
                                <statusInfo.icon className="w-5 h-5" />
                                {statusInfo.label}
                            </div>
                        </div>
                    </div>

                    <div className="p-8 space-y-12">
                        {/* Summary Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <MapPin className="w-5 h-5 text-indigo-600" /> Rental Details
                                </h3>
                                <div className="space-y-4 text-gray-600 bg-gray-50 p-6 rounded-xl">
                                    <div className="flex justify-between">
                                        <span className="font-medium">Rental Period:</span>
                                        <span>
                                            {order.rental_start_date ? new Date(order.rental_start_date).toLocaleDateString() : 'N/A'} -
                                            {order.rental_end_date ? new Date(order.rental_end_date).toLocaleDateString() : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="font-medium">Delivery Method:</span>
                                        <span className="capitalize">{order.delivery_method || 'Pickup'}</span>
                                    </div>
                                    <div className="grid grid-cols-1 gap-4 pt-2">
                                        {order.delivery_address && (
                                            <div className="flex flex-col">
                                                <span className="text-xs font-black uppercase text-gray-400 tracking-widest mb-1">Delivery Address</span>
                                                <span className="text-sm bg-white p-3 rounded-xl border border-gray-200 text-gray-900 shadow-sm">{order.delivery_address}</span>
                                            </div>
                                        )}
                                        {order.billing_address && (
                                            <div className="flex flex-col">
                                                <span className="text-xs font-black uppercase text-gray-400 tracking-widest mb-1">Billing Address</span>
                                                <span className="text-sm bg-white p-3 rounded-xl border border-gray-200 text-gray-900 shadow-sm">{order.billing_address}</span>
                                            </div>
                                        )}
                                        {!order.delivery_address && !order.billing_address && (
                                            <div className="text-sm text-gray-400 italic">No address details provided</div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <CreditCard className="w-5 h-5 text-indigo-600" /> Payment Summary
                                </h3>
                                <div className="space-y-3 text-gray-600 bg-gray-50 p-6 rounded-xl">
                                    <div className="flex justify-between">
                                        <span>Subtotal</span>
                                        <span className="font-medium text-gray-900">₹{order.subtotal}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Tax (GST)</span>
                                        <span className="font-medium text-gray-900">₹{order.tax_amount}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Security Deposit</span>
                                        <span className="font-medium text-gray-900">₹{order.security_deposit}</span>
                                    </div>
                                    {order.discount_amount > 0 && (
                                        <div className="flex justify-between text-green-600">
                                            <span>Discount</span>
                                            <span className="font-medium">-₹{order.discount_amount}</span>
                                        </div>
                                    )}
                                    <div className="flex justify-between text-lg font-bold text-gray-900 border-t border-gray-200 pt-3 mt-3">
                                        <span>Total Amount</span>
                                        <span className="text-indigo-600">₹{order.total_amount}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Order Items */}
                        <div className="space-y-6">
                            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Package className="w-5 h-5 text-indigo-600" /> Items Ordered
                            </h3>
                            <div className="border border-gray-100 rounded-xl overflow-hidden shadow-sm">
                                <table className="w-full text-left">
                                    <thead className="bg-gray-50 text-gray-600 text-sm uppercase font-semibold">
                                        <tr>
                                            <th className="px-6 py-4">Product</th>
                                            <th className="px-6 py-4 text-center">Quantity</th>
                                            <th className="px-6 py-4 text-right">Price</th>
                                            <th className="px-6 py-4 text-right">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {order.items?.map((item) => {
                                            const hasReview = existingReviews.some(r => r.product_id === item.product_id);
                                            const showFeedbackBtn = (order.status === OrderStatus.PICKED_UP || order.status === OrderStatus.ACTIVE) && !hasReview;

                                            return (
                                                <tr key={item.id} className="hover:bg-gray-50 transition">
                                                    <td className="px-6 py-6">
                                                        <div className="font-bold text-gray-900">{item.product_name}</div>
                                                        <div className="text-xs text-gray-500 mt-1">SKU: {item.product_sku || 'N/A'}</div>
                                                        {hasReview && (
                                                            <div className="mt-2 inline-flex items-center gap-1 text-[10px] text-green-600 font-bold bg-green-50 px-2 py-0.5 rounded">
                                                                <CheckCircle2 className="w-3 h-3" /> FEEDBACK SUBMITTED
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-6 text-center text-gray-600">{item.quantity}</td>
                                                    <td className="px-6 py-6 text-right text-gray-600">₹{item.unit_price}</td>
                                                    <td className="px-6 py-6 text-right">
                                                        <div className="font-bold text-gray-900">₹{item.line_total}</div>
                                                        <div className="flex flex-col items-end gap-2 mt-2">
                                                            {showFeedbackBtn && (
                                                                <button
                                                                    onClick={() => handleOpenReview(item.product_id, item.product_name)}
                                                                    className="text-[10px] font-black uppercase tracking-widest text-blue-600 hover:text-blue-800 flex items-center gap-1"
                                                                >
                                                                    <Star className="w-3 h-3 fill-blue-600" /> Leave Feedback
                                                                </button>
                                                            )}
                                                            {(order.status === OrderStatus.PICKED_UP || order.status === OrderStatus.ACTIVE) && (
                                                                <button
                                                                    onClick={() => handleOpenComplaint(item.product_id, item.product_name)}
                                                                    className="text-[10px] font-black uppercase tracking-widest text-red-500 hover:text-red-700 flex items-center gap-1"
                                                                >
                                                                    <AlertCircle className="w-3 h-3" /> Register Complaint
                                                                </button>
                                                            )}
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Review Modal */}
            {isReviewModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="bg-blue-600 p-8 text-white relative">
                            <button
                                onClick={() => setIsReviewModalOpen(false)}
                                className="absolute top-4 right-4 text-white/50 hover:text-white"
                            >
                                <XCircle className="w-6 h-6" />
                            </button>
                            <MessageSquare className="w-12 h-12 mb-4 opacity-50" />
                            <h2 className="text-2xl font-black">Share Your Experience</h2>
                            <p className="text-blue-100 text-sm mt-1">Reviewing: {selectedItem?.productName}</p>
                        </div>

                        <div className="p-8 space-y-6">
                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Rating</label>
                                <div className="flex gap-2">
                                    {[1, 2, 3, 4, 5].map((star) => (
                                        <button
                                            key={star}
                                            onClick={() => setRating(star)}
                                            className="transition-transform active:scale-95"
                                        >
                                            <Star
                                                className={`w-8 h-8 ${star <= rating ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
                                            />
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Your Comment</label>
                                <textarea
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                    placeholder="How was the product quality and delivery experience?"
                                    className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition h-32 resize-none text-sm outline-none"
                                />
                            </div>

                            <button
                                onClick={handleReviewSubmit}
                                disabled={submittingReview}
                                className="w-full py-4 bg-blue-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-blue-700 disabled:opacity-50 transition shadow-lg shadow-blue-200"
                            >
                                {submittingReview ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                ) : (
                                    <>
                                        Submit Feedback <Send className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Complaint Modal */}
            {isComplaintModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200 border-2 border-red-50">
                        <div className="bg-red-500 p-8 text-white relative">
                            <button
                                onClick={() => setIsComplaintModalOpen(false)}
                                className="absolute top-4 right-4 text-white/50 hover:text-white"
                            >
                                <XCircle className="w-6 h-6" />
                            </button>
                            <ShieldAlert className="w-12 h-12 mb-4 opacity-50 text-red-100" />
                            <h2 className="text-2xl font-black">Register Item Complaint</h2>
                            <p className="text-red-100 text-sm mt-1">Reporting issue with: {selectedItem?.productName}</p>
                        </div>

                        <div className="p-8 space-y-6">
                            <div className="bg-red-50 p-4 rounded-xl border border-red-100 mb-2">
                                <p className="text-[10px] text-red-600 font-bold uppercase tracking-tight leading-tight">
                                    Note: This complaint is sent directly to the Admin support team. The vendor will not see this.
                                </p>
                            </div>

                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Issue Subject</label>
                                <input
                                    type="text"
                                    value={complaintSubject}
                                    onChange={(e) => setComplaintSubject(e.target.value)}
                                    placeholder="e.g. Broken part, wrong item, late arrival"
                                    className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Detailed Description</label>
                                <textarea
                                    value={complaintDescription}
                                    onChange={(e) => setComplaintDescription(e.target.value)}
                                    placeholder="Please describe the issue in detail..."
                                    className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-red-500 focus:bg-white transition h-32 resize-none text-sm outline-none"
                                />
                            </div>

                            <button
                                onClick={handleComplaintSubmit}
                                disabled={submittingComplaint}
                                className="w-full py-4 bg-red-500 text-white rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-red-600 disabled:opacity-50 transition shadow-lg shadow-red-200"
                            >
                                {submittingComplaint ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                ) : (
                                    <>
                                        Submit Complaint <Send className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
