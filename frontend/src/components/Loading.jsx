function Loading({ text = "Analyzing image..." }) {
    return (
        <div
            style={{
                minHeight: "200px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                gap: "15px",
            }}
        >
            <div
                style={{
                    width: "45px",
                    height: "45px",
                    border: "5px solid #e5e7eb",
                    borderTop: "5px solid #2563eb",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                }}
            />

            <p
                style={{
                    color: "#6b7280",
                    margin: 0,
                }}
            >
                {text}
            </p>

            <style>
                {`
                    @keyframes spin {
                        from {
                            transform: rotate(0deg);
                        }
                        to {
                            transform: rotate(360deg);
                        }
                    }
                `}
            </style>
        </div>
    );
}

export default Loading;