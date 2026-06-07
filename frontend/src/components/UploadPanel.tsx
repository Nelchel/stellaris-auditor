import { useState } from 'react'
import { auditSave, compareSaves, ApiResponse } from '../lib/api'

type UploadPanelProps = { onResult: (result: ApiResponse) => void }

export function UploadPanel({ onResult }: UploadPanelProps) {
  const [mode, setMode] = useState<'single' | 'timeline'>('single')
  const [save, setSave] = useState<File | null>(null)
  const [oldSave, setOldSave] = useState<File | null>(null)
  const [newSave, setNewSave] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    setError('')
    setLoading(true)
    try {
      if (mode === 'single') {
        if (!save) throw new Error('Ajoute une save .sav.')
        onResult(await auditSave(save))
      } else {
        if (!oldSave || !newSave) throw new Error('Ajoute les deux saves.')
        onResult(await compareSaves(oldSave, newSave))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card upload-card">
      <h2>Analyser une save</h2>
      {import.meta.env.VITE_DEMO_MODE === 'true' && <p className="metric-small">GitHub Pages demo mode : les uploads chargent un rapport d’exemple.</p>}
      <div className="tabs">
        <label><input type="radio" checked={mode === 'single'} onChange={() => setMode('single')} /> Audit simple</label>
        <label><input type="radio" checked={mode === 'timeline'} onChange={() => setMode('timeline')} /> Comparaison timeline</label>
      </div>

      {mode === 'single' ? (
        <div className="upload-grid">
          <div>
            <label className="file-label">Save</label>
            <input type="file" accept=".sav" onChange={(e) => setSave(e.target.files?.[0] ?? null)} />
          </div>
        </div>
      ) : (
        <div className="upload-grid">
          <div>
            <label className="file-label">Ancienne save</label>
            <input type="file" accept=".sav" onChange={(e) => setOldSave(e.target.files?.[0] ?? null)} />
          </div>
          <div>
            <label className="file-label">Nouvelle save</label>
            <input type="file" accept=".sav" onChange={(e) => setNewSave(e.target.files?.[0] ?? null)} />
          </div>
        </div>
      )}

      <button className="button" disabled={loading} onClick={submit}>
        {loading ? 'Analyse en cours...' : 'Lancer l’audit'}
      </button>

      {error && <div className="error">{error}</div>}
    </div>
  )
}
