import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import "./Results.css";

// =========================================================
// BACKEND URL
// =========================================================

const API_BASE = "http://127.0.0.1:5001";


// =========================================================
// HELPER
// =========================================================

const makeUrl = (value) => {
    if (!value) {
        return "";
    }

    if (
        value.startsWith("http://") ||
        value.startsWith("https://") ||
        value.startsWith("blob:")
    ) {
        return value;
    }

    return `${API_BASE}${value.startsWith("/") ? "" : "/"}${value}`;
};


function Results() {
    const location = useLocation();

    const [result, setResult] = useState(null);
    const [imageUrl, setImageUrl] = useState("");
    const [elaUrl, setElaUrl] = useState("");
    const [gradcamUrl, setGradcamUrl] = useState("");
    const [imageError, setImageError] = useState(false);
    const [elaError, setElaError] = useState(false);
    const [gradcamError, setGradcamError] = useState(false);


    // =====================================================
    // LOAD RESULT
    // =====================================================

    useEffect(() => {
        const stateResult =
            location.state?.result;

        if (stateResult) {
            setResult(stateResult);
            return;
        }

        // Fallback for refresh/direct navigation
        try {
            const stored =
                localStorage.getItem(
                    "latestInvestigation"
                );

            if (stored) {
                setResult(
                    JSON.parse(stored)
                );
            }
        } catch (error) {
            console.error(
                "Unable to restore investigation:",
                error
            );
        }
    }, [location.state]);


    // =====================================================
    // STORE LATEST RESULT
    // =====================================================

    useEffect(() => {
        if (!result) {
            return;
        }

        try {
            localStorage.setItem(
                "latestInvestigation",
                JSON.stringify(result)
            );
        } catch (error) {
            console.warn(
                "Unable to save latest investigation:",
                error
            );
        }
    }, [result]);


    // =====================================================
    // VALUES
    // =====================================================

    const prediction =
        String(
            result?.prediction?.predicted_class ||
            result?.prediction?.result ||
            result?.result_label ||
            result?.result ||
            "UNKNOWN"
        ).toUpperCase();


    const filename =
        result?.filename ||
        result?.fileName ||
        "Unknown evidence";


    const caseId =
        result?.case_id ||
        result?.caseId ||
        "CASE-PENDING";


    const createdAt =
        result?.created_at ||
        result?.createdAt ||
        result?.analyzedAt ||
        null;


    const processingTime =
        result?.processing_time ??
        result?.processingTime ??
        null;


    // =====================================================
    // CONFIDENCE
    // =====================================================

    const confidence = useMemo(() => {

        let value =
            result?.prediction?.confidence_percentage ??
            result?.confidence_percentage ??
            result?.prediction?.confidence ??
            result?.confidence ??
            0;

        value = Number(value);

        if (Number.isNaN(value)) {
            return 0;
        }

        if (value <= 1) {
            value *= 100;
        }

        return Math.max(
            0,
            Math.min(100, value)
        );

    }, [result]);


    // =====================================================
    // PROBABILITIES
    // =====================================================

    const probabilities = useMemo(() => {

        const source =
            result?.prediction?.probabilities ||
            result?.probabilities ||
            {};

        const normalize = (value) => {
            let number =
                Number(value) || 0;

            if (number <= 1) {
                number *= 100;
            }

            return Math.max(
                0,
                Math.min(100, number)
            );
        };

        return {
            AI_GENERATED:
                normalize(
                    source.AI_GENERATED
                ),

            AUTHENTIC:
                normalize(
                    source.AUTHENTIC
                ),

            MANIPULATED:
                normalize(
                    source.MANIPULATED
                ),
        };

    }, [result]);


    // =====================================================
    // RISK
    // =====================================================

    const riskLevel =
        String(
            result?.risk_level ||
            result?.risk ||
            "REVIEW"
        ).toUpperCase();


    const riskText = {
        HIGH:
            "High-risk evidence requiring further forensic verification.",

        MEDIUM:
            "Moderate forensic concern detected. Additional review is recommended.",

        LOW:
            "Low forensic risk based on the current model evidence.",

        REVIEW:
            "Manual forensic review is recommended before a final determination.",
    }[riskLevel] ||
        "Review the complete forensic evidence.";


    // =====================================================
    // RESULT TYPE
    // =====================================================

    const resultType = useMemo(() => {

        if (
            prediction.includes(
                "MANIPULATED"
            ) ||
            prediction.includes(
                "FAKE"
            )
        ) {
            return "manipulated";
        }

        if (
            prediction.includes(
                "AI_GENERATED"
            )
        ) {
            return "ai";
        }

        if (
            prediction.includes(
                "AUTHENTIC"
            ) ||
            prediction.includes(
                "REAL"
            )
        ) {
            return "authentic";
        }

        return "review";

    }, [prediction]);


    const resultLabel = {
        manipulated:
            "MANIPULATED",

        ai:
            "AI GENERATED",

        authentic:
            "AUTHENTIC",

        review:
            "REVIEW",
    }[resultType];


    const resultIcon = {
        manipulated: "!",
        ai: "AI",
        authentic: "✓",
        review: "?",
    }[resultType];


    // =====================================================
    // DATE
    // =====================================================

    const formattedDate = useMemo(() => {

        if (!createdAt) {
            return "Analysis completed";
        }

        try {
            return new Date(
                createdAt
            ).toLocaleString(
                undefined,
                {
                    dateStyle: "medium",
                    timeStyle: "short",
                }
            );
        } catch {
            return "Analysis completed";
        }

    }, [createdAt]);


    // =====================================================
    // URLS
    // =====================================================

    useEffect(() => {

        if (!result) {
            return;
        }

        setImageError(false);
        setElaError(false);
        setGradcamError(false);

        setImageUrl(
            makeUrl(
                result.image_url ||
                result.imageUrl ||
                result.image
            )
        );

        setElaUrl(
            makeUrl(
                result.ela_url ||
                result.elaUrl ||
                result.ela_file
            )
        );

        setGradcamUrl(
            makeUrl(
                result.gradcam_url ||
                result.gradcamUrl ||
                result.gradcam_file
            )
        );

    }, [result]);


    // =====================================================
    // ELA DATA
    // =====================================================

    const elaStats =
        result?.ela_statistics ||
        result?.elaStatistics ||
        {};


    // =====================================================
    // EMPTY STATE
    // =====================================================

    if (!result) {

        return (
            <main className="results-page">

                <div className="results-empty">

                    <div className="results-empty-icon">
                        ◌
                    </div>

                    <span>
                        FORENSIC REPORT
                    </span>

                    <h1>
                        No investigation selected
                    </h1>

                    <p>
                        Start a forensic investigation first
                        to generate an evidence analysis report.
                    </p>

                    <Link
                        to="/analyze"
                        className="results-primary-btn"
                    >
                        Start Investigation
                        <b>→</b>
                    </Link>

                </div>

            </main>
        );
    }


    return (
        <main className="results-page">


            {/* =================================================
                BACKGROUND
            ================================================= */}

            <div className="results-orb results-orb-one"></div>
            <div className="results-orb results-orb-two"></div>


            <div className="results-container">


                {/* =================================================
                    HEADER
                ================================================= */}

                <section className="results-header">

                    <div>

                        <div className="results-eyebrow">

                            <span></span>

                            DIGITAL FORENSICS
                            <b>/</b>
                            INVESTIGATION REPORT

                        </div>


                        <h1>
                            Evidence
                            <span>
                                Analysis Result
                            </span>
                        </h1>


                        <p>
                            AI-powered forensic examination
                            of the submitted digital evidence.
                        </p>

                    </div>


                    <div className="results-header-actions">

                        <Link
                            to="/analyze"
                            className="results-secondary-btn"
                        >
                            Analyze Another
                        </Link>

                        <Link
                            to="/history"
                            className="results-primary-btn"
                        >
                            Evidence Vault
                            <b>→</b>
                        </Link>

                    </div>

                </section>


                {/* =================================================
                    CASE META
                ================================================= */}

                <section className="results-meta">

                    <div>

                        <span>
                            CASE ID
                        </span>

                        <strong>
                            {caseId}
                        </strong>

                    </div>


                    <div>

                        <span>
                            FILE
                        </span>

                        <strong>
                            {filename}
                        </strong>

                    </div>


                    <div>

                        <span>
                            ANALYZED
                        </span>

                        <strong>
                            {formattedDate}
                        </strong>

                    </div>


                    <div>

                        <span>
                            PROCESSING
                        </span>

                        <strong>
                            {processingTime !== null
                                ? `${processingTime} sec`
                                : "—"}
                        </strong>

                    </div>


                    <div className="results-complete">
                        <span></span>
                        COMPLETED
                    </div>

                </section>


                {/* =================================================
                    PRIMARY ANALYSIS
                ================================================= */}

                <section className="results-primary-grid">


                    {/* ORIGINAL IMAGE */}

                    <article className="results-evidence-card">

                        <div className="results-card-label">
                            DIGITAL EVIDENCE
                        </div>


                        <div className="results-card-heading">

                            <div>

                                <h2>
                                    Original Evidence
                                </h2>

                                <p>
                                    Source image submitted to the
                                    forensic analysis engine.
                                </p>

                            </div>


                            <span className="results-file-chip">
                                IMAGE
                            </span>

                        </div>


                        <div className="results-original-image">

                            {imageUrl && !imageError ? (

                                <img
                                    src={imageUrl}
                                    alt={filename}
                                    onError={() =>
                                        setImageError(true)
                                    }
                                />

                            ) : (

                                <div className="results-image-placeholder">

                                    <span>
                                        IMG
                                    </span>

                                    <strong>
                                        Evidence preview unavailable
                                    </strong>

                                    <small>
                                        The analysis result is still available.
                                    </small>

                                </div>

                            )}


                            <div className="results-image-overlay">
                                ORIGINAL EVIDENCE
                            </div>

                        </div>

                    </article>


                    {/* VERDICT */}

                    <article
                        className={
                            `results-verdict-card ${resultType}`
                        }
                    >

                        <div className="results-card-label">
                            FORENSIC VERDICT
                        </div>


                        <div className="results-verdict-icon">
                            {resultIcon}
                        </div>


                        <span className="results-verdict-caption">
                            PRIMARY CLASSIFICATION
                        </span>


                        <h2>
                            {resultLabel}
                        </h2>


                        <div className="results-confidence-number">

                            <strong>
                                {confidence.toFixed(2)}
                            </strong>

                            <span>
                                %
                            </span>

                        </div>


                        <div className="results-confidence-title">
                            MODEL CONFIDENCE
                        </div>


                        <div className="results-confidence-track">

                            <span
                                style={{
                                    width:
                                        `${confidence}%`,
                                }}
                            ></span>

                        </div>


                        <div className="results-risk">

                            <div>

                                <span>
                                    RISK LEVEL
                                </span>

                                <strong>
                                    {riskLevel}
                                </strong>

                            </div>


                            <p>
                                {riskText}
                            </p>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    PROBABILITIES
                ================================================= */}

                <section className="results-section-card">

                    <div className="results-section-heading">

                        <div>

                            <span>
                                CLASSIFICATION ANALYSIS
                            </span>

                            <h2>
                                Model probability distribution
                            </h2>

                            <p>
                                Probability assigned to every
                                supported classification.
                            </p>

                        </div>


                        <div className="results-model-chip">
                            RESNET50
                        </div>

                    </div>


                    <div className="results-probabilities">


                        <div className="results-probability-row">

                            <div className="results-probability-title">

                                <span className="probability-dot ai"></span>

                                <div>
                                    <strong>
                                        AI Generated
                                    </strong>

                                    <small>
                                        Synthetic imagery
                                    </small>
                                </div>

                            </div>


                            <div className="results-probability-bar">

                                <span
                                    className="ai"
                                    style={{
                                        width:
                                            `${probabilities.AI_GENERATED}%`,
                                    }}
                                ></span>

                            </div>


                            <strong className="results-probability-value">
                                {probabilities.AI_GENERATED.toFixed(2)}%
                            </strong>

                        </div>


                        <div className="results-probability-row">

                            <div className="results-probability-title">

                                <span className="probability-dot authentic"></span>

                                <div>
                                    <strong>
                                        Authentic
                                    </strong>

                                    <small>
                                        Original / camera evidence
                                    </small>
                                </div>

                            </div>


                            <div className="results-probability-bar">

                                <span
                                    className="authentic"
                                    style={{
                                        width:
                                            `${probabilities.AUTHENTIC}%`,
                                    }}
                                ></span>

                            </div>


                            <strong className="results-probability-value">
                                {probabilities.AUTHENTIC.toFixed(2)}%
                            </strong>

                        </div>


                        <div className="results-probability-row">

                            <div className="results-probability-title">

                                <span className="probability-dot manipulated"></span>

                                <div>
                                    <strong>
                                        Manipulated
                                    </strong>

                                    <small>
                                        Edited / altered evidence
                                    </small>
                                </div>

                            </div>


                            <div className="results-probability-bar">

                                <span
                                    className="manipulated"
                                    style={{
                                        width:
                                            `${probabilities.MANIPULATED}%`,
                                    }}
                                ></span>

                            </div>


                            <strong className="results-probability-value">
                                {probabilities.MANIPULATED.toFixed(2)}%
                            </strong>

                        </div>

                    </div>

                </section>


                {/* =================================================
                    ELA + GRAD-CAM
                ================================================= */}

                <section className="results-evidence-grid">


                    {/* ELA */}

                    <article className="results-section-card">

                        <div className="results-section-heading">

                            <div>

                                <span>
                                    FORENSIC VISUALIZATION
                                </span>

                                <h2>
                                    Error Level Analysis
                                </h2>

                                <p>
                                    Compression-level differences
                                    that may reveal editing anomalies.
                                </p>

                            </div>


                            <span className="results-tool-chip ela">
                                ELA
                            </span>

                        </div>


                        <div className="results-analysis-image">

                            {elaUrl && !elaError ? (

                                <img
                                    src={elaUrl}
                                    alt="Error Level Analysis"
                                    onError={() =>
                                        setElaError(true)
                                    }
                                />

                            ) : (

                                <div className="results-image-placeholder">

                                    <span>
                                        ELA
                                    </span>

                                    <strong>
                                        ELA visualization unavailable
                                    </strong>

                                </div>

                            )}

                        </div>


                        <div className="results-ela-stats">


                            <div>
                                <span>
                                    MEAN
                                </span>

                                <strong>
                                    {elaStats.mean !== undefined
                                        ? Number(
                                            elaStats.mean
                                        ).toFixed(2)
                                        : "—"}
                                </strong>
                            </div>


                            <div>
                                <span>
                                    STD
                                </span>

                                <strong>
                                    {elaStats.std !== undefined
                                        ? Number(
                                            elaStats.std
                                        ).toFixed(2)
                                        : "—"}
                                </strong>
                            </div>


                            <div>
                                <span>
                                    MAX
                                </span>

                                <strong>
                                    {elaStats.max ?? "—"}
                                </strong>
                            </div>


                            <div>
                                <span>
                                    MIN
                                </span>

                                <strong>
                                    {elaStats.min ?? "—"}
                                </strong>
                            </div>

                        </div>

                    </article>


                    {/* GRAD-CAM */}

                    <article className="results-section-card">

                        <div className="results-section-heading">

                            <div>

                                <span>
                                    EXPLAINABLE AI
                                </span>

                                <h2>
                                    Grad-CAM Analysis
                                </h2>

                                <p>
                                    Regions that influenced the model's
                                    final classification.
                                </p>

                            </div>


                            <span className="results-tool-chip cam">
                                GRAD-CAM
                            </span>

                        </div>


                        <div className="results-analysis-image">

                            {gradcamUrl && !gradcamError ? (

                                <img
                                    src={gradcamUrl}
                                    alt="Grad-CAM visualization"
                                    onError={() =>
                                        setGradcamError(true)
                                    }
                                />

                            ) : (

                                <div className="results-image-placeholder">

                                    <span>
                                        CAM
                                    </span>

                                    <strong>
                                        Grad-CAM unavailable
                                    </strong>

                                </div>

                            )}

                        </div>


                        <div className="results-explanation">

                            <div className="results-explanation-icon">
                                AI
                            </div>

                            <p>
                                Brighter highlighted regions indicate
                                areas that contributed more strongly
                                to the model's decision.
                            </p>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    FORENSIC SUMMARY
                ================================================= */}

                <section className="results-summary-card">

                    <div className="results-summary-icon">
                        IF
                    </div>


                    <div>

                        <span>
                            INVESTIGATION SUMMARY
                        </span>

                        <h2>
                            Forensic assessment completed
                        </h2>

                        <p>
                            The submitted evidence was processed
                            through ResNet50 classification, Error
                            Level Analysis and Grad-CAM explainability.
                            Review all supporting evidence before making
                            a final forensic determination.
                        </p>

                    </div>


                    <div className="results-summary-status">
                        <span></span>
                        COMPLETE
                    </div>

                </section>


                {/* =================================================
                    ACTIONS
                ================================================= */}

                <section className="results-footer-actions">

                    <Link
                        to="/analyze"
                        className="results-secondary-btn"
                    >
                        ← Analyze Another
                    </Link>


                    <Link
                        to="/history"
                        className="results-primary-btn"
                    >
                        Open Evidence Vault
                        <b>→</b>
                    </Link>

                </section>


                {/* =================================================
                    FOOTER
                ================================================= */}

                <footer className="results-footer">

                    <div>

                        <span className="results-footer-dot"></span>

                        Forensic AI Engine Operational

                    </div>


                    <div>

                        ResNet50
                        <span>•</span>

                        ELA
                        <span>•</span>

                        Grad-CAM

                    </div>

                </footer>

            </div>

        </main>
    );
}

export default Results;