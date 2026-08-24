import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css";

const API_URL = "http://127.0.0.1:5001";

function Dashboard() {
    const [stats, setStats] = useState({
        total_cases: 0,
        real_images: 0,
        fake_images: 0,
        requires_review: 0,
        average_confidence: 0,
        ai_generated_images: 0,
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    /* =========================================================
       FETCH STATISTICS
    ========================================================= */

    const fetchStats = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_URL}/api/stats`
            );

            if (!response.ok) {
                throw new Error(
                    "Unable to fetch dashboard statistics."
                );
            }

            const data = await response.json();

            if (!data.success || !data.data) {
                throw new Error(
                    data.error ||
                    "Invalid statistics response."
                );
            }

            const result = data.data;

            setStats({
                total_cases:
                    Number(result.total_cases) || 0,

                real_images:
                    Number(
                        result.real_images ??
                        result.authentic_images ??
                        0
                    ),

                fake_images:
                    Number(
                        result.fake_images ??
                        result.manipulated_images ??
                        0
                    ),

                requires_review:
                    Number(
                        result.requires_review ??
                        result.risk?.review ??
                        0
                    ),

                average_confidence:
                    Number(
                        result.average_confidence
                    ) || 0,

                ai_generated_images:
                    Number(
                        result.ai_generated_images
                    ) || 0,
            });

        } catch (err) {
            console.error(
                "Dashboard error:",
                err
            );

            setError(
                "Unable to connect to the forensic backend."
            );

        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchStats();
    }, []);


    /* =========================================================
       VALUES
    ========================================================= */

    const total =
        stats.total_cases;

    const authentic =
        stats.real_images;

    const manipulated =
        stats.fake_images;

    const review =
        stats.requires_review;

    const aiGenerated =
        stats.ai_generated_images;


    /* =========================================================
       CONFIDENCE
    ========================================================= */

    let confidence =
        Number(
            stats.average_confidence
        ) || 0;

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


    /* =========================================================
       PERCENTAGES
    ========================================================= */

    const authenticPercentage =
        total > 0
            ? (authentic / total) * 100
            : 0;

    const manipulatedPercentage =
        total > 0
            ? (manipulated / total) * 100
            : 0;

    const reviewPercentage =
        total > 0
            ? (review / total) * 100
            : 0;

    const aiGeneratedPercentage =
        total > 0
            ? (aiGenerated / total) * 100
            : 0;


    /* =========================================================
       CLASSIFICATION DONUT
    ========================================================= */

    const donutStyle = useMemo(() => {

        if (total === 0) {
            return {
                background:
                    "#e8edf5",
            };
        }

        const authenticEnd =
            authenticPercentage;

        const aiEnd =
            authenticEnd +
            aiGeneratedPercentage;

        const manipulatedEnd =
            aiEnd +
            manipulatedPercentage;

        return {
            background: `
                conic-gradient(
                    #22c55e 0% ${authenticEnd}%,
                    #8b5cf6 ${authenticEnd}% ${aiEnd}%,
                    #ef4444 ${aiEnd}% ${manipulatedEnd}%,
                    #f59e0b ${manipulatedEnd}% 100%
                )
            `,
        };

    }, [
        total,
        authenticPercentage,
        aiGeneratedPercentage,
        manipulatedPercentage,
    ]);


    /* =========================================================
       CONFIDENCE MESSAGE
    ========================================================= */

    const confidenceMessage =
        confidence >= 90
            ? {
                icon: "✓",
                title: "Excellent confidence",
                text:
                    "The forensic model is showing strong confidence across analyzed cases.",
            }
            : confidence >= 70
                ? {
                    icon: "●",
                    title: "Good confidence",
                    text:
                        "The model is performing well, while continued monitoring is recommended.",
                }
                : confidence > 0
                    ? {
                        icon: "!",
                        title: "Review recommended",
                        text:
                            "Average confidence is relatively low and manual verification may be useful.",
                    }
                    : {
                        icon: "◌",
                        title: "No analysis yet",
                        text:
                            "Analyze images to generate confidence statistics.",
                    };


    /* =========================================================
       RENDER
    ========================================================= */

    return (
        <main className="analytics-dashboard">


            {/* =================================================
                BACKGROUND DECORATION
            ================================================= */}

            <div className="analytics-orb analytics-orb-one"></div>

            <div className="analytics-orb analytics-orb-two"></div>


            <div className="analytics-container">


                {/* =================================================
                    PAGE HEADER
                ================================================= */}

                <section className="analytics-header">

                    <div className="analytics-header-copy">

                        <div className="analytics-eyebrow">
                            <span></span>
                            FORENSIC INTELLIGENCE
                        </div>

                        <h1>
                            Investigation
                            <span>
                                Analytics
                            </span>
                        </h1>

                        <p>
                            Monitor classification outcomes,
                            AI confidence and forensic engine
                            performance from one intelligence view.
                        </p>

                    </div>


                    <div className="analytics-header-actions">

                        <button
                            type="button"
                            className="analytics-refresh-btn"
                            onClick={fetchStats}
                            disabled={loading}
                        >
                            <span>
                                ↻
                            </span>

                            {loading
                                ? "Refreshing..."
                                : "Refresh data"}
                        </button>

                        <Link
                            to="/analyze"
                            className="analytics-primary-btn"
                        >
                            <span>+</span>
                            New Investigation
                            <b>→</b>
                        </Link>

                    </div>

                </section>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div className="analytics-error">

                        <div>
                            <strong>
                                Backend connection problem
                            </strong>

                            <span>
                                {error}
                            </span>
                        </div>

                        <button
                            type="button"
                            onClick={fetchStats}
                        >
                            Retry
                        </button>

                    </div>

                )}


                {/* =================================================
                    TOP METRICS
                ================================================= */}

                <section className="analytics-stat-grid">


                    {/* TOTAL */}

                    <article className="analytics-stat-card blue">

                        <div className="analytics-stat-head">

                            <span>
                                TOTAL CASES
                            </span>

                            <div className="analytics-stat-icon">
                                ◈
                            </div>

                        </div>

                        <strong>
                            {loading
                                ? "..."
                                : total}
                        </strong>

                        <p>
                            Cases processed by the engine
                        </p>

                        <div className="analytics-stat-line"></div>

                    </article>


                    {/* AUTHENTIC */}

                    <article className="analytics-stat-card green">

                        <div className="analytics-stat-head">

                            <span>
                                AUTHENTIC
                            </span>

                            <div className="analytics-stat-icon">
                                ✓
                            </div>

                        </div>

                        <strong>
                            {loading
                                ? "..."
                                : authentic}
                        </strong>

                        <p>
                            Verified authentic images
                        </p>

                        <div className="analytics-stat-line"></div>

                    </article>


                    {/* AI */}

                    <article className="analytics-stat-card purple">

                        <div className="analytics-stat-head">

                            <span>
                                AI GENERATED
                            </span>

                            <div className="analytics-stat-icon">
                                AI
                            </div>

                        </div>

                        <strong>
                            {loading
                                ? "..."
                                : aiGenerated}
                        </strong>

                        <p>
                            Synthetic imagery detected
                        </p>

                        <div className="analytics-stat-line"></div>

                    </article>


                    {/* MANIPULATED */}

                    <article className="analytics-stat-card red">

                        <div className="analytics-stat-head">

                            <span>
                                MANIPULATED
                            </span>

                            <div className="analytics-stat-icon">
                                !
                            </div>

                        </div>

                        <strong>
                            {loading
                                ? "..."
                                : manipulated}
                        </strong>

                        <p>
                            Potential editing detected
                        </p>

                        <div className="analytics-stat-line"></div>

                    </article>


                    {/* CONFIDENCE */}

                    <article className="analytics-stat-card cyan">

                        <div className="analytics-stat-head">

                            <span>
                                AVG CONFIDENCE
                            </span>

                            <div className="analytics-stat-icon">
                                ◉
                            </div>

                        </div>

                        <strong>
                            {loading
                                ? "..."
                                : confidence > 0
                                    ? `${confidence.toFixed(1)}%`
                                    : "—"}
                        </strong>

                        <p>
                            Average model confidence
                        </p>

                        <div className="analytics-stat-line"></div>

                    </article>

                </section>


                {/* =================================================
                    MAIN ANALYTICS
                ================================================= */}

                <section className="analytics-main-grid">


                    {/* =================================================
                        CLASSIFICATION
                    ================================================= */}

                    <article className="analytics-card classification-card">

                        <div className="analytics-card-header">

                            <div>

                                <span>
                                    CLASSIFICATION OVERVIEW
                                </span>

                                <h2>
                                    Investigation outcomes
                                </h2>

                            </div>

                            <div className="analytics-live-badge">
                                <span></span>
                                LIVE
                            </div>

                        </div>


                        <div className="classification-content">


                            {/* DONUT */}

                            <div className="classification-visual">

                                <div
                                    className="classification-donut"
                                    style={donutStyle}
                                >
                                    <div className="classification-donut-center">

                                        <strong>
                                            {loading
                                                ? "..."
                                                : total}
                                        </strong>

                                        <span>
                                            CASES
                                        </span>

                                    </div>
                                </div>

                                <div className="classification-caption">
                                    Classification
                                    distribution
                                </div>

                            </div>


                            {/* LEGEND */}

                            <div className="classification-legend">


                                <div className="classification-item green">

                                    <div className="classification-item-left">

                                        <span></span>

                                        <div>
                                            <strong>
                                                Authentic
                                            </strong>

                                            <small>
                                                Real / camera captured
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {authenticPercentage.toFixed(0)}%
                                    </b>

                                </div>


                                <div className="classification-item purple">

                                    <div className="classification-item-left">

                                        <span></span>

                                        <div>
                                            <strong>
                                                AI Generated
                                            </strong>

                                            <small>
                                                Synthetic imagery
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {aiGeneratedPercentage.toFixed(0)}%
                                    </b>

                                </div>


                                <div className="classification-item red">

                                    <div className="classification-item-left">

                                        <span></span>

                                        <div>
                                            <strong>
                                                Manipulated
                                            </strong>

                                            <small>
                                                Edited imagery
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {manipulatedPercentage.toFixed(0)}%
                                    </b>

                                </div>


                                <div className="classification-item amber">

                                    <div className="classification-item-left">

                                        <span></span>

                                        <div>
                                            <strong>
                                                Requires Review
                                            </strong>

                                            <small>
                                                Needs investigation
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {reviewPercentage.toFixed(0)}%
                                    </b>

                                </div>

                            </div>

                        </div>

                    </article>


                    {/* =================================================
                        CONFIDENCE
                    ================================================= */}

                    <article className="analytics-card confidence-card">

                        <div className="analytics-card-header">

                            <div>

                                <span>
                                    AI PERFORMANCE
                                </span>

                                <h2>
                                    Confidence score
                                </h2>

                            </div>

                            <div className="analytics-model-badge">
                                ResNet50
                            </div>

                        </div>


                        <div className="confidence-content">

                            <div className="confidence-ring-wrap">

                                <div
                                    className="confidence-ring"
                                    style={{
                                        "--score":
                                            `${confidence * 3.6}deg`,
                                    }}
                                >
                                    <div>
                                        <strong>
                                            {loading
                                                ? "..."
                                                : confidence > 0
                                                    ? confidence.toFixed(1)
                                                    : "—"}
                                        </strong>

                                        <span>
                                            %
                                        </span>
                                    </div>
                                </div>

                            </div>


                            <div className="confidence-info">

                                <div className="confidence-status">
                                    {confidenceMessage.icon}
                                </div>

                                <div>
                                    <strong>
                                        {confidenceMessage.title}
                                    </strong>

                                    <p>
                                        {confidenceMessage.text}
                                    </p>
                                </div>

                            </div>


                            <div className="confidence-scale">

                                <div className="confidence-bar">

                                    <span
                                        style={{
                                            width:
                                                `${confidence}%`,
                                        }}
                                    ></span>

                                </div>

                                <div>
                                    <span>0%</span>
                                    <span>50%</span>
                                    <span>100%</span>
                                </div>

                            </div>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    SECOND ROW
                ================================================= */}

                <section className="analytics-secondary-grid">


                    {/* =================================================
                        DISTRIBUTION
                    ================================================= */}

                    <article className="analytics-card distribution-card">

                        <div className="analytics-card-header">

                            <div>

                                <span>
                                    FORENSIC DISTRIBUTION
                                </span>

                                <h2>
                                    Result breakdown
                                </h2>

                            </div>

                        </div>


                        <div className="distribution-list">


                            <div className="distribution-item">

                                <div className="distribution-item-head">

                                    <div>

                                        <span className="distribution-dot green"></span>

                                        <div>
                                            <strong>
                                                Authentic
                                            </strong>

                                            <small>
                                                Verified real images
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {authentic}
                                    </b>

                                </div>

                                <div className="distribution-track">

                                    <span
                                        className="green"
                                        style={{
                                            width:
                                                `${Math.min(
                                                    100,
                                                    authenticPercentage
                                                )}%`,
                                        }}
                                    ></span>

                                </div>

                            </div>


                            <div className="distribution-item">

                                <div className="distribution-item-head">

                                    <div>

                                        <span className="distribution-dot purple"></span>

                                        <div>
                                            <strong>
                                                AI Generated
                                            </strong>

                                            <small>
                                                Synthetic imagery
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {aiGenerated}
                                    </b>

                                </div>

                                <div className="distribution-track">

                                    <span
                                        className="purple"
                                        style={{
                                            width:
                                                `${Math.min(
                                                    100,
                                                    aiGeneratedPercentage
                                                )}%`,
                                        }}
                                    ></span>

                                </div>

                            </div>


                            <div className="distribution-item">

                                <div className="distribution-item-head">

                                    <div>

                                        <span className="distribution-dot red"></span>

                                        <div>
                                            <strong>
                                                Manipulated
                                            </strong>

                                            <small>
                                                Potential manipulation
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {manipulated}
                                    </b>

                                </div>

                                <div className="distribution-track">

                                    <span
                                        className="red"
                                        style={{
                                            width:
                                                `${Math.min(
                                                    100,
                                                    manipulatedPercentage
                                                )}%`,
                                        }}
                                    ></span>

                                </div>

                            </div>


                            <div className="distribution-item">

                                <div className="distribution-item-head">

                                    <div>

                                        <span className="distribution-dot amber"></span>

                                        <div>
                                            <strong>
                                                Requires Review
                                            </strong>

                                            <small>
                                                Manual investigation
                                            </small>
                                        </div>

                                    </div>

                                    <b>
                                        {review}
                                    </b>

                                </div>

                                <div className="distribution-track">

                                    <span
                                        className="amber"
                                        style={{
                                            width:
                                                `${Math.min(
                                                    100,
                                                    reviewPercentage
                                                )}%`,
                                        }}
                                    ></span>

                                </div>

                            </div>

                        </div>

                    </article>


                    {/* =================================================
                        ENGINE STATUS
                    ================================================= */}

                    <article className="analytics-card engine-card">

                        <div className="analytics-card-header">

                            <div>

                                <span>
                                    SYSTEM
                                </span>

                                <h2>
                                    AI engine status
                                </h2>

                            </div>

                            <div className="engine-online">
                                <span></span>
                                ONLINE
                            </div>

                        </div>


                        <div className="engine-main">

                            <div className="engine-core">

                                <div className="engine-core-inner">
                                    IF
                                </div>

                            </div>


                            <div>

                                <strong>
                                    Forensic AI Operational
                                </strong>

                                <p>
                                    All forensic analysis services
                                    are ready to process evidence.
                                </p>

                            </div>

                        </div>


                        <div className="engine-services">

                            <div>
                                <span>
                                    RESNET50
                                </span>

                                <strong>
                                    ✓ READY
                                </strong>
                            </div>

                            <div>
                                <span>
                                    ELA
                                </span>

                                <strong>
                                    ✓ READY
                                </strong>
                            </div>

                            <div>
                                <span>
                                    GRAD-CAM
                                </span>

                                <strong>
                                    ✓ READY
                                </strong>
                            </div>

                            <div>
                                <span>
                                    API
                                </span>

                                <strong>
                                    ✓ ONLINE
                                </strong>
                            </div>

                        </div>

                    </article>

                </section>


                {/* =================================================
                    ACTION BANNER
                ================================================= */}

                <section className="analytics-action-banner">

                    <div>

                        <span>
                            READY FOR YOUR NEXT INVESTIGATION?
                        </span>

                        <h2>
                            Analyze new digital evidence
                        </h2>

                        <p>
                            Run the complete forensic pipeline
                            with classification, ELA and Grad-CAM.
                        </p>

                    </div>


                    <div className="analytics-action-buttons">

                        <Link
                            to="/analyze"
                            className="analytics-primary-btn"
                        >
                            Start Investigation
                            <b>→</b>
                        </Link>

                        <Link
                            to="/history"
                            className="analytics-secondary-btn"
                        >
                            Evidence Vault
                        </Link>

                    </div>

                </section>


                {/* =================================================
                    FOOTER
                ================================================= */}

                <footer className="analytics-footer">

                    <div>
                        <strong>
                            ImageForensics
                        </strong>

                        <span>
                            Digital evidence intelligence platform
                        </span>
                    </div>

                    <div>
                        <span>
                            SYSTEM
                        </span>

                        <strong>
                            ● OPERATIONAL
                        </strong>
                    </div>

                </footer>

            </div>

        </main>
    );
}

export default Dashboard;