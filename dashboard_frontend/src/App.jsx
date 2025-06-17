import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import Factory2D from './components/Factory2D'
import Inventory from './components/Inventory'

function App() {
  return (
    <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/factory2d" element={<Factory2D />} />
          <Route path="/inventory" element={<Inventory />} />
        </Routes>
    </BrowserRouter>
  )
}

export default App