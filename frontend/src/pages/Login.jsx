import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Login() {
    const navigate = useNavigate();

    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const [form, setForm] = useState({
        email: "",
        password: "",
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

        if (!form.email || !form.password) {
            setError("Please enter your email and password.");
            return;
        }

        setLoading(true);

        /*
         * Temporary frontend authentication.
         * Real authentication will be connected
         * to the backend later.
         */

        setTimeout(() => {
            setLoading(false);

            localStorage.setItem(
                "forensicsUser",
                JSON.stringify({
                    email: form.email,
                })
            );

            navigate("/home");
        }, 1200);
    };

    return (
        <div className="auth-page">

            {/* Background effects */}

            <div className="auth-grid"></div>

            <div className="auth-glow auth-glow-one"></div>
            <div className="auth-glow auth-glow-two"></div>


            {/* Back */}

            <Link
                to="/"
                className="auth-back"
            >
                ← Back to platform
            </Link>


            <div className="auth-container">

                {/* =================================================
                    LEFT SIDE
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
                        AI IMAGE FORENSICS
                    </span>

                    <h1>
                        Enter the
                        <br />
                        <span>investigation lab.</span>
                    </h1>

                    <p>
                        Access your forensic workspace, review previous
                        investigations and analyze suspicious images
                        with AI-powered tools.
                    </p>


                    <div className="auth-feature-list">

                        <div>
                            <span>✓</span>
                            AI image classification
                        </div>

                        <div>
                            <span>✓</span>
                            ELA forensic analysis
                        </div>

                        <div>
                            <span>✓</span>
                            Grad-CAM explainability
                        </div>

                    </div>

                </div>


                {/* =================================================
                    LOGIN CARD
                ================================================= */}

                <div className="auth-card">

                    <div className="auth-card-header">

                        <span className="auth-card-label">
                            SECURE ACCESS
                        </span>

                        <h2>
                            Welcome back
                        </h2>

                        <p>
                            Sign in to continue your investigation.
                        </p>

                    </div>


                    <form
                        onSubmit={handleSubmit}
                        className="auth-form"
                    >

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

                            <div className="password-label-row">

                                <label>
                                    PASSWORD
                                </label>

                                <button
                                    type="button"
                                    className="forgot-password"
                                    onClick={() =>
                                        alert(
                                            "Password recovery will be connected in the authentication phase."
                                        )
                                    }
                                >
                                    Forgot password?
                                </button>

                            </div>

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
                                    placeholder="Enter your password"
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
                                    {showPassword ? "Hide" : "Show"}
                                </button>

                            </div>

                        </div>


                        {/* Error */}

                        {error && (

                            <div className="auth-error">
                                <span>!</span>
                                {error}
                            </div>

                        )}


                        {/* Submit */}

                        <button
                            type="submit"
                            className="auth-submit"
                            disabled={loading}
                        >

                            {loading ? (
                                <>
                                    <span className="button-spinner"></span>
                                    Authenticating...
                                </>
                            ) : (
                                <>
                                    Enter Investigation Lab
                                    <span>→</span>
                                </>
                            )}

                        </button>

                    </form>


                    {/* Divider */}

                    <div className="auth-divider">
                        <span>OR</span>
                    </div>


                    {/* Demo access */}

                    <button
                        className="demo-access"
                        onClick={() => {

                            setForm({
                                email: "demo@imageforensics.ai",
                                password: "demo123",
                            });

                        }}
                    >
                        <span>◈</span>

                        Use demo investigator account

                    </button>


                    {/* Signup */}

                    <p className="auth-switch">

                        New investigator?

                        <Link to="/signup">
                            Create an account
                        </Link>

                    </p>

                </div>

            </div>


            {/* Footer */}

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

export default Login;