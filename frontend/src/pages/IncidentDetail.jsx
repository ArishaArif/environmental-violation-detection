import { useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import mockIncidents from '../mock/incidents.mock.json'
import ViolationTag from '../components/incidents/ViolationTag'
import StatusButtonGroup from '../components/incidents/StatusButtonGroup'
import PlateReadout from '../components/incidents/PlateReadout'
import { updateIncidentStatus } from '../api/incidents'
import { formatTimeAgo, evidenceSrc, REVIEW_STATUSES } from '../lib/incidents'
import './IncidentDetail.css'

function findIncident(idParam) {
  const numeric = String(idParam ?? '').replace(/\D/g, '')
  if (!numeric) return undefined
  return mockIncidents.find((incident) => String(incident.id) === numeric)
}

function formatCoordinates(lat, lng) {
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return 'Location unavailable'
  const ns = lat >= 0 ? 'N' : 'S'
  const ew = lng >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(4)}° ${ns}, ${Math.abs(lng).toFixed(4)}° ${ew}`
}

function cameraId(id) {
  return `CAM-LHR-${String(id).slice(-2)}`
}

function EvidenceImage({ src, alt }) {
  const [failed, setFailed] = useState(false)

  if (!src || failed) {
    return (
      <div className="incident-detail__evidence-fallback">
        <span className="incident-detail__evidence-icon" aria-hidden="true" />
        <span className="incident-detail__evidence-note">Evidence frame unavailable</span>
      </div>
    )
  }

  return (
    <img
      className="incident-detail__evidence-img"
      src={src}
      alt={alt}
      onError={() => setFailed(true)}
    />
  )
}

function IncidentDetail() {
  const { id } = useParams()
  const incident = findIncident(id)
  const [overrides, setOverrides] = useState({})
  const [updateError, setUpdateError] = useState(null)
  const errorTimer = useRef(null)

  if (!incident) {
    return (
      <section className="incident-detail">
        <div className="incident-detail__inner">
          <Link className="incident-detail__back" to="/">
            Full Console
          </Link>
          <div className="incident-detail__missing">
            <span className="incident-detail__missing-code">Incident Not Found</span>
            <p className="incident-detail__missing-text">
              No incident matches “{id}”. It may have been cleared from the active queue.
            </p>
          </div>
        </div>
      </section>
    )
  }

  const incidentId = `INC-${incident.id}`
  const timeAgo = formatTimeAgo(incident.timestamp)
  const status = overrides[incident.id] ?? incident.review_status

  const handleStatusChange = (next) => {
    if (!REVIEW_STATUSES.includes(next)) return

    const previousStatus = status
    if (previousStatus === next) return

    setOverrides((prev) => ({ ...prev, [incident.id]: next }))
    if (errorTimer.current) window.clearTimeout(errorTimer.current)
    setUpdateError(null)

    updateIncidentStatus(incident.id, next).catch((err) => {
      console.warn('Status update failed; reverting.', err)
      setOverrides((prev) => ({ ...prev, [incident.id]: previousStatus }))
      setUpdateError(err.message)
      errorTimer.current = window.setTimeout(() => setUpdateError(null), 4000)
    })
  }

  return (
    <section className="incident-detail">
      <div className="incident-detail__inner">
        <Link className="incident-detail__back" to="/">
          Full Console
        </Link>

        <header className="incident-detail__head">
          <div className="incident-detail__heading">
            <span className="incident-detail__id">{incidentId}</span>
            <span className="incident-detail__tag">Incident Review</span>
          </div>
          <div className="incident-detail__head-meta">
            <ViolationTag violationType={incident.violation_type} />
            <span className="incident-detail__time">Detected {timeAgo}</span>
          </div>
        </header>

        <figure className="incident-detail__evidence">
          <EvidenceImage
            src={evidenceSrc(incident)}
            alt={`Evidence for ${incident.plate_number ?? 'unidentified plate'}`}
          />
        </figure>

        <div className="incident-detail__grid">
          <PlateReadout
            plate={incident.plate_number}
            confidence={incident.plate_confidence}
          />

          <div className="location-block">
            <span className="location-block__label">Location</span>
            <dl className="location-block__list">
              <div className="location-block__row">
                <dt>Camera</dt>
                <dd>{cameraId(incident.id)}</dd>
              </div>
              <div className="location-block__row">
                <dt>Coordinates</dt>
                <dd>{formatCoordinates(incident.location_lat, incident.location_lng)}</dd>
              </div>
              <div className="location-block__row">
                <dt>Zone</dt>
                <dd>Lahore Metro</dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="incident-detail__actions">
          <span className="incident-detail__actions-label">Dispatch Decision</span>
          {updateError ? (
            <span className="incident-detail__update-error" role="alert" title={updateError}>
              Update failed — reverted
            </span>
          ) : null}
          <StatusButtonGroup size="lg" status={status} onChange={handleStatusChange} />
        </div>
      </div>
    </section>
  )
}

export default IncidentDetail
