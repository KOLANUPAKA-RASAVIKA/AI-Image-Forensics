import { useMemo } from "react";
import {
    Link,
    useLocation,
} from "react-router-dom";

import "./AnalysisResult.css";


const API_BASE =
    "http://127.0.0.1:5001";


function AnalysisResult() {

    const location =
        useLocation();


    // =========================================================
    // GET RESULT DATA
    // =========================================================

    const data =
        location.state?.result ||
        location.state ||
        (() => {
            try {
                const stored =
                    localStorage.getItem(
                        "latestAnalysisResult"
                    );

                return stored
                    ? JSON.parse(stored)
                    : null;
            } catch {
                return null;
            }
        })() ||
        {};


    // =========================================================
    // PREDICTION
    // =========================================================

    const predictionObject =
        data?.prediction &&
        typeof data.prediction === "object"
            ? data.prediction
            : {};


    let prediction =
        predictionObject?.predicted_class ||
        predictionObject?.class ||
        data?.predicted_class ||
        data?.result_label ||
        data?.result ||
        "UNKNOWN";


    if (
        typeof prediction === "object"
    ) {
        prediction =
            prediction?.predicted_class ||
            prediction?.class ||
            prediction?.result ||
            "UNKNOWN";
    }


    prediction =
        String(prediction).toUpperCase();


    // =========================================================
    // CONFIDENCE
    // =========================================================

    let confidence =
        predictionObject?.confidence_percentage ??
        data?.confidence_percentage ??
        predictionObject?.confidence ??
        data?.confidence ??
        0;


    confidence =
        Number(confidence) || 0;


    if (confidence <= 1) {
        confidence *= 100;
    }


    confidence =
        Math.max(
            0,
            Math.min(
                100,
                confidence
            )
        );


    // =========================================================
    // PROBABILITIES
    // =========================================================

    const probabilities =
        predictionObject?.probabilities ||
        data?.probabilities ||
        {};


    const aiProbability =
        Number(
            probabilities?.AI_GENERATED ??
            0
        ) * 100;


    const authenticProbability =
        Number(
            probabilities?.AUTHENTIC ??
            0
        ) * 100;


    const manipulatedProbability =
        Number(
            probabilities?.MANIPULATED ??
            0
        ) * 100;


    // =========================================================
    // OTHER DATA
    // =========================================================

    const caseId =
        data?.case_id ||
        "CASE NOT AVAILABLE";


    const processingTime =
        data?.processing_time ??
        "--";


    const risk =
        String(
            data?.risk_level ||
            data?.risk ||
            (
                prediction === "AUTHENTIC"
                    ? "LOW"
                    : prediction === "AI_GENERATED"
                        ? "HIGH"
                        : prediction === "MANIPULATED"
                            ? "HIGH"
                            : "REVIEW"
            )
        ).toUpperCase();


    const fileName =
        data?.filename ||
        data?.fileName ||
        "Submitted evidence";


    const createdAt =
        data?.created_at ||
        data?.createdAt ||
        null;


    // =========================================================
    // IMAGE URL HELPER
    // =========================================================

    const makeUrl = (url) => {

        if (!url) {
            return "";
        }


        if (
            typeof url !== "string"
        ) {
            return "";
        }


        if (
            url.startsWith("http://") ||
            url.startsWith("https://")
        ) {
            return url;
        }


        if (
            url.startsWith("/")
        ) {
            return `${API_BASE}${url}`;
        }


        return `${API_BASE}/${url}`;
    };


    // =========================================================
    // IMAGE URLS
    // =========================================================

    const originalUrl =
        makeUrl(
            data?.image_url ||
            data?.imageUrl
        );


    const elaUrl =
        makeUrl(
            data?.ela_url ||
            data?.elaUrl
        );


    const gradcamUrl =
        makeUrl(
            data?.gradcam_url ||
            data?.gradcamUrl
        );


    // =========================================================
    // RESULT CLASS
    // =========================================================

    const resultClass =
        useMemo(() => {

            if (
                prediction ===
                "AI_GENERATED"
            ) {
                return "result-ai";
            }

            if (
                prediction ===
                "AUTHENTIC"
            ) {
                return "result-authentic";
            }

            if (
                prediction ===
                "MANIPULATED"
            ) {
                return "result-manipulated";
            }

            return "result-review";

        }, [prediction]);


    // =========================================================
    // VERDICT TEXT
    // =========================================================

    const verdictTitle = {

        AI_GENERATED:
            "AI Generated",

        AUTHENTIC:
            "Authentic",

        MANIPULATED:
            "Manipulated",

        UNKNOWN:
            "Requires Review",

    }[prediction] || "Requires Review";


    const verdictDescription = {

        AI_GENERATED:
            "The forensic model detected patterns strongly associated with synthetic or AI-generated imagery.",

        AUTHENTIC:
            "The forensic model found the submitted image consistent with an authentic camera-captured image.",

        MANIPULATED:
            "The forensic model detected patterns associated with image editing or digital manipulation.",

        UNKNOWN:
            "The evidence could not be confidently classified and should be reviewed manually.",

    }[prediction] || (
        "Manual review is recommended."
    );


    // =========================================================
    // FORMAT DATE
    // =========================================================

    const formattedDate =
        createdAt
            ? new Date(
                createdAt
            ).toLocaleString(
                undefined,
                {
                    dateStyle: "medium",
                    timeStyle: "short",
                }
            )
            : "Just now";


    // =========================================================
    // NO DATA STATE
    // =========================================================

    if (
        !data ||
        Object.keys(data).length === 0
    ) {

        return (
            <main className="analysis-result-page">

                <section className="analysis-empty-state">

                    <div className="analysis-empty-icon">
                        !
                    </div>

                    <span className="analysis-kicker">
                        FORENSIC INTELLIGENCE
                    </span>

                    <h1>
                        No investigation result
                    </h1>

                    <p>
                        Start a new image investigation
                        to generate a forensic report.
                    </p>

                    <Link
                        to="/analyze"
                        className="analysis-primary-btn"
                    >
                        Start Investigation
                        <span>→</span>
                    </Link>

                </section>

            </main>
        );
    }


    return (
        <main className="analysis-result-page">

            {/* =================================================
                DECORATIVE BACKGROUND
            ================================================= */}

            <div className="analysis-bg-orb analysis-bg-orb-one"></div>

            <div className="analysis-bg-orb analysis-bg-orb-two"></div>


            <div className="analysis-result-container">


                {/* =================================================
                    TOP HEADER
                ================================================= */}

                <section className="analysis-result-header">

                    <div className="analysis-heading">

                        <div className="analysis-kicker-row">

                            <span className="analysis-kicker">
                                DIGITAL FORENSICS
                            </span>

                            <span className="analysis-kicker-slash">
                                /
                            </span>

                            <span className="analysis-kicker muted">
                                INVESTIGATION REPORT
                            </span>

                        </div>

                        <h1>
                            Evidence Analysis
                            <span>
                                Result
                            </span>
                        </h1>

                        <p>
                            AI-powered forensic examination
                            of the submitted digital evidence.
                        </p>

                    </div>


                    <div className="analysis-header-actions">

                        <Link
                            to="/analyze"
                            className="analysis-primary-btn"
                        >
                            Analyze Another
                            <span>→</span>
                        </Link>

                        <Link
                            to="/history"
                            className="analysis-secondary-btn"
                        >
                            Investigation History
                        </Link>

                    </div>

                </section>


                {/* =================================================
                    SUCCESS NOTICE
                ================================================= */}

                <div className="analysis-save-notice">

                    <div className="analysis-save-icon">
                        ✓
                    </div>

                    <div>
                        <strong>
                            Investigation saved
                        </strong>

                        <span>
                            Your forensic evidence has been
                            added to the case archive.
                        </span>
                    </div>

                </div>


                {/* =================================================
                    CASE SUMMARY
                ================================================= */}

                <section className="analysis-summary-grid">


                    {/* VERDICT */}

                    <article
                        className={
                            `analysis-verdict-card ${resultClass}`
                        }
                    >

                        <div className="analysis-verdict-top">

                            <div className="analysis-verdict-label">
                                AI FORENSIC VERDICT
                            </div>

                            <div className="analysis-verdict-pulse">
                                <span></span>
                            </div>

                        </div>


                        <div className="analysis-verdict-icon">
                            {prediction === "AUTHENTIC"
                                ? "✓"
                                : prediction === "AI_GENERATED"
                                    ? "AI"
                                    : prediction === "MANIPULATED"
                                        ? "!"
                                        : "?"
                            }
                        </div>


                        <h2>
                            {verdictTitle}
                        </h2>


                        <p>
                            {verdictDescription}
                        </p>


                        <div className="analysis-confidence-row">

                            <div>

                                <span>
                                    MODEL CONFIDENCE
                                </span>

                                <strong>
                                    {confidence.toFixed(2)}%
                                </strong>

                            </div>

                            <div
                                className="analysis-confidence-ring"
                                style={{
                                    "--confidence":
                                        `${confidence * 3.6}deg`,
                                }}
                            >
                                <span>
                                    {Math.round(
                                        confidence
                                    )}
                                </span>
                            </div>

                        </div>


                        <div className="analysis-confidence-track">

                            <div
                                style={{
                                    width:
                                        `${confidence}%`,
                                }}
                            ></div>

                        </div>

                    </article>


                    {/* ORIGINAL IMAGE */}

                    <article className="analysis-evidence-card">

                        <div className="analysis-card-kicker">
                            EVIDENCE
                        </div>

                        <div className="analysis-card-header">

                            <div>
                                <h2>
                                    Original Image
                                </h2>

                                <p>
                                    Submitted evidence analyzed
                                    by the forensic engine.
                                </p>
                            </div>

                        </div>


                        <div className="analysis-main-image-wrap">

                            {originalUrl ? (

                                <img
                                    src={originalUrl}
                                    alt="Original submitted evidence"
                                    className="analysis-main-image"
                                />

                            ) : (

                                <div className="analysis-image-placeholder">
                                    No preview available
                                </div>

                            )}

                        </div>


                        <div className="analysis-file-row">

                            <div>
                                <span>
                                    FILE
                                </span>

                                <strong>
                                    {fileName}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    PROCESSED
                                </span>

                                <strong>
                                    {formattedDate}
                                </strong>
                            </div>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    METRICS
                ================================================= */}

                <section className="analysis-metrics-grid">

                    <div className="analysis-metric-card blue">

                        <span>
                            CASE ID
                        </span>

                        <strong>
                            {caseId}
                        </strong>

                    </div>


                    <div className="analysis-metric-card cyan">

                        <span>
                            PROCESSING TIME
                        </span>

                        <strong>
                            {processingTime}
                            <small>
                                sec
                            </small>
                        </strong>

                    </div>


                    <div className="analysis-metric-card purple">

                        <span>
                            RISK LEVEL
                        </span>

                        <strong>
                            {risk}
                        </strong>

                    </div>


                    <div className="analysis-metric-card green">

                        <span>
                            ENGINE
                        </span>

                        <strong>
                            ResNet50
                        </strong>

                    </div>

                </section>


                {/* =================================================
                    PROBABILITY ANALYSIS
                ================================================= */}

                <section className="analysis-section-card">

                    <div className="analysis-section-heading">

                        <div>
                            <span>
                                MODEL BREAKDOWN
                            </span>

                            <h2>
                                Classification probabilities
                            </h2>
                        </div>

                        <span className="analysis-live-badge">
                            ● ANALYSIS COMPLETE
                        </span>

                    </div>


                    <div className="analysis-probability-grid">


                        {/* AI */}

                        <div className="analysis-probability-item ai">

                            <div className="analysis-probability-title">

                                <span className="analysis-probability-dot"></span>

                                <span>
                                    AI Generated
                                </span>

                                <strong>
                                    {aiProbability.toFixed(2)}%
                                </strong>

                            </div>

                            <div className="analysis-probability-track">

                                <div
                                    style={{
                                        width:
                                            `${Math.min(
                                                100,
                                                Math.max(
                                                    0,
                                                    aiProbability
                                                )
                                            )}%`,
                                    }}
                                ></div>

                            </div>

                        </div>


                        {/* AUTHENTIC */}

                        <div className="analysis-probability-item authentic">

                            <div className="analysis-probability-title">

                                <span className="analysis-probability-dot"></span>

                                <span>
                                    Authentic
                                </span>

                                <strong>
                                    {authenticProbability.toFixed(2)}%
                                </strong>

                            </div>

                            <div className="analysis-probability-track">

                                <div
                                    style={{
                                        width:
                                            `${Math.min(
                                                100,
                                                Math.max(
                                                    0,
                                                    authenticProbability
                                                )
                                            )}%`,
                                    }}
                                ></div>

                            </div>

                        </div>


                        {/* MANIPULATED */}

                        <div className="analysis-probability-item manipulated">

                            <div className="analysis-probability-title">

                                <span className="analysis-probability-dot"></span>

                                <span>
                                    Manipulated
                                </span>

                                <strong>
                                    {manipulatedProbability.toFixed(2)}%
                                </strong>

                            </div>

                            <div className="analysis-probability-track">

                                <div
                                    style={{
                                        width:
                                            `${Math.min(
                                                100,
                                                Math.max(
                                                    0,
                                                    manipulatedProbability
                                                )
                                            )}%`,
                                    }}
                                ></div>

                            </div>

                        </div>

                    </div>

                </section>


                {/* =================================================
                    EXPLAINABILITY OUTPUTS
                ================================================= */}

                <section className="analysis-section-card">

                    <div className="analysis-section-heading">

                        <div>
                            <span>
                                EXPLAINABLE AI
                            </span>

                            <h2>
                                Evidence visualization
                            </h2>
                        </div>

                        <span className="analysis-engine-tag">
                            ELA + GRAD-CAM
                        </span>

                    </div>


                    <div className="analysis-output-grid">


                        {/* ELA */}

                        <article className="analysis-output-card ela">

                            <div className="analysis-output-header">

                                <div>

                                    <span>
                                        01
                                    </span>

                                    <div>
                                        <strong>
                                            Error Level Analysis
                                        </strong>

                                        <small>
                                            Compression & manipulation evidence
                                        </small>
                                    </div>

                                </div>

                                <span className="analysis-output-status">
                                    COMPLETE
                                </span>

                            </div>


                            <div className="analysis-output-image">

                                {elaUrl ? (

                                    <img
                                        src={elaUrl}
                                        alt="Error Level Analysis"
                                    />

                                ) : (

                                    <div>
                                        ELA output unavailable
                                    </div>

                                )}

                            </div>

                        </article>


                        {/* GRAD-CAM */}

                        <article className="analysis-output-card gradcam">

                            <div className="analysis-output-header">

                                <div>

                                    <span>
                                        02
                                    </span>

                                    <div>
                                        <strong>
                                            Grad-CAM
                                        </strong>

                                        <small>
                                            Model attention visualization
                                        </small>
                                    </div>

                                </div>

                                <span className="analysis-output-status">
                                    COMPLETE
                                </span>

                            </div>


                            <div className="analysis-output-image">

                                {gradcamUrl ? (

                                    <img
                                        src={gradcamUrl}
                                        alt="Grad-CAM model attention"
                                    />

                                ) : (

                                    <div>
                                        Grad-CAM output unavailable
                                    </div>

                                )}

                            </div>

                        </article>

                    </div>

                </section>


                {/* =================================================
                    FOOTER ACTION
                ================================================= */}

                <section className="analysis-next-action">

                    <div>

                        <span>
                            NEXT INVESTIGATION
                        </span>

                        <h2>
                            Continue forensic analysis
                        </h2>

                        <p>
                            Analyze another image or review
                            the complete investigation archive.
                        </p>

                    </div>


                    <div className="analysis-next-buttons">

                        <Link
                            to="/analyze"
                            className="analysis-primary-btn"
                        >
                            Analyze Another
                            <span>→</span>
                        </Link>

                        <Link
                            to="/history"
                            className="analysis-secondary-btn"
                        >
                            Evidence Vault
                        </Link>

                    </div>

                </section>


            </div>

        </main>
    );
}

export default AnalysisResult;