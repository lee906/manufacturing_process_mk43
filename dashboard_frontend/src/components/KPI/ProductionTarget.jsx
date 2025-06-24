import React from 'react';

const ProductionTarget = ({ current = 0, target = 1000 }) => {
  const achievementRate = target > 0 ? (current / target * 100).toFixed(1) : 0;
  
  // 달성률에 따른 색상 결정
  const getProgressColor = (rate) => {
    if (rate >= 90) return 'bg-success';
    if (rate >= 70) return 'bg-warning';
    return 'bg-danger';
  };

  // 달성률에 따른 텍스트 색상
  const getTextColor = (rate) => {
    if (rate >= 90) return 'text-success';
    if (rate >= 70) return 'text-warning';
    return 'text-danger';
  };

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">생산 목표</h3>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-3 me-2">{current.toLocaleString()}</div>
          <div className="me-auto">
            <span className="text-muted">/ {target.toLocaleString()}</span>
          </div>
          <div className={getTextColor(achievementRate)}>
            {achievementRate}%
          </div>
        </div>
        <div className="progress mb-2" style={{ height: '8px' }}>
          <div 
            className={`progress-bar ${getProgressColor(achievementRate)}`}
            style={{ width: `${Math.min(achievementRate, 100)}%` }}
            role="progressbar"
            aria-valuenow={achievementRate}
            aria-valuemin="0"
            aria-valuemax="100"
          >
          </div>
        </div>
        <div className="row text-center">
          <div className="col-4">
            <div className="text-muted small">잔여</div>
            <div className="text-primary fw-bold">
              {Math.max(0, target - current).toLocaleString()}
            </div>
          </div>
          <div className="col-4">
            <div className="text-muted small">달성률</div>
            <div className={`fw-bold ${getTextColor(achievementRate)}`}>
              {achievementRate}%
            </div>
          </div>
          <div className="col-4">
            <div className="text-muted small">상태</div>
            <div className={`fw-bold ${getTextColor(achievementRate)}`}>
              {achievementRate >= 90 ? '우수' : achievementRate >= 70 ? '양호' : '개선필요'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductionTarget;