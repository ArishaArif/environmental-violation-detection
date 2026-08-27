import { Outlet } from 'react-router-dom'
import TopBar from './TopBar'
import './AppLayout.css'

function AppLayout() {
  return (
    <div className="app-shell">
      <TopBar activeDispatches={47} consoleId="LAHORE_CONSOLE_03" />
      <main className="app-shell__content">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
