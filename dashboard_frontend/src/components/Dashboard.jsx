import ProductionStatus from './ProductionStatus'
import PowerEfficiency from './PowerEfficiency'


const Dashboard = () => {
  return (
    <div className="row g-3">
      <div className="col-sm-12 col-lg-8">
        <div className="row g-2 mt-2"></div>
        <ProductionStatus />
      </div>
      <div className="col-sm-12 col-lg-4">
        <PowerEfficiency />
      </div>
      <div className="col-sm-12 col-lg-6">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">설비 관리 KPI(개발중)</h3>
            <h3 className="card-content">OEE, Throughput, Cycle Time, 설비 가동률</h3>
          </div>
        </div>
      </div>
      <div className="col-sm-12 col-lg-6">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">품질 관리 KPI(개발중)</h3>
            <h3 className="card-content">FTY, PPM, Scrap Rate, 재작업률</h3>
          </div>
        </div>
      </div>
      <div className="col-12">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">실시간 로봇 모니터링(개발중)</h3>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard