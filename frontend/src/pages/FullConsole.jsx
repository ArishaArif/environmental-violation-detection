import { useEffect, useState } from 'react'
import IncidentCard from '../components/incidents/IncidentCard'
import mockIncidents from '../mock/incidents.mock.json'
import './FullConsole.css'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function FullConsole() {
  const [incidents, setIncidents] = useState([])
  const [usingFallback, setUsingFallback] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadIncidents() {
      try {
        const res = await fetch(`${API_BASE}/incidents/`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        const list = Array.isArray(data) ? data : []
        if (!cancelled) {
          setIncidents(list)
          setUsingFallback(false)
        }
      } catch (err) {
        if (!cancelled) {
          console.warn('Could not load incidents from backend; using sample data.', err)
          setIncidents(mockIncidents)
          setUsingFallback(true)
        }
      }
    }

    loadIncidents()
    return () => {
      cancelled = true
    }
  }, [])

  const handleStatusChange = (id, newStatus) => {
    setIncidents((current) =>
      current.map((incident) =>
        incident.id === id
          ? { ...incident, review_status: newStatus }
          : incident,
      ),
    )
  }

  return (
    <div className="full-console">
      <section className="full-console__feed" aria-label="Live incident feed">
        <div className="full-console__section-head">
          <h2 className="full-console__section-title">Live Incident Feed</h2>
          {usingFallback ? (
            <span
              className="full-console__section-note"
              style={{
                marginLeft: 'var(--space-3)',
                fontSize: 'var(--fs-sm)',
                color: 'var(--text-secondary)',
                opacity: 0.75,
              }}
            >
              Backend unavailable — showing sample data
            </span>
          ) : null}
        </div>
        <div className="full-console__feed-list">
          {incidents.map((incident) => (
            <IncidentCard
              key={incident.id}
              incident={incident}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      </section>

      <section className="full-console__map" aria-label="Lahore active violation plot">
        <div className="full-console__section-head">
          <h2 className="full-console__section-title">Lahore Active Violation Plot</h2>
        </div>
        <div className="full-console__map-body">
          <div className="full-console__map-placeholder">
            <span className="full-console__map-placeholder-label">Map Placeholder</span>
          </div>
        </div>
      </section>
    </div>
  )
}

export default FullConsole
