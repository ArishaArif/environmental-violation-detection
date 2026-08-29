import './MapLegend.css'

const LEGEND_ITEMS = [
  { id: 'litter', label: 'Litter Detected', shape: 'square', tone: 'litter' },
  { id: 'smoke', label: 'Smoke Detected', shape: 'diamond', tone: 'smoke' },
  { id: 'new', label: 'Pulsing New Arrivals', shape: 'pulse', tone: 'new' },
]

function MapLegend() {
  return (
    <div className="map-legend" role="list" aria-label="Marker legend">
      {LEGEND_ITEMS.map((item) => (
        <div className="map-legend__row" role="listitem" key={item.id}>
          <span
            className={`map-legend__icon map-legend__icon--${item.shape} map-legend__icon--${item.tone}`}
            aria-hidden="true"
          />
          <span className="map-legend__label">{item.label}</span>
        </div>
      ))}
    </div>
  )
}

export default MapLegend
