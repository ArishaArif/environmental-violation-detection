import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import FullConsole from './pages/FullConsole'
import IncidentDetail from './pages/IncidentDetail'
import ExpandedMap from './pages/ExpandedMap'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<FullConsole />} />
          <Route path="/incident/:id" element={<IncidentDetail />} />
          <Route path="/map" element={<ExpandedMap />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
