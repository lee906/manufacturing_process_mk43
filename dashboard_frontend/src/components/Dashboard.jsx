import ProductionStatus from './KPI/ProductionStatus'
import PowerEfficiency from './KPI/PowerEfficiency'

const Dashboard = () => {
  return (
    <div className="row g-3">
      {/* 첫 번째 큰 카드 (3x2 그리드를 포함) */}
      <div className="col-sm-12 col-lg-8">
        <div className="card">
          <div className="card-body">
            <div className="row g-3">
              {/* 1행 1열 */}
              <div className="col-sm-12 col-md-4">
                <ProductionStatus />
              </div>
              {/* 1행 2열 */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">시간 당 생산 수</h3>
                  </div>
                </div>
              </div>
              {/* 1행 3열 */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">FTY(일발양품률)</h3>
                  </div>
                </div>
              </div>
              {/* 2행 1열 */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">OTD(정기납기율)</h3>
                  </div>
                </div>
              </div>
              {/* 2행 2열 */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">Cycle Time</h3>
                  </div>
                </div>
              </div>
              {/* 2행 3열 */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">Lead Time</h3>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="col-sm-12 col-lg-4">
  <div className="card">
    <div className="card-body">
      <div className="row g-3">
        <div className="col-6">
          <div className="card">
            <div className="card-body">
              <h3 className="card-title">현재 생산량</h3>
            </div>
          </div>
        </div>
        <div className="col-6">
          <div className="card">
            <div className="card-body">
              <h3 className="card-title">목표 달성률</h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
      <div className="col-sm-12 col-lg-6">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">설비 관리 KPI(개발중)</h3>
            <h3 className="card-content">설비 가동률, MTBF, MTTR, 정지 시간</h3>
          </div>
        </div>
      </div>
      <div className="col-sm-12 col-lg-6">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">품질 관리 KPI(개발중)</h3>
            <h3 className="card-content">불량률, PPM, Scrap Rate, 재작업률</h3>
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
      <div className="col-12">
        <div className="card">
          <div className="card-body" style={{ height: "20rem" }}>
            <h3 className="card-title">재고 현황(개발중)</h3>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard