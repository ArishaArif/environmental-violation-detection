import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import MapLegend from './MapLegend'
import { VIOLATION_LABELS } from '../../lib/incidents'
import { fetchAnalytics } from '../../api/incidents'
import './ViolationMap.css'

const LAHORE_CENTER = [31.5204, 74.3587]
const DEFAULT_ZOOM = 12

function distinctCameraCount(incidents) {
  const cameras = new Set()
  incidents.forEach((incident) => {
    const lat = Number(incident?.location_lat)
    const lng = Number(incident?.location_lng)
    if (Number.isNaN(lat) || Number.isNaN(lng)) return
    cameras.add(`${lat.toFixed(4)}, ${lng.toFixed(4)}`)
  })
  return cameras.size
}

function hourlyCounts(incidents) {
  const buckets = Array.from({ length: 24 }, () => 0)
  incidents.forEach((incident) => {
    const then = new Date(incident?.timestamp)
    if (Number.isNaN(then.getTime())) return
    buckets[then.getHours()] += 1
  })
  return buckets
}

const MARKER_ICONS = {
  littering: L.divIcon({
    className: 'violation-pin',
    html: '<span class="violation-pin__shape violation-pin__shape--litter"></span>',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  }),
}

const NEW_MARKER_ICON = L.divIcon({
  className: 'violation-pin violation-pin--new',
  html: '<span class="violation-pin__ping" aria-hidden="true"></span><span class="violation-pin__shape violation-pin__shape--litter"></span>',
  iconSize: [22, 22],
  iconAnchor: [11, 11],
})

function iconFor(violationType, isNew) {
  if (isNew) return NEW_MARKER_ICON
  return MARKER_ICONS[violationType] ?? MARKER_ICONS.littering
}

function hasCoordinates(incident) {
  return (
    Number.isFinite(incident?.location_lat) &&
    Number.isFinite(incident?.location_lng)
  )
}

function HourlyRateChart({ data }) {
  const peak = Math.max(...data, 1)
  return (
    <div
      className="hourly-chart"
      role="img"
      aria-label="Hourly violation rate by hour of day"
    >
      {data.map((value, index) => (
        <div
          className="hourly-chart__bar"
          key={index}
          style={{ height: `${Math.max(8, (value / peak) * 100)}%` }}
          title={`${String(index).padStart(2, '0')}:00 — ${value} violations`}
        />
      ))}
    </div>
  )
}

function HotspotsTile({ hotspots }) {
  const top = [...hotspots].sort((a, b) => b.count - a.count).slice(0, 3)
  return (
    <div className="stat-tile stat-tile--chart">
      <div className="stat-tile__head">
        <span className="stat-tile__label">Top Hotspots</span>
      </div>
      {top.length === 0 ? (
        <span className="hotspots-list__empty">No hotspot data yet</span>
      ) : (
        <ul className="hotspots-list">
          {top.map((spot, index) => (
            <li className="hotspots-list__row" key={`${spot.lat}-${spot.lng}`}>
              <span className="hotspots-list__rank">{index + 1}</span>
              <span className="hotspots-list__coords">
                {spot.lat.toFixed(2)}, {spot.lng.toFixed(2)}
              </span>
              <span className="hotspots-list__count">{spot.count}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function StatTile({ tone, label, value }) {
  return (
    <div className="stat-tile">
      <div className="stat-tile__head">
        <span
          className={`stat-tile__mark stat-tile__mark--${tone}`}
          aria-hidden="true"
        />
        <span className="stat-tile__label">{label}</span>
      </div>
      <span className="stat-tile__value">{value}</span>
    </div>
  )
}

function ViolationMap({ incidents = [], newIds = {} }) {
  const [hotspots, setHotspots] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchAnalytics()
      .then((data) => {
        if (!cancelled) setHotspots(Array.isArray(data?.by_hotspot) ? data.by_hotspot : [])
      })
      .catch(() => {
        if (!cancelled) setHotspots(null)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const plotted = incidents.filter(hasCoordinates)

  const litterDetected = incidents.filter(
    (incident) => incident.violation_type === 'littering',
  ).length

  const unresolvedAlerts = incidents.filter(
    (incident) =>
      incident.review_status === 'pending' ||
      incident.review_status === 'needs_investigation',
  ).length

  const camerasActive = distinctCameraCount(incidents)
  const hourly = hourlyCounts(incidents)

  return (
    <div className="violation-map">
      <div className="violation-map__canvas">
        <MapContainer
          className="violation-map__leaflet"
          center={LAHORE_CENTER}
          zoom={DEFAULT_ZOOM}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.basemap.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
            attribution="&copy; OpenStreetMap contributors &copy; CARTO"
          />
          {plotted.map((incident) => (
            <Marker
              key={incident.id}
              position={[incident.location_lat, incident.location_lng]}
              icon={iconFor(incident.violation_type, Boolean(newIds[incident.id]))}
            >
              <Tooltip
                className="violation-tooltip"
                direction="top"
                offset={[0, -10]}
                opacity={1}
              >
                <span className="violation-tooltip__plate">
                  {incident.plate_number ?? 'NO PLATE'}
                </span>
                <span className="violation-tooltip__type">
                  {VIOLATION_LABELS[incident.violation_type] ??
                    incident.violation_type}
                </span>
              </Tooltip>
            </Marker>
          ))}
        </MapContainer>
        <MapLegend />
      </div>

      <div className="violation-map__stats">
        <StatTile tone="litter" label="Litter Detected" value={litterDetected} />
        <StatTile tone="cameras" label="Cameras Active" value={camerasActive} />
        <StatTile tone="alerts" label="Unresolved Alerts" value={unresolvedAlerts} />
        <div className="stat-tile stat-tile--chart">
          <div className="stat-tile__head">
            <span className="stat-tile__label">Hourly Rate</span>
          </div>
          <HourlyRateChart data={hourly} />
        </div>
        {hotspots !== null ? <HotspotsTile hotspots={hotspots} /> : null}
      </div>
    </div>
  )
}

export default ViolationMap
