import React, { useEffect, useRef } from 'react';

const Factory2D = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 수직 컨베이어 벨트
    for (let x = 130; x <= 1330; x += 400) {
      ctx.fillStyle = 'gray';
      ctx.fillRect(x, 100, 40, 700);
    }

    // 수평 컨베이어 벨트
    for (let i = 0; i < 3; i++) {
      ctx.fillStyle = 'gray';
      ctx.fillRect(200 + (i * 400), i % 2 === 0 ? 30 : 830, 300, 40);
    }
    
    // 상단과 하단의 녹색 사각형들
    for (let x = 100; x <= 1300; x += 400) {
      ctx.fillStyle = 'green';
      ctx.fillRect(x, 0, 100, 100);    // 상단 사각형
      ctx.fillRect(x, 800, 100, 100);  // 하단 사각형
    }
  }, []);

  return (
    <div className="row g-3">
      <div className="col-sm-6 col-lg-4">
        <div className="card">
          <div className="card-body" style={{ height: "50rem" }}>
          </div>
        </div>
      </div>
      
      <div className="col-sm-6 col-lg-8">
        <div className="card">
          <div className="card-body" style={{ height: "50rem" }}>
            <canvas
              ref={canvasRef}
              width="1500"
              height="900"
              style={{ 
                width: '100%',
                height: '100%',
                objectFit: 'contain'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Factory2D;