const API_BASE_URL = "http://127.0.0.1:5001";

export const API_URL = API_BASE_URL;


// =========================================================
// PREDICT IMAGE
// =========================================================

export async function predictImage(file) {

    const formData = new FormData();

    formData.append("image", file);

    const response = await fetch(
        `${API_BASE_URL}/predict`,
        {
            method: "POST",
            body: formData,
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || "Image analysis failed."
        );
    }

    return data;
}


// =========================================================
// OUTPUT URL
// Handles both:
// /outputs/...
// /uploads/...
// full URLs
// =========================================================

export function getOutputUrl(path) {

    if (!path) {
        return "";
    }

    // Already a full URL
    if (path.startsWith("http://") || path.startsWith("https://")) {
        return path;
    }

    // Backend already returned /outputs/... or /uploads/...
    if (path.startsWith("/")) {
        return `${API_BASE_URL}${path}`;
    }

    // If only filename/path was provided
    return `${API_BASE_URL}/outputs/${path}`;
}