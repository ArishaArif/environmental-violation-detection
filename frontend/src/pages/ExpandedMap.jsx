import ViolationMap from '../components/map/ViolationMap'
import { useIncidentFeed } from '../hooks/useIncidentFeed'
import './ExpandedMap.css'

function ExpandedMap() {
  const { incidents, loading, error, highlightedIds } = useIncidentFeed()

  return (
    <div className="expanded-map">
      <div className="expanded-map__badge">
        <span className="expanded-map__badge-dot" aria-hidden="true" />
        Live Map Streaming Active
      </div>

      {error ? (
        <div className="expanded-map__banner" role="alert">
          <span className="expanded-map__banner-title">Backend Unreachable</span>
          <span className="expanded-map__banner-text">
            {error} Showing the most recent data; retrying every 30s.
          </span>
        </div>
      ) : null}

      {loading ? (
        <p className="expanded-map__state" role="status">
          Connecting to detection backend…
        </p>
      ) : (
        <div className="expanded-map__body">
          <ViolationMap incidents={incidents} newIds={highlightedIds} />
        </div>
      )}
    </div>
  )
}

export default ExpandedMap
