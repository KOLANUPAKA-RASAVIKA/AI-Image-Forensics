import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "./History.css";

const API_URL = "http://127.0.0.1:5001";

function History() {
    const [investigations, setInvestigations] = useState([]);
    const [search, setSearch] = useState("");
    const [filter, setFilter] = useState("ALL");


    /* =====================================================
       LOAD HISTORY
    ===================================================== */

    useEffect(() => {
        loadHistory();
    }, []);


    const loadHistory = () => {
        try {
            const storedHistory =
                localStorage.getItem(
                    "investigationHistory"
                );

            if (!storedHistory) {
                setInvestigations([]);
                return;
            }

            const parsed =
                JSON.parse(storedHistory);

            if (Array.isArray(parsed)) {
                setInvestigations(parsed);
            } else {
                setInvestigations([]);
            }

        } catch (error) {
            console.error(
                "Unable to load investigation history:",
                error
            );

            setInvestigations([]);
        }
    };


    /* =====================================================
       HELPERS
    ===================================================== */

    const getPrediction = (item) => {
        const prediction =
            item?.prediction;

        if (
            prediction &&
            typeof prediction === "object"
        ) {
            return String(
                prediction?.predicted_class ||
                prediction?.result ||
                prediction?.class ||
                item?.result_label ||
                item?.result ||
                "UNKNOWN"
            ).toUpperCase();
        }

        return String(
            prediction ||
            item?.result_label ||
            item?.result ||
            item?.label ||
            "UNKNOWN"
        ).toUpperCase();
    };


    const getFileName = (item) => {
        return (
            item?.fileName ||
            item?.filename ||
            item?.name ||
            "Unknown image"
        );
    };


    const getConfidenceValue = (item) => {
        let value;

        if (
            item?.prediction &&
            typeof item.prediction === "object"
        ) {
            value =
                item.prediction?.confidence_percentage ??
                item.prediction?.confidence;
        }

        if (
            value === undefined ||
            value === null
        ) {
            value =
                item?.confidence_percentage ??
                item?.confidence ??
                item?.score ??
                item?.probability;
        }

        const numericValue =
            Number(value);

        if (
            Number.isNaN(numericValue)
        ) {
            return 0;
        }

        const percentage =
            numericValue <= 1
                ? numericValue * 100
                : numericValue;

        return Math.max(
            0,
            Math.min(
                100,
                percentage
            )
        );
    };


    const getConfidence = (item) => {
        const value =
            getConfidenceValue(item);

        return value > 0
            ? `${value.toFixed(1)}%`
            : "—";
    };


    const getDate = (item) => {
        const dateValue =
            item?.created_at ||
            item?.createdAt ||
            item?.date ||
            item?.timestamp;

        if (!dateValue) {
            return "Unknown date";
        }

        try {
            return new Date(
                dateValue
            ).toLocaleString(
                undefined,
                {
                    dateStyle: "medium",
                    timeStyle: "short",
                }
            );
        } catch {
            return "Unknown date";
        }
    };


    const getCaseId = (
        item,
        index
    ) => {
        return (
            item?.case_id ||
            item?.caseId ||
            item?.id ||
            `CASE-${String(
                index + 1
            ).padStart(4, "0")}`
        );
    };


    const getImageUrl = (item) => {
        const url =
            item?.image_url ||
            item?.imageUrl ||
            item?.image;

        if (!url) {
            return "";
        }

        if (
            url.startsWith("http://") ||
            url.startsWith("https://")
        ) {
            return url;
        }

        return `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
    };


    const getStatusClass = (
        prediction
    ) => {

        const value =
            String(prediction)
                .toUpperCase();

        if (
            value.includes("AUTHENTIC") ||
            value.includes("REAL")
        ) {
            return "history-authentic";
        }

        if (
            value.includes("AI_GENERATED")
        ) {
            return "history-ai";
        }

        if (
            value.includes("MANIPULATED") ||
            value.includes("FAKE")
        ) {
            return "history-manipulated";
        }

        return "history-review";
    };


    const getStatusLabel = (
        prediction
    ) => {

        const value =
            String(prediction)
                .toUpperCase();

        if (
            value.includes("AUTHENTIC") ||
            value.includes("REAL")
        ) {
            return "AUTHENTIC";
        }

        if (
            value.includes("AI_GENERATED")
        ) {
            return "AI GENERATED";
        }

        if (
            value.includes("MANIPULATED") ||
            value.includes("FAKE")
        ) {
            return "MANIPULATED";
        }

        return "REVIEW";
    };


    const getStatusIcon = (
        prediction
    ) => {

        const value =
            String(prediction)
                .toUpperCase();

        if (
            value.includes("AUTHENTIC") ||
            value.includes("REAL")
        ) {
            return "✓";
        }

        if (
            value.includes("AI_GENERATED")
        ) {
            return "AI";
        }

        if (
            value.includes("MANIPULATED") ||
            value.includes("FAKE")
        ) {
            return "!";
        }

        return "?";
    };


    /* =====================================================
       FILTER
    ===================================================== */

    const filteredInvestigations =
        useMemo(() => {

            return investigations.filter(
                (item) => {

                    const fileName =
                        getFileName(item);

                    const prediction =
                        getPrediction(item);

                    const searchValue =
                        search
                            .trim()
                            .toLowerCase();

                    const matchesSearch =
                        !searchValue ||
                        fileName
                            .toLowerCase()
                            .includes(searchValue) ||
                        prediction
                            .toLowerCase()
                            .includes(searchValue);

                    let matchesFilter =
                        true;

                    if (
                        filter === "AUTHENTIC"
                    ) {
                        matchesFilter =
                            prediction.includes(
                                "AUTHENTIC"
                            ) ||
                            prediction.includes(
                                "REAL"
                            );
                    }

                    if (
                        filter === "AI"
                    ) {
                        matchesFilter =
                            prediction.includes(
                                "AI_GENERATED"
                            );
                    }

                    if (
                        filter === "MANIPULATED"
                    ) {
                        matchesFilter =
                            prediction.includes(
                                "MANIPULATED"
                            ) ||
                            prediction.includes(
                                "FAKE"
                            );
                    }

                    if (
                        filter === "REVIEW"
                    ) {
                        matchesFilter =
                            !prediction.includes(
                                "AUTHENTIC"
                            ) &&
                            !prediction.includes(
                                "REAL"
                            ) &&
                            !prediction.includes(
                                "AI_GENERATED"
                            ) &&
                            !prediction.includes(
                                "MANIPULATED"
                            ) &&
                            !prediction.includes(
                                "FAKE"
                            );
                    }

                    return (
                        matchesSearch &&
                        matchesFilter
                    );
                }
            );

        }, [
            investigations,
            search,
            filter,
        ]);


    /* =====================================================
       COUNTS
    ===================================================== */

    const totalInvestigations =
        investigations.length;

    const authenticCount =
        investigations.filter(
            (item) => {

                const prediction =
                    getPrediction(item);

                return (
                    prediction.includes(
                        "AUTHENTIC"
                    ) ||
                    prediction.includes(
                        "REAL"
                    )
                );
            }
        ).length;


    const aiCount =
        investigations.filter(
            (item) =>
                getPrediction(
                    item
                ).includes(
                    "AI_GENERATED"
                )
        ).length;


    const manipulatedCount =
        investigations.filter(
            (item) => {

                const prediction =
                    getPrediction(item);

                return (
                    prediction.includes(
                        "MANIPULATED"
                    ) ||
                    prediction.includes(
                        "FAKE"
                    )
                );
            }
        ).length;


    const reviewCount =
        Math.max(
            0,
            totalInvestigations -
            authenticCount -
            aiCount -
            manipulatedCount
        );


    /* =====================================================
       CLEAR HISTORY
    ===================================================== */

    const clearHistory = () => {

        const confirmed =
            window.confirm(
                "Are you sure you want to clear all investigation history?"
            );

        if (!confirmed) {
            return;
        }

        localStorage.removeItem(
            "investigationHistory"
        );

        setInvestigations([]);
    };


    /* =====================================================
       RENDER
    ===================================================== */

    return (
        <main className="history-page">


            {/* =================================================
                DECORATIVE BACKGROUND
            ================================================= */}

            <div className="history-orb history-orb-one"></div>

            <div className="history-orb history-orb-two"></div>


            <div className="history-container-main">


                {/* =================================================
                    HEADER
                ================================================= */}

                <section className="history-header">

                    <div>

                        <div className="history-eyebrow">
                            <span></span>
                            EVIDENCE VAULT
                        </div>

                        <h1>
                            Investigation
                            <span>
                                History
                            </span>
                        </h1>

                        <p>
                            Review, search and manage
                            your previously analyzed
                            digital evidence.
                        </p>

                    </div>


                    <Link
                        to="/analyze"
                        className="history-new-btn"
                    >
                        <span>
                            +
                        </span>

                        New Investigation

                        <b>
                            →
                        </b>
                    </Link>

                </section>


                {/* =================================================
                    STATISTICS
                ================================================= */}

                <section className="history-stats">


                    <article className="history-stat-card blue">

                        <div className="history-stat-icon">
                            ◈
                        </div>

                        <div>
                            <span>
                                TOTAL CASES
                            </span>

                            <strong>
                                {totalInvestigations}
                            </strong>

                            <small>
                                Investigations
                            </small>
                        </div>

                    </article>


                    <article className="history-stat-card green">

                        <div className="history-stat-icon">
                            ✓
                        </div>

                        <div>
                            <span>
                                AUTHENTIC
                            </span>

                            <strong>
                                {authenticCount}
                            </strong>

                            <small>
                                Verified images
                            </small>
                        </div>

                    </article>


                    <article className="history-stat-card purple">

                        <div className="history-stat-icon">
                            AI
                        </div>

                        <div>
                            <span>
                                AI GENERATED
                            </span>

                            <strong>
                                {aiCount}
                            </strong>

                            <small>
                                Synthetic images
                            </small>
                        </div>

                    </article>


                    <article className="history-stat-card red">

                        <div className="history-stat-icon">
                            !
                        </div>

                        <div>
                            <span>
                                MANIPULATED
                            </span>

                            <strong>
                                {manipulatedCount}
                            </strong>

                            <small>
                                Suspicious images
                            </small>
                        </div>

                    </article>


                    <article className="history-stat-card amber">

                        <div className="history-stat-icon">
                            ?
                        </div>

                        <div>
                            <span>
                                REVIEW
                            </span>

                            <strong>
                                {reviewCount}
                            </strong>

                            <small>
                                Manual review
                            </small>
                        </div>

                    </article>

                </section>


                {/* =================================================
                    TOOLBAR
                ================================================= */}

                <section className="history-toolbar">

                    <div className="history-search">

                        <span>
                            ⌕
                        </span>

                        <input
                            type="text"
                            placeholder="Search by filename or classification..."
                            value={search}
                            onChange={(event) =>
                                setSearch(
                                    event.target.value
                                )
                            }
                        />

                        {search && (
                            <button
                                type="button"
                                className="history-search-clear"
                                onClick={() =>
                                    setSearch("")
                                }
                            >
                                ×
                            </button>
                        )}

                    </div>


                    <div className="history-filters">

                        {[
                            {
                                value: "ALL",
                                label: "All",
                            },
                            {
                                value: "AUTHENTIC",
                                label: "Authentic",
                            },
                            {
                                value: "AI",
                                label: "AI Generated",
                            },
                            {
                                value: "MANIPULATED",
                                label: "Manipulated",
                            },
                            {
                                value: "REVIEW",
                                label: "Review",
                            },
                        ].map(
                            (item) => (

                                <button
                                    key={item.value}
                                    type="button"
                                    className={
                                        filter ===
                                        item.value
                                            ? `history-filter active ${item.value.toLowerCase()}`
                                            : "history-filter"
                                    }
                                    onClick={() =>
                                        setFilter(
                                            item.value
                                        )
                                    }
                                >
                                    {item.label}
                                </button>

                            )
                        )}

                    </div>


                    {investigations.length > 0 && (

                        <button
                            type="button"
                            className="clear-history-btn"
                            onClick={clearHistory}
                        >
                            Clear
                        </button>

                    )}

                </section>


                {/* =================================================
                    RESULTS HEADER
                ================================================= */}

                <div className="history-results-heading">

                    <div>

                        <span>
                            CASE ARCHIVE
                        </span>

                        <strong>
                            {filteredInvestigations.length}
                            {" "}
                            {filteredInvestigations.length === 1
                                ? "investigation"
                                : "investigations"}
                        </strong>

                    </div>

                    <span className="history-sort-label">
                        Latest activity
                    </span>

                </div>


                {/* =================================================
                    CASE LIST
                ================================================= */}

                {filteredInvestigations.length > 0 ? (

                    <section className="history-list">

                        {filteredInvestigations.map(
                            (item, index) => {

                                const prediction =
                                    getPrediction(
                                        item
                                    );

                                const statusClass =
                                    getStatusClass(
                                        prediction
                                    );

                                const statusLabel =
                                    getStatusLabel(
                                        prediction
                                    );

                                const statusIcon =
                                    getStatusIcon(
                                        prediction
                                    );

                                const imageUrl =
                                    getImageUrl(
                                        item
                                    );

                                const confidence =
                                    getConfidenceValue(
                                        item
                                    );

                                const caseId =
                                    getCaseId(
                                        item,
                                        index
                                    );


                                return (
                                    <article
                                        className={
                                            `history-case-card ${statusClass}`
                                        }
                                        key={
                                            item?.id ||
                                            item?.case_id ||
                                            item?.caseId ||
                                            `${getFileName(item)}-${index}`
                                        }
                                    >

                                        {/* IMAGE */}

                                        <div className="history-thumbnail">

                                            {imageUrl ? (

                                                <img
                                                    src={imageUrl}
                                                    alt={
                                                        getFileName(
                                                            item
                                                        )
                                                    }
                                                />

                                            ) : (

                                                <div className="history-thumbnail-placeholder">
                                                    <span>
                                                        IMG
                                                    </span>
                                                </div>

                                            )}

                                            <div className="history-thumbnail-overlay">
                                                View Case
                                            </div>

                                        </div>


                                        {/* CASE CONTENT */}

                                        <div className="history-case-main">

                                            <div className="history-case-top">

                                                <div className="history-case-id">
                                                    {caseId}
                                                </div>

                                                <span
                                                    className={
                                                        `history-status ${statusClass}`
                                                    }
                                                >
                                                    <i>
                                                        {statusIcon}
                                                    </i>

                                                    {statusLabel}
                                                </span>

                                            </div>


                                            <h2>
                                                {getFileName(
                                                    item
                                                )}
                                            </h2>


                                            <div className="history-case-meta">

                                                <span>
                                                    {getDate(
                                                        item
                                                    )}
                                                </span>

                                                <span>
                                                    ResNet50
                                                </span>

                                                <span>
                                                    ELA
                                                </span>

                                                <span>
                                                    Grad-CAM
                                                </span>

                                            </div>


                                            <div className="history-case-bottom">

                                                <div className="history-confidence-block">

                                                    <div className="history-confidence-label">
                                                        <span>
                                                            CONFIDENCE
                                                        </span>

                                                        <strong>
                                                            {getConfidence(
                                                                item
                                                            )}
                                                        </strong>
                                                    </div>

                                                    <div className="history-confidence-track">

                                                        <span
                                                            style={{
                                                                width:
                                                                    `${confidence}%`,
                                                            }}
                                                        ></span>

                                                    </div>

                                                </div>


                                                <Link
                                                    to="/results"
                                                    state={{
                                                        result:
                                                            item,
                                                    }}
                                                    className="history-view-btn"
                                                >
                                                    View Investigation
                                                    <span>
                                                        →
                                                    </span>
                                                </Link>

                                            </div>

                                        </div>

                                    </article>
                                );
                            }
                        )}

                    </section>

                ) : (

                    /* =================================================
                       EMPTY STATE
                    ================================================= */

                    <section className="history-empty">

                        <div className="history-empty-visual">

                            <div className="history-empty-ring ring-a"></div>

                            <div className="history-empty-ring ring-b"></div>

                            <div className="history-empty-icon">
                                ◌
                            </div>

                        </div>


                        <span className="history-empty-kicker">
                            EVIDENCE VAULT
                        </span>

                        <h2>
                            {investigations.length === 0
                                ? "No investigations yet"
                                : "No matching investigations"}
                        </h2>

                        <p>
                            {investigations.length === 0
                                ? "Completed forensic analyses will appear here automatically."
                                : "Try a different search term or classification filter."}
                        </p>


                        {investigations.length === 0 && (

                            <Link
                                to="/analyze"
                                className="history-empty-btn"
                            >
                                Start First Investigation
                                <span>
                                    →
                                </span>
                            </Link>

                        )}

                    </section>

                )}


                {/* =================================================
                    FOOTER
                ================================================= */}

                <footer className="history-footer">

                    <div>

                        <span className="history-footer-dot"></span>

                        <span>
                            Forensic AI Engine Operational
                        </span>

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

export default History;