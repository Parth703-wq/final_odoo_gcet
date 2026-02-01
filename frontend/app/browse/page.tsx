'use client';

import { useState, useEffect } from 'react';
import { productsApi, categoriesApi } from '@/lib/api/endpoints';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';
import { getImageUrl } from '@/lib/utils/images';

export default function BrowseProductsPage() {
    const { user } = useAuth();
    const [products, setProducts] = useState<any[]>([]);
    const [categories, setCategories] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

    useEffect(() => {
        fetchData();
    }, [selectedCategory]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [productsData, categoriesData] = await Promise.all([
                productsApi.list({ category_id: selectedCategory, is_published: true }),
                categoriesApi.list(),
            ]);
            setProducts(Array.isArray(productsData) ? productsData : productsData?.items || []);
            setCategories(Array.isArray(categoriesData) ? categoriesData : categoriesData?.items || []);
        } catch (error: any) {
            console.error('Failed to load products', error);
            setProducts([]);
            setCategories([]);
        } finally {
            setLoading(false);
        }
    };

    const filteredProducts = products.filter((product) =>
        (product.name || '').toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Browse Products</h1>
                        <div className="flex items-center gap-4">
                            {user ? (
                                <>
                                    <Link
                                        href="/cart"
                                        className="text-gray-600 hover:text-gray-900 font-medium"
                                    >
                                        Cart
                                    </Link>
                                    <Link
                                        href="/orders"
                                        className="text-gray-600 hover:text-gray-900 font-medium"
                                    >
                                        My Orders
                                    </Link>
                                    <span className="text-gray-600 text-sm">
                                        {user.first_name} {user.last_name}
                                    </span>
                                    <button
                                        onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
                                        className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium text-sm"
                                    >
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <Link
                                    href="/login"
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                                >
                                    Login
                                </Link>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex gap-8">
                    {/* Sidebar Filters */}
                    <aside className="w-64 flex-shrink-0">
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>

                            {/* Search */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Search
                                </label>
                                <input
                                    type="text"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    placeholder="Search products..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                />
                            </div>

                            {/* Categories */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Category
                                </label>
                                <div className="space-y-2">
                                    <button
                                        onClick={() => setSelectedCategory(null)}
                                        className={`w-full text-left px-3 py-2 rounded-lg transition ${selectedCategory === null
                                            ? 'bg-blue-50 text-blue-600 font-medium'
                                            : 'hover:bg-gray-50'
                                            }`}
                                    >
                                        All Categories
                                    </button>
                                    {categories.map((category) => (
                                        <button
                                            key={category.id}
                                            onClick={() => setSelectedCategory(category.id)}
                                            className={`w-full text-left px-3 py-2 rounded-lg transition ${selectedCategory === category.id
                                                ? 'bg-blue-50 text-blue-600 font-medium'
                                                : 'hover:bg-gray-50'
                                                }`}
                                        >
                                            {category.name}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </aside>

                    {/* Products Grid */}
                    <main className="flex-1">
                        {loading ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {[...Array(6)].map((_, i) => (
                                    <div key={i} className="bg-white rounded-lg shadow-sm p-4 animate-pulse">
                                        <div className="bg-gray-200 h-48 rounded-lg mb-4"></div>
                                        <div className="bg-gray-200 h-4 rounded w-3/4 mb-2"></div>
                                        <div className="bg-gray-200 h-4 rounded w-1/2"></div>
                                    </div>
                                ))}
                            </div>
                        ) : filteredProducts.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-gray-500">No products found</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {filteredProducts.map((product) => (
                                    <Link
                                        key={product.id}
                                        href={`/products/${product.id}`}
                                        className="bg-white rounded-lg shadow-sm hover:shadow-md transition overflow-hidden group"
                                    >
                                        <div className="relative h-48 bg-gray-200">
                                            {product.image_url ? (
                                                <img
                                                    src={getImageUrl(product.image_url)}
                                                    alt={product.name}
                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                                />
                                            ) : product.gallery_images && product.gallery_images.length > 0 ? (
                                                <img
                                                    src={getImageUrl(product.gallery_images[0])}
                                                    alt={product.name}
                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                                />
                                            ) : (
                                                <div className="flex items-center justify-center h-full text-gray-400">
                                                    No Image
                                                </div>
                                            )}
                                        </div>
                                        <div className="p-4">
                                            <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition">
                                                {product.name}
                                            </h3>
                                            <p className="text-sm text-gray-500 mb-2 line-clamp-2">
                                                {product.description}
                                            </p>
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <span className="text-lg font-bold text-blue-600">
                                                        ₹{product.rental_price_daily || 0}
                                                    </span>
                                                    <span className="text-sm text-gray-500">/day</span>
                                                </div>
                                                <span className="text-sm text-gray-500">
                                                    {(product.available_quantity ?? product.quantity_on_hand) || 0} available
                                                </span>
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </main>
                </div>
            </div>
        </div>
    );
}
