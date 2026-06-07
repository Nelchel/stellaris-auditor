import {
  Chart as ChartJS,
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar, Line, Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(RadialLinearScale, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend)

const chartText = '#e6edf3'
const grid = '#30363d'

const lineOptions: any = {
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { color: chartText }, grid: { color: grid } },
    y: { ticks: { color: chartText }, grid: { color: grid } },
  },
  plugins: { legend: { labels: { color: chartText } } },
}

const radarOptions: any = {
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: { color: chartText, backdropColor: 'transparent' },
      grid: { color: grid },
      angleLines: { color: grid },
      pointLabels: { color: chartText },
    },
  },
  plugins: { legend: { labels: { color: chartText } } },
}

export function EmpireRadar({ scores }: { scores: any }) {
  return (
    <Radar
      data={{
        labels: ['Economy', 'Military', 'Research', 'Expansion', 'Stability'],
        datasets: [{
          label: 'Empire Profile',
          data: [scores?.economy ?? 0, scores?.military ?? 0, scores?.research ?? 0, scores?.expansion ?? 0, scores?.stability ?? 0],
        }],
      }}
      options={radarOptions}
    />
  )
}

export function CompareRadar({ visual }: { visual: any }) {
  return (
    <Radar
      data={{
        labels: ['Economy', 'Military', 'Research', 'Expansion', 'Stability'],
        datasets: [
          { label: 'Old Save', data: visual?.score_radar_old ?? [] },
          { label: 'New Save', data: visual?.score_radar_new ?? [] },
        ],
      }}
      options={radarOptions}
    />
  )
}

export function SpecializationDonut({ summary }: { summary: Record<string, number> }) {
  return (
    <Doughnut
      data={{ labels: Object.keys(summary ?? {}), datasets: [{ data: Object.values(summary ?? {}) }] }}
      options={{ maintainAspectRatio: false, plugins: { legend: { labels: { color: chartText }, position: 'bottom' } } }}
    />
  )
}

export function ScoresLine({ visual }: { visual: any }) {
  const labels = visual?.labels ?? []
  return (
    <Line
      data={{
        labels,
        datasets: [
          { label: 'Global', data: visual?.scores_over_time?.global ?? [] },
          { label: 'Economy', data: visual?.scores_over_time?.economy ?? [] },
          { label: 'Military', data: visual?.scores_over_time?.military ?? [] },
          { label: 'Research', data: visual?.scores_over_time?.research ?? [] },
          { label: 'Stability', data: visual?.scores_over_time?.stability ?? [] },
        ],
      }}
      options={lineOptions}
    />
  )
}

export function CoreMetricsBar({ visual }: { visual: any }) {
  const labels = visual?.labels ?? []
  return (
    <Bar
      data={{
        labels,
        datasets: [
          { label: 'Economy Core', data: visual?.core_metrics?.economy_core ?? [] },
          { label: 'Research Total', data: visual?.core_metrics?.research_total ?? [] },
          { label: 'Military Power', data: visual?.core_metrics?.military_power ?? [] },
          { label: 'Empire Size', data: visual?.core_metrics?.empire_size ?? [] },
        ],
      }}
      options={lineOptions}
    />
  )
}

export function RiskStabilityLine({ visual }: { visual: any }) {
  return (
    <Line
      data={{
        labels: visual?.labels ?? [],
        datasets: [
          { label: 'Risk', data: visual?.risk_vs_stability?.risk ?? [] },
          { label: 'Stability', data: visual?.risk_vs_stability?.stability ?? [] },
        ],
      }}
      options={lineOptions}
    />
  )
}

export function ResearchPressureLine({ visual }: { visual: any }) {
  return (
    <Line
      data={{
        labels: visual?.labels ?? [],
        datasets: [
          { label: 'Research Density', data: visual?.research_pressure?.research_density ?? [] },
          { label: 'Empire Size', data: visual?.research_pressure?.empire_size ?? [] },
        ],
      }}
      options={lineOptions}
    />
  )
}

export function SpecializationShiftBar({ visual }: { visual: any }) {
  return (
    <Bar
      data={{
        labels: visual?.specialization_shift?.labels ?? [],
        datasets: [
          { label: 'Old', data: visual?.specialization_shift?.old ?? [] },
          { label: 'New', data: visual?.specialization_shift?.new ?? [] },
        ],
      }}
      options={lineOptions}
    />
  )
}
