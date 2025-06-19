import React from 'react';

const ProductionTarget = () => {
  // 실제 데이터는 API나 props로 받아와야 합니다
  const currentProduction = 848;
  const target = 1000;
  const achievementRate = (currentProduction / target * 100).toFixed(1);

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">생산 목표</h3>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-3 me-2">{currentProduction}</div>
          <div className="me-auto">
            <span className="text-muted">/ {target}</span>
          </div>
          <div className="text-muted">{achievementRate}%</div>
        </div>
        <div className="progress">
          <div 
            className="progress-bar" 
            style={{width: `${achievementRate}%`}}
            role="progressbar"
            aria-valuenow={achievementRate}
            aria-valuemin="0"
            aria-valuemax="100"
          >
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductionTarget;