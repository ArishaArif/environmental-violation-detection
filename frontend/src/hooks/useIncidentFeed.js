import { useEffect, useMemo, useRef, useState } from 'react'
import { fetchIncidents } from '../api/incidents'
import { normalizeIncident } from '../lib/incidents'
import mockIncidents from '../mock/incidents.mock.json'

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

export function useIncidentFeed() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newIds, setNewIds] = useState({})
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

  const highlightedIds = useMemo(() => {
    const merged = { ...newIds }
    recentIncidentIds(incidents, INITIAL_PULSE_COUNT).forEach((id) => {
      merged[id] = true
    })
    return merged
  }, [incidents, newIds])

  return {
    incidents,
    setIncidents,
    loading,
    error,
    highlightedIds,
    pendingIds,
  }
}
