import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const analyzeReport = async () => {
    if (!file) {
      setError("Please select a medical report first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // STEP 1: Send image to FastAPI OCR
      const formData = new FormData();
      formData.append("file", file);

      const extractResponse = await fetch(
        "http://127.0.0.1:8000/extract",
        {
          method: "POST",
          body: formData,
        }
      );

      const extractData = await extractResponse.json();

      if (!extractData.success) {
        throw new Error(extractData.error || "OCR failed");
      }

      // STEP 2: Send extracted text to Gemini
      const analyzeResponse = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: extractData.text,
          }),
        }
      );

      const analyzeData = await analyzeResponse.json();

      if (!analyzeData.success) {
        throw new Error(analyzeData.error || "AI analysis failed");
      }

      setResult(analyzeData.analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">⚕</div>

        <div>
          <h1>Medical Report Simplifier</h1>
          <p>Understand your medical reports in simple language</p>
        </div>
      </header>

      <main className="container">

        <section className="hero">
          <span className="badge">AI POWERED</span>

          <h2>
            Your medical report,
            <br />
            <span>made easier to understand.</span>
          </h2>

          <p>
            Upload a medical report and let AI explain complex
            medical terminology, findings and values in
            patient-friendly language.
          </p>
        </section>

        <section className="upload-card">

          <div className="upload-icon">📄</div>

          <h3>Upload Medical Report</h3>

          <p>
            Select a JPG or PNG image of your medical report
          </p>

          <label className="upload-button">
            Choose Report
            <input
              type="file"
              accept=".jpg,.jpeg,.png"
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="selected-file">
              <span>📎</span>
              <span>{file.name}</span>
            </div>
          )}

          <button
            className="analyze-button"
            onClick={analyzeReport}
            disabled={!file || loading}
          >
            {loading ? "Analyzing Report..." : "Analyze Report →"}
          </button>

          {error && (
            <div className="error">
              ⚠ {error}
            </div>
          )}

        </section>

        {result && (
          <section className="results">

            <div className="results-title">
              <span className="badge">AI ANALYSIS</span>
              <h2>Report Explanation</h2>
            </div>

            <div className="result-card summary">
              <h3>🧠 Simple Summary</h3>
              <p>{result.summary}</p>
            </div>

            <div className="result-card">
              <h3>🔬 Findings</h3>

              <ul>
                {result.findings?.map((finding, index) => (
                  <li key={index}>{finding}</li>
                ))}
              </ul>
            </div>

            <div className="result-card">
              <h3>📖 Medical Terms</h3>

              <div className="terms">
                {result.medical_terms?.map((item, index) => (
                  <div className="term" key={index}>
                    <strong>{item.term}</strong>
                    <p>{item.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="result-card">
              <h3>⚠️ General Precautions</h3>

              <ul>
                {result.precautions?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="result-card">
              <h3>👨‍⚕️ Follow-up</h3>
              <p>{result.follow_up}</p>
            </div>

            <div className="disclaimer">
              <strong>Medical Disclaimer</strong>
              <p>{result.disclaimer}</p>
            </div>

          </section>
        )}

      </main>

      <footer>
        Medical Report Simplifier • AI-assisted educational tool
      </footer>
    </div>
  );
}

export default App;