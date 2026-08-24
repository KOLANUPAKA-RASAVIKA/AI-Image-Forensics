import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import "./Home.css";

const API_URL = "http://127.0.0.1:5001";

function Home() {
    const [user, setUser] = useState(null);

    const [stats, setStats] = useState({
        total_cases: 0,
        authentic_images: 0,
        manipulated_images: 0,
        ai_generated_images: 0,
        requires_review: 0,
        average_confidence: 0,
    });

    const [statsLoading, setStatsLoading] = useState(true);
    const [statsError, setStatsError] = useState(false);


    /* =========================================================
       LOAD USER
    ========================================================= */

    useEffect(() => {
        const storedUser =
            localStorage.getItem("forensicsUser");

        if (!storedUser) {
            return;
        }

        try {
            setUser(JSON.parse(storedUser));
        } catch {
            setUser(null);
        }
    }, []);


    /* =========================================================
       LOAD STATISTICS
    ========================================================= */

    const fetchStats = async () => {
        try {
            setStatsLoading(true);
            setStatsError(false);

            const response = await fetch(
                `${API_URL}/api/stats`
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to fetch statistics"
                );
            }

            const data = await response.json();

            if (!data.success || !data.data) {
                throw new Error(
                    "Invalid statistics response"
                );
            }

            const result = data.data;

            setStats({
                total_cases:
                    Number(result.total_cases) || 0,

                authentic_images:
                    Number(
                        result.authentic_images ??
                        result.real_images ??
                        0
                    ),

                manipulated_images:
                    Number(
                        result.manipulated_images ??
                        result.fake_images ??
                        0
                    ),

                ai_generated_images:
                    Number(
                        result.ai_generated_images ??
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
            });

        } catch (error) {
            console.error(
                "Failed to load dashboard statistics:",
                error
            );

            setStatsError(true);

        } finally {
            setStatsLoading(false);
        }
    };


    useEffect(() => {
        fetchStats();
    }, []);


    /* =========================================================
       USER NAME
    ========================================================= */

    const userName =
        user?.name ||
        user?.email?.split("@")[0] ||
        "Investigator";


    /* =========================================================
       STAT VALUES
    ========================================================= */

    const total =
        stats.total_cases;

    const authentic =
        stats.authentic_images;

    const manipulated =
        stats.manipulated_images;

    const aiGenerated =
        stats.ai_generated_images;

    const review =
        stats.requires_review;

    let confidence =
        Number(stats.average_confidence) || 0;

    if (confidence <= 1 && confidence > 0) {
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

    const aiPercentage =
        total > 0
            ? (aiGenerated / total) * 100
            : 0;

    const manipulatedPercentage =
        total > 0
            ? (manipulated / total) * 100
            : 0;

    const reviewPercentage =
        total > 0
            ? (review / total) * 100
            : 0;


    /* =========================================================
       DONUT
    ========================================================= */

    const donutBackground = useMemo(() => {
        if (total === 0) {
            return "#e8eef6";
        }

        const first =
            authenticPercentage;

        const second =
            first + aiPercentage;

        const third =
            second + manipulatedPercentage;

        return `
            conic-gradient(
                #22c55e 0% ${first}%,
                #8b5cf6 ${first}% ${second}%,
                #ef4444 ${second}% ${third}%,
                #f59e0b ${third}% 100%
            )
        `;
    }, [
        total,
        authenticPercentage,
        aiPercentage,
        manipulatedPercentage,
    ]);


    /* =========================================================
       RENDER
    ========================================================= */

    return (
        <main className="home-page">

            {/* =================================================
                BACKGROUND
            ================================================= */}

            <div className="home-orb home-orb-one"></div>
            <div className="home-orb home-orb-two"></div>


            {/* =================================================
                HERO
            ================================================= */}

            <section className="home-hero">

                <div className="home-hero-copy">

                    <div className="home-kicker">
                        <span></span>
                        FORENSIC INTELLIGENCE CENTER
                    </div>


                    <h1>
                        Welcome back,
                        <span>
                            {userName}.
                        </span>
                    </h1>


                    <p>
                        Investigate digital evidence with
                        AI-powered image classification,
                        forensic analysis and explainable AI.
                    </p>


                    <div className="home-hero-actions">

                        <Link
                            to="/analyze"
                            className="home-primary-btn"
                        >
                            <span className="home-btn-icon">
                                +
                            </span>

                            Start Investigation

                            <span className="home-btn-arrow">
                                →
                            </span>
                        </Link>


                        <Link
                            to="/dashboard"
                            className="home-secondary-btn"
                        >
                            View Analytics

                            <span>
                                →
                            </span>
                        </Link>

                    </div>


                    <div className="home-trust-row">

                        <div>
                            <span className="home-trust-dot green"></span>
                            AI ENGINE ONLINE
                        </div>

                        <div>
                            <span className="home-trust-dot blue"></span>
                            RESNET50
                        </div>

                        <div>
                            <span className="home-trust-dot purple"></span>
                            ELA + GRAD-CAM
                        </div>

                    </div>

                </div>


                {/* =================================================
                    3D FORENSIC VISUAL
                ================================================= */}

                <div className="home-hero-visual">

                    <div className="home-visual-grid"></div>

                    <div className="home-visual-ring ring-one"></div>
                    <div className="home-visual-ring ring-two"></div>
                    <div className="home-visual-ring ring-three"></div>


                    <div className="home-hologram">

                        <div className="home-hologram-face face-top">
                            IF
                        </div>

                        <div className="home-hologram-face face-front">

                            <strong>
                                IF
                            </strong>

                            <span>
                                FORENSICS
                            </span>

                        </div>

                        <div className="home-hologram-face face-left"></div>
                        <div className="home-hologram-face face-right"></div>

                    </div>


                    <div className="home-scan-platform">
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>


                    <div className="home-floating-chip chip-one">
                        <span>AI</span>
                        <strong>Detection</strong>
                    </div>


                    <div className="home-floating-chip chip-two">
                        <span>ELA</span>
                        <strong>Analysis</strong>
                    </div>


                    <div className="home-floating-chip chip-three">
                        <span>CAM</span>
                        <strong>Explainability</strong>
                    </div>

                </div>

            </section>


            {/* =================================================
                SYSTEM STATUS
            ================================================= */}

            <section className="home-status-card">

                <div className="home-status-main">

                    <div className="home-status-icon">
                        <span></span>
                    </div>

                    <div>

                        <strong>
                            Forensic AI Engine Operational
                        </strong>

                        <p>
                            ResNet50 classification •
                            Error Level Analysis •
                            Grad-CAM explainability
                        </p>

                    </div>

                </div>


                <div className="home-status-metrics">

                    <div>
                        <span>
                            MODEL
                        </span>

                        <strong>
                            ResNet50
                        </strong>
                    </div>


                    <div>
                        <span>
                            API
                        </span>

                        <strong className="green-text">
                            ONLINE
                        </strong>
                    </div>


                    <div>
                        <span>
                            ENGINE
                        </span>

                        <strong className="green-text">
                            READY
                        </strong>
                    </div>

                </div>

            </section>


            {/* =================================================
                STATISTICS
            ================================================= */}

            <section className="home-stats-grid">

                <article className="home-stat-card blue">

                    <div className="home-stat-top">
                        <span>
                            TOTAL CASES
                        </span>

                        <div className="home-stat-icon">
                            ◈
                        </div>
                    </div>

                    <strong>
                        {statsLoading
                            ? "..."
                            : total}
                    </strong>

                    <p>
                        Investigations processed
                    </p>

                    <div className="home-stat-accent"></div>

                </article>


                <article className="home-stat-card green">

                    <div className="home-stat-top">
                        <span>
                            AUTHENTIC
                        </span>

                        <div className="home-stat-icon">
                            ✓
                        </div>
                    </div>

                    <strong>
                        {statsLoading
                            ? "..."
                            : authentic}
                    </strong>

                    <p>
                        Camera / authentic evidence
                    </p>

                    <div className="home-stat-accent"></div>

                </article>


                <article className="home-stat-card purple">

                    <div className="home-stat-top">
                        <span>
                            AI GENERATED
                        </span>

                        <div className="home-stat-icon">
                            AI
                        </div>
                    </div>

                    <strong>
                        {statsLoading
                            ? "..."
                            : aiGenerated}
                    </strong>

                    <p>
                        Synthetic imagery detected
                    </p>

                    <div className="home-stat-accent"></div>

                </article>


                <article className="home-stat-card red">

                    <div className="home-stat-top">
                        <span>
                            MANIPULATED
                        </span>

                        <div className="home-stat-icon">
                            !
                        </div>
                    </div>

                    <strong>
                        {statsLoading
                            ? "..."
                            : manipulated}
                    </strong>

                    <p>
                        Potentially edited evidence
                    </p>

                    <div className="home-stat-accent"></div>

                </article>


                <article className="home-stat-card cyan">

                    <div className="home-stat-top">
                        <span>
                            AVG CONFIDENCE
                        </span>

                        <div className="home-stat-icon">
                            ◉
                        </div>
                    </div>

                    <strong>
                        {statsLoading
                            ? "..."
                            : confidence > 0
                                ? `${confidence.toFixed(1)}%`
                                : "—"}
                    </strong>

                    <p>
                        Model prediction confidence
                    </p>

                    <div className="home-stat-accent"></div>

                </article>

            </section>


            {/* =================================================
                ERROR
            ================================================= */}

            {statsError && (
                <div className="home-error">

                    <div>

                        <strong>
                            Live statistics unavailable
                        </strong>

                        <span>
                            Make sure the Flask AI engine is
                            running on port 5001.
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
                WORKSPACE
            ================================================= */}

            <section className="home-workspace-grid">


                {/* INVESTIGATION */}

                <article className="home-investigation-card">

                    <div className="home-section-heading">

                        <div>

                            <span>
                                FORENSIC WORKFLOW
                            </span>

                            <h2>
                                Start an investigation
                            </h2>

                        </div>

                        <div className="home-card-number">
                            01
                        </div>

                    </div>


                    <p className="home-investigation-description">
                        Upload an image and let the forensic
                        intelligence engine examine authenticity,
                        manipulation patterns and AI-generation signals.
                    </p>


                    <div className="home-workflow">

                        <div className="home-workflow-step active">
                            <div>
                                01
                            </div>

                            <span>
                                Upload
                            </span>
                        </div>


                        <div className="home-workflow-line"></div>


                        <div className="home-workflow-step">
                            <div>
                                02
                            </div>

                            <span>
                                Detect
                            </span>
                        </div>


                        <div className="home-workflow-line"></div>


                        <div className="home-workflow-step">
                            <div>
                                03
                            </div>

                            <span>
                                Explain
                            </span>
                        </div>


                        <div className="home-workflow-line"></div>


                        <div className="home-workflow-step">
                            <div>
                                04
                            </div>

                            <span>
                                Report
                            </span>
                        </div>

                    </div>


                    <Link
                        to="/analyze"
                        className="home-investigate-btn"
                    >
                        Begin Image Investigation

                        <span>
                            →
                        </span>
                    </Link>

                </article>


                {/* DISTRIBUTION */}

                <article className="home-distribution-card">

                    <div className="home-section-heading">

                        <div>

                            <span>
                                CASE DISTRIBUTION
                            </span>

                            <h2>
                                Investigation overview
                            </h2>

                        </div>

                    </div>


                    <div className="home-distribution-content">

                        <div
                            className="home-donut"
                            style={{
                                background:
                                    donutBackground,
                            }}
                        >

                            <div className="home-donut-center">

                                <strong>
                                    {statsLoading
                                        ? "..."
                                        : total}
                                </strong>

                                <span>
                                    CASES
                                </span>

                            </div>

                        </div>


                        <div className="home-legend">

                            <div className="home-legend-item">

                                <span className="green"></span>

                                <div>
                                    <strong>
                                        Authentic
                                    </strong>

                                    <small>
                                        {authentic} cases
                                    </small>
                                </div>

                                <b>
                                    {authenticPercentage.toFixed(0)}%
                                </b>

                            </div>


                            <div className="home-legend-item">

                                <span className="purple"></span>

                                <div>
                                    <strong>
                                        AI Generated
                                    </strong>

                                    <small>
                                        {aiGenerated} cases
                                    </small>
                                </div>

                                <b>
                                    {aiPercentage.toFixed(0)}%
                                </b>

                            </div>


                            <div className="home-legend-item">

                                <span className="red"></span>

                                <div>
                                    <strong>
                                        Manipulated
                                    </strong>

                                    <small>
                                        {manipulated} cases
                                    </small>
                                </div>

                                <b>
                                    {manipulatedPercentage.toFixed(0)}%
                                </b>

                            </div>


                            <div className="home-legend-item">

                                <span className="amber"></span>

                                <div>
                                    <strong>
                                        Review
                                    </strong>

                                    <small>
                                        {review} cases
                                    </small>
                                </div>

                                <b>
                                    {reviewPercentage.toFixed(0)}%
                                </b>

                            </div>

                        </div>

                    </div>

                </article>

            </section>


            {/* =================================================
                QUICK ACTIONS + CAPABILITIES
            ================================================= */}

            <section className="home-bottom-grid">


                <article className="home-quick-card">

                    <div className="home-section-heading">

                        <div>

                            <span>
                                WORKSPACE
                            </span>

                            <h2>
                                Quick actions
                            </h2>

                        </div>

                    </div>


                    <div className="home-quick-list">

                        <Link
                            to="/analyze"
                            className="home-quick-action blue"
                        >

                            <div className="home-quick-icon">
                                ↑
                            </div>

                            <div>
                                <strong>
                                    Analyze Image
                                </strong>

                                <span>
                                    Start a new forensic scan
                                </span>
                            </div>

                            <b>
                                →
                            </b>

                        </Link>


                        <Link
                            to="/dashboard"
                            className="home-quick-action purple"
                        >

                            <div className="home-quick-icon">
                                ◒
                            </div>

                            <div>
                                <strong>
                                    Analytics
                                </strong>

                                <span>
                                    Explore investigation data
                                </span>
                            </div>

                            <b>
                                →
                            </b>

                        </Link>


                        <Link
                            to="/history"
                            className="home-quick-action amber"
                        >

                            <div className="home-quick-icon">
                                ▣
                            </div>

                            <div>
                                <strong>
                                    Evidence Vault
                                </strong>

                                <span>
                                    Review saved investigations
                                </span>
                            </div>

                            <b>
                                →
                            </b>

                        </Link>

                    </div>

                </article>


                <article className="home-capabilities-card">

                    <div className="home-section-heading">

                        <div>

                            <span>
                                INTELLIGENCE ENGINE
                            </span>

                            <h2>
                                Analysis layers
                            </h2>

                        </div>

                        <span className="home-live-badge">
                            ● ONLINE
                        </span>

                    </div>


                    <div className="home-capability">

                        <div className="home-capability-number blue">
                            01
                        </div>

                        <div>

                            <strong>
                                ResNet50 Classification
                            </strong>

                            <p>
                                Identifies authentic,
                                AI-generated and manipulated imagery.
                            </p>

                        </div>

                        <span>
                            READY
                        </span>

                    </div>


                    <div className="home-capability">

                        <div className="home-capability-number cyan">
                            02
                        </div>

                        <div>

                            <strong>
                                Error Level Analysis
                            </strong>

                            <p>
                                Examines compression and
                                manipulation anomalies.
                            </p>

                        </div>

                        <span>
                            READY
                        </span>

                    </div>


                    <div className="home-capability">

                        <div className="home-capability-number purple">
                            03
                        </div>

                        <div>

                            <strong>
                                Grad-CAM Explainability
                            </strong>

                            <p>
                                Visualizes regions influencing
                                the model decision.
                            </p>

                        </div>

                        <span>
                            READY
                        </span>

                    </div>

                </article>

            </section>


            {/* =================================================
                FOOTER
            ================================================= */}

            <footer className="home-footer">

                <div>

                    <strong>
                        ImageForensics
                    </strong>

                    <span>
                        AI-powered digital evidence analysis
                    </span>

                </div>


                <div>

                    <span>
                        SYSTEM STATUS
                    </span>

                    <strong>
                        ● OPERATIONAL
                    </strong>

                </div>

            </footer>

        </main>
    );
}

export default Home;