'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';

interface ImageUploadProps {
    maxImages?: number;
    onImagesChange: (files: File[]) => void;
    existingImages?: string[];
    onRemoveExisting?: (index: number) => void;
}

export default function ImageUpload({
    maxImages = 5,
    onImagesChange,
    existingImages = [],
    onRemoveExisting
}: ImageUploadProps) {
    const [previews, setPreviews] = useState<string[]>([]);
    const [files, setFiles] = useState<File[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = Array.from(e.target.files || []);
        const totalImages = existingImages.length + files.length + selectedFiles.length;

        if (totalImages > maxImages) {
            alert(`You can only upload up to ${maxImages} images`);
            return;
        }

        const newFiles = [...files, ...selectedFiles];
        setFiles(newFiles);
        onImagesChange(newFiles);

        // Create previews
        const newPreviews = selectedFiles.map(file => URL.createObjectURL(file));
        setPreviews(prev => [...prev, ...newPreviews]);
    };

    const handleRemoveNew = (index: number) => {
        const newFiles = files.filter((_, i) => i !== index);
        const newPreviews = previews.filter((_, i) => i !== index);

        // Revoke the object URL to free memory
        URL.revokeObjectURL(previews[index]);

        setFiles(newFiles);
        setPreviews(newPreviews);
        onImagesChange(newFiles);
    };

    const handleRemoveExisting = (index: number) => {
        if (onRemoveExisting) {
            onRemoveExisting(index);
        }
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const canAddMore = existingImages.length + files.length < maxImages;

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-gray-700">
                    Product Images ({existingImages.length + files.length}/{maxImages})
                </label>
                {canAddMore && (
                    <button
                        type="button"
                        onClick={handleClick}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                    >
                        + Add Images
                    </button>
                )}
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileChange}
                className="hidden"
            />

            {/* Image Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {/* Existing Images */}
                {existingImages.map((url, index) => (
                    <div key={`existing-${index}`} className="relative group">
                        <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200">
                            <Image
                                src={url}
                                alt={`Product ${index + 1}`}
                                width={200}
                                height={200}
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <button
                            type="button"
                            onClick={() => handleRemoveExisting(index)}
                            className="absolute top-2 right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            ×
                        </button>
                        <div className="absolute bottom-2 left-2 bg-green-600 text-white text-xs px-2 py-1 rounded">
                            Saved
                        </div>
                    </div>
                ))}

                {/* New Image Previews */}
                {previews.map((preview, index) => (
                    <div key={`new-${index}`} className="relative group">
                        <div className="aspect-square rounded-lg overflow-hidden border-2 border-blue-400">
                            <img
                                src={preview}
                                alt={`Preview ${index + 1}`}
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <button
                            type="button"
                            onClick={() => handleRemoveNew(index)}
                            className="absolute top-2 right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            ×
                        </button>
                        <div className="absolute bottom-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                            New
                        </div>
                    </div>
                ))}

                {/* Empty state or add more button */}
                {existingImages.length === 0 && files.length === 0 && (
                    <button
                        type="button"
                        onClick={handleClick}
                        className="aspect-square rounded-lg border-2 border-dashed border-gray-300 hover:border-blue-400 flex flex-col items-center justify-center text-gray-400 hover:text-blue-600 transition-colors"
                    >
                        <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span className="text-sm">Add Image</span>
                    </button>
                )}
            </div>

            <p className="text-xs text-gray-500">
                Accepted formats: JPG, PNG, GIF. Max {maxImages} images. Recommended size: 800x800px or larger.
            </p>
        </div>
    );
}
