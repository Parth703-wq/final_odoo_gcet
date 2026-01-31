'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ordersApi, invoicesApi } from '@/lib/api/endpoints';
import { Order, Invoice } from '@/types';
import toast from 'react-hot-toast';
import { formatErrorMessage } from '@/lib/utils/errors';

declare global {
    interface Window {
        Razorpay: any;
    }
}

export default function CheckoutPage() {
    const params = useParams();
    const router = useRouter();
    const [order, setOrder] = useState<Order | null>(null);
    const [invoice, setInvoice] = useState<Invoice | null>(null);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);

    const [formData, setFormData] = useState({
        deliveryMethod: 'pickup',
        deliveryAddress: '',
        billingAddress: '',
    });

    useEffect(() => {
        fetchOrder();
        // Load Razorpay script
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
    }, []);

    const fetchOrder = async () => {
        try {
            const orderData = await ordersApi.getById(Number(params.id));
            setOrder(orderData);

            // Create invoice
            const invoiceData = await invoicesApi.create(orderData.id);
            setInvoice(invoiceData);
        } catch (error) {
            toast.error('Failed to load order');
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmOrder = async () => {
        if (!order || !invoice) return;

        setProcessing(true);
        try {
            // Confirm order
            await ordersApi.confirmOrder(order.id, formData);

            // Create Razorpay order
            const razorpayOrder = await invoicesApi.createRazorpayOrder({
                invoice_id: invoice.id,
                amount: invoice.amountDue,
            });

            // Open Razorpay payment
            const options = {
                key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
                amount: razorpayOrder.amount,
                currency: razorpayOrder.currency,
                name: 'Rental Management System',
                description: `Invoice #${invoice.invoiceNumber}`,
                order_id: razorpayOrder.id,
                handler: async function (response: any) {
                    try {
                        await invoicesApi.verifyPayment({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                            invoice_id: invoice.id,
                        });
                        toast.success('Payment successful!');
                        router.push('/orders');
                    } catch (error) {
                        toast.error('Payment verification failed');
                    }
                },
                prefill: {
                    email: order.customer?.email || '',
                    contact: order.customer?.phone || '',
                },
            };

            const razorpay = new window.Razorpay(options);
            razorpay.open();
        } catch (error: any) {
            toast.error(formatErrorMessage(error));
        } finally {
            setProcessing(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!order || !invoice) {
        return <div>Order not found</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Delivery Details */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h2 className="text-xl font-semibold mb-4">Delivery Details</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Delivery Method
                                </label>
                                <select
                                    value={formData.deliveryMethod}
                                    onChange={(e) => setFormData({ ...formData, deliveryMethod: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="pickup">Pickup</option>
                                    <option value="delivery">Delivery</option>
                                </select>
                            </div>

                            {formData.deliveryMethod === 'delivery' && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Delivery Address
                                    </label>
                                    <textarea
                                        value={formData.deliveryAddress}
                                        onChange={(e) => setFormData({ ...formData, deliveryAddress: e.target.value })}
                                        rows={3}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Billing Address
                                </label>
                                <textarea
                                    value={formData.billingAddress}
                                    onChange={(e) => setFormData({ ...formData, billingAddress: e.target.value })}
                                    rows={3}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Order Summary */}
                    <div>
                        <div className="bg-white rounded-lg shadow-sm p-6 mb-4">
                            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
                            <div className="space-y-3">
                                {order.items.map((item) => (
                                    <div key={item.id} className="flex justify-between text-sm">
                                        <span className="text-gray-600">{item.productName} x{item.quantity}</span>
                                        <span className="font-medium">₹{item.lineTotal}</span>
                                    </div>
                                ))}
                                <div className="border-t pt-3 space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Subtotal</span>
                                        <span className="font-medium">₹{invoice.subtotal}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Tax (GST)</span>
                                        <span className="font-medium">₹{invoice.taxAmount}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Deposit</span>
                                        <span className="font-medium">₹{invoice.depositAmount}</span>
                                    </div>
                                    <div className="flex justify-between text-lg font-bold border-t pt-2">
                                        <span>Total</span>
                                        <span className="text-blue-600">₹{invoice.totalAmount}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={handleConfirmOrder}
                            disabled={processing}
                            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
                        >
                            {processing ? 'Processing...' : 'Confirm & Pay'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
