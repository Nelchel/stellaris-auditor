import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import { getHistory } from '../lib/api'

const chartText = '#e6edf3'
const grid = '#30363d'

const chartOptions: any = {
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { color: chartText }, grid: { color: grid } },
    y: { ticks: { color: chartText }, grid: { color: grid } },
  },
  plugins: { legend: { labels: { color: chartText } } },
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
    return <div className="card error">{error}</div>
  }

  if (!history) {
    return <div className="card">Chargement de l’historique...</div>
  }

  if ((history.count ?? 0) < 2) {
    return (
      <div className="card">
        <h2>History Analytics</h2>
        <p>Pas encore assez de snapshots. Lance plusieurs audits ou une comparaison timeline.</p>
        <button className="button" onClick={load}>Rafraîchir</button>
      </div>
    )
  }

  return (
    <>
      <div className="section card">
        <div className="history-header">
          <div>
            <h2>History Analytics</h2>
            <p className="metric-small">Courbes multi-saves reconstruites depuis les rapports backend.</p>
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
                  { label: 'Global', data: series.scores.global },
                  { label: 'Economy', data: series.scores.economy },
                  { label: 'Military', data: series.scores.military },
                  { label: 'Research', data: series.scores.research },
                  { label: 'Stability', data: series.scores.stability },
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
                  { label: 'Economy Core', data: series.metrics.economy_core },
                  { label: 'Research Total', data: series.metrics.research_total },
                  { label: 'Military Power', data: series.metrics.military_power },
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
                  { label: 'Research Density', data: series.metrics.research_density },
                  { label: 'Empire Size', data: series.metrics.empire_size },
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
                  { label: 'Risk Score', data: series.scores.risk },
                  { label: 'Stability Score', data: series.scores.stability },
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
