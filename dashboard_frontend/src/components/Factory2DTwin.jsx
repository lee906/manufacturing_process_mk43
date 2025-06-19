import React, { useRef, useEffect, useState } from 'react';

const Factory2DTwin = () => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 800 });

  // 부모 컨테이너 크기 감지
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setContainerSize({
          width: rect.width,
          height: rect.height
        });
      }
    };

    const resizeObserver = new ResizeObserver(updateSize);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    updateSize(); // 초기 크기 설정

    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // devicePixelRatio를 적용해서 선명하게 만들기
    const dpr = window.devicePixelRatio || 1;
    
    // 캔버스 실제 크기를 devicePixelRatio만큼 확대
    canvas.width = containerSize.width * dpr;
    canvas.height = containerSize.height * dpr;
    
    // CSS 표시 크기는 원래대로
    canvas.style.width = containerSize.width + 'px';
    canvas.style.height = containerSize.height + 'px';
    
    // 컨텍스트를 devicePixelRatio만큼 스케일
    ctx.scale(dpr, dpr);
    
    // 배경
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, containerSize.width, containerSize.height);
    
    // 기준 크기 800x800에서 현재 컨테이너 크기로 스케일링
    const scaleX = containerSize.width / 800;
    const scaleY = containerSize.height / 800;
    const scale = Math.min(scaleX, scaleY); // 비율 유지
    
    // 중앙 정렬을 위한 오프셋
    const offsetX = (containerSize.width - 800 * scale) / 2;
    const offsetY = (containerSize.height - 800 * scale) / 2;
    
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);
    
    // 컨베이어 벨트 그리기 (더 두껍게, 동일한 간격)
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 12;
    
    // A라인 (상단) - 좌에서 우로
    ctx.beginPath();
    ctx.moveTo(100, 150);
    ctx.lineTo(700, 150);
    ctx.stroke();
    
    // A→B 연결 (우측 하향)
    ctx.beginPath();
    ctx.moveTo(700, 150);
    ctx.lineTo(700, 250);
    ctx.stroke();
    
    // B라인 (중상) - 우에서 좌로
    ctx.beginPath();
    ctx.moveTo(700, 250);
    ctx.lineTo(100, 250);
    ctx.stroke();
    
    // B→C 연결 (좌측 하향)
    ctx.beginPath();
    ctx.moveTo(100, 250);
    ctx.lineTo(100, 350);
    ctx.stroke();
    
    // C라인 (중하) - 좌에서 우로
    ctx.beginPath();
    ctx.moveTo(100, 350);
    ctx.lineTo(700, 350);
    ctx.stroke();
    
    // C→D 연결 (우측 하향)
    ctx.beginPath();
    ctx.moveTo(700, 350);
    ctx.lineTo(700, 450);
    ctx.stroke();
    
    // D라인 (하단) - 우에서 좌로
    ctx.beginPath();
    ctx.moveTo(700, 450);
    ctx.lineTo(100, 450);
    ctx.stroke();
    
    // 노드 그리기 (동일한 간격으로)
    const nodes = [
      // A라인 노드들
      {x: 100, y: 150}, {x: 200, y: 150}, {x: 300, y: 150}, {x: 400, y: 150}, {x: 500, y: 150}, {x: 600, y: 150}, {x: 700, y: 150},
      // B라인 노드들  
      {x: 700, y: 250}, {x: 600, y: 250}, {x: 500, y: 250}, {x: 400, y: 250}, {x: 300, y: 250}, {x: 200, y: 250}, {x: 100, y: 250},
      // C라인 노드들
      {x: 100, y: 350}, {x: 200, y: 350}, {x: 300, y: 350}, {x: 400, y: 350}, {x: 500, y: 350}, {x: 600, y: 350}, {x: 700, y: 350},
      // D라인 노드들
      {x: 700, y: 450}, {x: 600, y: 450}, {x: 500, y: 450}, {x: 400, y: 450}, {x: 300, y: 450}, {x: 200, y: 450}, {x: 100, y: 450}
    ];
    
    nodes.forEach(node => {
      ctx.beginPath();
      ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI);
      ctx.fillStyle = '#4CAF50';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 3;
      ctx.stroke();
    });
    
    // 공정 박스들 (동일한 간격으로 재배치)
    const processes = [
      // A라인 (트림) - 상단
      {name: '도어탈거', x: 130, y: 90},
      {name: '와이어링', x: 230, y: 90},
      {name: '헤드라이너', x: 330, y: 90},
      {name: '크래쉬패드', x: 530, y: 90},
      
      // B라인 (샤시) - 중상단 (역순)
      {name: '머플러', x: 230, y: 190},
      {name: '샤시메리지', x: 330, y: 190},
      {name: '연료탱크', x: 530, y: 190},
      
      // C라인 (파이널) - 중하단
      {name: 'FEM', x: 130, y: 290},
      {name: '범퍼', x: 230, y: 290},
      {name: '글라스', x: 330, y: 290},
      {name: '시트', x: 430, y: 290},
      {name: '타이어', x: 630, y: 290},
      
      // D라인 (검차) - 하단 (역순)
      {name: '수밀검사', x: 330, y: 390},
      {name: '휠 얼라이언트', x: 430, y: 390},
      {name: '헤드램프', x: 630, y: 390}
    ];
    
    processes.forEach(process => {
      // 박스 그리기 (더 크게)
      ctx.fillStyle = '#e3f2fd';
      ctx.strokeStyle = '#1976d2';
      ctx.lineWidth = 2;
      ctx.fillRect(process.x, process.y, 80, 45);
      ctx.strokeRect(process.x, process.y, 80, 45);
      
      // 텍스트 (더 크게)
      ctx.fillStyle = '#333';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(process.name, process.x + 40, process.y + 28);
      
      // 연결선 (동일한 간격)
      let lineY;
      if (process.y === 90) lineY = 150; // A라인
      else if (process.y === 190) lineY = 250; // B라인
      else if (process.y === 290) lineY = 350; // C라인
      else lineY = 450; // D라인
      
      ctx.strokeStyle = '#bbb';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(process.x + 40, process.y + 45);
      ctx.lineTo(process.x + 40, lineY);
      ctx.stroke();
      ctx.setLineDash([]);
    });
    
    // 라인 라벨 (동일한 간격)
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('A라인 (트림)', 20, 145);
    ctx.fillText('B라인 (샤시)', 20, 245);
    ctx.fillText('C라인 (파이널)', 20, 345);
    ctx.fillText('D라인 (검차)', 20, 445);
    
    // 화살표 함수 (더 크게)
    const drawArrow = (x, y, angle) => {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.fillStyle = '#2196F3';
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(-12, -6);
      ctx.lineTo(-12, 6);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    };
    
    // A라인 화살표들 (→)
    drawArrow(150, 140, 0);
    drawArrow(250, 140, 0);
    drawArrow(350, 140, 0);
    drawArrow(450, 140, 0);
    drawArrow(550, 140, 0);
    drawArrow(650, 140, 0);
    
    // A→B 연결 화살표 (↓)
    drawArrow(710, 200, Math.PI/2);
    
    // B라인 화살표들 (←)
    drawArrow(650, 240, Math.PI);
    drawArrow(550, 240, Math.PI);
    drawArrow(450, 240, Math.PI);
    drawArrow(350, 240, Math.PI);
    drawArrow(250, 240, Math.PI);
    drawArrow(150, 240, Math.PI);
    
    // B→C 연결 화살표 (↓)
    drawArrow(90, 300, Math.PI/2);
    
    // C라인 화살표들 (→)
    drawArrow(150, 340, 0);
    drawArrow(250, 340, 0);
    drawArrow(350, 340, 0);
    drawArrow(450, 340, 0);
    drawArrow(550, 340, 0);
    drawArrow(650, 340, 0);
    
    // C→D 연결 화살표 (↓)
    drawArrow(710, 400, Math.PI/2);
    
    // D라인 화살표들 (←)
    drawArrow(650, 440, Math.PI);
    drawArrow(550, 440, Math.PI);
    drawArrow(450, 440, Math.PI);
    drawArrow(350, 440, Math.PI);
    drawArrow(250, 440, Math.PI);
    drawArrow(150, 440, Math.PI);
    
    // 시작/완료 표시
    ctx.fillStyle = '#4CAF50';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('시작', 100, 130);
    
    ctx.fillStyle = '#2196F3';
    ctx.fillText('완료', 100, 470);
    
    ctx.restore();
    
  }, [containerSize]);

  return (
    <div 
      ref={containerRef}
      style={{ 
        width: '100%', 
        height: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '10px'
      }}
    >
      <canvas
        ref={canvasRef}
        style={{ 
          display: 'block',
          maxWidth: '100%',
          maxHeight: '100%',
          imageRendering: '-webkit-optimize-contrast',
          WebkitImageRendering: '-webkit-optimize-contrast',
          msInterpolationMode: 'nearest-neighbor'
        }}
      />
    </div>
  );
};

export default Factory2DTwin;