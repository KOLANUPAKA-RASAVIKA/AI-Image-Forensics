import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { predictImage } from "../services/api";

function Upload() {
    const navigate = useNavigate();

    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // =========================================================
    // SELECT IMAGE
    // =========================================================

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];

        setError("");

        if (!selectedFile) {
            setFile(null);
            setPreview(null);
            return;
        }

        // Validate image
        if (!selectedFile.type.startsWith("image/")) {
            setError("Please select a valid image file.");
            setFile(null);
            setPreview(null);
            return;
        }

        // Save selected file
        setFile(selectedFile);

        // Create preview
        const previewUrl = URL.createObjectURL(selectedFile);
        setPreview(previewUrl);
    };

    // =========================================================
    // UPLOAD + ANALYZE
    // =========================================================

    const handleAnalyze = async () => {
        if (!file) {
            setError("Please select an image first.");
            return;
        }

        try {
            setLoading(true);
            setError("");

            console.log("Uploading image:", file.name);

            const result = await predictImage(file);

            console.log("================================");
            console.log("FORENSIC BACKEND RESPONSE");
            console.log("================================");
            console.log(result);

            // Check backend response
            if (!result) {
                throw new Error("No response received from backend.");
            }

            if (result.success === false) {
                throw new Error(
                    result.error || "Forensic analysis failed."
                );
            }

            // Navigate to Results page
            navigate("/results", {
                state: {
                    result: result,
                },
            });

        } catch (err) {
            console.error("Upload / Analysis Error:", err);

            let message =
                "Unable to analyze the image. Please try again.";

            if (err?.response?.data?.error) {
                message = err.response.data.error;
            } else if (err?.message) {
                message = err.message;
            }

            setError(message);

        } finally {
            setLoading(false);
        }
    };

    // =========================================================
    // STYLES
    // =========================================================

    const styles = {
        page: {
            padding: "35px",
            color: "#f8fafc",
            minHeight: "100vh",
            boxSizing: "border-box",
        },

        title: {
            fontSize: "32px",
            fontWeight: "900",
            marginBottom: "8px",
        },

        subtitle: {
            color: "#94a3b8",
            marginBottom: "30px",
        },

        card: {
            maxWidth: "850px",
            margin: "0 auto",
            padding: "35px",
            borderRadius: "22px",
            background:
                "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.78))",
            border:
                "1px solid rgba(148,163,184,0.15)",
            boxShadow:
                "0 20px 60px rgba(0,0,0,0.25)",
        },

        uploadBox: {
            display: "block",
            border:
                "2px dashed rgba(96,165,250,0.45)",
            borderRadius: "18px",
            padding: "50px 30px",
            textAlign: "center",
            background:
                "rgba(2,6,23,0.65)",
            cursor: loading ? "not-allowed" : "pointer",
        },

        icon: {
            fontSize: "50px",
            marginBottom: "15px",
        },

        uploadText: {
            fontSize: "18px",
            fontWeight: "800",
        },

        uploadHint: {
            color: "#64748b",
            marginTop: "8px",
            fontSize: "13px",
        },

        previewBox: {
            marginTop: "25px",
            background: "#020617",
            borderRadius: "15px",
            padding: "15px",
            textAlign: "center",
        },

        preview: {
            maxWidth: "100%",
            maxHeight: "400px",
            objectFit: "contain",
            borderRadius: "12px",
        },

        fileName: {
            marginTop: "12px",
            color: "#94a3b8",
            fontSize: "13px",
            wordBreak: "break-word",
        },

        button: {
            width: "100%",
            marginTop: "25px",
            padding: "14px",
            border: "none",
            borderRadius: "12px",
            background:
                "linear-gradient(135deg,#2563eb,#7c3aed)",
            color: "white",
            fontWeight: "800",
            fontSize: "15px",
            cursor: loading || !file
                ? "not-allowed"
                : "pointer",
            opacity: loading || !file ? 0.6 : 1,
        },

        error: {
            marginTop: "20px",
            padding: "13px",
            borderRadius: "10px",
            background:
                "rgba(239,68,68,0.1)",
            border:
                "1px solid rgba(239,68,68,0.25)",
            color: "#f87171",
            fontSize: "13px",
        },
    };

    return (
        <div style={styles.page}>

            <h1 style={styles.title}>
                New Investigation
            </h1>

            <p style={styles.subtitle}>
                Upload an image for AI-powered forensic analysis.
            </p>

            <div style={styles.card}>

                {/* =================================================
                    FILE UPLOAD
                ================================================= */}

                <label
                    htmlFor="image-upload"
                    style={styles.uploadBox}
                >
                    <div style={styles.icon}>
                        🖼️
                    </div>

                    <div style={styles.uploadText}>
                        Upload Evidence Image
                    </div>

                    <div style={styles.uploadHint}>
                        Click here to select JPG, JPEG, PNG,
                        WEBP, TIFF or BMP
                    </div>

                    <input
                        id="image-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        disabled={loading}
                        style={{
                            display: "none",
                        }}
                    />
                </label>

                {/* =================================================
                    PREVIEW
                ================================================= */}

                {preview && (
                    <div style={styles.previewBox}>

                        <img
                            src={preview}
                            alt="Selected evidence"
                            style={styles.preview}
                        />

                        <div style={styles.fileName}>
                            Selected file:{" "}
                            <strong>{file?.name}</strong>
                        </div>

                    </div>
                )}

                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (
                    <div style={styles.error}>
                        ⚠️ {error}
                    </div>
                )}

                {/* =================================================
                    ANALYZE BUTTON
                ================================================= */}

                <button
                    onClick={handleAnalyze}
                    disabled={loading || !file}
                    style={styles.button}
                >
                    {loading
                        ? "⏳ Analyzing Evidence..."
                        : "🔍 Start Forensic Analysis"}
                </button>

            </div>

        </div>
    );
}

export default Upload;