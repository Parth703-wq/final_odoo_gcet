'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function VendorSignupPage() {
    const { signup, user } = useAuth();
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        phone: '',
        company_name: '',
        gstin: '',
        address_line1: '',
        city: '',
        state: '',
        zip_code: '',
    });
    const [loading, setLoading] = useState(false);

    // Redirect if already logged in
    if (user) {
        router.push('/');
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await signup(formData, true);
        } catch (error) {
            // Error toast handled in AuthContext
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl w-full">
                <div className="bg-white rounded-2xl shadow-xl p-8">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">Become a Vendor</h1>
                        <p className="mt-2 text-sm text-gray-600">
                            Join our platform and start renting your products
                        </p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Personal Info */}
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-3">Personal Information</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                                        First Name *
                                    </label>
                                    <input
                                        id="first_name"
                                        name="first_name"
                                        type="text"
                                        required
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                                        Last Name *
                                    </label>
                                    <input
                                        id="last_name"
                                        name="last_name"
                                        type="text"
                                        required
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mt-4">
                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                                        Email Address *
                                    </label>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        required
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                                        Phone Number *
                                    </label>
                                    <input
                                        id="phone"
                                        name="phone"
                                        type="tel"
                                        required
                                        value={formData.phone}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                <div>
                                    <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                                        Password *
                                    </label>
                                    <input
                                        id="password"
                                        name="password"
                                        type="password"
                                        required
                                        minLength={8}
                                        value={formData.password}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                                        Confirm *
                                    </label>
                                    <input
                                        id="confirm_password"
                                        name="confirm_password"
                                        type="password"
                                        required
                                        minLength={8}
                                        value={formData.confirm_password}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Company Info */}
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Company Information</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-1">
                                        Company Name *
                                    </label>
                                    <input
                                        id="company_name"
                                        name="company_name"
                                        type="text"
                                        required
                                        value={formData.company_name}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="gstin" className="block text-sm font-medium text-gray-700 mb-1">
                                        GSTIN *
                                    </label>
                                    <input
                                        id="gstin"
                                        name="gstin"
                                        type="text"
                                        required
                                        value={formData.gstin}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                        placeholder="22AAAAA0000A1Z5"
                                    />
                                </div>
                            </div>

                            <div className="mt-4">
                                <label htmlFor="address_line1" className="block text-sm font-medium text-gray-700 mb-1">
                                    Address *
                                </label>
                                <input
                                    id="address_line1"
                                    name="address_line1"
                                    type="text"
                                    required
                                    value={formData.address_line1}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                />
                            </div>

                            <div className="grid grid-cols-3 gap-4 mt-4">
                                <div>
                                    <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                                        City *
                                    </label>
                                    <input
                                        id="city"
                                        name="city"
                                        type="text"
                                        required
                                        value={formData.city}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
                                        State *
                                    </label>
                                    <input
                                        id="state"
                                        name="state"
                                        type="text"
                                        required
                                        value={formData.state}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-1">
                                        Pincode *
                                    </label>
                                    <input
                                        id="zip_code"
                                        name="zip_code"
                                        type="text"
                                        required
                                        value={formData.zip_code}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Creating vendor account...
                                </span>
                            ) : (
                                'Create Vendor Account'
                            )}
                        </button>
                    </form>

                    {/* Login Link */}
                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
