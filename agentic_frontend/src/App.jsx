import { useState, useEffect } from 'react'


import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import HomeUpload from './HomeUpload'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'


function App() {
  const [theme, setTheme] = useState(
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  );

  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark-mode' : 'light-mode';
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  return (
    <Router>
      <div className={`app-root ${theme}-mode`}>
        {/* Navigation Bar */}
        <nav className="navbar" style={{ width: '100%' }}>
          <div className="nav-logo">
            <img src={viteLogo} alt="Vite" style={{ height: 32, marginRight: 8 }} />
            <span className="nav-title">Agentic</span>
          </div>
          <div className="nav-links">
            <Link to="/upload">Upload</Link>
            <Link to="/">Home</Link>
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle light/dark mode">
              {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
            </button>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/upload" element={<HomeUpload theme={theme} />} />
            <Route path="/" element={
              <section className="about-section" style={{ width: '100%', maxWidth: 1200, margin: '0 auto', padding: '0 2em' }}>
                {/* Animated Hero Section */}
                <div style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  padding: '2em 0 1em 0',
                  animation: 'fadeIn 1.2s',
                }}>
                  <h1 style={{ fontSize: '2.7rem', fontWeight: 800, marginBottom: '0.7em', color: theme === 'dark' ? '#61dafb' : '#646cff', letterSpacing: 1 }}>
                    Evolving AI for Everyone
                  </h1>
                  <p style={{ fontSize: '1.25rem', lineHeight: 1.7, color: theme === 'dark' ? '#cfcfcf' : '#444', maxWidth: 600, textAlign: 'center', marginBottom: '1.5em' }}>
                    Welcome to <span style={{ fontWeight: 700, color: theme === 'dark' ? '#61dafb' : '#646cff' }}>Agentic</span>, your next-generation RAG (Retrieval Augmented Generation) platform.<br />
                    Upload files, create embeddings, and unlock powerful AI search and chat capabilities.
                  </p>
                  <Link to="/upload">
                    <button className="card button" style={{ fontSize: '1.15rem', marginTop: '0.5em', boxShadow: '0 2px 8px rgba(100,108,255,0.10)' }}>
                      🚀 Get Started: Upload File
                    </button>
                  </Link>
                </div>
                {/* Feature Cards */}
                <div style={{
                  display: 'flex', flexWrap: 'wrap', gap: '1.5em', justifyContent: 'center', margin: '2em 0 1em 0',
                }}>
                  <div className="feature-card" style={{ flex: '1 1 220px', minWidth: 220, maxWidth: 270, background: theme === 'dark' ? '#23263a' : '#f7f8fa', borderRadius: 16, boxShadow: '0 2px 12px rgba(100,108,255,0.08)', padding: '1.2em', textAlign: 'center', transition: 'background 0.3s' }}>
                    <div style={{ fontSize: '2.2rem', marginBottom: 8 }}>⚡</div>
                    <h3 style={{ color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 700, marginBottom: 6 }}>Fast & Scalable</h3>
                    <p style={{ fontSize: '1.05rem', color: theme === 'dark' ? '#cfcfcf' : '#444' }}>Built for speed and scale, Agentic handles large datasets and real-time AI workflows with ease.</p>
                  </div>
                  <div className="feature-card" style={{ flex: '1 1 220px', minWidth: 220, maxWidth: 270, background: theme === 'dark' ? '#23263a' : '#f7f8fa', borderRadius: 16, boxShadow: '0 2px 12px rgba(100,108,255,0.08)', padding: '1.2em', textAlign: 'center', transition: 'background 0.3s' }}>
                    <div style={{ fontSize: '2.2rem', marginBottom: 8 }}>🤖</div>
                    <h3 style={{ color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 700, marginBottom: 6 }}>Modern AI Workflows</h3>
                    <p style={{ fontSize: '1.05rem', color: theme === 'dark' ? '#cfcfcf' : '#444' }}>Seamlessly integrate with the latest AI models and tools for advanced retrieval and generation.</p>
                  </div>
                  <div className="feature-card" style={{ flex: '1 1 220px', minWidth: 220, maxWidth: 270, background: theme === 'dark' ? '#23263a' : '#f7f8fa', borderRadius: 16, boxShadow: '0 2px 12px rgba(100,108,255,0.08)', padding: '1.2em', textAlign: 'center', transition: 'background 0.3s' }}>
                    <div style={{ fontSize: '2.2rem', marginBottom: 8 }}>📱</div>
                    <h3 style={{ color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 700, marginBottom: 6 }}>Mobile-First UI</h3>
                    <p style={{ fontSize: '1.05rem', color: theme === 'dark' ? '#cfcfcf' : '#444' }}>Enjoy a beautiful, responsive experience on any device, from desktop to mobile.</p>
                  </div>
                  <div className="feature-card" style={{ flex: '1 1 220px', minWidth: 220, maxWidth: 270, background: theme === 'dark' ? '#23263a' : '#f7f8fa', borderRadius: 16, boxShadow: '0 2px 12px rgba(100,108,255,0.08)', padding: '1.2em', textAlign: 'center', transition: 'background 0.3s' }}>
                    <div style={{ fontSize: '2.2rem', marginBottom: 8 }}>🔒</div>
                    <h3 style={{ color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 700, marginBottom: 6 }}>Privacy & Control</h3>
                    <p style={{ fontSize: '1.05rem', color: theme === 'dark' ? '#cfcfcf' : '#444' }}>Your data stays secure and private, with full control over access and sharing.</p>
                  </div>
                </div>
                {/* Theme Showcase */}
                <div style={{ textAlign: 'center', margin: '2em 0 1em 0' }}>
                  <span style={{ fontSize: '1.1rem', color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 600 }}>
                    Try switching between <span style={{ fontWeight: 700 }}>{theme === 'dark' ? 'Dark' : 'Light'}</span> mode for a different look!
                  </span>
                </div>
                {/* Why Agentic vs ChatGPT Section */}
                <div className="why-agentic" style={{ background: theme === 'dark' ? '#23263a' : '#f7f8fa', borderRadius: 18, boxShadow: '0 2px 12px rgba(100,108,255,0.08)', padding: '2em 2em', maxWidth: 1200, margin: '2em auto', color: theme === 'dark' ? '#cfcfcf' : '#444' }}>
                  <h2 style={{ color: theme === 'dark' ? '#61dafb' : '#646cff', fontWeight: 800, fontSize: '1.7rem', marginBottom: '1.5em', textAlign: 'center', letterSpacing: 1 }}>
                    Why Agentic is Better Than ChatGPT for Enterprise, Legal, and Compliance Use
                  </h2>
                  <ul style={{ fontSize: '1.10rem', lineHeight: 1.85, maxWidth: 800, margin: '0 auto', textAlign: 'left', padding: 0 }}>
                    <li style={{ marginBottom: '1.2em', paddingLeft: '0.5em' }}><strong>Built to Go Beyond ChatGPT:</strong> Agentic was designed from the ground up to query long, private documents with reliable, traceable answers. Unlike ChatGPT, which struggles with document length and auditability, Agentic ensures your legal, financial, and compliance records are always accessible and defensible.</li>
                    <li style={{ marginBottom: '1.2em', paddingLeft: '0.5em' }}><strong>Context Window Limitations:</strong> ChatGPT is limited to ~32K tokens per query. Agentic’s Retrieval Augmented Generation (RAG) system can process much larger documents and multi-step queries, so you never lose critical context or detail.</li>
                    <li style={{ marginBottom: '1.2em', paddingLeft: '0.5em' }}><strong>Hallucination Risk:</strong> ChatGPT may hallucinate or generate made-up information. Agentic’s RAG approach only responds based on your provided data, minimizing risk and ensuring factual, legally-defensible outputs.</li>
                    <li style={{ marginBottom: '1.2em', paddingLeft: '0.5em' }}><strong>Data Freshness & Customization:</strong> Even if your company’s data is online, ChatGPT may not have the latest updates. Agentic always works with your most current, private documents—no stale or missing information.</li>
                    <li style={{ marginBottom: '1.2em', paddingLeft: '0.5em' }}><strong>Compliance & Data Sovereignty:</strong> Uploading sensitive financial or legal documents to external LLM servers (like ChatGPT) can create compliance and privacy risks. Agentic keeps your data secure, private, and under your control—meeting regulatory requirements for privacy, data residency, and audit trails.</li>
                  </ul>
                  <div style={{ marginTop: '2em', fontSize: '1.15rem', color: theme === 'dark' ? '#61dafb' : '#646cff', textAlign: 'center', fontWeight: 600, letterSpacing: 0.5 }}>
                    <span role="img" aria-label="shield">🛡️</span> Built for legal, financial, and enterprise-grade privacy.
                  </div>
                  <div style={{ marginTop: '2.5em', fontSize: '1.13rem', color: theme === 'dark' ? '#cfcfcf' : '#444', textAlign: 'center', fontStyle: 'italic', background: theme === 'dark' ? '#181a20' : '#eaf0ff', borderRadius: 12, padding: '1.2em 1em', maxWidth: 700, margin: '2em auto 0 auto' }}>
                    <span style={{ fontWeight: 700, color: theme === 'dark' ? '#61dafb' : '#646cff' }}>Founder’s Note:</span> <br />
                    “I built Agentic to go beyond ChatGPT. My system ensures long, private documents can be queried reliably with traceable answers—something ChatGPT alone doesn’t handle well. For legal, compliance, and enterprise use, Agentic is the trusted choice.”
                  </div>
                </div>
              </section>
            } />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="footer">
          <span>© {new Date().getFullYear()} Agentic. All rights reserved.</span>
          <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
            <img src={reactLogo} alt="React" style={{ height: 24, marginLeft: 8 }} />
          </a>
        </footer>
      </div>
    </Router>
  );
}

export default App
