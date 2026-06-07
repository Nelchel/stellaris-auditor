export function PlanetTable({ title, planets, mode = 'problems' }: { title: string, planets: any[], mode?: 'problems' | 'economic' | 'best' | 'issues' }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Planet</th>
            <th>Spec</th>
            <th>Efficiency</th>
            {mode === 'economic' && <th>Profitability</th>}
            {mode === 'economic' && <th>Status</th>}
            {mode !== 'economic' && <th>Stability</th>}
            {mode !== 'economic' && <th>Amenities</th>}
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {(planets ?? []).map((planet: any) => (
            <tr key={`${title}-${planet.id ?? planet.name}`}>
              <td><strong>{planet.display_name ?? planet.name}</strong></td>
              <td>{planet.specialization_guess}</td>
              <td>{planet.efficiency_score}</td>
              {mode === 'economic' && <td>{planet.profitability_score}</td>}
              {mode === 'economic' && <td>{planet.economic_status}</td>}
              {mode !== 'economic' && <td>{planet.stability}</td>}
              {mode !== 'economic' && <td>{planet.free_amenities_normalized}</td>}
              <td>
                {(mode === 'economic' ? planet.economic_recommendations : planet.specialization_issues ?? planet.alerts ?? planet.advice ?? []).map((a: string) => (
                  <div key={a}>• {a}</div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
