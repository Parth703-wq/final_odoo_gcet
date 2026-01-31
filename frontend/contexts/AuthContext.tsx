'use client';

import React, { createContext, useState, useContext, useEffect } from 'react';
import { authApi } from '@/lib/api/endpoints';
import { User, UserRole, LoginRequest, SignupRequest, AuthResponse } from '@/types';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { formatErrorMessage } from '@/lib/utils/errors';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: LoginRequest) => Promise<void>;
    signup: (data: SignupRequest, isVendor?: boolean) => Promise<void>;
    logout: () => void;
    updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    // Load user from localStorage on mount
    useEffect(() => {
        const loadUser = () => {
            // Only access localStorage on client-side after mount
            if (typeof window === 'undefined') {
                setLoading(false);
                return;
            }

            try {
                const storedUser = localStorage.getItem('user');
                const token = localStorage.getItem('access_token');

                if (storedUser && token) {
                    setUser(JSON.parse(storedUser));
                }
            } catch (error) {
                console.error('Error loading user:', error);
                localStorage.removeItem('user');
                localStorage.removeItem('access_token');
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    const login = async (data: LoginRequest) => {
        try {
            const response: AuthResponse = await authApi.login(data);

            // Store token and user
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user', JSON.stringify(response.user));
            setUser(response.user);

            toast.success('Login successful!');

            // Redirect based on role
            if (response.user.role === UserRole.ADMIN) {
                router.push('/admin/dashboard');
            } else if (response.user.role === UserRole.VENDOR) {
                router.push('/vendor/dashboard');
            } else {
                router.push('/browse');
            }
        } catch (error: any) {
            const message = formatErrorMessage(error);
            toast.error(message);
            throw error;
        }
    };

    const signup = async (data: SignupRequest, isVendor: boolean = false) => {
        try {
            const response: AuthResponse = isVendor
                ? await authApi.signupVendor(data)
                : await authApi.signupCustomer(data);

            // Store token and user
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user', JSON.stringify(response.user));
            setUser(response.user);

            toast.success('Account created successfully!');

            // Redirect based on role
            if (response.user.role === UserRole.VENDOR) {
                router.push('/vendor/dashboard');
            } else {
                router.push('/browse');
            }
        } catch (error: any) {
            const message = formatErrorMessage(error);
            toast.error(message);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setUser(null);
        toast.success('Logged out successfully');
        router.push('/login');
    };

    const updateUser = (updatedUser: User) => {
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setUser(updatedUser);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, signup, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// Protected Route Component
export function ProtectedRoute({
    children,
    allowedRoles,
}: {
    children: React.ReactNode;
    allowedRoles?: UserRole[];
}) {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (!user) {
                router.push('/login');
            } else if (allowedRoles && !allowedRoles.includes(user.role)) {
                toast.error('You do not have permission to access this page');
                router.push('/');
            }
        }
    }, [user, loading, allowedRoles, router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    if (!user || (allowedRoles && !allowedRoles.includes(user.role))) {
        return null;
    }

    return <>{children}</>;
}
