
import React, { useState, useRef } from "react";
const VITE_API_URL = import.meta.env.VITE_API_URL;

export default function HomeUpload({ theme }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef();

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setMessage("");
    setProgress(0);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setMessage("");
      setProgress(0);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }
    setUploading(true);
    setMessage("");
    setProgress(0);
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append("file", file);
      // Show progress bar (fake for now)
      let prog = 0;
      const interval = setInterval(() => {
        prog += 10;
        setProgress(prog);
      }, 80);
      // Send to backend
      const response = await fetch(`${VITE_API_URL}/api/embeddings/upload`, {
        method: "POST",
        body: formData,
      });
      clearInterval(interval);
      setProgress(100);
      setUploading(false);
      if (response.ok) {
        const data = await response.json();
        setMessage(`✅ ${data.message}`);
      } else {
        setMessage("❌ Upload failed. Please try again.");
      }
    } catch (err) {
      setUploading(false);
      setMessage("❌ Error uploading file. Please try again.");
    }
  };

  return (
    <div
      className={`card upload-card ${theme === 'dark' ? 'dark-mode' : 'light-mode'}${dragActive ? ' drag-active' : ''}`}
      style={{ margin: "2rem auto", maxWidth: 420, boxShadow: dragActive ? "0 0 24px #61dafb55" : undefined, transition: "box-shadow 0.3s" }}
      onDragEnter={handleDrag}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
        <div style={{ fontSize: 48, marginBottom: 8, color: theme === 'dark' ? '#61dafb' : '#646cff', transition: "color 0.3s" }}>
          <span role="img" aria-label="upload">📤</span>
        </div>
        <h2 style={{ fontWeight: 700, fontSize: "1.5rem", marginBottom: 8, letterSpacing: 1 }}>Upload File for Embedding</h2>
        <div
          className="upload-dropzone"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: dragActive ? "2px dashed #61dafb" : "2px dashed #bbb",
            background: dragActive ? (theme === 'dark' ? "#23263a" : "#eaf0ff") : (theme === 'dark' ? "#23263a" : "#f7f8fa"),
            borderRadius: 12,
            padding: "1.2em 1em",
            width: "100%",
            marginBottom: 12,
            transition: "background 0.3s, border 0.3s"
          }}
        >
          <input
            ref={inputRef}
            type="file"
            style={{ display: "none" }}
            onChange={handleFileChange}
            disabled={uploading}
          />
          <button
            type="button"
            className="upload-btn"
            style={{ fontSize: "1rem", padding: "0.5em 1.2em", borderRadius: 8, background: theme === 'dark' ? '#646cff' : '#61dafb', color: theme === 'dark' ? '#fff' : '#222', border: 'none', cursor: 'pointer', marginBottom: 8 }}
            onClick={() => inputRef.current.click()}
            disabled={uploading}
          >
            {file ? "Change File" : "Choose File"}
          </button>
          <div style={{ fontSize: "1.05rem", color: file ? (theme === 'dark' ? '#61dafb' : '#646cff') : '#888', marginBottom: 4 }}>
            {file ? file.name : "No file chosen"}
          </div>
          <div style={{ fontSize: "0.95rem", color: '#888' }}>
            or drag & drop here
          </div>
        </div>
        <form onSubmit={handleUpload} style={{ width: "100%" }}>
          <button
            type="submit"
            disabled={uploading || !file}
            style={{
              background: uploading ? '#bbb' : (theme === 'dark' ? '#61dafb' : '#646cff'),
              color: uploading ? '#666' : (theme === 'dark' ? '#222' : '#fff'),
              border: 'none',
              borderRadius: 8,
              padding: '0.6em 1.5em',
              fontSize: '1.1rem',
              fontWeight: 600,
              cursor: uploading ? 'not-allowed' : 'pointer',
              boxShadow: uploading ? 'none' : '0 2px 8px rgba(100,108,255,0.10)',
              transition: 'background 0.2s, color 0.2s'
            }}
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
        {uploading && (
          <div style={{ width: '100%', marginTop: 12 }}>
            <div style={{ height: 8, width: '100%', background: theme === 'dark' ? '#23263a' : '#eaf0ff', borderRadius: 8, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${progress}%`, background: theme === 'dark' ? '#61dafb' : '#646cff', transition: 'width 0.2s' }} />
            </div>
            <div style={{ fontSize: '0.95rem', color: theme === 'dark' ? '#61dafb' : '#646cff', marginTop: 4 }}>{progress}%</div>
          </div>
        )}
        {message && <div style={{ marginTop: 18, fontSize: '1.08rem', color: message.startsWith('✅') ? (theme === 'dark' ? '#61dafb' : '#646cff') : '#ff5252', fontWeight: 500, transition: 'color 0.3s' }}>{message}</div>}
      </div>
    </div>
  );
}
