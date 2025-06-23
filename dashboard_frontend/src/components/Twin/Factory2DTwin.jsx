import React, { useRef, useEffect, useState } from 'react';
import ClickRobot from './ClickRobot'; // ClickRobot 컴포넌트 import

const Factory2DTwin = () => {
  // ===== DOM 참조 및 상태 관리 =====
  const canvasRef = useRef(null);      // 캔버스 요소 참조
  const containerRef = useRef(null);   // 컨테이너 요소 참조 (크기 감지용)
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 }); // 컨테이너 실제 크기
  
  // ===== 로봇 선택 팝오버 상태 관리 =====
  const [popoverState, setPopoverState] = useState({
    isOpen: false,
    selectedProcess: '',
    selectedRobot: null,
    position: { x: 0, y: 0 }
  });

  // ===== 스케일링 정보를 저장할 ref (클릭 좌표 변환용) =====
  const scaleInfoRef = useRef({ scale: 1, offsetX: 0, offsetY: 0 });

  // ===== 컨테이너 크기 변화 감지 및 반응형 처리 =====
  useEffect(() => {
    // 컨테이너 크기를 측정하고 상태 업데이트하는 함수
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const newWidth = Math.floor(rect.width);   // 정수로 변환 (안정성)
        const newHeight = Math.floor(rect.height);
        
        // 기존 크기와 비교하여 실제 변화가 있을 때만 업데이트 (무한 리렌더링 방지)
        setContainerSize(prevSize => {
          if (Math.abs(prevSize.width - newWidth) > 5 || Math.abs(prevSize.height - newHeight) > 5) {
            return { width: newWidth, height: newHeight };
          }
          return prevSize; // 변화가 미미하면 기존 상태 유지
        });
      }
    };

    // 초기 크기 설정 (DOM 렌더링 완료 후 실행)
    const timer = setTimeout(updateSize, 100);
    
    // ResizeObserver로 컨테이너 크기 변화 실시간 감지
    const resizeObserver = new ResizeObserver(entries => {
      clearTimeout(resizeObserver.timer);
      // 디바운싱: 연속된 리사이즈 이벤트를 150ms 지연으로 처리
      resizeObserver.timer = setTimeout(updateSize, 150);
    });

    // 컨테이너 관찰 시작
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // 클린업: 타이머와 옵저버 정리
    return () => {
      clearTimeout(timer);
      clearTimeout(resizeObserver.timer);
      resizeObserver.disconnect();
    };
  }, []); // 마운트 시에만 실행

  // ===== 조립 라인 데이터 정의 (라인별 동일한 높이 적용) =====
  const beltWidth = 60;      // 일반 라인 벨트 너비 (A, B라인)
  const beltWidthWide = 40;  // 병렬 라인 벨트 너비 (C, D라인 - 3개씩)
  
  // 라인별 공통 높이 정의
  const singleLineBoxHeight = 120;  // A, B라인 공통 박스 높이
  const multiLineBoxHeight = 180;   // C, D라인 공통 박스 높이
  
  const lines = [
    { 
      name: 'A',             // 라인 이름 (간소화)
      y: 120,                // Y 좌표 위치 (더 간격 벌림)
      dir: 1,                // 방향 (1: 좌→우, -1: 우→좌)
      width: beltWidth,      // 벨트 너비
      lanes: 1,              // 레인 수 (1: 단일, 3: 병렬)
      processes: [           // 각 라인의 공정 리스트 (너비만 다르고 높이는 동일)
        { name: '도어탈거', x: 150, width: 120, height: singleLineBoxHeight },
        { name: '와이어링', x: 300, width: 120, height: singleLineBoxHeight },
        { name: '헤드라이너', x: 450, width: 120, height: singleLineBoxHeight },
        { name: '크래쉬패드', x: 750, width: 350, height: singleLineBoxHeight }
      ]
    },
    { 
      name: 'B',             // 라인 이름 (간소화)
      y: 320, // Y 좌표 위치 (더 간격 벌림)
      dir: -1,               // 우→좌 방향
      width: beltWidth,
      lanes: 1,
      processes: [
        { name: '연료탱크', x: 850, width: 100, height: singleLineBoxHeight },
        { name: '샤시메리지', x: 500, width: 500, height: singleLineBoxHeight },
        { name: '머플러', x: 150, width: 100, height: singleLineBoxHeight }
      ]
    },
    { 
      name: 'C',             // 라인 이름 (간소화)
      y: 520, // Y 좌표 위치 (더 간격 벌림)
      dir: 1,                // 좌→우 방향
      width: beltWidthWide,  // 병렬 라인용 너비
      lanes: 3,              // 3개 병렬 레인
      processes: [
        { name: 'FEM', x: 150, width: 120, height: multiLineBoxHeight },
        { name: '범퍼', x: 300, width: 120, height: multiLineBoxHeight },
        { name: '글라스', x: 450, width: 120, height: multiLineBoxHeight },
        { name: '시트', x: 600, width: 120, height: multiLineBoxHeight },
        { name: '타이어', x: 750, width: 120, height: multiLineBoxHeight }
      ]
    },
    { 
      name: 'D',             // 라인 이름 (간소화)
      y: 720, // Y 좌표 위치 (더 간격 벌림)
      dir: -1,               // 우→좌 방향
      width: beltWidthWide,
      lanes: 3,              // 3개 병렬 레인
      processes: [
        { name: '수밀검사', x: 320, width: 450, height: multiLineBoxHeight },
        { name: '헤드램프', x: 650, width: 120, height: multiLineBoxHeight },
        { name: '휠 얼라이언트', x: 800, width: 120, height: multiLineBoxHeight }
      ]
    }
  ];

  // ===== 캔버스 클릭 이벤트 핸들러 =====
  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clientX = event.clientX - rect.left;
    const clientY = event.clientY - rect.top;

    // 클릭 좌표를 캔버스 좌표계로 변환
    const { scale, offsetX, offsetY } = scaleInfoRef.current;
    const canvasX = (clientX - offsetX) / scale;
    const canvasY = (clientY - offsetY) / scale;

    // 각 공정 박스의 텍스트 영역에 대해 클릭 여부 확인
    for (const line of lines) {
      let commonBoxY;
      const commonBoxHeight = line.processes[0].height;
      
      if (line.lanes === 1) {
        commonBoxY = line.y - commonBoxHeight/2;
      } else {
        const totalBeltHeight = line.width * 3;
        commonBoxY = line.y - totalBeltHeight/2 - (commonBoxHeight - totalBeltHeight)/2;
      }
      
      for (const process of line.processes) {
        const boxLeft = process.x - process.width/2;
        const boxRight = process.x + process.width/2;
        
        // 공정명 텍스트 영역 정의 (박스 상단 부분)
        const textAreaTop = commonBoxY;
        const textAreaBottom = commonBoxY + 30; // 텍스트가 있는 상단 30px 영역만
        
        // 클릭 지점이 텍스트 영역 내부에 있는지 확인
        if (canvasX >= boxLeft && canvasX <= boxRight && 
            canvasY >= textAreaTop && canvasY <= textAreaBottom) {
          
          // 팝오버 위치를 브라우저 좌표계로 정확히 계산
          // 공정 박스의 상단 중앙 위치를 화면 좌표로 변환
          const boxCenterX = process.x; // 캔버스 좌표계에서 박스 중앙 X
          const boxTopY = textAreaTop; // 캔버스 좌표계에서 텍스트 영역 상단 Y
          
          // 캔버스 좌표를 브라우저 화면 좌표로 변환
          const popoverX = rect.left + offsetX + (boxCenterX * scale);
          const popoverY = rect.top + offsetY + (boxTopY * scale);
          
          // 로봇 선택 팝오버 열기
          setPopoverState({
            isOpen: true,
            selectedProcess: process.name,
            selectedRobot: null,
            position: { x: popoverX, y: popoverY }
          });
          return; // 첫 번째 매치되는 박스에서 중단
        }
      }
    }
    
    // 빈 곳을 클릭했을 때 팝오버 닫기
    setPopoverState(prev => ({ ...prev, isOpen: false }));
  };

  // ===== 마우스 이동 이벤트 핸들러 (커서 변경용) =====
  const handleMouseMove = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clientX = event.clientX - rect.left;
    const clientY = event.clientY - rect.top;

    // 클릭 좌표를 캔버스 좌표계로 변환
    const { scale, offsetX, offsetY } = scaleInfoRef.current;
    const canvasX = (clientX - offsetX) / scale;
    const canvasY = (clientY - offsetY) / scale;

    let isOverClickableArea = false;

    // 각 공정 박스의 텍스트 영역에 대해 마우스 위치 확인
    for (const line of lines) {
      let commonBoxY;
      const commonBoxHeight = line.processes[0].height;
      
      if (line.lanes === 1) {
        commonBoxY = line.y - commonBoxHeight/2;
      } else {
        const totalBeltHeight = line.width * 3;
        commonBoxY = line.y - totalBeltHeight/2 - (commonBoxHeight - totalBeltHeight)/2;
      }
      
      for (const process of line.processes) {
        const boxLeft = process.x - process.width/2;
        const boxRight = process.x + process.width/2;
        
        // 공정명 텍스트 영역 정의 (박스 상단 부분)
        const textAreaTop = commonBoxY;
        const textAreaBottom = commonBoxY + 30; // 텍스트가 있는 상단 30px 영역만
        
        // 마우스가 텍스트 영역 내부에 있는지 확인
        if (canvasX >= boxLeft && canvasX <= boxRight && 
            canvasY >= textAreaTop && canvasY <= textAreaBottom) {
          isOverClickableArea = true;
          break;
        }
      }
      if (isOverClickableArea) break;
    }

    // 커서 스타일 변경
    canvas.style.cursor = isOverClickableArea ? 'pointer' : 'default';
  };
  const handleRobotSelect = (robot) => {
    setPopoverState(prev => ({
      ...prev,
      selectedRobot: robot
    }));
    
    // 선택된 로봇 정보를 콘솔에 출력 (실제 사용시에는 상태 관리나 API 호출 등으로 처리)
    console.log(`선택된 로봇:`, {
      process: popoverState.selectedProcess,
      robot: robot
    });
    
    // 여기서 추가 로직 수행 가능 (예: 로봇 상세 정보 표시, 제어 패널 열기 등)
  };

  // ===== 팝오버 닫기 핸들러 =====
  const handleClosePopover = () => {
    setPopoverState({
      isOpen: false,
      selectedProcess: '',
      selectedRobot: null,
      position: { x: 0, y: 0 }
    });
  };

  // ===== 화면 클릭시 팝오버 닫기 이벤트 =====
  useEffect(() => {
    const handleClickOutside = (event) => {
      // 팝오버가 열려있고, 클릭한 곳이 캔버스가 아닐 때만 닫기
      if (popoverState.isOpen && !canvasRef.current?.contains(event.target)) {
        handleClosePopover();
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [popoverState.isOpen]);

  // ===== 캔버스 그리기 메인 로직 =====
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return; // 캔버스가 없으면 종료

    const ctx = canvas.getContext('2d'); // 2D 렌더링 컨텍스트
    const dpr = window.devicePixelRatio || 1; // 고해상도 디스플레이 대응

    // === 캔버스 고해상도 설정 ===
    canvas.width = containerSize.width * dpr;   // 실제 캔버스 해상도
    canvas.height = containerSize.height * dpr;
    canvas.style.width = containerSize.width + 'px';   // CSS 표시 크기
    canvas.style.height = containerSize.height + 'px';
    ctx.scale(dpr, dpr); // 컨텍스트 스케일 조정 (선명도 향상)

    // === 콘텐츠 스케일링 및 중앙 정렬 설정 ===
    const contentW = 1000, contentH = 800; // 기준 콘텐츠 크기
    // 컨테이너에 맞춰 비례 스케일링 (가로/세로 중 작은 비율 선택, 5% 여백)
    const scale = Math.min(containerSize.width / contentW, containerSize.height / contentH) * 0.95;
    // 중앙 정렬을 위한 오프셋 계산
    const offsetX = (containerSize.width - contentW * scale) / 2;
    const offsetY = (containerSize.height - contentH * scale) / 2;

    // 스케일링 정보 저장 (클릭 이벤트에서 사용)
    scaleInfoRef.current = { scale, offsetX, offsetY };

    // 좌표계 변환 적용
    ctx.save(); // 현재 변환 상태 저장
    ctx.translate(offsetX, offsetY); // 중앙 정렬 이동
    ctx.scale(scale, scale); // 비례 스케일링

    // ===== 통합된 컨베이어 시스템 그리기 (연결부 폭 통일) =====
    ctx.fillStyle = '#444'; // 컨베이어 색상 (진한 회색)
    
    // Path2D를 사용하여 전체 컨베이어를 하나의 도형으로 그리기
    const conveyorPath = new Path2D();
    
    // 전체 X축 범위: 0부터 1000까지 (화살표 포함)
    
    // A라인 전체 영역 (화살표부터 끝까지)
    conveyorPath.rect(0, 90, 1000, 60);   // X=0~1000, Y=90~150 (60px 높이)
    
    // A→B 수직 연결 (A라인과 같은 폭 60px)
    conveyorPath.rect(940, 150, 60, 140); // X=940~1000, Y=150~290 (60px 폭)
    
    // B라인 전체 영역 (끝에서 끝까지)  
    conveyorPath.rect(0, 290, 1000, 60);  // X=0~1000, Y=290~350 (60px 높이)
    
    // B→C 수직 연결 (B라인과 같은 폭 60px)
    conveyorPath.rect(0, 350, 60, 110);   // X=0~60, Y=350~460 (60px 폭)
    
    // C라인 전체 영역 (끝에서 끝까지)
    conveyorPath.rect(0, 460, 1000, 120); // X=0~1000, Y=460~580 (120px 높이)
    
    // C→D 수직 연결 (D라인과 같은 폭 120px)  
    conveyorPath.rect(880, 580, 120, 80); // X=880~1000, Y=580~660 (120px 폭)
    
    // D라인 전체 영역 (끝에서 끝까지)
    conveyorPath.rect(0, 660, 1000, 120); // X=0~1000, Y=660~780 (120px 높이)
    
    // 전체 경로를 한 번에 채우기 (겹침 없음)
    ctx.fill(conveyorPath);

    // ===== 공정 박스 그리기 (각 라인별로 동일한 Y축과 높이) =====
    lines.forEach(line => {
      // 각 라인별로 박스 Y좌표를 동일하게 계산 (높이가 모두 같으므로 간단해짐)
      let commonBoxY;
      const commonBoxHeight = line.processes[0].height; // 모든 박스가 같은 높이
      
      if (line.lanes === 1) {
        // 단일 라인: 컨베이어 중심에서 위아래로 확장
        commonBoxY = line.y - commonBoxHeight/2;
      } else {
        // 병렬 라인: 3개 레인을 모두 감싸도록 확장
        const totalBeltHeight = line.width * 3; // 3개 레인 전체 높이
        commonBoxY = line.y - totalBeltHeight/2 - (commonBoxHeight - totalBeltHeight)/2;
      }
      
      line.processes.forEach(process => {
        // 너비만 다르고 높이와 Y좌표는 모두 동일
        const boxWidth = process.width;   // 공정별 개별 너비
        const boxHeight = commonBoxHeight; // 라인별 공통 높이
        
        // 박스 테두리만 그리기 (채우기 없음)
        ctx.strokeStyle = '#1976d2'; // 진한 파란색 테두리
        ctx.lineWidth = 2;           // 테두리 두께
        ctx.strokeRect(process.x - boxWidth/2, commonBoxY, boxWidth, boxHeight);
        
        // 공정명 텍스트 그리기 (상단 배치)
        ctx.fillStyle = '#333';      // 텍스트 색상 (검은색)
        ctx.font = 'bold 16px Arial'; // 폰트 설정
        ctx.textAlign = 'center';    // 중앙 정렬
        ctx.fillText(process.name, process.x, commonBoxY + 25);
      });
    });

    // ===== 방향 화살표 그리기 함수 (큰 삼각형 화살표) =====
    const drawArrow = (x, y, angle, strokeColor = '#ffffff', lineWidth = 3) => {
      ctx.save();                // 현재 변환 상태 저장
      ctx.translate(x, y);       // 화살표 위치로 이동
      ctx.rotate(angle);         // 화살표 방향으로 회전
      ctx.strokeStyle = strokeColor; // 화살표 테두리 색상 (흰색)
      ctx.lineWidth = lineWidth;     // 테두리 두께
      ctx.beginPath();
      // 큰 삼각형 화살표 그리기 (컨베이어 크기에 맞게)
      ctx.moveTo(0, 0);          // 화살표 끝점
      ctx.lineTo(-25, -15);      // 왼쪽 모서리 (크기 크게 증가)
      ctx.lineTo(-25, 15);       // 오른쪽 모서리 (크기 크게 증가)
      ctx.closePath();
      ctx.stroke();              // 테두리만 그리기
      ctx.restore();             // 변환 상태 복원
    };

    // ===== 각 라인별 방향 화살표 그리기 (컨베이어 밖으로 이동) =====
    
    // A라인 화살표 (좌→우 방향, 컨베이어 밖)
    drawArrow(30, 120, 0); // X=30 (컨베이어 밖), Y=120 (A라인 중앙), 0도 (우향)

    // B라인 화살표 (우→좌 방향, 컨베이어 밖 - B,D 위치에 추가)
    drawArrow(970, 320, Math.PI); // X=970 (컨베이어 밖), Y=320 (B라인 중앙), 180도 (좌향)

    // C라인 화살표 (좌→우 방향, 컨베이어 밖)
    drawArrow(30, 520, 0); // X=30 (컨베이어 밖), Y=520 (C라인 중앙), 0도 (우향)

    // D라인 화살표 (우→좌 방향, 컨베이어 밖 - B,D 위치에 추가)
    drawArrow(970, 720, Math.PI); // X=970 (컨베이어 밖), Y=720 (D라인 중앙), 180도 (좌향)

    // ===== 컨베이어 벨트 내부에 라인 알파벳 표시 =====
    ctx.fillStyle = '#ffffff';      // 흰색 텍스트
    ctx.font = 'bold 20px Arial';   // 화살표와 비슷한 크기
    ctx.textAlign = 'center';       // 중앙 정렬
    
    // A라인 알파벳 (좌측에 표시)
    ctx.fillText('A', 80, 120 + 7); // X=80 (좌측), Y=120+7 (수직 중앙)
    
    // B라인 알파벳 (좌측에 표시 - A와 같은 X축)  
    ctx.fillText('B', 80, 320 + 7); // X=80 (좌측), Y=320+7 (수직 중앙)
    
    // C라인 알파벳 (좌측에 표시)
    ctx.fillText('C', 80, 520 + 7); // X=80 (좌측), Y=520+7 (수직 중앙)
    
    // D라인 알파벳 (좌측에 표시 - A,C와 같은 X축)
    ctx.fillText('D', 80, 720 + 7); // X=80 (좌측), Y=720+7 (수직 중앙)

    ctx.restore(); // 좌표계 변환 복원
  }, [containerSize]); // containerSize가 변경될 때마다 다시 그리기

  // ===== 컴포넌트 렌더링 =====
  return (
    <>
      <div 
        ref={containerRef} // 크기 감지를 위한 ref
        style={{ 
          width: '100%',           // 부모 요소의 전체 너비 사용
          height: '100%',          // 부모 요소의 전체 높이 사용
          display: 'flex',         // Flexbox 레이아웃
          justifyContent: 'center', // 수평 중앙 정렬
          alignItems: 'center',     // 수직 중앙 정렬
          padding: '10px'          // 여백
        }}
      >
        <canvas
          ref={canvasRef} // 그리기를 위한 ref
          onClick={handleCanvasClick} // 클릭 이벤트 핸들러 추가
          onMouseMove={handleMouseMove} // 마우스 이동 이벤트 핸들러 추가
          style={{
            display: 'block',        // 인라인 요소 기본 여백 제거
            maxWidth: '100%',        // 부모를 넘지 않는 최대 너비
            maxHeight: '100%',       // 부모를 넘지 않는 최대 높이
            // 고해상도 디스플레이에서 선명도 향상을 위한 CSS 속성들
            imageRendering: '-webkit-optimize-contrast',
            WebkitImageRendering: '-webkit-optimize-contrast',
            msInterpolationMode: 'nearest-neighbor' // IE/Edge 호환성
          }}
        />
      </div>
      
      {/* 로봇 선택 팝오버 */}
      <ClickRobot
        isOpen={popoverState.isOpen}
        processName={popoverState.selectedProcess}
        position={popoverState.position}
        onClose={handleClosePopover}
        onSelectRobot={handleRobotSelect}
      />
    </>
  );
};

export default Factory2DTwin;