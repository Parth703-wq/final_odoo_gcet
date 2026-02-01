/**
 * Formats image URLs to be absolute if they are relative
 */
export const getImageUrl = (url?: string | null): string => {
    if (!url) return '';

    // If it's already an absolute URL, return it
    if (url.startsWith('http')) {
        return url;
    }

    // Get backend base URL (removing /api/v1 if present)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const backendUrl = apiUrl.replace('/api/v1', '');

    // Return formatted URL
    return `${backendUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};
