import { NavLink, Link } from "react-router-dom";
import { useEffect, useState } from "react";

function Navbar() {
    const [user, setUser] = useState(null);

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

    const userName =
        user?.name ||
        user?.email?.split("@")[0] ||
        "Investigator";

    const initials =
        userName
            .split(" ")
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part.charAt(0).toUpperCase())
            .join("") || "I";

    const navItems = [
        {
            label: "Command Center",
            to: "/home",
            icon: "⌂",
        },
        {
            label: "Analyze",
            to: "/analyze",
            icon: "⌕",
        },
        {
            label: "Analytics",
            to: "/dashboard",
            icon: "◫",
        },
        {
            label: "Evidence Vault",
            to: "/history",
            icon: "◴",
        },
    ];

    return (
        <header className="navbar">

            {/* =====================================================
                BRAND
            ===================================================== */}

            <Link
                to="/home"
                className="navbar-brand"
            >
                <div className="navbar-brand-mark">
                    IF
                </div>

                <div className="navbar-brand-copy">
                    <strong>
                        ImageForensics
                    </strong>

                    <span>
                        DIGITAL EVIDENCE INTELLIGENCE
                    </span>
                </div>
            </Link>


            {/* =====================================================
                CENTER NAVIGATION
            ===================================================== */}

            <nav className="navbar-navigation">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            `navbar-nav-link ${
                                isActive
                                    ? "active"
                                    : ""
                            }`
                        }
                    >
                        <span className="navbar-nav-icon">
                            {item.icon}
                        </span>

                        <span>
                            {item.label}
                        </span>
                    </NavLink>
                ))}
            </nav>


            {/* =====================================================
                RIGHT SIDE
            ===================================================== */}

            <div className="navbar-actions">

                <div className="navbar-engine-status">
                    <span className="navbar-status-dot"></span>

                    <div>
                        <strong>
                            AI ENGINE
                        </strong>

                        <small>
                            ONLINE
                        </small>
                    </div>
                </div>


                <div className="navbar-divider"></div>


                <button
                    type="button"
                    className="navbar-icon-button"
                    title="Notifications"
                >
                    🔔
                </button>


                <Link
                    to="/profile"
                    className="navbar-user"
                >
                    <div className="navbar-avatar">
                        {initials}
                    </div>

                    <div className="navbar-user-copy">
                        <strong>
                            {userName}
                        </strong>

                        <span>
                            Investigator
                        </span>
                    </div>

                    <span className="navbar-user-arrow">
                        ▾
                    </span>
                </Link>

            </div>

        </header>
    );
}

export default Navbar;