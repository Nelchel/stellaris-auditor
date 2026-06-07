import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import { getHistory } from '../lib/api'

const chartText = '#e6edf3'
const mutedText = '#9aa4b2'
const grid = 'rgba(148, 163, 184, 0.22)'

const palette = {
  blue: '#38bdf8',
  pink: '#f472b6',
  orange: '#fb923c',
  yellow: '#facc15',
  teal: '#2dd4bf',
  purple: '#c084fc',
  green: '#4ade80',
  red: '#fb7185',
}

function lineDataset(label: string, data: number[], color: string) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: color,
    pointBackgroundColor: color,
    pointBorderColor: color,
    pointRadius: 4,
    pointHoverRadius: 6,
    borderWidth: 3,
    tension: 0.25,
  }
}

const chartOptions: any = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  scales: {
    x: {
      ticks: { color: chartText, font: { size: 13, weight: 'bold' } },
      grid: { color: grid },
    },
    y: {
      ticks: { color: chartText, font: { size: 13, weight: 'bold' } },
      grid: { color: grid },
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      labels: {
        color: chartText,
        boxWidth: 18,
        boxHeight: 12,
        font: { size: 13, weight: 'bold' },
      },
    },
    tooltip: {
      backgroundColor: '#0f172a',
      titleColor: chartText,
      bodyColor: chartText,
      borderColor: '#334155',
      borderWidth: 1,
    },
  },
}

export function History() {
  const [history, setHistory] = useState<any>(null)
  const [error, setError] = useState('')

  async function load() {
    try {
      setError('')
      setHistory(await getHistory())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load history')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const series = history?.series
  const labels = series?.labels ?? []

  if (error) {
    return (
      <div className="card error">
        <h2>History unavailable</h2>
        <p>{error}</p>
        <p className="metric-small">
          Sur GitHub Pages, l’historique utilise le mode demo. En local, vérifie que le backend FastAPI tourne sur 127.0.0.1:8000.
        </p>
        <button className="button" onClick={load}>Réessayer</button>
      </div>
    )
  }

  if (!history) {
    return <div className="card">Chargement de l’historique...</div>
  }

  if (!series || labels.length === 0) {
    return (
      <div className="card">
        <h2>History Analytics</h2>
        <p>Aucun snapshot exploitable pour le moment.</p>
        <p className="metric-small">
          Lance un audit simple ou une comparaison timeline. Les rapports seront sauvegardés dans backend/data/reports.
        </p>
        <button className="button" onClick={load}>Rafraîchir</button>
      </div>
    )
  }

  return (
    <>
      <div className="section card history-card">
        <div className="history-header">
          <div>
            <h2>History Analytics</h2>
            <p className="metric-small">Courbes multi-saves reconstruites depuis les rapports backend ou la démo GitHub Pages.</p>
            <span className={`badge ${history.source?.includes('fallback') ? 'badge-warn' : 'badge-ok'}`}>
              Source: {history.source ?? 'unknown'}
            </span>
          </div>
          <button className="button" onClick={load}>Rafraîchir</button>
        </div>

        <div className="grid cards">
          <div className="mini-card">
            <div className="metric-title">Snapshots</div>
            <div className="metric-value accent">{history.count}</div>
          </div>

          <div className="mini-card">
            <div className="metric-title">First Year</div>
            <div className="metric-value">{labels[0]}</div>
          </div>

          <div className="mini-card">
            <div className="metric-title">Last Year</div>
            <div className="metric-value">{labels[labels.length - 1]}</div>
          </div>

          <div className="mini-card">
            <div className="metric-title">Latest Risk</div>
            <div className="metric-value warn">{series?.scores?.risk?.at(-1)}</div>
          </div>

          <div className="mini-card">
            <div className="metric-title">Latest Research</div>
            <div className="metric-value accent">{series?.scores?.research?.at(-1)}</div>
          </div>
        </div>
      </div>

      <div className="section grid two">
        <div className="card">
          <h2>Scores Over Time</h2>
          <div className="chart-box">
            <Line
              data={{
                labels,
                datasets: [
                  lineDataset('Global', series.scores.global, palette.blue),
                  lineDataset('Economy', series.scores.economy, palette.pink),
                  lineDataset('Military', series.scores.military, palette.orange),
                  lineDataset('Research', series.scores.research, palette.yellow),
                  lineDataset('Stability', series.scores.stability, palette.teal),
                ],
              }}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="card">
          <h2>Core Metrics Over Time</h2>
          <div className="chart-box">
            <Line
              data={{
                labels,
                datasets: [
                  lineDataset('Economy Core', series.metrics.economy_core, palette.blue),
                  lineDataset('Research Total', series.metrics.research_total, palette.purple),
                  lineDataset('Military Power', series.metrics.military_power, palette.orange),
                ],
              }}
              options={chartOptions}
            />
          </div>
        </div>
      </div>

      <div className="section grid two">
        <div className="card">
          <h2>Research Density vs Empire Size</h2>
          <div className="chart-box">
            <Line
              data={{
                labels,
                datasets: [
                  lineDataset('Research Density', series.metrics.research_density, palette.purple),
                  lineDataset('Empire Size', series.metrics.empire_size, palette.yellow),
                ],
              }}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="card">
          <h2>Risk Escalation</h2>
          <div className="chart-box">
            <Line
              data={{
                labels,
                datasets: [
                  lineDataset('Risk Score', series.scores.risk, palette.red),
                  lineDataset('Stability Score', series.scores.stability, palette.teal),
                ],
              }}
              options={chartOptions}
            />
          </div>
        </div>
      </div>

      <div className="section card">
        <h2>Archetype Evolution</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Archetype</th>
              <th>Global</th>
              <th>Research</th>
              <th>Stability</th>
              <th>Risk</th>
              <th>Report</th>
            </tr>
          </thead>
          <tbody>
            {(series.snapshots ?? []).map((snapshot: any) => (
              <tr key={`${snapshot.year}-${snapshot.report_file}`}>
                <td>{snapshot.year}</td>
                <td>{snapshot.archetype}</td>
                <td>{snapshot.global}</td>
                <td>{snapshot.research}</td>
                <td>{snapshot.stability}</td>
                <td>{snapshot.risk}</td>
                <td>{snapshot.report_file}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
