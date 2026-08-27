import { useState } from 'react'
import './IncidentCard.css'

const VIOLATIONS = {
  littering: { label: 'Litter Violation' },
  smoke: { label: 'Smoke Emission' },
}

const STATUS_ACTIONS = [
  { status: 'accepted', label: 'Accept', modifier: 'accept' },
  { status: 'needs_investigation', label: 'Investigate', modifier: 'investigate' },
  { status: 'rejected', label: 'Reject', modifier: 'reject' },
]

const STATUS_LABELS = {
  pending: 'Pending',
  accepted: 'Accepted',
  needs_investigation: 'Investigating',
  rejected: 'Rejected',
}

function formatTimeAgo(timestamp) {
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

function formatConfidence(value) {
  if (value == null || Number.isNaN(value)) return ''
  return `${Math.round(value * 100)}%`
}

function IncidentCard({ incident, onStatusChange }) {
  const {
    id,
    plate_number,
    violation_type,
    timestamp,
    confidence,
    evidence_path,
    review_status,
  } = incident

  const [thumbFailed, setThumbFailed] = useState(false)

  const violation = VIOLATIONS[violation_type] ?? { label: violation_type }
  const timeAgo = formatTimeAgo(timestamp)
  const incidentId = `INC-${id}`
  const plateLabel = plate_number ?? 'No Plate'
  const confidenceLabel = formatConfidence(confidence)
  const statusLabel = STATUS_LABELS[review_status] ?? review_status
  const showThumb = Boolean(evidence_path) && !thumbFailed

  return (
    <article
      className="incident-card"
      data-violation={violation_type}
      data-status={review_status}
    >
      <header className="incident-card__head">
        <span className="incident-card__badge">{violation.label}</span>
        <div className="incident-card__head-right">
          <span className="incident-card__status">{statusLabel}</span>
          <span className="incident-card__id">{incidentId}</span>
        </div>
      </header>

      <div className="incident-card__body">
        <div className="incident-card__thumb">
          {showThumb ? (
            <img
              className="incident-card__thumb-img"
              src={evidence_path}
              alt={`Evidence for ${plateLabel}`}
              onError={() => setThumbFailed(true)}
            />
          ) : null}
        </div>

        <div className="incident-card__info">
          <div className="incident-card__plate">{plateLabel}</div>
          <div className="incident-card__meta">
            <span className="incident-card__meta-time">TIME {timeAgo}</span>
            <span className="incident-card__meta-sep" aria-hidden="true">
              |
            </span>
            <span className="incident-card__meta-conf">CONF {confidenceLabel}</span>
          </div>
        </div>
      </div>

      <div className="incident-card__actions">
        {STATUS_ACTIONS.map((action) => {
          const isActive = review_status === action.status
          return (
            <button
              key={action.status}
              type="button"
              className={`incident-card__btn incident-card__btn--${action.modifier}${isActive ? ' is-active' : ''}`}
              aria-pressed={isActive}
              onClick={() => onStatusChange?.(id, action.status)}
            >
              {action.label}
            </button>
          )
        })}
      </div>
    </article>
  )
}

export default IncidentCard
