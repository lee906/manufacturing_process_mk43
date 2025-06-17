import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import Factory2D from './components/Factory2D'


// 임시 컴포넌트들 - 실제 파일이 없을 경우 사용

const Inventory = () => {
  return (
    <div className="row g-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h3 className="card-title">재고 관리</h3>
            <p className="text-secondary">Inventory 페이지 (개발중)</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/factory2d" element={<Factory2D />} />
          <Route path="/inventory" element={<Inventory />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App