export const VIOLATION_LABELS = {
  littering: 'Litter Violation',
  unknown: 'Unknown',
}

export const STATUS_LABELS = {
  pending: 'Pending',
  accepted: 'Accepted',
  needs_investigation: 'Investigating',
  rejected: 'Rejected',
  unknown: 'Unknown',
}

export const STATUS_ACTIONS = [
  { status: 'accepted', label: 'Accept', modifier: 'accept' },
  { status: 'needs_investigation', label: 'Investigate', modifier: 'investigate' },
  { status: 'rejected', label: 'Reject', modifier: 'reject' },
]

export const VIOLATION_TYPES = ['littering']

export const REVIEW_STATUSES = ['pending', 'accepted', 'rejected', 'needs_investigation']

export function normalizeViolationType(value) {
  return VIOLATION_TYPES.includes(value) ? value : 'unknown'
}

export function normalizeStatus(value) {
  return REVIEW_STATUSES.includes(value) ? value : 'unknown'
}

export function normalizeIncident(incident) {
  return {
    ...incident,
    violation_type: normalizeViolationType(incident?.violation_type),
    review_status: normalizeStatus(incident?.review_status),
  }
}

export function formatTimeAgo(timestamp) {
  if (timestamp == null) return ''
  const then = new Date(timestamp).getTime()
  if (Number.isNaN(then)) return ''

  const seconds = Math.max(0, Math.round((Date.now() - then) / 1000))
  if (seconds < 60) return `${seconds}s ago`

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`

  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function formatConfidence(value) {
  if (value == null || Number.isNaN(value)) return ''
  return `${Math.round(value * 100)}%`
}

export function evidenceSrc(incident) {
  return incident?.evidence_url ?? incident?.evidence_path ?? null
}
