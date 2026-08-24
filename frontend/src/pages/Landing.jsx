import { Link } from "react-router-dom";
import { useState } from "react";

function Landing() {
    const [activeFeature, setActiveFeature] = useState(0);

    const features = [
        {
            icon: "◉",
            title: "AI Image Detection",
            text: "Analyze images using your trained ResNet-based forensic classification model."
        },
        {
            icon: "⌁",
            title: "ELA Analysis",
            text: "Reveal compression inconsistencies and suspicious regions using Error Level Analysis."
        },
        {
            icon: "✦",
            title: "Grad-CAM Explainability",
            text: "Visualize the regions that influenced the AI model's prediction."
        }
    ];

    return (
        <div className="landing-page">

            {/* ================= NAVBAR ================= */}

            <nav className="landing-navbar">

                <Link to="/" className="landing-brand">

                    <div className="forensic-logo">
                        <div className="logo-core">
                            IF
                        </div>

                        <span className="logo-ring ring-one"></span>
                        <span className="logo-ring ring-two"></span>
                    </div>

                    <div>
                        <strong>ImageForensics</strong>
                        <span>AI Investigation Platform</span>
                    </div>

                </Link>

                <div className="landing-nav-links">
                    <a href="#features">Capabilities</a>
                    <a href="#workflow">How It Works</a>
                    <a href="#about">Technology</a>

                    <Link
                        to="/login"
                        className="landing-login"
                    >
                        Sign In
                    </Link>

                    <Link
                        to="/signup"
                        className="landing-nav-cta"
                    >
                        Start Investigation
                    </Link>
                </div>

            </nav>


            {/* ================= HERO ================= */}

            <section className="hero-section">

                <div className="hero-content">

                    <div className="status-pill">
                        <span className="status-dot"></span>

                        AI FORENSIC ENGINE ONLINE

                        <span className="status-arrow">
                            →
                        </span>
                    </div>

                    <h1>
                        Discover the truth
                        <br />

                        <span className="gradient-text">
                            behind every image.
                        </span>
                    </h1>

                    <p className="hero-description">
                        An AI-powered digital image investigation platform
                        designed to detect manipulation, analyze forensic
                        evidence, and explain what your image model sees.
                    </p>

                    <div className="hero-actions">

                        <Link
                            to="/upload"
                            className="primary-hero-btn"
                        >
                            <span>Start New Investigation</span>
                            <span>→</span>
                        </Link>

                        <a
                            href="#workflow"
                            className="secondary-hero-btn"
                        >
                            Explore Platform
                        </a>

                    </div>

                    <div className="hero-trust">

                        <div className="trust-item">
                            <span>✓</span>
                            AI-assisted detection
                        </div>

                        <div className="trust-item">
                            <span>✓</span>
                            ELA forensic analysis
                        </div>

                        <div className="trust-item">
                            <span>✓</span>
                            Grad-CAM explainability
                        </div>

                    </div>

                </div>


                {/* ================= 3D FORENSIC VISUAL ================= */}

                <div className="hero-visual">

                    <div className="visual-glow"></div>

                    <div className="forensic-orbit orbit-one"></div>
                    <div className="forensic-orbit orbit-two"></div>

                    <div className="forensic-core">

                        <div className="core-scanner"></div>

                        <div className="core-icon">
                            ◈
                        </div>

                        <div className="core-label">
                            <span>FORENSIC</span>
                            <strong>SCAN</strong>
                        </div>

                    </div>

                    <div className="floating-card card-confidence">

                        <div className="mini-icon green">
                            ✓
                        </div>

                        <div>
                            <span>Model Confidence</span>
                            <strong>94.13%</strong>
                        </div>

                    </div>

                    <div className="floating-card card-detection">

                        <div className="mini-icon blue">
                            ✦
                        </div>

                        <div>
                            <span>AI Verdict</span>
                            <strong>REAL IMAGE</strong>
                        </div>

                    </div>

                    <div className="floating-card card-signal">

                        <div className="signal-bars">
                            <i></i>
                            <i></i>
                            <i></i>
                            <i></i>
                            <i></i>
                        </div>

                        <div>
                            <span>Forensic Signal</span>
                            <strong>ANALYZING</strong>
                        </div>

                    </div>

                </div>

            </section>


            {/* ================= FEATURES ================= */}

            <section
                className="features-section"
                id="features"
            >

                <div className="section-heading">

                    <span className="section-label">
                        FORENSIC CAPABILITIES
                    </span>

                    <h2>
                        More than a prediction.
                    </h2>

                    <p>
                        Combine AI classification with visual forensic
                        evidence to understand why an image may be suspicious.
                    </p>

                </div>


                <div className="feature-grid">

                    {features.map((feature, index) => (

                        <div
                            key={feature.title}
                            className={`feature-card ${
                                activeFeature === index
                                    ? "feature-active"
                                    : ""
                            }`}
                            onMouseEnter={() =>
                                setActiveFeature(index)
                            }
                        >

                            <div className="feature-icon">
                                {feature.icon}
                            </div>

                            <span className="feature-number">
                                0{index + 1}
                            </span>

                            <h3>
                                {feature.title}
                            </h3>

                            <p>
                                {feature.text}
                            </p>

                            <div className="feature-arrow">
                                →
                            </div>

                        </div>

                    ))}

                </div>

            </section>


            {/* ================= WORKFLOW ================= */}

            <section
                className="workflow-section"
                id="workflow"
            >

                <div className="section-heading">

                    <span className="section-label">
                        INVESTIGATION WORKFLOW
                    </span>

                    <h2>
                        From image to evidence.
                    </h2>

                    <p>
                        A structured workflow turns a simple upload into
                        an AI-assisted forensic investigation.
                    </p>

                </div>


                <div className="workflow">

                    <div className="workflow-line"></div>

                    <div className="workflow-step">

                        <div className="workflow-number">
                            01
                        </div>

                        <h3>
                            Upload Evidence
                        </h3>

                        <p>
                            Submit the image you want to investigate.
                        </p>

                    </div>

                    <div className="workflow-step">

                        <div className="workflow-number">
                            02
                        </div>

                        <h3>
                            AI Classification
                        </h3>

                        <p>
                            The trained model evaluates the image.
                        </p>

                    </div>

                    <div className="workflow-step">

                        <div className="workflow-number">
                            03
                        </div>

                        <h3>
                            Forensic Analysis
                        </h3>

                        <p>
                            ELA and Grad-CAM provide additional evidence.
                        </p>

                    </div>

                    <div className="workflow-step">

                        <div className="workflow-number">
                            04
                        </div>

                        <h3>
                            Investigate
                        </h3>

                        <p>
                            Review the evidence and generate a report.
                        </p>

                    </div>

                </div>

            </section>


            {/* ================= CTA ================= */}

            <section
                className="landing-cta"
                id="about"
            >

                <div className="cta-glow"></div>

                <span className="section-label">
                    READY TO INVESTIGATE?
                </span>

                <h2>
                    Don't just look at an image.
                    <br />
                    <span>Investigate it.</span>
                </h2>

                <p>
                    Start your first AI-assisted image forensic investigation.
                </p>

                <Link
                    to="/upload"
                    className="primary-hero-btn"
                >
                    Start Investigation →
                </Link>

            </section>


            {/* ================= FOOTER ================= */}

            <footer className="landing-footer">

                <div>
                    <strong>ImageForensics</strong>
                    <span>
                        AI-assisted digital image investigation.
                    </span>
                </div>

                <span>
                    © 2026 ImageForensics
                </span>

            </footer>

        </div>
    );
}

export default Landing;