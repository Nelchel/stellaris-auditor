import { demoReport } from '../demo/demoReport'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

export type ApiResponse = {
  mode: 'single' | 'timeline'
  data: any
}

export async function auditSave(save: File): Promise<ApiResponse> {
  if (DEMO_MODE) {
    return demoReport as ApiResponse
  }

  const form = new FormData()
  form.append('save', save)
  const response = await fetch(`${API_BASE}/audit`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

export async function compareSaves(oldSave: File, newSave: File): Promise<ApiResponse> {
  if (DEMO_MODE) {
    return demoReport as ApiResponse
  }

  const form = new FormData()
  form.append('old_save', oldSave)
  form.append('new_save', newSave)
  const response = await fetch(`${API_BASE}/compare`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

export async function getHistory(): Promise<any> {
  if (DEMO_MODE) {
    return {
      count: 2,
      series: {
        labels: ['2242', '2285'],
        scores: {
          global: [61, 64],
          economy: [72, 95],
          military: [37, 77],
          research: [51, 49],
          stability: [85, 27],
          risk: [9, 42],
        },
        metrics: {
          economy_core: [896, 1635],
          research_total: [204.9, 336.69],
          military_power: [2275.03, 11658.97],
          empire_size: [181, 402],
          research_density: [1.132, 0.838],
        },
        snapshots: [
          { year: '2242', archetype: 'Balanced Empire', global: 61, research: 51, stability: 85, risk: 9, report_file: 'demo-old.json' },
          { year: '2285', archetype: 'Trade-Industrial-Militarist-Internally-Unstable Empire', global: 64, research: 49, stability: 27, risk: 42, report_file: 'demo-new.json' },
        ],
      },
    }
  }

  const response = await fetch(`${API_BASE}/history`)
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

export async function getReports(): Promise<any> {
  const response = await fetch(`${API_BASE}/reports`)
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}
