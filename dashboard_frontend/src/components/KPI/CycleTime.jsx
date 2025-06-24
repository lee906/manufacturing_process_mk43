import React from 'react';

const CycleTime = ({ time = 0 }) => {
  // Cycle Time에 따른 효율성 판단 (목표: 85초 이하)
  const getEfficiency = (time) => {
    if (time <= 80) return { color: 'text-success', efficiency: '우수', icon: '⚡' };
    if (time <= 90) return { color: 'text-warning', efficiency: '양호', icon: '⏱️' };
    return { color: 'text-danger', efficiency: '개선필요', icon: '⚠️' };
  };

  const efficiency = getEfficiency(time);
  const targetTime = 85; // 목표 Cycle Time
  const improvement = time > targetTime ? `+${(time - targetTime).toFixed(1)}` : `-${(targetTime - time).toFixed(1)}`;

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">Cycle Time</h3>
        <div className="d-flex align-items-baseline">
          <div className={`h1 mb-3 me-2 ${efficiency.color}`}>{time}</div>
          <div className="me-auto">
            <span className="text-muted">초/개</span>
          </div>
          <div className="text-end">
            <div style={{ fontSize: '1.2em' }}>{efficiency.icon}</div>
          </div>
        </div>
        <div className="row text-center mt-2">
          <div className="col-6">
            <div className="text-muted small">효율성</div>
            <div className={`fw-bold ${efficiency.color}`}>{efficiency.efficiency}</div>
          </div>
          <div className="col-6">
            <div className="text-muted small">목표 대비</div>
            <div className={time <= targetTime ? 'text-success fw-bold' : 'text-danger fw-bold'}>
              {improvement}초
            </div>
          </div>
        </div>
        <div className="progress mt-2" style={{ height: '4px' }}>
          <div 
            className={time <= targetTime ? 'progress-bar bg-success' : 'progress-bar bg-danger'}
            style={{ width: `${Math.min((targetTime / time) * 100, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default CycleTime;