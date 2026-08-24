import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Signup() {

    const navigate = useNavigate();

    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const [form, setForm] = useState({
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
    });

    const [error, setError] = useState("");

    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });

        setError("");
    };


    const handleSubmit = (e) => {

        e.preventDefault();

        if (
            !form.name ||
            !form.email ||
            !form.password ||
            !form.confirmPassword
        ) {
            setError("Please complete all fields.");
            return;
        }

        if (form.password.length < 6) {
            setError(
                "Password must contain at least 6 characters."
            );
            return;
        }

        if (form.password !== form.confirmPassword) {
            setError(
                "Passwords do not match."
            );
            return;
        }

        setLoading(true);

        setTimeout(() => {

            localStorage.setItem(
                "forensicsUser",
                JSON.stringify({
                    name: form.name,
                    email: form.email,
                })
            );

            setLoading(false);

            navigate("/home");

        }, 1200);
    };


    return (
        <div className="auth-page">

            <div className="auth-grid"></div>

            <div className="auth-glow auth-glow-one"></div>
            <div className="auth-glow auth-glow-two"></div>


            <Link
                to="/"
                className="auth-back"
            >
                ← Back to platform
            </Link>


            <div className="auth-container">


                {/* =================================================
                    LEFT
                ================================================= */}

                <div className="auth-info">

                    <div className="auth-logo">

                        <div className="auth-logo-core">
                            IF
                        </div>

                        <span></span>
                        <span></span>

                    </div>

                    <span className="auth-eyebrow">
                        CREATE INVESTIGATOR PROFILE
                    </span>

                    <h1>
                        Build your
                        <br />
                        <span>forensic workspace.</span>
                    </h1>

                    <p>
                        Create your investigator profile and keep
                        your image analysis history organized in
                        one secure workspace.
                    </p>


                    <div className="auth-feature-list">

                        <div>
                            <span>✓</span>
                            Investigation history
                        </div>

                        <div>
                            <span>✓</span>
                            Evidence organization
                        </div>

                        <div>
                            <span>✓</span>
                            AI analysis dashboard
                        </div>

                    </div>

                </div>


                {/* =================================================
                    SIGNUP CARD
                ================================================= */}

                <div className="auth-card">

                    <div className="auth-card-header">

                        <span className="auth-card-label">
                            NEW INVESTIGATOR
                        </span>

                        <h2>
                            Create account
                        </h2>

                        <p>
                            Set up your forensic workspace.
                        </p>

                    </div>


                    <form
                        onSubmit={handleSubmit}
                        className="auth-form"
                    >

                        {/* Name */}

                        <div className="auth-field">

                            <label>
                                FULL NAME
                            </label>

                            <div className="input-wrapper">

                                <span className="input-icon">
                                    ◉
                                </span>

                                <input
                                    type="text"
                                    name="name"
                                    placeholder="Your name"
                                    value={form.name}
                                    onChange={handleChange}
                                />

                            </div>

                        </div>


                        {/* Email */}

                        <div className="auth-field">

                            <label>
                                EMAIL ADDRESS
                            </label>

                            <div className="input-wrapper">

                                <span className="input-icon">
                                    @
                                </span>

                                <input
                                    type="email"
                                    name="email"
                                    placeholder="investigator@example.com"
                                    value={form.email}
                                    onChange={handleChange}
                                />

                            </div>

                        </div>


                        {/* Password */}

                        <div className="auth-field">

                            <label>
                                PASSWORD
                            </label>

                            <div className="input-wrapper">

                                <span className="input-icon">
                                    •
                                </span>

                                <input
                                    type={
                                        showPassword
                                            ? "text"
                                            : "password"
                                    }
                                    name="password"
                                    placeholder="Minimum 6 characters"
                                    value={form.password}
                                    onChange={handleChange}
                                />

                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() =>
                                        setShowPassword(
                                            !showPassword
                                        )
                                    }
                                >
                                    {showPassword
                                        ? "Hide"
                                        : "Show"}
                                </button>

                            </div>

                        </div>


                        {/* Confirm */}

                        <div className="auth-field">

                            <label>
                                CONFIRM PASSWORD
                            </label>

                            <div className="input-wrapper">

                                <span className="input-icon">
                                    •
                                </span>

                                <input
                                    type={
                                        showPassword
                                            ? "text"
                                            : "password"
                                    }
                                    name="confirmPassword"
                                    placeholder="Repeat your password"
                                    value={form.confirmPassword}
                                    onChange={handleChange}
                                />

                            </div>

                        </div>


                        {error && (

                            <div className="auth-error">

                                <span>!</span>

                                {error}

                            </div>

                        )}


                        <button
                            type="submit"
                            className="auth-submit"
                            disabled={loading}
                        >

                            {loading ? (
                                <>
                                    <span className="button-spinner"></span>
                                    Creating workspace...
                                </>
                            ) : (
                                <>
                                    Create Investigator Account
                                    <span>→</span>
                                </>
                            )}

                        </button>

                    </form>


                    <p className="auth-switch">

                        Already have an account?

                        <Link to="/login">
                            Sign in
                        </Link>

                    </p>

                </div>

            </div>


            <div className="auth-footer">

                <span>
                    🔒 Secure AI Investigation Environment
                </span>

                <span>
                    ImageForensics © 2026
                </span>

            </div>

        </div>
    );
}

export default Signup;