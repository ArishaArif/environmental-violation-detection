import { STATUS_ACTIONS } from '../../lib/incidents'
import './StatusButtonGroup.css'

function StatusButtonGroup({ status, onChange, size = 'md' }) {
  return (
    <div className={`status-buttons status-buttons--${size}`}>
      {STATUS_ACTIONS.map((action) => {
        const isActive = status === action.status
        return (
          <button
            key={action.status}
            type="button"
            className={`status-buttons__btn status-buttons__btn--${action.modifier}${isActive ? ' is-active' : ''}`}
            aria-pressed={isActive}
            onClick={() => onChange?.(action.status)}
          >
            {action.label}
          </button>
        )
      })}
    </div>
  )
}

export default StatusButtonGroup
