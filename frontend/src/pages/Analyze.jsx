import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Analyze.css";

const API_BASE =
    "http://127.0.0.1:5001";

function Analyze() {
    const navigate = useNavigate();

    const [selectedFile, setSelectedFile] =
        useState(null);

    const [preview, setPreview] =
        useState(null);

    const [isDragging, setIsDragging] =
        useState(false);

    const [isAnalyzing, setIsAnalyzing] =
        useState(false);

    const [error, setError] =
        useState("");


    /* =========================================================
       VALIDATE FILE
    ========================================================= */

    const validateFile = (file) => {

        if (!file) {
            return "Please select an image.";
        }

        const allowedTypes = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        ];

        if (
            !allowedTypes.includes(
                file.type
            )
        ) {
            return (
                "Only JPG, JPEG, PNG and WEBP " +
                "images are supported."
            );
        }

        const maxSize =
            10 * 1024 * 1024;

        if (file.size > maxSize) {
            return (
                "Image size must be less than 10 MB."
            );
        }

        return "";
    };


    /* =========================================================
       HANDLE FILE
    ========================================================= */

    const handleFileSelect = (file) => {

        setError("");

        const validationError =
            validateFile(file);

        if (validationError) {
            setSelectedFile(null);
            setPreview(null);
            setError(validationError);
            return;
        }

        if (preview) {
            URL.revokeObjectURL(preview);
        }

        setSelectedFile(file);

        const previewUrl =
            URL.createObjectURL(file);

        setPreview(previewUrl);
    };


    /* =========================================================
       INPUT
    ========================================================= */

    const handleInputChange = (
        event
    ) => {

        const file =
            event.target.files?.[0];

        if (file) {
            handleFileSelect(file);
        }
    };


    /* =========================================================
       DRAG
    ========================================================= */

    const handleDragOver = (
        event
    ) => {

        event.preventDefault();

        setIsDragging(true);
    };


    const handleDragLeave = (
        event
    ) => {

        event.preventDefault();

        setIsDragging(false);
    };


    const handleDrop = (
        event
    ) => {

        event.preventDefault();

        setIsDragging(false);

        const file =
            event.dataTransfer
                .files?.[0];

        if (file) {
            handleFileSelect(file);
        }
    };


    /* =========================================================
       REMOVE
    ========================================================= */

    const handleRemove = () => {

        if (preview) {
            URL.revokeObjectURL(preview);
        }

        setSelectedFile(null);
        setPreview(null);
        setError("");
    };


    /* =========================================================
       ANALYZE
    ========================================================= */

    const handleAnalyze =
        async () => {

            if (!selectedFile) {
                setError(
                    "Please upload an image before starting the investigation."
                );

                return;
            }

            setError("");
            setIsAnalyzing(true);

            try {

                const formData =
                    new FormData();

                formData.append(
                    "image",
                    selectedFile
                );


                const response =
                    await axios.post(
                        `${API_BASE}/predict`,
                        formData,
                        {
                            headers: {
                                "Content-Type":
                                    "multipart/form-data",
                            },

                            timeout: 120000,
                        }
                    );


                const data =
                    response.data;


                if (
                    !data ||
                    data.success === false
                ) {
                    throw new Error(
                        data?.error ||
                        data?.message ||
                        "The forensic engine could not analyze the image."
                    );
                }


                /* ===============================================
                   RESULT OBJECT
                =============================================== */

                const resultData = {
                    ...data,

                    image:
                        preview,

                    filename:
                        selectedFile.name,

                    fileName:
                        selectedFile.name,

                    fileSize:
                        selectedFile.size,

                    fileType:
                        selectedFile.type,

                    analyzedAt:
                        new Date().toISOString(),
                };


                /* ===============================================
                   SAVE HISTORY LOCALLY
                =============================================== */

                try {

                    const existing =
                        localStorage.getItem(
                            "investigationHistory"
                        );

                    const history =
                        existing
                            ? JSON.parse(existing)
                            : [];

                    const safeHistory =
                        Array.isArray(history)
                            ? history
                            : [];

                    const historyItem = {
                        ...resultData,

                        image:
                            undefined,
                    };

                    safeHistory.unshift(
                        historyItem
                    );

                    const limitedHistory =
                        safeHistory.slice(
                            0,
                            100
                        );

                    localStorage.setItem(
                        "investigationHistory",
                        JSON.stringify(
                            limitedHistory
                        )
                    );

                } catch (historyError) {

                    console.warn(
                        "Unable to save local history:",
                        historyError
                    );
                }


                /* ===============================================
                   GO TO RESULT PAGE
                =============================================== */

                navigate(
                    "/results",
                    {
                        state: {
                            result:
                                resultData,
                        },
                    }
                );

            } catch (error) {

                console.error(
                    "Forensic analysis error:",
                    error
                );


                if (
                    error.response
                ) {

                    const backendMessage =
                        error.response
                            .data?.error ||
                        error.response
                            .data?.message ||
                        "The forensic engine could not analyze the image.";

                    setError(
                        backendMessage
                    );

                } else if (
                    error.request
                ) {

                    setError(
                        "Unable to connect to the forensic AI engine. Make sure Flask is running on port 5001."
                    );

                } else {

                    setError(
                        error.message ||
                        "Something went wrong while analyzing the image."
                    );
                }

            } finally {

                setIsAnalyzing(false);
            }
        };


    /* =========================================================
       RENDER
    ========================================================= */

    return (
        <main className="analyze-page">


            {/* =================================================
                DECORATIVE BACKGROUND
            ================================================= */}

            <div className="analyze-orb analyze-orb-one"></div>

            <div className="analyze-orb analyze-orb-two"></div>


            <div className="analyze-container">


                {/* =================================================
                    HEADER
                ================================================= */}

                <section className="analyze-header">

                    <div>

                        <div className="analyze-eyebrow">
                            <span></span>
                            FORENSIC ANALYSIS
                        </div>

                        <h1>
                            New
                            <span>
                                Investigation
                            </span>
                        </h1>

                        <p>
                            Submit digital evidence to the
                            forensic intelligence engine for
                            authenticity and manipulation analysis.
                        </p>

                    </div>


                    <div className="analyze-header-actions">

                        <div className="analyze-security">

                            <span></span>

                            <div>
                                <strong>
                                    ENGINE ONLINE
                                </strong>

                                <small>
                                    ResNet50
                                </small>
                            </div>

                        </div>


                        <button
                            type="button"
                            className="analyze-history-btn"
                            onClick={() =>
                                navigate(
                                    "/history"
                                )
                            }
                        >
                            Evidence Vault
                            <span>
                                →
                            </span>
                        </button>

                    </div>

                </section>


                {/* =================================================
                    PIPELINE
                ================================================= */}

                <section className="analysis-pipeline">

                    <div className="pipeline-item active">

                        <div className="pipeline-number">
                            01
                        </div>

                        <div>
                            <strong>
                                Upload
                            </strong>

                            <small>
                                Digital evidence
                            </small>
                        </div>

                    </div>


                    <div className="pipeline-connector"></div>


                    <div
                        className={
                            `pipeline-item ${
                                isAnalyzing ||
                                selectedFile
                                    ? "active"
                                    : ""
                            }`
                        }
                    >

                        <div className="pipeline-number">
                            02
                        </div>

                        <div>
                            <strong>
                                Analyze
                            </strong>

                            <small>
                                AI forensic engine
                            </small>
                        </div>

                    </div>


                    <div className="pipeline-connector"></div>


                    <div className="pipeline-item">

                        <div className="pipeline-number">
                            03
                        </div>

                        <div>
                            <strong>
                                Report
                            </strong>

                            <small>
                                Investigation result
                            </small>
                        </div>

                    </div>

                </section>


                {/* =================================================
                    MAIN GRID
                ================================================= */}

                <section className="analyze-grid">


                    {/* =================================================
                        UPLOAD CARD
                    ================================================= */}

                    <article className="upload-card">

                        <div className="card-top">

                            <div>

                                <span>
                                    DIGITAL EVIDENCE
                                </span>

                                <h2>
                                    Upload image
                                </h2>

                                <p>
                                    Select a source image for forensic
                                    examination.
                                </p>

                            </div>

                            <div className="card-number">
                                01
                            </div>

                        </div>


                        {!selectedFile ? (

                            <label
                                className={
                                    `upload-area ${
                                        isDragging
                                            ? "dragging"
                                            : ""
                                    }`
                                }
                                onDragOver={
                                    handleDragOver
                                }
                                onDragLeave={
                                    handleDragLeave
                                }
                                onDrop={
                                    handleDrop
                                }
                            >

                                <input
                                    type="file"
                                    accept="
                                        image/jpeg,
                                        image/jpg,
                                        image/png,
                                        image/webp
                                    "
                                    onChange={
                                        handleInputChange
                                    }
                                    hidden
                                />


                                <div className="upload-visual">

                                    <div className="upload-orbit orbit-one"></div>

                                    <div className="upload-orbit orbit-two"></div>

                                    <div className="upload-icon">
                                        ↑
                                    </div>

                                </div>


                                <h3>
                                    Drop your evidence here
                                </h3>

                                <p>
                                    Drag and drop an image or
                                    click to browse your files.
                                </p>


                                <div className="upload-format-row">

                                    <span>
                                        JPG
                                    </span>

                                    <span>
                                        JPEG
                                    </span>

                                    <span>
                                        PNG
                                    </span>

                                    <span>
                                        WEBP
                                    </span>

                                </div>


                                <small>
                                    Maximum file size: 10 MB
                                </small>

                            </label>

                        ) : (

                            <div className="selected-image-section">


                                <div className="selected-preview">

                                    <img
                                        src={preview}
                                        alt="Selected forensic evidence"
                                    />


                                    <div className="preview-badge">
                                        SELECTED EVIDENCE
                                    </div>

                                </div>


                                <div className="selected-file-info">

                                    <span>
                                        EVIDENCE FILE
                                    </span>

                                    <h3>
                                        {selectedFile.name}
                                    </h3>

                                    <p>
                                        {(
                                            selectedFile.size /
                                            1024 /
                                            1024
                                        ).toFixed(2)}
                                        {" "}
                                        MB
                                        {" • "}
                                        {selectedFile.type}
                                    </p>


                                    <div className="selected-actions">

                                        <label className="change-image-btn">

                                            Change Image

                                            <input
                                                type="file"
                                                accept="
                                                    image/jpeg,
                                                    image/jpg,
                                                    image/png,
                                                    image/webp
                                                "
                                                onChange={
                                                    handleInputChange
                                                }
                                                hidden
                                            />

                                        </label>


                                        <button
                                            type="button"
                                            className="remove-image-btn"
                                            onClick={
                                                handleRemove
                                            }
                                        >
                                            Remove
                                        </button>

                                    </div>

                                </div>

                            </div>

                        )}


                        {/* ERROR */}

                        {error && (

                            <div className="analyze-error">

                                <div>
                                    !
                                </div>

                                <div>
                                    <strong>
                                        Investigation Error
                                    </strong>

                                    <p>
                                        {error}
                                    </p>
                                </div>

                            </div>

                        )}


                        {/* START BUTTON */}

                        {selectedFile && (

                            <div className="analyze-action">

                                <button
                                    type="button"
                                    className="start-analysis-btn"
                                    onClick={
                                        handleAnalyze
                                    }
                                    disabled={
                                        isAnalyzing
                                    }
                                >

                                    {isAnalyzing ? (

                                        <>
                                            <span className="loading-spinner"></span>
                                            Running forensic analysis...
                                        </>

                                    ) : (

                                        <>
                                            Start Forensic Analysis
                                            <span>
                                                →
                                            </span>
                                        </>

                                    )}

                                </button>


                                <p>
                                    Classification + ELA +
                                    Grad-CAM explainability
                                </p>

                            </div>

                        )}

                    </article>


                    {/* =================================================
                        ENGINE CARD
                    ================================================= */}

                    <article className="engine-card">

                        <div className="card-top">

                            <div>

                                <span>
                                    ANALYSIS ENGINE
                                </span>

                                <h2>
                                    Forensic pipeline
                                </h2>

                                <p>
                                    Three complementary analysis
                                    layers work together.
                                </p>

                            </div>

                            <div className="engine-online">
                                <span></span>
                                ONLINE
                            </div>

                        </div>


                        <div className="engine-visual">

                            <div className="engine-core">

                                <div className="engine-core-ring"></div>

                                <div className="engine-core-center">
                                    IF
                                </div>

                            </div>

                            <span className="engine-line line-one"></span>
                            <span className="engine-line line-two"></span>
                            <span className="engine-line line-three"></span>

                            <div className="engine-floating-label label-one">
                                AI
                            </div>

                            <div className="engine-floating-label label-two">
                                ELA
                            </div>

                            <div className="engine-floating-label label-three">
                                CAM
                            </div>

                        </div>


                        <div className="engine-layers">

                            <div className="engine-layer">

                                <div className="layer-number blue">
                                    01
                                </div>

                                <div>
                                    <strong>
                                        ResNet50 Classification
                                    </strong>

                                    <p>
                                        Authentic, AI-generated and
                                        manipulated image classification.
                                    </p>
                                </div>

                                <span>
                                    READY
                                </span>

                            </div>


                            <div className="engine-layer">

                                <div className="layer-number cyan">
                                    02
                                </div>

                                <div>
                                    <strong>
                                        Error Level Analysis
                                    </strong>

                                    <p>
                                        Examines compression and
                                        editing anomalies.
                                    </p>
                                </div>

                                <span>
                                    READY
                                </span>

                            </div>


                            <div className="engine-layer">

                                <div className="layer-number purple">
                                    03
                                </div>

                                <div>
                                    <strong>
                                        Grad-CAM Explainability
                                    </strong>

                                    <p>
                                        Highlights regions affecting
                                        the model decision.
                                    </p>
                                </div>

                                <span>
                                    READY
                                </span>

                            </div>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    BOTTOM INFORMATION
                ================================================= */}

                <section className="analysis-info-grid">


                    <article>

                        <div className="info-icon blue">
                            ✓
                        </div>

                        <div>
                            <strong>
                                Secure processing
                            </strong>

                            <p>
                                Evidence is submitted directly to
                                your local forensic AI service.
                            </p>
                        </div>

                    </article>


                    <article>

                        <div className="info-icon purple">
                            AI
                        </div>

                        <div>
                            <strong>
                                Explainable prediction
                            </strong>

                            <p>
                                Results include confidence,
                                ELA and Grad-CAM evidence.
                            </p>
                        </div>

                    </article>


                    <article>

                        <div className="info-icon green">
                            ✓
                        </div>

                        <div>
                            <strong>
                                Investigation archive
                            </strong>

                            <p>
                                Completed investigations are
                                available in the Evidence Vault.
                            </p>
                        </div>

                    </article>

                </section>

            </div>

        </main>
    );
}

export default Analyze;