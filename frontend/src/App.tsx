import { useState } from 'react'
import { UploadPanel } from './components/UploadPanel'
import { Dashboard } from './components/Dashboard'
import { History } from './components/History'
import './styles.css'

function App() {
  const [result, setResult] = useState<any>(null)
  const [view, setView] = useState<'dashboard' | 'history'>('dashboard')

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>🚀 Stellaris Auditor V3.5.1</h1>
          <div className="subtitle">React + FastAPI — GitHub-ready + Pages demo + FastAPI backend.</div>
          <div>
            <span className="badge">V3.5</span>
            <span className="badge">React</span>
            <span className="badge">FastAPI</span>
            <span className="badge">History</span>
          </div>
        </div>
      </div>

      <div className="nav-tabs">
        <button className={`button ${view === 'dashboard' ? '' : 'secondary'}`} onClick={() => setView('dashboard')}>
          Dashboard
        </button>
        <button className={`button ${view === 'history' ? '' : 'secondary'}`} onClick={() => setView('history')}>
          History Analytics
        </button>
      </div>

      {view === 'dashboard' ? (
        <>
          <UploadPanel onResult={(nextResult) => {
            setResult(nextResult)
            setView('dashboard')
          }} />

          {result ? <Dashboard result={result} /> : (
            <div className="card">
              <h2>Ready</h2>
              <p>Upload une save Stellaris ou compare deux saves pour lancer l’audit.</p>
            </div>
          )}
        </>
      ) : (
        <History />
      )}
    </div>
  )
}

export default App
