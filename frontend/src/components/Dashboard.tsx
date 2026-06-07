import { KpiCard } from './KpiCard'
import {
  EmpireRadar,
  CompareRadar,
  SpecializationDonut,
  ScoresLine,
  CoreMetricsBar,
  RiskStabilityLine,
  ResearchPressureLine,
  SpecializationShiftBar,
} from './Charts'
import { PlanetTable } from './Tables'

type DashboardProps = { result: any }

export function Dashboard({ result }: DashboardProps) {
  const data = result?.data ?? result
  const current = data?.new_audit ?? data

  const scores = current?.scores ?? {}
  const strategic = current?.strategic_analysis ?? {}
  const risk = current?.risk_analysis ?? {}
  const meta = current?.meta_benchmarking ?? {}
  const metrics = current?.metrics ?? {}
  const income = current?.resources?.income ?? {}
  const planetIntel = current?.planet_intelligence ?? {}
  const topPlanets = current?.top_problem_planets ?? []
  const visual = data?.visual_analytics
  const narrative = data?.campaign_narrative
  const evolution = data?.evolution_analysis

  return (
    <>
      <div className="grid cards">
        <KpiCard title="Global Score" value={scores.global ?? '?'} subtitle="/100" />
        <KpiCard title="Economy" value={scores.economy ?? '?'} tone="good" />
        <KpiCard title="Research" value={scores.research ?? '?'} tone={(scores.research ?? 100) < 55 ? 'bad' : 'accent'} />
        <KpiCard title="Collapse Risk" value={risk.collapse_risk ?? 'Unknown'} tone={risk.collapse_risk === 'Medium' ? 'warn' : risk.collapse_risk === 'High' ? 'bad' : 'accent'} />
        <KpiCard title="War Readiness" value={risk.war_readiness ?? 'Unknown'} tone="purple" />
      </div>

      <div className="section grid two">
        <div className="card">
          <h2>Empire Radar</h2>
          <div className="chart-box"><EmpireRadar scores={scores} /></div>
        </div>
        <div className="card">
          <h2>Strategic Verdict</h2>
          <p>{strategic.verdict ?? 'No verdict available.'}</p>
          <h3>Priority Actions</h3>
          <ul className="clean">{(strategic.priority_actions ?? []).map((item: string) => <li key={item}>{item}</li>)}</ul>
          <h3>Risk Verdict</h3>
          <p>{risk.verdict ?? 'No risk analysis available.'}</p>
        </div>
      </div>

      <div className="section grid three">
        <div className="card">
          <h2>Meta Benchmark</h2>
          <div className="kv">
            <div>Year</div><div>{meta.save_year ?? '?'}</div>
            <div>Reference</div><div>{meta.benchmark_reference_year ?? '?'}</div>
            <div>Research</div><div>{meta.research_curve ?? '?'}</div>
            <div>Military</div><div>{meta.military_curve ?? '?'}</div>
            <div>Economy</div><div>{meta.economy_curve ?? '?'}</div>
          </div>
          <p className="metric-small">{meta.overall_meta_position}</p>
        </div>

        <div className="card">
          <h2>Income Snapshot</h2>
          <div className="kv">
            <div>Energy</div><div>{income.energy?.toFixed?.(1) ?? 0}</div>
            <div>Minerals</div><div>{income.minerals?.toFixed?.(1) ?? 0}</div>
            <div>Alloys</div><div>{income.alloys?.toFixed?.(1) ?? 0}</div>
            <div>Research</div><div>{metrics.research?.research_total?.toFixed?.(1) ?? 0}</div>
            <div>Trade</div><div>{income.trade?.toFixed?.(1) ?? 0}</div>
          </div>
        </div>

        <div className="card">
          <h2>Specializations</h2>
          <div className="chart-box small"><SpecializationDonut summary={current?.planet_specialization_summary ?? {}} /></div>
        </div>
      </div>

      {visual && (
        <div className="section card visual-card">
          <h2>Visual Analytics Cockpit</h2>
          <div className="grid two section">
            <div className="mini-card"><h3>Old vs New Radar</h3><div className="chart-box"><CompareRadar visual={visual} /></div></div>
            <div className="mini-card"><h3>Scores Over Time</h3><div className="chart-box"><ScoresLine visual={visual} /></div></div>
          </div>
          <div className="grid two section">
            <div className="mini-card"><h3>Core Metrics</h3><div className="chart-box"><CoreMetricsBar visual={visual} /></div></div>
            <div className="mini-card"><h3>Risk vs Stability</h3><div className="chart-box"><RiskStabilityLine visual={visual} /></div></div>
          </div>
          <div className="grid two section">
            <div className="mini-card"><h3>Research Pressure</h3><div className="chart-box"><ResearchPressureLine visual={visual} /></div></div>
            <div className="mini-card"><h3>Specialization Shift</h3><div className="chart-box"><SpecializationShiftBar visual={visual} /></div></div>
          </div>
        </div>
      )}

      {narrative && (
        <div className="section card narrative-card">
          <h2>Campaign Narrative</h2>
          <div className="campaign-verdict">{narrative.campaign_verdict}</div>
          <p className="metric-small">{narrative.summary}</p>
          <div className="grid three section">
            <div className="mini-card"><h3>Main Trajectory</h3><ul className="clean">{(narrative.main_trajectory ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul></div>
            <div className="mini-card"><h3>What Went Well</h3><ul className="clean">{(narrative.what_went_well ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul></div>
            <div className="mini-card"><h3>What Went Wrong</h3><ul className="clean">{(narrative.what_went_wrong ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul></div>
          </div>
          <div className="grid two section">
            <div className="mini-card"><h3>Turning Points</h3><ul className="clean">{(narrative.turning_points ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul></div>
            <div className="mini-card"><h3>Next Strategic Pivot</h3><ul className="clean">{(narrative.next_strategic_pivot ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul></div>
          </div>
        </div>
      )}

      {evolution && (
        <div className="section card">
          <h2>Empire Evolution</h2>
          <div className="grid three">
            {Object.entries(evolution.score_deltas ?? {}).map(([key, value]: [string, any]) => (
              <div className="mini-card" key={key}>
                <div className="metric-title">{key}</div>
                <div className="metric-small">{value.old} → {value.new}</div>
                <div className={`metric-value ${value.delta > 0 ? 'good' : value.delta < 0 ? 'bad' : 'accent'}`}>
                  {value.delta > 0 ? '+' : ''}{value.delta}
                </div>
              </div>
            ))}
          </div>
          <h3>Strategic Insights</h3>
          <ul className="clean">{(evolution.insights ?? []).map((i: string) => <li key={i}>{i}</li>)}</ul>
        </div>
      )}

      <div className="section card">
        <h2>Planet Intelligence</h2>
        <p>{planetIntel.summary ?? 'No planet intelligence available.'}</p>
        <div className="grid four section">
          {Object.entries(planetIntel.pressure_summary ?? {}).map(([key, value]) => (
            <div className="mini-card" key={key}>
              <div className="metric-title">{key}</div>
              <div className={`metric-value ${key === 'Critical' ? 'bad' : key === 'High' ? 'warn' : key === 'Low' ? 'good' : 'accent'}`}>{String(value)}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="section grid two">
        <PlanetTable title="Worst Managed Planets" planets={planetIntel.worst_planets ?? topPlanets} mode="issues" />
        <PlanetTable title="Best Planets" planets={planetIntel.best_planets ?? []} mode="best" />
      </div>

      <div className="section grid two">
        <PlanetTable title="Economic Intelligence" planets={planetIntel.worst_planets ?? []} mode="economic" />
        <PlanetTable title="Specialization Issues" planets={planetIntel.specialization_issues ?? []} mode="issues" />
      </div>
    </>
  )
}
