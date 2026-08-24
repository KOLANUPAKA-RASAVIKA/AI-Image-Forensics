import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import "./App.css";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Analyze from "./pages/Analyze";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Results from "./pages/Results";

import Layout from "./components/Layout";


function App() {

    return (
        <BrowserRouter>

            <Routes>

                {/* =================================================
                    PUBLIC PAGES
                ================================================= */}

                <Route
                    path="/"
                    element={<Landing />}
                />

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/signup"
                    element={<Signup />}
                />


                {/* =================================================
                    APPLICATION PAGES
                    All pages use the common Layout
                ================================================= */}

                <Route
                    path="/home"
                    element={
                        <Layout>
                            <Home />
                        </Layout>
                    }
                />

                <Route
                    path="/upload"
                    element={
                        <Layout>
                            <Upload />
                        </Layout>
                    }
                />

                <Route
                    path="/analyze"
                    element={
                        <Layout>
                            <Analyze />
                        </Layout>
                    }
                />

                <Route
                    path="/dashboard"
                    element={
                        <Layout>
                            <Dashboard />
                        </Layout>
                    }
                />

                <Route
                    path="/history"
                    element={
                        <Layout>
                            <History />
                        </Layout>
                    }
                />

                <Route
                    path="/results"
                    element={
                        <Layout>
                            <Results />
                        </Layout>
                    }
                />


                {/* =================================================
                    UNKNOWN URL
                ================================================= */}

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/"
                            replace
                        />
                    }
                />

            </Routes>

        </BrowserRouter>
    );
}


export default App;