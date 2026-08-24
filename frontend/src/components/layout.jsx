import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function Layout({ children }) {
    return (
        <div className="app">

            <Navbar />

            <div className="app-layout">

                <Sidebar />

                <main className="main-content">

                    <div className="page-container">
                        {children}
                    </div>

                </main>

            </div>

        </div>
    );
}

export default Layout;