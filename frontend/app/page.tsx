'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || loading) return;

    if (user) {
      // Redirect based on role
      switch (user.role) {
        case UserRole.ADMIN:
          router.push('/admin/dashboard');
          break;
        case UserRole.VENDOR:
          router.push('/vendor/dashboard');
          break;
        case UserRole.CUSTOMER:
          router.push('/browse');
          break;
        default:
          router.push('/browse');
      }
    } else {
      // Not logged in, redirect to login
      router.push('/login');
    }
  }, [user, loading, router, mounted]);

  // Show loading state
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
