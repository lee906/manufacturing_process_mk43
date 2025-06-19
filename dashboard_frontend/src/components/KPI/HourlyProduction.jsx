import React from 'react';

const HourlyProduction = () => {
  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">시간당 생산수</h3>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-3 me-2">42</div>
          <div className="me-auto">
            <span className="text-muted">개/시간</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HourlyProduction;