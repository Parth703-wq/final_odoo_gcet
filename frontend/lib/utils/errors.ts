/**
 * Format error message from API response
 * Handles both string errors and validation error arrays from FastAPI
 */
export function formatErrorMessage(error: any): string {
    // If error.response.data exists
    if (error.response?.data) {
        const { detail } = error.response.data;

        // If detail is a string, return it
        if (typeof detail === 'string') {
            return detail;
        }

        // If detail is an array (FastAPI validation errors)
        if (Array.isArray(detail)) {
            // Extract error messages from validation errors
            const messages = detail.map((err: any) => {
                if (err.msg) return err.msg;
                if (typeof err === 'string') return err;
                return 'Validation error';
            });
            return messages.join(', ');
        }

        // If detail is an object with a message
        if (detail && typeof detail === 'object' && detail.message) {
            return detail.message;
        }
    }

    // Fallback to error message
    if (error.message) {
        return error.message;
    }

    return 'An error occurred';
}
