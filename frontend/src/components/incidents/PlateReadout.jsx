import { formatConfidence } from '../../lib/incidents'
import './PlateReadout.css'

function levelFor(pct) {
  if (pct == null) return 'none'
  if (pct >= 85) return 'high'
  if (pct >= 70) return 'med'
  return 'low'
}

function PlateReadout({ plate, confidence }) {
  const hasPlate = Boolean(plate)
  const pct =
    confidence == null || Number.isNaN(confidence)
      ? null
      : Math.round(confidence * 100)
  const level = levelFor(pct)

  return (
    <div className="plate-readout">
      <span className="plate-readout__label">Detected Plate</span>
      <div
        className={`plate-readout__plate${hasPlate ? '' : ' plate-readout__plate--empty'}`}
      >
        {hasPlate ? plate : 'NO PLATE'}
      </div>

      <div className="plate-readout__confidence">
        <div className="plate-readout__confidence-head">
          <span className="plate-readout__confidence-label">AI Confidence</span>
          <span className="plate-readout__confidence-value" data-level={level}>
            {pct == null ? '—' : formatConfidence(confidence)}
          </span>
        </div>
        <div
          className="plate-readout__meter"
          role="meter"
          aria-valuenow={pct ?? 0}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Plate recognition confidence"
        >
          <div
            className="plate-readout__meter-fill"
            style={{ width: `${pct ?? 0}%` }}
            data-level={level}
          />
        </div>
      </div>
    </div>
  )
}

export default PlateReadout
