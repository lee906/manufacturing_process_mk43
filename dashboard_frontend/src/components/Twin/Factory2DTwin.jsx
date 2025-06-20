import React, { useRef, useEffect, useState } from 'react';

const Factory2DTwin = () => {
  // 캔버스와 컨테이너 DOM 참조
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  
  // 부모 컨테이너의 실제 크기를 저장하는 상태
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });

  // 부모 컨테이너 크기 변화를 감지하는 이펙트
  useEffect(() => {
    // 컨테이너 크기를 측정하고 상태를 업데이트하는 함수
    const updateSize = () => {
      if (containerRef.current) {
        // getBoundingClientRect()로 실제 렌더링된 크기 가져오기
        const rect = containerRef.current.getBoundingClientRect();
        const newWidth = Math.floor(rect.width);   // 소수점 제거로 안정성 확보
        const newHeight = Math.floor(rect.height);
        
        // 이전 크기와 비교해서 실제로 변경된 경우만 업데이트 (무한 리렌더링 방지)
        setContainerSize(prevSize => {
          // 5px 이상 차이날 때만 업데이트 (미세한 변화 무시)
          if (Math.abs(prevSize.width - newWidth) > 5 || Math.abs(prevSize.height - newHeight) > 5) {
            return { width: newWidth, height: newHeight };
          }
          return prevSize; // 변화가 없으면 기존 상태 유지
        });
      }
    };

    // 초기 크기 설정을 위한 지연 타이머 (DOM 렌더링 완료 후 실행)
    const timer = setTimeout(updateSize, 100);
    
    // ResizeObserver로 컨테이너 크기 변화 감지
    const resizeObserver = new ResizeObserver(entries => {
      // 디바운싱: 연속된 리사이즈 이벤트를 150ms 지연으로 처리
      clearTimeout(resizeObserver.timer);
      resizeObserver.timer = setTimeout(updateSize, 150);
    });

    // 컨테이너가 존재하면 ResizeObserver 등록
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // 클린업 함수: 타이머와 옵저버 정리
    return () => {
      clearTimeout(timer);
      clearTimeout(resizeObserver.timer);
      resizeObserver.disconnect();
    };
  }, []); // 빈 의존성 배열: 컴포넌트 마운트 시에만 실행

  // 캔버스 그리기를 담당하는 이펙트
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return; // 캔버스가 없으면 종료

    const ctx = canvas.getContext('2d'); // 2D 렌더링 컨텍스트 가져오기
    const dpr = window.devicePixelRatio || 1; // 디바이스 픽셀 비율 (고해상도 디스플레이 대응)

    // === 캔버스 설정 (고해상도 디스플레이 대응) ===
    canvas.width = containerSize.width * dpr;   // 실제 캔버스 크기를 devicePixelRatio만큼 확대
    canvas.height = containerSize.height * dpr;
    canvas.style.width = containerSize.width + 'px';   // CSS 표시 크기는 원래대로
    canvas.style.height = containerSize.height + 'px';
    ctx.scale(dpr, dpr); // 컨텍스트를 devicePixelRatio만큼 스케일 (선명도 향상)

    // === 배경 그리기 ===
    ctx.fillStyle = '#f8f9fa'; // 연한 회색 배경
    ctx.fillRect(0, 0, containerSize.width, containerSize.height);

    // === 콘텐츠 스케일링 및 중앙 정렬 계산 ===
    const contentW = 800, contentH = 800; // 정사각형 디자인 기준 크기 (800x800)
    // 컨테이너 크기에 맞춰 비례 스케일링 (가로/세로 중 작은 비율 선택)
    const scale = Math.min(containerSize.width / contentW, containerSize.height / contentH) * 1; // 0.9는 여백 확보
    // 중앙 정렬을 위한 오프셋 계산
    const offsetX = (containerSize.width - contentW * scale) / 2;
    const offsetY = (containerSize.height - contentH * scale) / 2;

    // 좌표계 변환 적용 (중앙 정렬 + 스케일링)
    ctx.save(); // 현재 변환 상태 저장
    ctx.translate(offsetX, offsetY); // 중앙 정렬을 위한 이동
    ctx.scale(scale, scale); // 비례 스케일링

    // === 데이터 정의 (800x800 정사각형, 동일 간격) ===
    const margin = 100; // 여백
    const lineSpacing = 200; // 라인 간격
    
    // 각 라인의 정보 (Y좌표, 라벨, 방향: 1=좌→우, -1=우→좌)
    const lines = [
      { y: margin + lineSpacing * 0, label: 'A라인 (트림)', dir: 1 },     // Y=100
      { y: margin + lineSpacing * 1, label: 'B라인 (샤시)', dir: -1 },    // Y=250
      { y: margin + lineSpacing * 2, label: 'C라인 (파이널)', dir: 1 },   // Y=400
      { y: margin + lineSpacing * 3, label: 'D라인 (검차)', dir: -1 }     // Y=550
    ];

    // 각 라인별 공정 정보 (2차원 배열)
    const processes = [
      // A라인: 좌→우 순서
      [{ name: '도어탈거', x: 150 }, { name: '와이어링', x: 250 }, { name: '헤드라이너', x: 400 }, { name: '크래쉬패드', x: 600 }],
      // B라인: 우→좌 순서 (역순)
      [{ name: '연료탱크', x: 600 }, { name: '샤시메리지', x: 400 }, { name: '머플러', x: 250 }],
      // C라인: 좌→우 순서
      [{ name: 'FEM', x: 150 }, { name: '범퍼', x: 250 }, { name: '글라스', x: 350 }, { name: '시트', x: 500 }, { name: '타이어', x: 650 }],
      // D라인: 우→좌 순서 (역순)
      [{ name: '헤드램프', x: 650 }, { name: '휠 얼라이언트', x: 500 }, { name: '수밀검사', x: 350 }]
    ];

    // === 컨베이어 벨트 그리기 ===
    ctx.strokeStyle = '#666'; // 진한 회색
    ctx.lineWidth = 90; // 두꺼운 선
    
    lines.forEach((line, i) => {
      // 각 라인의 수평 컨베이어 벨트 (동일한 시작점과 끝점)
      ctx.beginPath();
      ctx.moveTo(margin, line.y);        // 시작점 (X=100)
      ctx.lineTo(800 - margin, line.y);  // 끝점 (X=700)
      ctx.stroke();

      // 라인 간 연결 수직선 (마지막 라인은 제외)
      if (i < lines.length - 1) {
        const nextY = lines[i + 1].y; // 다음 라인의 Y좌표
        const x = line.dir === 1 ? (800 - margin) : margin; // 방향에 따라 연결점 결정 (우측 또는 좌측)
        ctx.beginPath();
        ctx.moveTo(x, line.y);    // 현재 라인에서
        ctx.lineTo(x, nextY);     // 다음 라인으로
        ctx.stroke();
      }
    });

    

    // === 공정 박스 그리기 ===
    processes.forEach((lineProcesses, lineIndex) => {
      const y = lines[lineIndex].y; // 해당 라인의 Y좌표
      lineProcesses.forEach(process => {
        // 공정 박스 (라인 위쪽에 배치)
        ctx.fillStyle = '#e3f2fd'; // 연한 파랑 배경
        ctx.strokeStyle = '#1976d2'; // 진한 파랑 테두리
        ctx.lineWidth = 1;
        ctx.fillRect(process.x - 40, y - 70, 80, 150); // 중앙 정렬된 박스
        ctx.strokeRect(process.x - 40, y - 70, 80, 150); // 테두리

        // 공정명 텍스트
        ctx.fillStyle = '#333'; // 진한 회색
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(process.name, process.x, y - 45); // 박스 중앙에 텍스트

        // 공정에서 컨베이어로 연결하는 점선
        ctx.strokeStyle = '#bbb'; // 연한 회색
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]); // 점선 스타일
        ctx.beginPath();
        ctx.moveTo(process.x, y - 25); // 박스 하단에서
        ctx.lineTo(process.x, y);      // 컨베이어까지
        ctx.stroke();
        ctx.setLineDash([]); // 점선 스타일 초기화
      });
    });

    // === 라인 라벨 그리기 ===
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'left';
    lines.forEach(line => {
      ctx.fillText(line.label, 20, line.y - 5); // 각 라인 왼쪽에 라벨 표시
    });

    // === 화살표 그리기 함수 ===
    const drawArrow = (x, y, angle) => {
      ctx.save(); // 현재 변환 상태 저장
      ctx.translate(x, y); // 화살표 위치로 이동
      ctx.rotate(angle); // 화살표 방향으로 회전
      ctx.fillStyle = '#2196F3'; // 파란색
      ctx.beginPath();
      // 삼각형 화살표 그리기
      ctx.moveTo(0, 0);     // 화살표 끝점
      ctx.lineTo(-12, -6);  // 왼쪽 모서리
      ctx.lineTo(-12, 6);   // 오른쪽 모서리
      ctx.closePath();
      ctx.fill();
      ctx.restore(); // 변환 상태 복원
    };

    // === 방향 화살표들 그리기 ===
    lines.forEach((line, i) => {
      const arrowY = line.y - 15; // 컨베이어 위쪽에 화살표 배치
      
      if (line.dir === 1) { 
        // 좌→우 방향 화살표들
        for (let x = margin + 50; x <= 800 - margin - 50; x += 100) {
          drawArrow(x, arrowY, 0); // 0도 (우향)
        }
      } else { 
        // 우→좌 방향 화살표들
        for (let x = 800 - margin - 50; x >= margin + 50; x -= 100) {
          drawArrow(x, arrowY, Math.PI); // 180도 (좌향)
        }
      }

      // 라인 간 연결 화살표 (마지막 라인 제외)
      if (i < lines.length - 1) {
        const x = line.dir === 1 ? (800 - margin + 15) : (margin - 15); // 연결 위치
        const nextY = lines[i + 1].y;
        drawArrow(x, line.y + (nextY - line.y) / 2, Math.PI / 2); // 90도 (하향)
      }
    });

    ctx.restore(); // 좌표계 변환 복원
  }, [containerSize]); // containerSize가 변경될 때마다 다시 그리기

  return (
    <div 
      ref={containerRef} // 크기 감지를 위한 ref
      style={{ 
        width: '100%',  // 부모 요소의 전체 너비 사용
        height: '100%', // 부모 요소의 전체 높이 사용
        display: 'flex', // Flexbox 레이아웃
        justifyContent: 'center', // 수평 중앙 정렬
        alignItems: 'center',     // 수직 중앙 정렬
        padding: '10px' // 여백 (선택적)
      }}
    >
      <canvas
        ref={canvasRef} // 그리기를 위한 ref
        style={{
          display: 'block', // 인라인 요소 기본 여백 제거
          maxWidth: '100%',  // 부모를 넘지 않는 최대 너비
          maxHeight: '100%', // 부모를 넘지 않는 최대 높이
          // 고해상도 디스플레이에서 선명도 향상을 위한 CSS 속성들
          imageRendering: '-webkit-optimize-contrast',
          WebkitImageRendering: '-webkit-optimize-contrast',
          msInterpolationMode: 'nearest-neighbor' // IE/Edge 호환성
        }}
      />
    </div>
  );
};

export default Factory2DTwin;