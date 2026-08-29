import { VIOLATION_LABELS } from '../../lib/incidents'
import './ViolationTag.css'

function ViolationTag({ violationType }) {
  const label = VIOLATION_LABELS[violationType] ?? violationType
  return (
    <span className="violation-tag" data-violation={violationType}>
      {label}
    </span>
  )
}

export default ViolationTag
