'use client';

import { useState, useEffect } from 'react';
import { productsApi, categoriesApi } from '@/lib/api/endpoints';
import { UserRole } from '@/types';
import { ProtectedRoute } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

function VendorProductsContent() {
    const [products, setProducts] = useState<any[]>([]);
    const [categories, setCategories] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [productsData, categoriesData] = await Promise.all([
                productsApi.getVendorProducts(),
                categoriesApi.list(),
            ]);
            setProducts(Array.isArray(productsData) ? productsData : []);
            setCategories(Array.isArray(categoriesData) ? categoriesData : []);
        } catch (error) {
            console.error('Failed to load products:', error);
            setProducts([]);
            setCategories([]);
        } finally {
            setLoading(false);
        }
    };

    const handleTogglePublish = async (productId: number) => {
        try {
            await productsApi.togglePublish(productId);
            toast.success('Product updated');
            fetchData();
        } catch (error) {
            toast.error('Failed to update product');
        }
    };

    const handleDelete = async (productId: number) => {
        if (!confirm('Are you sure you want to delete this product?')) return;
        try {
            await productsApi.delete(productId);
            toast.success('Product deleted');
            fetchData();
        } catch (error) {
            toast.error('Failed to delete product');
        }
    };

    // Filter products
    const filteredProducts = products.filter((product) => {
        const matchesCategory = !selectedCategory || product.category_id === parseInt(selectedCategory);
        const matchesSearch = !searchTerm ||
            product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            product.sku?.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">My Products</h1>
                        <div className="flex gap-4">
                            <Link
                                href="/vendor/products/new"
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                + Add Product
                            </Link>
                            <Link
                                href="/vendor/dashboard"
                                className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
                            >
                                ← Dashboard
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            {/* Filters */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div className="bg-white rounded-lg shadow-sm p-4 flex flex-wrap gap-4 items-center">
                    <div className="flex-1 min-w-[200px]">
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search products..."
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div className="min-w-[200px]">
                        <select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">All Categories</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>
                                    {cat.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="text-sm text-gray-500">
                        Showing {filteredProducts.length} of {products.length} products
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                {filteredProducts.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <div className="text-6xl mb-4">📦</div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                            {products.length === 0 ? 'No Products Yet' : 'No products match your filter'}
                        </h3>
                        <p className="text-gray-600 mb-6">
                            {products.length === 0 ? 'Start by adding your first product' : 'Try adjusting your filters'}
                        </p>
                        {products.length === 0 && (
                            <Link
                                href="/vendor/products/new"
                                className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                            >
                                + Add Your First Product
                            </Link>
                        )}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredProducts.map((product) => (
                            <div key={product.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition">
                                {/* Product Image */}
                                <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                                    {product.image_url ? (
                                        <img
                                            src={product.image_url}
                                            alt={product.name}
                                            className="w-full h-full object-cover"
                                        />
                                    ) : product.gallery_images && product.gallery_images.length > 0 ? (
                                        <img
                                            src={product.gallery_images[0]}
                                            alt={product.name}
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="text-6xl">📦</div>
                                    )}
                                </div>

                                {/* Product Info */}
                                <div className="p-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="text-lg font-bold text-gray-900 flex-1">{product.name}</h3>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${product.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                            }`}>
                                            {product.is_published ? 'Published' : 'Draft'}
                                        </span>
                                    </div>

                                    {/* Category Badge */}
                                    {product.category && (
                                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs mb-2">
                                            {product.category.name}
                                        </span>
                                    )}

                                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>

                                    <div className="border-t pt-3 mb-3">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-600">Daily Rate:</span>
                                            <span className="font-bold text-blue-600">₹{(product.rental_price_daily || 0).toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">Available:</span>
                                            <span className="font-medium">{product.quantity_on_hand || 0} units</span>
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleTogglePublish(product.id)}
                                            className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 text-center text-sm font-medium"
                                        >
                                            {product.is_published ? 'Unpublish' : 'Publish'}
                                        </button>
                                        <button
                                            onClick={() => handleDelete(product.id)}
                                            className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 text-sm font-medium"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default function VendorProducts() {
    return (
        <ProtectedRoute allowedRoles={[UserRole.VENDOR, UserRole.ADMIN]}>
            <VendorProductsContent />
        </ProtectedRoute>
    );
}
