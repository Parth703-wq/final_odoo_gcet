'use client';

import React, { useEffect, useState } from 'react';
import { complaintsApi } from '@/lib/api/endpoints';
import { ProtectedRoute } from '@/contexts/AuthContext';
import { UserRole } from '@/types';
import toast from 'react-hot-toast';
import {
    ShieldAlert,
    Clock,
    CheckCircle2,
    AlertCircle,
    MessageSquare,
    Search,
    Filter,
    ArrowRight,
    XCircle
} from 'lucide-react';

function AdminComplaintsContent() {
    const [complaints, setComplaints] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [selectedComplaint, setSelectedComplaint] = useState<any>(null);
    const [adminNotes, setAdminNotes] = useState('');
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        fetchComplaints();
    }, []);

    const fetchComplaints = async () => {
        try {
            setLoading(true);
            const data = await complaintsApi.list();
            setComplaints(data.items || []);
        } catch (error) {
            toast.error('Failed to load complaints');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async (id: number, status: string) => {
        try {
            setUpdating(true);
            await complaintsApi.update(id, { status, admin_notes: adminNotes || undefined });
            toast.success(`Complaint marked as ${status}`);
            fetchComplaints();
            setSelectedComplaint(null);
            setAdminNotes('');
        } catch (error) {
            toast.error('Failed to update complaint');
        } finally {
            setUpdating(false);
        }
    };

    const filteredComplaints = complaints.filter(c => {
        if (filter === 'all') return true;
        return c.status === filter;
    });

    const getStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            'pending': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'in_progress': 'bg-blue-100 text-blue-800 border-blue-200',
            'resolved': 'bg-green-100 text-green-800 border-green-200',
            'rejected': 'bg-red-100 text-red-800 border-red-200',
        };
        return styles[status] || styles.pending;
    };

    return (
        <div className="min-h-screen bg-gray-50/50 p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 flex items-center gap-3">
                            <ShieldAlert className="w-10 h-10 text-red-500" /> Support Center
                        </h1>
                        <p className="text-gray-500 mt-2 font-medium">Manage and resolve customer complaints</p>
                    </div>

                    <div className="flex bg-white p-1 rounded-2xl shadow-sm border border-gray-100">
                        {['all', 'pending', 'resolved'].map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${filter === f
                                    ? 'bg-gray-900 text-white shadow-lg'
                                    : 'text-gray-400 hover:text-gray-600'
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Complaints List */}
                    <div className="lg:col-span-2 space-y-4">
                        {loading ? (
                            <div className="flex justify-center p-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
                            </div>
                        ) : filteredComplaints.length === 0 ? (
                            <div className="text-center p-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
                                <MessageSquare className="w-16 h-16 text-gray-100 mx-auto mb-4" />
                                <h3 className="text-xl font-bold text-gray-400 uppercase tracking-widest">Everything is Quiet</h3>
                                <p className="text-gray-300 text-sm mt-1">No complaints found for this filter.</p>
                            </div>
                        ) : (
                            filteredComplaints.map((c) => (
                                <div
                                    key={c.id}
                                    onClick={() => {
                                        setSelectedComplaint(c);
                                        setAdminNotes(c.admin_notes || '');
                                    }}
                                    className={`bg-white p-6 rounded-3xl border-2 transition-all cursor-pointer hover:shadow-xl ${selectedComplaint?.id === c.id
                                        ? 'border-indigo-500 shadow-indigo-100'
                                        : 'border-transparent hover:border-gray-100'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center text-red-500 font-bold">
                                                {c.id}
                                            </div>
                                            <div>
                                                <h3 className="font-bold text-gray-900">{c.subject}</h3>
                                                <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">
                                                    Order #{c.order_number} • {c.product_name}
                                                </p>
                                            </div>
                                        </div>
                                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${getStatusBadge(c.status)}`}>
                                            {c.status.replace('_', ' ')}
                                        </span>
                                    </div>
                                    <p className="text-gray-600 text-sm line-clamp-2 italic mb-4">"{c.description}"</p>
                                    <div className="flex justify-between items-center pt-4 border-t border-gray-50">
                                        <div className="flex items-center gap-2">
                                            <div className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-[10px]">👤</div>
                                            <span className="text-xs font-bold text-gray-400 uppercase tracking-tighter">{c.customer_name}</span>
                                        </div>
                                        <span className="text-[10px] text-gray-300 font-bold uppercase">{new Date(c.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Resolution Sidebar */}
                    <div className="lg:col-start-3">
                        {selectedComplaint ? (
                            <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden sticky top-8">
                                <div className="bg-gray-900 p-8 text-white">
                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 block mb-2">Complaint Resolution</label>
                                    <h2 className="text-2xl font-black">Ticket #{selectedComplaint.id}</h2>
                                </div>
                                <div className="p-8 space-y-8">
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Complaint Details</label>
                                        <div className="bg-gray-50 p-6 rounded-2xl italic text-gray-600 text-sm border-l-4 border-red-500">
                                            "{selectedComplaint.description}"
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Resolution Notes</label>
                                        <textarea
                                            value={adminNotes}
                                            onChange={(e) => setAdminNotes(e.target.value)}
                                            placeholder="Add private notes or resolution steps..."
                                            className="w-full px-5 py-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition h-40 resize-none text-sm outline-none"
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 pt-4">
                                        <button
                                            onClick={() => handleUpdateStatus(selectedComplaint.id, 'resolved')}
                                            disabled={updating}
                                            className="bg-green-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-green-700 shadow-lg shadow-green-100 flex items-center justify-center gap-2 transition"
                                        >
                                            <CheckCircle2 className="w-4 h-4" /> Resolve
                                        </button>
                                        <button
                                            onClick={() => handleUpdateStatus(selectedComplaint.id, 'rejected')}
                                            disabled={updating}
                                            className="bg-red-50 text-red-500 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-red-100 flex items-center justify-center gap-2 transition"
                                        >
                                            <XCircle className="w-4 h-4" /> Reject
                                        </button>
                                    </div>
                                    <button
                                        onClick={() => handleUpdateStatus(selectedComplaint.id, 'in_progress')}
                                        disabled={updating}
                                        className="w-full bg-blue-50 text-blue-600 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-blue-100 flex items-center justify-center gap-2 transition"
                                    >
                                        <Clock className="w-4 h-4" /> Mark In Progress
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-gray-100/50 rounded-3xl border-2 border-dashed border-gray-200 h-96 flex flex-col items-center justify-center p-10 text-center sticky top-8">
                                <Search className="w-12 h-12 text-gray-200 mb-4" />
                                <h3 className="font-bold text-gray-400 uppercase text-xs tracking-[0.2em]">Select a ticket</h3>
                                <p className="text-gray-300 text-[10px] mt-1 font-bold uppercase tracking-widest">Click a complaint to perform resolution actions</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function AdminComplaints() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
            <AdminComplaintsContent />
        </ProtectedRoute>
    );
}
