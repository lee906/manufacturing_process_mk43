import React from 'react';

const HourlyProduction = ({ rate = 0 }) => {
  // 시간당 생산량에 따른 상태 판단
  const getStatus = (rate) => {
    if (rate >= 45) return { color: 'text-success', status: '우수', icon: '📈' };
    if (rate >= 35) return { color: 'text-warning', status: '보통', icon: '📊' };
    return { color: 'text-danger', status: '저조', icon: '📉' };
  };

  const status = getStatus(rate);

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">시간당 생산수</h3>
        <div className="d-flex align-items-baseline">
          <div className={`h1 mb-3 me-2 ${status.color}`}>{rate}</div>
          <div className="me-auto">
            <span className="text-muted">개/시간</span>
          </div>
          <div className="text-end">
            <div style={{ fontSize: '1.2em' }}>{status.icon}</div>
          </div>
        </div>
        <div className="row text-center mt-2">
          <div className="col-6">
            <div className="text-muted small">상태</div>
            <div className={`fw-bold ${status.color}`}>{status.status}</div>
          </div>
          <div className="col-6">
            <div className="text-muted small">목표 대비</div>
            <div className={rate >= 40 ? 'text-success fw-bold' : 'text-warning fw-bold'}>
              {rate >= 40 ? '달성' : '미달'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HourlyProduction;