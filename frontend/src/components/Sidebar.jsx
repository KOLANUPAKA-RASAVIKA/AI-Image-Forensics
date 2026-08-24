import { NavLink, Link } from "react-router-dom";
import { useState } from "react";

function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);

    const menuItems = [
        {
            path: "/home",
            icon: "⌂",
            label: "Home",
        },
        {
            path: "/analyze",
            icon: "⌁",
            label: "New Investigation",
        },
        {
            path: "/dashboard",
            icon: "▦",
            label: "Dashboard",
        },
        {
            path: "/history",
            icon: "◷",
            label: "Investigation History",
        },
    ];

    return (
        <>
            {/* MOBILE / DRAWER BACKDROP */}
            {isOpen && (
                <div
                    className="sidebar-backdrop"
                    onClick={() => setIsOpen(false)}
                ></div>
            )}

            <aside
                className={`sidebar ${
                    isOpen ? "open" : "collapsed"
                }`}
            >
                {/* =================================================
                    TOP
                ================================================= */}

                <div className="sidebar-top">

                    <button
                        type="button"
                        className="sidebar-toggle"
                        onClick={() =>
                            setIsOpen((value) => !value)
                        }
                        aria-label={
                            isOpen
                                ? "Close sidebar"
                                : "Open sidebar"
                        }
                    >
                        <span
                            className={
                                isOpen
                                    ? "toggle-icon rotated"
                                    : "toggle-icon"
                            }
                        >
                            ☰
                        </span>
                    </button>


                    {/* BRAND */}

                    <div className="sidebar-header">

                        <div className="sidebar-brand-mark">
                            IF
                        </div>

                        <div className="sidebar-brand-text">
                            <strong>
                                Forensic Workspace
                            </strong>

                            <span>
                                Investigation Center
                            </span>
                        </div>

                    </div>

                </div>


                {/* =================================================
                    NAVIGATION
                ================================================= */}

                <div className="sidebar-navigation">

                    {/* WORKSPACE */}

                    <div className="sidebar-section">

                        <p className="sidebar-title">
                            WORKSPACE
                        </p>

                        {menuItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) =>
                                    `sidebar-link ${
                                        isActive
                                            ? "active"
                                            : ""
                                    }`
                                }
                                onClick={() => {
                                    if (
                                        window.innerWidth <=
                                        800
                                    ) {
                                        setIsOpen(false);
                                    }
                                }}
                            >
                                <span className="sidebar-icon">
                                    {item.icon}
                                </span>

                                <span className="sidebar-label">
                                    {item.label}
                                </span>
                            </NavLink>
                        ))}

                    </div>


                    {/* TOOLS */}

                    <div className="sidebar-section">

                        <p className="sidebar-title">
                            TOOLS
                        </p>

                        <NavLink
                            to="/analyze"
                            className={({ isActive }) =>
                                `sidebar-link ${
                                    isActive
                                        ? "active"
                                        : ""
                                }`
                            }
                            onClick={() => {
                                if (
                                    window.innerWidth <=
                                    800
                                ) {
                                    setIsOpen(false);
                                }
                            }}
                        >
                            <span className="sidebar-icon">
                                ◈
                            </span>

                            <span className="sidebar-label">
                                Image Analyzer
                            </span>
                        </NavLink>

                    </div>

                </div>


                {/* =================================================
                    BOTTOM
                ================================================= */}

                <div className="sidebar-bottom">


                    {/* ENGINE */}

                    <div className="security-card">

                        <div className="security-icon">
                            <span>
                                ✓
                            </span>
                        </div>

                        <div className="security-content">

                            <div className="security-title-row">

                                <strong>
                                    AI Engine Online
                                </strong>

                                <span className="security-live-dot"></span>

                            </div>

                            <span>
                                ResNet50 • ELA • Grad-CAM
                            </span>

                        </div>

                    </div>


                    {/* NEW INVESTIGATION */}

                    <Link
                        to="/analyze"
                        className="sidebar-investigation-card"
                        onClick={() => {
                            if (
                                window.innerWidth <= 800
                            ) {
                                setIsOpen(false);
                            }
                        }}
                    >
                        <div className="sidebar-investigation-icon">
                            +
                        </div>

                        <div className="sidebar-investigation-copy">

                            <strong>
                                New Investigation
                            </strong>

                            <span>
                                Upload digital evidence
                            </span>

                        </div>

                        <span className="sidebar-investigation-arrow">
                            →
                        </span>

                    </Link>


                    {/* SYSTEM */}

                    <div className="sidebar-system-info">

                        <div>
                            <span>
                                SYSTEM
                            </span>

                            <strong>
                                OPERATIONAL
                            </strong>
                        </div>

                        <div>
                            <span>
                                VERSION
                            </span>

                            <strong>
                                v1.0
                            </strong>
                        </div>

                    </div>


                    <p className="version">
                        ImageForensics
                        <span>•</span>
                        Digital Evidence Intelligence
                    </p>

                </div>

            </aside>
        </>
    );
}

export default Sidebar;