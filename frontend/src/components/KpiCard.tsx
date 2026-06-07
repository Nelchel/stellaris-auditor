type KpiCardProps = {
  title: string
  value: string | number
  subtitle?: string
  tone?: 'good' | 'warn' | 'bad' | 'accent' | 'purple'
}

export function KpiCard({ title, value, subtitle, tone = 'accent' }: KpiCardProps) {
  return (
    <div className="card">
      <div className="metric-title">{title}</div>
      <div className={`metric-value ${tone}`}>{value}</div>
      {subtitle && <div className="metric-small">{subtitle}</div>}
    </div>
  )
}
