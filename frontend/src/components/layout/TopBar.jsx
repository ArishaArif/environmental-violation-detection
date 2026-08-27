import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './TopBar.css'

const TABS = [
  {
    id: 'full-console',
    label: 'Full Console',
    to: '/',
    isActive: (path) => path === '/',
  },
  {
    id: 'incident-detail',
    label: 'Incident Detail',
    to: '/incident/INC-8821',
    isActive: (path) => path.startsWith('/incident'),
  },
  {
    id: 'expanded-map',
    label: 'Expanded Map',
    to: '/map',
    isActive: (path) => path.startsWith('/map'),
  },
]

const CLOCK_TIME_ZONE = 'America/Los_Angeles'
const CLOCK_LABEL = 'PST'
const clockFormatter = new Intl.DateTimeFormat('en-GB', {
  timeZone: CLOCK_TIME_ZONE,
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
})

function Clock() {
  const [time, setTime] = useState(() => clockFormatter.format(new Date()))

  useEffect(() => {
    const id = setInterval(
      () => setTime(clockFormatter.format(new Date())),
      1000,
    )
    return () => clearInterval(id)
  }, [])

  return (
    <div className="topbar__clock">
      <span className="topbar__clock-time">{time}</span>
      <span className="topbar__clock-tz">{CLOCK_LABEL}</span>
    </div>
  )
}

function TopBar({ activeDispatches = 0, consoleId = 'LAHORE_CONSOLE_03' }) {
  const { pathname } = useLocation()

  return (
    <header className="topbar">
      <div className="topbar__left">
        <span className="topbar__wordmark">Clean City</span>
        <span className="topbar__badge">
          <span className="topbar__badge-dot" aria-hidden="true" />
          {activeDispatches} Active Dispatches
        </span>
      </div>

      <nav className="topbar__nav" aria-label="Screens">
        {TABS.map((tab, i) => {
          const isActive = tab.isActive(pathname)
          return (
            <Link
              key={tab.id}
              to={tab.to}
              className={`topbar__tab${isActive ? ' is-active' : ''}`}
              aria-current={isActive ? 'page' : undefined}
            >
              {i + 1}. {tab.label}
            </Link>
          )
        })}
      </nav>

      <div className="topbar__right">
        <Clock />
        <span className="topbar__console-id">{consoleId}</span>
      </div>
    </header>
  )
}

export default TopBar
