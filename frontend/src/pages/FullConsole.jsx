import { useRef, useState } from 'react'
import IncidentCard from '../components/incidents/IncidentCard'
import ViolationMap from '../components/map/ViolationMap'
import { updateIncidentStatus } from '../api/incidents'
import { REVIEW_STATUSES } from '../lib/incidents'
import { useIncidentFeed } from '../hooks/useIncidentFeed'
import './FullConsole.css'

function FullConsole() {
  const { incidents, setIncidents, loading, error, highlightedIds, pendingIds } = useIncidentFeed()
  const [statusErrors, setStatusErrors] = useState({})
  const errorTimers = useRef({})

  const clearStatusError = (id) => {
    if (errorTimers.current[id]) {
      window.clearTimeout(errorTimers.current[id])
      delete errorTimers.current[id]
    }
    setStatusErrors((current) => {
      if (!(id in current)) return current
      const next = { ...current }
      delete next[id]
      return next
    })
  }

  const flagStatusError = (id, message) => {
    setStatusErrors((current) => ({ ...current, [id]: message }))
    if (errorTimers.current[id]) window.clearTimeout(errorTimers.current[id])
    errorTimers.current[id] = window.setTimeout(() => {
      delete errorTimers.current[id]
      setStatusErrors((current) => {
        const next = { ...current }
        delete next[id]
        return next
      })
    }, 4000)
  }

  const handleStatusChange = (id, newStatus) => {
    if (!REVIEW_STATUSES.includes(newStatus)) return

    const target = incidents.find((incident) => incident.id === id)
    if (!target) return

    const previousStatus = target.review_status
    if (previousStatus === newStatus) return

    setIncidents((current) =>
      current.map((incident) =>
        incident.id === id ? { ...incident, review_status: newStatus } : incident,
      ),
    )
    clearStatusError(id)
    pendingIds.current.add(id)

    updateIncidentStatus(id, newStatus)
      .catch((err) => {
        console.warn('Status update failed; reverting.', err)
        setIncidents((current) =>
          current.map((incident) =>
            incident.id === id ? { ...incident, review_status: previousStatus } : incident,
          ),
        )
        flagStatusError(id, err.message)
      })
      .finally(() => {
        pendingIds.current.delete(id)
      })
  }

  return (
    <div className="full-console">
      <section className="full-console__feed" aria-label="Live incident feed">
        <div className="full-console__section-head">
          <h2 className="full-console__section-title">Live Incident Feed</h2>
        </div>

        {error ? (
          <div className="full-console__banner" role="alert">
            <span className="full-console__banner-title">Backend Unreachable</span>
            <span className="full-console__banner-text">
              {error} Showing the most recent data; retrying every 30s.
            </span>
          </div>
        ) : null}

        <div className="full-console__feed-list">
          {loading ? (
            <p className="full-console__state" role="status">
              Connecting to detection backend…
            </p>
          ) : incidents.length === 0 ? (
            <p className="full-console__state">No incidents to show yet.</p>
          ) : (
            incidents.map((incident) => (
              <IncidentCard
                key={incident.id}
                incident={incident}
                onStatusChange={handleStatusChange}
                updateError={statusErrors[incident.id]}
                isNew={Boolean(highlightedIds[incident.id])}
              />
            ))
          )}
        </div>
      </section>

      <section className="full-console__map" aria-label="Lahore active violation plot">
        <div className="full-console__section-head">
          <h2 className="full-console__section-title">Lahore Active Violation Plot</h2>
        </div>
        <div className="full-console__map-body">
          <ViolationMap incidents={incidents} newIds={highlightedIds} />
        </div>
      </section>
    </div>
  )
}

export default FullConsole
