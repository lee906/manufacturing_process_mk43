const Dashboard = () => {
  return (
    <div className="row g-3">
      <div className="col-sm-6 col-lg-4">
        <div className="card">
          <div className="card-body" style={{ height: "10rem" }}>
            <h3 className="card-title">로봇 상태</h3>
          </div>
        </div>
      </div>
      <div className="col-sm-6 col-lg-4">
        <div className="card">
          <div className="card-body" style={{ height: "10rem" }}>
            <h3 className="card-title">생산 현황</h3>
          </div>
        </div>
      </div>
      <div className="col-sm-6 col-lg-4">
        <div className="card">
          <div className="card-body" style={{ height: "10rem" }}>
            <h3 className="card-title">재고 현황</h3>
          </div>
        </div>
      </div>
      <div className="col-12">
        <div className="card">
          <div className="card-body" style={{ height: "10rem" }}>
            <h3 className="card-title">실시간 모니터링</h3>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard