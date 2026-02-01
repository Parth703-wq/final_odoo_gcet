'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useRef } from 'react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { toast } from 'react-hot-toast';
import {
    CheckCircle,
    Download
} from 'lucide-react';

import { invoicesApi, paymentsApi } from '@/lib/api/endpoints';
import { Invoice, InvoiceStatus } from '@/types';
import { useAuth } from '@/contexts/AuthContext';

declare global {
    interface Window {
        Razorpay: any;
    }
}

export default function InvoicePage() {
    const params = useParams();
    const router = useRouter();
    const searchParams = useSearchParams();
    const { user, loading: authLoading } = useAuth();
    const invoiceRef = useRef<HTMLDivElement>(null);

    const [invoice, setInvoice] = useState<Invoice | null>(null);
    const [loading, setLoading] = useState(true);
    const [processingPayment, setProcessingPayment] = useState(false);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        if (params.id) {
            fetchInvoice(Number(params.id));
        }

        // Load Razorpay script
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            if (document.body.contains(script)) {
                try {
                    document.body.removeChild(script);
                } catch (e) { }
            }
        };
    }, [params.id]);

    const fetchInvoice = async (id: number) => {
        try {
            setLoading(true);
            const data = await invoicesApi.get(id);
            setInvoice(data);

            // Check if automatic download is requested
            if (searchParams.get('download') === 'true') {
                // Wait for render
                setTimeout(() => {
                    handleDownload();
                }, 500);
            }
        } catch (error) {
            console.error('Failed to fetch invoice:', error);
            toast.error('Failed to load invoice');
            router.push('/orders');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        if (!invoiceRef.current || downloading) return;
        setDownloading(true);
        const toastId = toast.loading('Preparing your PDF...');

        try {
            // Ensure any previous scroll doesn't affect the screenshot
            const canvas = await html2canvas(invoiceRef.current, {
                scale: 2,
                useCORS: true,
                logging: false,
                backgroundColor: '#ffffff',
                allowTaint: true,
                scrollX: 0,
                scrollY: -window.scrollY,
                onclone: (clonedDoc) => {
                    const elements = clonedDoc.querySelectorAll('*');
                    elements.forEach((node) => {
                        const el = node as HTMLElement;
                        if (!el.style) return;

                        const style = window.getComputedStyle(el);
                        ['color', 'backgroundColor', 'borderColor'].forEach(prop => {
                            const val = (style as any)[prop];
                            if (val && (val.includes('oklch') || val.includes('lab') || val.includes('oklab'))) {
                                if (prop === 'backgroundColor') {
                                    el.style.backgroundColor = '#ffffff';
                                } else {
                                    el.style[prop as any] = '#374151';
                                }
                            }
                        });
                    });
                }
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(`Invoice-${invoice?.invoice_number?.replace(/\//g, '_') || 'download'}.pdf`);
            toast.success('Invoice downloaded!', { id: toastId });
        } catch (error: any) {
            console.error('PDF Generation failed:', error);
            toast.error(`Failed to generate PDF: ${error.message || 'Unknown error'}`, { id: toastId });
        } finally {
            setDownloading(false);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const handlePayment = async () => {
        if (!invoice) return;
        setProcessingPayment(true);
        try {
            const razorpayOrder = await paymentsApi.createRazorpayOrder({
                invoice_id: invoice.id,
                amount: invoice.amount_due
            });

            const options = {
                key: razorpayOrder.key_id || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
                amount: razorpayOrder.amount,
                currency: razorpayOrder.currency,
                name: 'Rental Management System',
                description: `Invoice #${invoice.invoice_number}`,
                order_id: razorpayOrder.razorpay_order_id,
                handler: async function (response: any) {
                    try {
                        await paymentsApi.verifyPayment({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                        });
                        toast.success('Payment successful!');
                        fetchInvoice(invoice.id);
                    } catch (error) {
                        toast.error('Payment verification failed');
                    }
                },
                prefill: {
                    email: user?.email || '',
                },
                theme: {
                    color: '#9333ea',
                },
            };

            const rzp = new window.Razorpay(options);
            rzp.open();
        } catch (error) {
            console.error('Payment initialization failed:', error);
            toast.error('Failed to initialize payment');
        } finally {
            setProcessingPayment(false);
        }
    };

    if (loading || authLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
            </div>
        );
    }

    if (!invoice) return null;

    const formatDate = (dateString: string | undefined) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency', currency: 'INR', maximumFractionDigits: 0
        }).format(amount);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8 print:p-0 print:bg-white text-gray-900">
            <style jsx global>{`
                @media print {
                    @page { margin: 0; size: auto; }
                    body { -webkit-print-color-adjust: exact; }
                    .no-print { display: none !important; }
                }
            `}</style>

            <div className="max-w-5xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden border border-gray-200 print:shadow-none print:border-none print:w-full">
                {/* Top Action Bar */}
                <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center justify-end gap-3 no-print">
                    {invoice.status !== InvoiceStatus.DRAFT && invoice.status !== InvoiceStatus.PAID && (
                        <button
                            onClick={handlePayment}
                            disabled={processingPayment}
                            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition font-bold flex items-center gap-2 shadow-md shadow-green-100"
                        >
                            <CheckCircle className="w-5 h-5" /> {processingPayment ? 'Processing...' : 'Pay Now'}
                        </button>
                    )}
                    <button
                        onClick={handleDownload}
                        disabled={downloading}
                        className="px-6 py-2 bg-indigo-600 text-white border border-indigo-700 rounded-lg hover:bg-indigo-700 transition font-bold flex items-center gap-2 shadow-md shadow-indigo-100 disabled:opacity-50"
                    >
                        <Download className="w-5 h-5" /> {downloading ? 'Downloading...' : 'Download PDF'}
                    </button>
                </div>

                {/* Content */}
                <div className="p-12 border-4 border-black m-4" ref={invoiceRef} style={{ backgroundColor: '#ffffff' }}>
                    <div className="flex justify-between items-start mb-12">
                        <div>
                            <h1 className="text-4xl font-black text-black tracking-tighter uppercase mb-2">Invoice</h1>
                            <div className="text-xl font-bold text-gray-900">{invoice.invoice_number}</div>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-black text-indigo-600">RENTAL MS</div>
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">Premium Equipment Rentals</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-12 mb-12">
                        <div className="space-y-4">
                            <h3 className="text-xs font-black uppercase tracking-widest text-gray-400 border-b border-gray-200 pb-2">Billed To</h3>
                            <div>
                                <div className="text-lg font-black text-black uppercase">{invoice.customer_name || 'Customer'}</div>
                                <div className="text-sm text-gray-600 leading-relaxed mt-2">
                                    {invoice.customer?.address_line1 || invoice.billing_address || 'N/A'}<br />
                                    {invoice.customer?.city || ''}, {invoice.customer?.state || ''} {invoice.customer?.zip_code || ''}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4 text-right">
                            <h3 className="text-xs font-black uppercase tracking-widest text-gray-400 border-b border-gray-200 pb-2">Invoice Details</h3>
                            <div className="space-y-2">
                                <div className="flex justify-end gap-8">
                                    <span className="text-xs font-bold uppercase text-gray-400">Date</span>
                                    <span className="text-sm font-black">{formatDate(invoice.invoice_date)}</span>
                                </div>
                                <div className="flex justify-end gap-8">
                                    <span className="text-xs font-bold uppercase text-gray-400">Due Date</span>
                                    <span className="text-sm font-black text-red-600">{formatDate(invoice.due_date)}</span>
                                </div>
                                <div className="flex justify-end gap-8 pt-2 border-t border-gray-100 mt-2">
                                    <span className="text-xs font-bold uppercase text-gray-400">Rental Period</span>
                                    <span className="text-sm font-black">{formatDate(invoice.rental_start_date)} - {formatDate(invoice.rental_end_date)}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mb-12">
                        <table className="w-full border-2 border-black border-collapse">
                            <thead>
                                <tr className="bg-black text-white">
                                    <th className="p-4 text-left text-xs font-black uppercase tracking-widest border border-black">Items & Description</th>
                                    <th className="p-4 text-center text-xs font-black uppercase tracking-widest border border-black w-24">Qty</th>
                                    <th className="p-4 text-right text-xs font-black uppercase tracking-widest border border-black w-32">Price</th>
                                    <th className="p-4 text-center text-xs font-black uppercase tracking-widest border border-black w-24">Tax</th>
                                    <th className="p-4 text-right text-xs font-black uppercase tracking-widest border border-black w-40">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoice.items.map((item, index) => (
                                    <tr key={index} className="border-b border-black">
                                        <td className="p-4 border-r border-black">
                                            <div className="font-black text-black uppercase">{item.product_name}</div>
                                            <div className="text-[10px] font-bold text-gray-500 mt-1 italic">
                                                Rental Coverage: {formatDate(item.rental_start_date)} to {formatDate(item.rental_end_date)}
                                            </div>
                                        </td>
                                        <td className="p-4 text-center font-bold border-r border-black">{item.quantity}</td>
                                        <td className="p-4 text-right font-bold border-r border-black">{formatCurrency(item.unit_price)}</td>
                                        <td className="p-4 text-center font-bold border-r border-black">{item.tax_amount > 0 ? '18%' : '0%'}</td>
                                        <td className="p-4 text-right font-black text-black">{formatCurrency(item.line_total)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="flex justify-end">
                        <div className="w-80 space-y-4 border-4 border-black p-6 bg-gray-50">
                            <div className="flex justify-between text-xs font-bold text-gray-500 uppercase">
                                <span>Subtotal</span>
                                <span>{formatCurrency(invoice.subtotal)}</span>
                            </div>
                            <div className="flex justify-between text-xs font-bold text-gray-500 uppercase">
                                <span>GST (18%)</span>
                                <span>{formatCurrency(invoice.tax_amount)}</span>
                            </div>
                            <div className="flex justify-between text-xs font-bold text-gray-500 uppercase pb-4 border-b-2 border-black">
                                <span>Security Deposit</span>
                                <span>{formatCurrency(invoice.security_deposit)}</span>
                            </div>
                            <div className="flex justify-between text-xl font-black text-black pt-2">
                                <span>TOTAL</span>
                                <span>{formatCurrency(invoice.total_amount)}</span>
                            </div>
                            {invoice.amount_paid > 0 && (
                                <div className="flex justify-between text-sm font-bold text-green-600 bg-green-50 px-2 py-1 rounded">
                                    <span>AMOUNT PAID</span>
                                    <span>-{formatCurrency(invoice.amount_paid)}</span>
                                </div>
                            )}
                            {invoice.amount_due > 0 && (
                                <div className="flex justify-between text-lg font-black text-red-600 border-t-2 border-red-200 pt-2">
                                    <span>BALANCE DUE</span>
                                    <span>{formatCurrency(invoice.amount_due)}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="mt-16 pt-8 border-t-2 border-black">
                        <h4 className="text-[10px] font-black uppercase text-gray-400 mb-2">Terms & Conditions</h4>
                        <p className="text-[9px] text-gray-500 leading-relaxed italic">
                            1. Equipment must be returned in the same condition as received.<br />
                            2. Late returns will be charged daily rental rates plus a 10% penalty fee.<br />
                            3. Security deposit will be refunded within 48 hours after quality check.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
