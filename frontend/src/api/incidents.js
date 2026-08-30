import { normalizeIncident, REVIEW_STATUSES } from '../lib/incidents'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

const FILTER_KEYS = ['violation_type', 'review_status', 'date_from', 'date_to']

function buildQuery(filters) {
  const params = new URLSearchParams()
  if (filters) {
    for (const key of FILTER_KEYS) {
      const value = filters[key]
      if (value != null && value !== '') {
        params.set(key, String(value))
      }
    }
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}

function unwrap(payload) {
  if (Array.isArray(payload)) {
    return { list: payload, total: payload.length }
  }
  if (payload && Array.isArray(payload.data)) {
    return { list: payload.data, total: payload.total ?? payload.data.length }
  }
  if (payload && Array.isArray(payload.incidents)) {
    return { list: payload.incidents, total: payload.total ?? payload.incidents.length }
  }
  return { list: [], total: 0 }
}

export async function fetchIncidents(filters) {
  const res = await fetch(`${API_BASE}/incidents/${buildQuery(filters)}`)
  if (!res.ok) {
    throw new Error(`Incidents request failed with status ${res.status}`)
  }
  const payload = await res.json()
  const { list, total } = unwrap(payload)
  const incidents = list.map(normalizeIncident)
  return { incidents, total }
}

async function readError(res) {
  try {
    const body = await res.json()
    if (body && body.error != null) {
      return typeof body.error === 'string' ? body.error : JSON.stringify(body.error)
    }
    if (body && typeof body.detail === 'string') {
      return body.detail
    }
  } catch {
    return `Request failed with status ${res.status}`
  }
  return `Request failed with status ${res.status}`
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`)
  if (!res.ok) {
    throw new Error(`Analytics request failed with status ${res.status}`)
  }
  return res.json()
}

export async function updateIncidentStatus(id, reviewStatus) {
  if (!REVIEW_STATUSES.includes(reviewStatus)) {
    throw new Error(`Refusing to send unknown review_status: ${reviewStatus}`)
  }
  const res = await fetch(`${API_BASE}/incidents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ review_status: reviewStatus }),
  })
  if (!res.ok) {
    throw new Error(await readError(res))
  }
  return normalizeIncident(await res.json())
}
