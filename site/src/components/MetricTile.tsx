interface MetricTileProps {
  label: string
  value: string
  note?: string
}

export default function MetricTile({ label, value, note }: MetricTileProps) {
  return (
    <div className="metric-tile">
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value}</p>
      {note ? <p className="metric-note">{note}</p> : null}
    </div>
  )
}
