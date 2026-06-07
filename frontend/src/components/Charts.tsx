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
  Filler,
} from 'chart.js'
import { Radar, Line, Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
)

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

function barDataset(label: string, data: number[], color: string) {
  return {
    label,
    data,
    backgroundColor: `${color}aa`,
    borderColor: color,
    borderWidth: 2,
    borderRadius: 8,
  }
}

function radarDataset(label: string, data: number[], color: string) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: `${color}44`,
    pointBackgroundColor: color,
    pointBorderColor: color,
    pointRadius: 4,
    borderWidth: 3,
  }
}

const lineOptions: any = {
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

const radarOptions: any = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: {
        color: mutedText,
        backdropColor: 'transparent',
        stepSize: 20,
        font: { size: 11, weight: 'bold' },
      },
      grid: { color: grid },
      angleLines: { color: grid },
      pointLabels: { color: chartText, font: { size: 13, weight: 'bold' } },
    },
  },
  plugins: {
    legend: {
      labels: {
        color: chartText,
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

export function EmpireRadar({ scores }: { scores: any }) {
  return (
    <Radar
      data={{
        labels: ['Economy', 'Military', 'Research', 'Expansion', 'Stability'],
        datasets: [
          radarDataset('Empire Profile', [
            scores?.economy ?? 0,
            scores?.military ?? 0,
            scores?.research ?? 0,
            scores?.expansion ?? 0,
            scores?.stability ?? 0,
          ], palette.blue),
        ],
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
          radarDataset('Old Save', visual?.score_radar_old ?? [], palette.blue),
          radarDataset('New Save', visual?.score_radar_new ?? [], palette.pink),
        ],
      }}
      options={radarOptions}
    />
  )
}

export function SpecializationDonut({ summary }: { summary: Record<string, number> }) {
  return (
    <Doughnut
      data={{
        labels: Object.keys(summary ?? {}),
        datasets: [{
          data: Object.values(summary ?? {}),
          backgroundColor: [
            palette.blue,
            palette.pink,
            palette.orange,
            palette.yellow,
            palette.teal,
            palette.purple,
            palette.green,
            palette.red,
          ],
          borderColor: '#111827',
          borderWidth: 3,
        }],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: chartText, font: { size: 12, weight: 'bold' } },
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: chartText,
            bodyColor: chartText,
            borderColor: '#334155',
            borderWidth: 1,
          },
        },
      }}
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
          lineDataset('Global', visual?.scores_over_time?.global ?? [], palette.blue),
          lineDataset('Economy', visual?.scores_over_time?.economy ?? [], palette.pink),
          lineDataset('Military', visual?.scores_over_time?.military ?? [], palette.orange),
          lineDataset('Research', visual?.scores_over_time?.research ?? [], palette.yellow),
          lineDataset('Stability', visual?.scores_over_time?.stability ?? [], palette.teal),
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
          barDataset('Economy Core', visual?.core_metrics?.economy_core ?? [], palette.blue),
          barDataset('Research Total', visual?.core_metrics?.research_total ?? [], palette.pink),
          barDataset('Military Power', visual?.core_metrics?.military_power ?? [], palette.orange),
          barDataset('Empire Size', visual?.core_metrics?.empire_size ?? [], palette.yellow),
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
          lineDataset('Risk', visual?.risk_vs_stability?.risk ?? [], palette.red),
          lineDataset('Stability', visual?.risk_vs_stability?.stability ?? [], palette.teal),
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
          lineDataset('Research Density', visual?.research_pressure?.research_density ?? [], palette.purple),
          lineDataset('Empire Size', visual?.research_pressure?.empire_size ?? [], palette.yellow),
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
          barDataset('Old', visual?.specialization_shift?.old ?? [], palette.blue),
          barDataset('New', visual?.specialization_shift?.new ?? [], palette.pink),
        ],
      }}
      options={lineOptions}
    />
  )
}
