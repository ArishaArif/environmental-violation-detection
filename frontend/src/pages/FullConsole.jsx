import { useEffect, useMemo, useRef, useState } from 'react'
import IncidentCard from '../components/incidents/IncidentCard'
import ViolationMap from '../components/map/ViolationMap'
import { fetchIncidents, updateIncidentStatus } from '../api/incidents'
import { normalizeIncident, REVIEW_STATUSES } from '../lib/incidents'
import mockIncidents from '../mock/incidents.mock.json'
import './FullConsole.css'

const FALLBACK_INCIDENTS = mockIncidents.map(normalizeIncident)

const INITIAL_PULSE_COUNT = 2

function recentIncidentIds(incidents, count) {
  return [...incidents]
    .filter((incident) => !Number.isNaN(new Date(incident.timestamp).getTime()))
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, count)
    .map((incident) => incident.id)
}

function sameIncident(a, b) {
  const keys = new Set([...Object.keys(a), ...Object.keys(b)])
  for (const key of keys) {
    if (a[key] !== b[key]) return false
  }
  return true
}

function mergeIncidents(prev, incoming, pending) {
  if (prev.length === 0) return incoming
  const prevById = new Map(prev.map((incident) => [incident.id, incident]))
  const incomingById = new Map(incoming.map((incident) => [incident.id, incident]))
  const merged = []
  prev.forEach((incident) => {
    const next = incomingById.get(incident.id)
    if (!next) return
    if (pending.has(incident.id) || sameIncident(incident, next)) {
      merged.push(incident)
    } else {
      merged.push(next)
    }
  })
  incoming.forEach((incident) => {
    if (!prevById.has(incident.id)) merged.push(incident)
  })
  return merged
}

function FullConsole() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusErrors, setStatusErrors] = useState({})
  const [newIds, setNewIds] = useState({})
  const errorTimers = useRef({})
  const newTimers = useRef({})
  const seenIds = useRef(new Set())
  const pendingIds = useRef(new Set())

  useEffect(() => {
    let cancelled = false
    let inFlight = false
    let skipTicks = 0

    const highlight = (ids) => {
      setNewIds((current) => {
        const next = { ...current }
        ids.forEach((id) => {
          next[id] = true
        })
        return next
      })
      ids.forEach((id) => {
        if (newTimers.current[id]) window.clearTimeout(newTimers.current[id])
        newTimers.current[id] = window.setTimeout(() => {
          delete newTimers.current[id]
          setNewIds((current) => {
            if (!(id in current)) return current
            const next = { ...current }
            delete next[id]
            return next
          })
        }, 6000)
      })
    }

    const apply = (rows, markNew) => {
      const arrived = []
      rows.forEach((row) => {
        if (!seenIds.current.has(row.id)) {
          seenIds.current.add(row.id)
          if (markNew) arrived.push(row.id)
        }
      })
      setIncidents((current) => mergeIncidents(current, rows, pendingIds.current))
      if (arrived.length > 0) highlight(arrived)
    }

    const poll = async (initial) => {
      if (cancelled || inFlight) return
      inFlight = true
      try {
        const { incidents: rows } = await fetchIncidents()
        if (cancelled) return
        apply(rows, !initial)
        setError(null)
        skipTicks = 0
      } catch (err) {
        if (cancelled) return
        console.warn('Incident fetch failed; keeping the most recent data.', err)
        if (initial) apply(FALLBACK_INCIDENTS, false)
        setError('Could not reach the detection backend at 127.0.0.1:8000.')
        skipTicks = 2
      } finally {
        inFlight = false
        if (initial && !cancelled) setLoading(false)
      }
    }

    poll(true)

    const interval = window.setInterval(() => {
      if (cancelled) return
      if (skipTicks > 0) {
        skipTicks -= 1
        return
      }
      poll(false)
    }, 10000)

    return () => {
      cancelled = true
      window.clearInterval(interval)
      Object.values(newTimers.current).forEach((timer) => window.clearTimeout(timer))
      newTimers.current = {}
    }
  }, [])

  useEffect(() => {
    const timers = errorTimers.current
    return () => {
      Object.values(timers).forEach((timer) => window.clearTimeout(timer))
    }
  }, [])

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

  const highlightedIds = useMemo(() => {
    const merged = { ...newIds }
    recentIncidentIds(incidents, INITIAL_PULSE_COUNT).forEach((id) => {
      merged[id] = true
    })
    return merged
  }, [incidents, newIds])

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
