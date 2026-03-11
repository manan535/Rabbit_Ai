import { useState, useRef, useCallback } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");
  const [step, setStep] = useState(0);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [copied, setCopied] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  }, []);

  const validateAndSetFile = (f) => {
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["csv", "xlsx", "xls"].includes(ext)) {
      setStatus("error");
      setMessage("Invalid file type. Please upload a .csv or .xlsx file.");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setStatus("error");
      setMessage("File too large. Maximum size is 10 MB.");
      return;
    }
    setFile(f);
    setStatus("idle");
    setMessage("");
    setSummary("");
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) validateAndSetFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !email) return;

    setStatus("loading");
    setSummary("");
    setStep(1);
    setMessage("Uploading your data...");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);

    try {
      setStep(2);
      setMessage("Analyzing sales data with AI...");

      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (res.status === 429) {
        throw new Error("Rate limit exceeded. Please wait a moment and try again.");
      }

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setStep(4);
      setStatus("success");
      setMessage(data.message || "Summary generated and sent!");
      setSummary(data.summary || "");
    } catch (err) {
      setStatus("error");
      setStep(0);
      setMessage(err.message || "An unexpected error occurred.");
    }
  };

  const resetForm = () => {
    setFile(null);
    setEmail("");
    setStatus("idle");
    setStep(0);
    setMessage("");
    setSummary("");
    setCopied(false);
    if (inputRef.current) inputRef.current.value = "";
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const pipelinePercent = step === 0 ? 0 : step === 1 ? 20 : step === 2 ? 55 : step === 3 ? 80 : 100;

  return (
    <div className="app">
      {/* Ambient Background Orbs */}
      <div className="ambient">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">R</div>
          <div className="header-text">
            <h1>Sales Insight Automator</h1>
            <p>AI-powered executive briefs</p>
          </div>
          <div className="header-right">
            <div className="header-badge">
              <span className="dot" />
              Online
            </div>
            <span className="header-version">v1.0</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        {!summary ? (
          <>
            {/* Hero */}
            <section className="hero">
              <div className="hero-chip">
                <span className="hero-chip-icon">⚡</span>
                Powered by Llama 3.3 70B
              </div>
              <h2>Turn raw sales data into executive insights</h2>
              <p className="hero-description">
                Upload a CSV or Excel file and our AI will generate a comprehensive
                sales brief — delivered straight to your inbox in seconds.
              </p>
            </section>

            {/* Upload Card */}
            <div className="upload-card">
              <form onSubmit={handleSubmit}>
                {/* Dropzone */}
                {!file ? (
                  <div
                    className={`dropzone ${dragActive ? "active" : ""}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => inputRef.current?.click()}
                  >
                    <div className="dropzone-icon">📁</div>
                    <h3>Drop your sales data here</h3>
                    <p>
                      or <span className="browse-link">browse files</span> — up to 10 MB
                    </p>
                    <div className="formats">
                      <span className="format-tag">.csv</span>
                      <span className="format-tag">.xlsx</span>
                      <span className="format-tag">.xls</span>
                    </div>
                    <input
                      ref={inputRef}
                      type="file"
                      className="file-input"
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileChange}
                    />
                  </div>
                ) : (
                  <div className="file-badge">
                    <span className="file-icon">📄</span>
                    <span className="file-info">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">
                        {file.size < 1024 * 1024
                          ? `${(file.size / 1024).toFixed(1)} KB`
                          : `${(file.size / (1024 * 1024)).toFixed(2)} MB`}
                      </span>
                    </span>
                    <button
                      type="button"
                      className="remove-btn"
                      onClick={resetForm}
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                )}

                {/* Email */}
                <div className="email-group">
                  <label htmlFor="email">
                    <span className="label-icon">📧</span>
                    Recipient Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    placeholder="team-lead@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={status === "loading"}
                  />
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={!file || !email || status === "loading"}
                >
                  {status === "loading" ? (
                    <>
                      <span className="spinner" /> Generating insight...
                    </>
                  ) : (
                    "Generate & Send Brief →"
                  )}
                </button>
              </form>

              {/* Pipeline Progress */}
              {status === "loading" && (
                <div className="pipeline">
                  <div className="pipeline-label">Processing Pipeline</div>
                  <div className="pipeline-track">
                    <div
                      className="pipeline-fill"
                      style={{ width: `${pipelinePercent}%` }}
                    />
                  </div>
                  <div className="steps">
                    <div className={`step ${step >= 1 ? (step > 1 ? "done" : "active") : ""}`}>
                      <span className="step-num">{step > 1 ? "✓" : "1"}</span>
                      Upload
                    </div>
                    <div className={`step ${step >= 2 ? (step > 2 ? "done" : "active") : ""}`}>
                      <span className="step-num">{step > 2 ? "✓" : "2"}</span>
                      AI Analysis
                    </div>
                    <div className={`step ${step >= 3 ? (step > 3 ? "done" : "active") : ""}`}>
                      <span className="step-num">{step > 3 ? "✓" : "3"}</span>
                      Delivery
                    </div>
                  </div>
                </div>
              )}

              {/* Status */}
              {message && (
                <div className={`status ${status}`}>
                  <span className="status-icon">
                    {status === "loading" && "⏳"}
                    {status === "success" && "✅"}
                    {status === "error" && "❌"}
                  </span>
                  <span>{message}</span>
                </div>
              )}
            </div>

            {/* Features Strip */}
            {status !== "loading" && (
              <div className="features">
                <div className="feature">
                  <div className="feature-icon purple">🧠</div>
                  <div className="feature-text">
                    <strong>AI Analysis</strong>
                    Llama 3.3 70B model
                  </div>
                </div>
                <div className="feature">
                  <div className="feature-icon blue">⚡</div>
                  <div className="feature-text">
                    <strong>Instant Delivery</strong>
                    Direct to inbox
                  </div>
                </div>
                <div className="feature">
                  <div className="feature-icon green">🔒</div>
                  <div className="feature-text">
                    <strong>Secure Pipeline</strong>
                    Encrypted & sandboxed
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          /* ── Summary View ── */
          <div className="summary-card">
            {/* Success Banner */}
            <div className="summary-success-banner">
              <div className="success-check">✓</div>
              <div className="success-text">
                <strong>Brief generated successfully</strong>
                <span>Summary has been sent to {email}</span>
              </div>
            </div>

            {/* Header */}
            <div className="summary-header">
              <h2>📊 Executive Sales Brief</h2>
              <div className="summary-actions">
                <button
                  className={`action-btn ${copied ? "copied" : ""}`}
                  onClick={copyToClipboard}
                >
                  {copied ? "✓ Copied" : "📋 Copy"}
                </button>
              </div>
            </div>

            {/* Meta Tags */}
            <div className="summary-meta">
              <span className="meta-tag">🤖 Llama 3.3 70B</span>
              <span className="meta-tag">📧 {email}</span>
              <span className="meta-tag">📄 {file?.name}</span>
            </div>

            {/* Body */}
            <div className="summary-body">{summary}</div>

            {/* New Report */}
            <button className="new-report-btn" onClick={resetForm}>
              ← Generate Another Report
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <span>Built by <a href="#">Rabbitt AI</a></span>
        <span className="footer-divider" />
        <span>Sales Insight Automator v1.0</span>
      </footer>
    </div>
  );
}

export default App;
