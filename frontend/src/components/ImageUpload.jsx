import React, { useState } from "react";
import { predictImage } from "../services/api";

const AI_SERVICE_URL = "http://127.0.0.1:5001";

function ImageUpload({ onResult }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith("image/")) {
            setError("Please select a valid image file.");
            return;
        }

        setSelectedFile(file);
        setError("");

        const previewURL = URL.createObjectURL(file);
        setPreview(previewURL);
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError("Please select an image first.");
            return;
        }

        try {
            setLoading(true);
            setError("");

            const result = await predictImage(selectedFile);

            console.log("Analysis Result:", result);

            // ------------------------------------------------
            // Convert Flask relative URLs into full URLs
            // ------------------------------------------------

            const fixedResult = {
                ...result,

                image_url: result.image_url
                    ? `${AI_SERVICE_URL}${result.image_url}`
                    : null,

                ela_url: result.ela_url
                    ? `${AI_SERVICE_URL}${result.ela_url}`
                    : null,

                gradcam_url: result.gradcam_url
                    ? `${AI_SERVICE_URL}${result.gradcam_url}`
                    : null,
            };

            console.log("Fixed Image URL:", fixedResult.image_url);
            console.log("Fixed ELA URL:", fixedResult.ela_url);
            console.log("Fixed Grad-CAM URL:", fixedResult.gradcam_url);

            if (onResult) {
                onResult(fixedResult);
            }

        } catch (err) {
            console.error("Prediction Error:", err);

            setError(
                err.response?.data?.error ||
                "Unable to analyze the image. Please try again."
            );

        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                background: "white",
                padding: "30px",
                borderRadius: "15px",
                boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                textAlign: "center",
            }}
        >
            <h2
                style={{
                    color: "#1f2937",
                    marginBottom: "10px",
                }}
            >
                Upload Image
            </h2>

            <p
                style={{
                    color: "#6b7280",
                    marginBottom: "25px",
                }}
            >
                Select an image to check whether it is real or manipulated.
            </p>

            <label
                style={{
                    display: "inline-block",
                    padding: "12px 25px",
                    background: "#2563eb",
                    color: "white",
                    borderRadius: "8px",
                    cursor: "pointer",
                    fontWeight: "bold",
                }}
            >
                Choose Image

                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{
                        display: "none",
                    }}
                />
            </label>

            {selectedFile && (
                <p
                    style={{
                        marginTop: "15px",
                        color: "#374151",
                    }}
                >
                    Selected: <strong>{selectedFile.name}</strong>
                </p>
            )}

            {preview && (
                <div
                    style={{
                        marginTop: "25px",
                    }}
                >
                    <h3>Image Preview</h3>

                    <img
                        src={preview}
                        alt="Selected preview"
                        style={{
                            width: "350px",
                            maxWidth: "100%",
                            borderRadius: "10px",
                            marginTop: "10px",
                        }}
                    />
                </div>
            )}

            <div>
                <button
                    onClick={handleUpload}
                    disabled={loading || !selectedFile}
                    style={{
                        marginTop: "25px",
                        padding: "12px 30px",
                        border: "none",
                        borderRadius: "8px",
                        background:
                            loading || !selectedFile
                                ? "#9ca3af"
                                : "#16a34a",
                        color: "white",
                        cursor:
                            loading || !selectedFile
                                ? "not-allowed"
                                : "pointer",
                        fontWeight: "bold",
                        fontSize: "16px",
                    }}
                >
                    {loading ? "Analyzing..." : "Analyze Image"}
                </button>
            </div>

            {error && (
                <p
                    style={{
                        marginTop: "20px",
                        color: "#dc2626",
                        fontWeight: "bold",
                    }}
                >
                    {error}
                </p>
            )}
        </div>
    );
}

export default ImageUpload;