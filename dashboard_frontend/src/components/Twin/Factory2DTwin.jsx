// Factory2DTwin.jsx - MQTT 실제 센서 데이터 + 자동차 제품명 + 실시간 이동

import React, { useRef, useEffect, useState } from 'react';
import ClickRobot from './ClickRobot';

const Factory2DTwin = () => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });
  const [popoverState, setPopoverState] = useState({
    isOpen: false,
    selectedProcess: '',
    selectedRobot: null,
    position: { x: 0, y: 0 }
  });
  const scaleInfoRef = useRef({ scale: 1, offsetX: 0, offsetY: 0 });

  // 🆕 실제 MQTT 데이터를 위한 상태들
  const [stationData, setStationData] = useState({});
  const [products, setProducts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // 라인 데이터 (컴포넌트 최상단으로 이동)
  const beltHeight = 60;
  const boxHeight = 120;
  
  const lines = [
    { 
      name: 'A',
      y: 150,
      dir: 1,
      processes: [
        { name: '도어탈거', x: 150, width: 120 },
        { name: '와이어링', x: 300, width: 120 },
        { name: '헤드라이너', x: 450, width: 120 },
        { name: '크래쉬패드', x: 750, width: 350 }
      ]
    },
    { 
      name: 'B',
      y: 350,
      dir: -1,
      processes: [
        { name: '연료탱크', x: 850, width: 100 },
        { name: '샤시메리지', x: 500, width: 500 },
        { name: '머플러', x: 150, width: 100 }
      ]
    },
    { 
      name: 'C',
      y: 550,
      dir: 1,
      processes: [
        { name: 'FEM', x: 150, width: 120 },
        { name: '글라스', x: 300, width: 120 },
        { name: '시트', x: 450, width: 120 },
        { name: '범퍼', x: 600, width: 120 },
        { name: '타이어', x: 750, width: 120 }
      ]
    },
    { 
      name: 'D',
      y: 750,
      dir: -1,
      processes: [
        { name: '수밀검사', x: 320, width: 450 },
        { name: '헤드램프', x: 650, width: 120 },
        { name: '휠 얼라이언트', x: 800, width: 120 }
      ]
    }
  ];

  // 🆕 실시간 애니메이션을 위한 상태
  const animationFrameRef = useRef(null);
  const lastUpdateTimeRef = useRef(Date.now());
  
  // 🆕 자동차 제품명 첫 글자 추출 함수
  const getVehicleInitial = (stationId) => {
    // 각 스테이션별로 다른 자동차 모델 할당 (순환)
    const stationIndex = parseInt(stationId.match(/\d+/)?.[0] || '0');
    const modelIndex = stationIndex % vehicleModels.length;
    const model = vehicleModels[modelIndex];
    return model.charAt(0).toUpperCase(); // 첫 글자 대문자
  };

  // 🆕 실제 MQTT 데이터 연결 + 디버깅
  useEffect(() => {
    // 즉시 첫 요청 실행
    const fetchData = async () => {
      try {
        console.log('🔍 API 요청 시도: http://localhost:8080/api/station/status/all');
        const response = await fetch('http://localhost:8080/api/station/status/all');
        
        if (response.ok) {
          const stations = await response.json();
          console.log('📊 받은 스테이션 데이터:', stations);
          console.log('📊 타임스탬프:', new Date().toISOString());
          updateStationData(stations);
          setIsConnected(true);
        } else {
          console.log('⚠️ Spring Boot API 응답 오류:', response.status);
          setIsConnected(false);
          // 🆕 연결 실패시 기존 데이터 클리어
          setStationData({});
          setProducts([]);
        }
      } catch (error) {
        console.log('❌ 백엔드 연결 실패:', error.message);
        setIsConnected(false);
        // 🆕 연결 실패시 기존 데이터 클리어
        setStationData({});
        setProducts([]);
      }
    };

    // 즉시 실행
    fetchData();
    
    // 3초마다 반복
    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);

  // 🆕 실시간 애니메이션 루프 (제거 - 실제 데이터만 사용)
  useEffect(() => {
    // 애니메이션 루프 완전 제거
    // 오직 API 데이터 변경시에만 렌더링
    console.log('🎨 애니메이션 루프 비활성화 - 실제 데이터만 사용');
  }, []);

  // 🆕 테스트용 가짜 데이터 생성 (API 연결 실패시)
  const generateTestData = () => {
    console.log('🧪 테스트 데이터 생성 중...');
    const testStations = [
      {
        stationId: 'A01_DOOR',
        progress: Math.random() * 100,
        currentOperation: '도어탈거_작업중',
        status: 'RUNNING',
        efficiency: 85 + Math.random() * 15,
        cycleTime: 180 + Math.random() * 30,
        productionCount: Math.floor(Math.random() * 50),
        timestamp: new Date().toISOString()
      },
      {
        stationId: 'A02_WIRE',
        progress: Math.random() * 100,
        currentOperation: '와이어링_진행중',
        status: 'RUNNING',
        efficiency: 80 + Math.random() * 20,
        cycleTime: 200 + Math.random() * 40,
        productionCount: Math.floor(Math.random() * 45),
        timestamp: new Date().toISOString()
      },
      {
        stationId: 'A03_HEAD',
        progress: Math.random() * 100,
        currentOperation: '헤드라이너_작업중',
        status: 'RUNNING',
        efficiency: 75 + Math.random() * 25,
        cycleTime: 160 + Math.random() * 20,
        productionCount: Math.floor(Math.random() * 40),
        timestamp: new Date().toISOString()
      },
      {
        stationId: 'B01_FUEL',
        progress: Math.random() * 100,
        currentOperation: '연료탱크_조립중',
        status: 'RUNNING',
        efficiency: 90 + Math.random() * 10,
        cycleTime: 150 + Math.random() * 25,
        productionCount: Math.floor(Math.random() * 55),
        timestamp: new Date().toISOString()
      },
      {
        stationId: 'C01_FEM',
        progress: Math.random() * 100,
        currentOperation: 'FEM_설치중',
        status: 'RUNNING',
        efficiency: 85 + Math.random() * 15,
        cycleTime: 170 + Math.random() * 30,
        productionCount: Math.floor(Math.random() * 48),
        timestamp: new Date().toISOString()
      }
    ];
    
    console.log('🧪 생성된 테스트 데이터:', testStations);
    updateStationData(testStations);
  };
  // 🆕 실제 스테이션 데이터 업데이트 (변화 감지 강화)
  const updateStationData = (stations) => {
    const timestamp = new Date().toISOString();
    console.log(`🔄 [${timestamp}] === 새로운 API 응답 수신 ===`);
    console.log('📦 받은 stations 데이터:', stations);
    
    if (!stations || !Array.isArray(stations)) {
      console.error('❌ 잘못된 데이터 형식:', stations);
      setStationData({});
      setProducts([]);
      return;
    }

    if (stations.length === 0) {
      console.warn('⚠️ 빈 배열 수신');
      setStationData({});
      setProducts([]);
      return;
    }

    const newStationData = {};
    
    stations.forEach((station, index) => {
      console.log(`\n📊 === 스테이션 ${index + 1}/${stations.length} 처리 ===`);
      console.log('🔍 원본 스테이션 데이터:', JSON.stringify(station, null, 2));
      
      const stationId = station.stationId || station.station_id || station.id || `STATION_${index}`;
      console.log(`🆔 스테이션 ID: ${stationId}`);
      
      // 🆕 이전 데이터와 비교
      const previousData = stationData[stationId];
      
      const currentData = {
        progress: station.progress || station.progressRate || 0,
        operation: station.currentOperation || station.operation || '대기',
        status: station.status || 'IDLE',
        efficiency: station.efficiency || 0,
        cycleTime: station.cycleTime || station.cycle_time || 0,
        productionCount: station.productionCount || station.production_count || 0,
        lastUpdate: station.timestamp || station.lastUpdate || timestamp,
        updateTime: Date.now()
      };
      
      // 🆕 변화 감지 및 로깅
      if (previousData) {
        console.log(`\n🔍 [${stationId}] 데이터 변화 감지:`);
        
        Object.keys(currentData).forEach(key => {
          if (key === 'updateTime' || key === 'lastUpdate') return; // 시간 필드 제외
          
          const oldValue = previousData[key];
          const newValue = currentData[key];
          
          if (oldValue !== newValue) {
            console.log(`  🔄 ${key}: ${oldValue} → ${newValue} *** 변화됨! ***`);
          } else {
            console.log(`  ⚪ ${key}: ${newValue} (변화없음)`);
          }
        });
      } else {
        console.log(`\n🆕 [${stationId}] 새로운 스테이션 데이터:`, currentData);
      }
      
      newStationData[stationId] = currentData;
    });
    
    console.log(`\n🎯 === 최종 처리 결과 ===`);
    console.log(`📋 처리된 스테이션 수: ${Object.keys(newStationData).length}`);
    console.log(`📋 스테이션 ID 목록:`, Object.keys(newStationData));
    
    setStationData(newStationData);
    updateProductPositions(newStationData);
  };

  // 🆕 제품 위치 업데이트 (디버깅 및 강제 업데이트)
  const updateProductPositions = (stationData) => {
    console.log('🚗 제품 위치 업데이트 시작:', stationData);
    
    const stationMapping = {
      // Line A - MQTT 토픽 기반
      'A01_DOOR': { line: 'A', processIndex: 0 },
      'A02_WIRE': { line: 'A', processIndex: 1 },
      'A03_HEAD': { line: 'A', processIndex: 2 },
      'A04_CRASH': { line: 'A', processIndex: 3 },
      // Line B
      'B01_FUEL': { line: 'B', processIndex: 0 },
      'B02_CHASSIS': { line: 'B', processIndex: 1 },
      'B03_MUFFLER': { line: 'B', processIndex: 2 },
      // Line C
      'C01_FEM': { line: 'C', processIndex: 0 },
      'C02_GLASS': { line: 'C', processIndex: 1 },
      'C03_SEAT': { line: 'C', processIndex: 2 },
      'C04_BUMPER': { line: 'C', processIndex: 3 },
      'C05_TIRE': { line: 'C', processIndex: 4 },
      // Line D
      'D01_WHEEL': { line: 'D', processIndex: 2 },
      'D02_LAMP': { line: 'D', processIndex: 1 },
      'D03_WATER': { line: 'D', processIndex: 0 }
    };

    const newProducts = [];

    Object.entries(stationData).forEach(([stationId, data]) => {
      console.log(`🔍 처리 중: ${stationId}`, data);
      
      const mapping = stationMapping[stationId];
      if (!mapping) {
        console.warn(`⚠️ 매핑되지 않은 스테이션: ${stationId}`);
        return;
      }

      const line = lines.find(l => l.name === mapping.line);
      if (!line || !line.processes[mapping.processIndex]) {
        console.warn(`⚠️ 라인을 찾을 수 없음: ${mapping.line}[${mapping.processIndex}]`);
        return;
      }

      const process = line.processes[mapping.processIndex];
      
      // 🆕 실제 진행률 사용 (시간 기반 변동 제거)
      const progressRatio = Math.max(0, Math.min(100, data.progress || 0)) / 100;
      let targetX;
      
      if (line.dir === 1) { // 우향
        targetX = process.x - (process.width / 2) + (process.width * progressRatio);
      } else { // 좌향
        targetX = process.x + (process.width / 2) - (process.width * progressRatio);
      }
      
      // 실제 상태에 따른 색상
      let color = '#4CAF50';
      if (data.status === 'ERROR' || data.status === 'FAULT') {
        color = '#f44336';
      } else if (data.status === 'IDLE' || data.status === 'STOPPED') {
        color = '#9E9E9E';
      } else if (data.status === 'WARNING') {
        color = '#FF9800';
      } else if (data.status === 'RUNNING') {
        if (data.progress < 30) color = '#FF9800';
        else if (data.progress < 70) color = '#2196F3';
        else color = '#4CAF50';
      }

      const product = {
        id: `product_${stationId}`,
        stationId: stationId,
        x: targetX, // 🆕 실제 API 데이터 기반 위치
        targetX: targetX,
        y: line.y,
        line: line.name,
        progress: data.progress || 0,
        status: data.status,
        operation: data.operation,
        cycleTime: data.cycleTime,
        productionCount: data.productionCount,
        vehicleInitial: getVehicleInitial(stationId),
        color: color,
        size: 14,
        lastUpdate: data.lastUpdate
      };

      console.log(`✅ 제품 생성: ${stationId}`, product);
      newProducts.push(product);
    });

    console.log('🎯 최종 제품 배열:', newProducts);
    setProducts(newProducts);
  };

  // 🆕 자동차 모델명 리스트 (데이터 제너레이터 기반)
  const vehicleModels = ['SEDAN_A', 'SUV_B', 'TRUCK_C'];
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const newWidth = Math.floor(rect.width);
        const newHeight = Math.floor(rect.height);
        
        setContainerSize(prevSize => {
          if (Math.abs(prevSize.width - newWidth) > 5 || Math.abs(prevSize.height - newHeight) > 5) {
            return { width: newWidth, height: newHeight };
          }
          return prevSize;
        });
      }
    };

    const timer = setTimeout(updateSize, 100);
    const resizeObserver = new ResizeObserver(entries => {
      clearTimeout(resizeObserver.timer);
      resizeObserver.timer = setTimeout(updateSize, 150);
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      clearTimeout(timer);
      clearTimeout(resizeObserver.timer);
      resizeObserver.disconnect();
    };
  }, []);

  // 컨테이너 크기 조정 (기존 코드 유지)

  // 제품 클릭 핸들러 (기존 코드 유지)
  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clientX = event.clientX - rect.left;
    const clientY = event.clientY - rect.top;

    const { scale, offsetX, offsetY } = scaleInfoRef.current;
    const canvasX = (clientX - offsetX) / scale;
    const canvasY = (clientY - offsetY) / scale;

    // 제품 클릭 확인 (우선순위)
    const clickedProduct = products.find(product => {
      const distance = Math.sqrt(
        Math.pow(canvasX - product.x, 2) + Math.pow(canvasY - product.y, 2)
      );
      return distance <= product.size + 5;
    });

    if (clickedProduct) {
      setSelectedProduct(clickedProduct);
      return;
    }

    // 기존 공정 박스 클릭 로직
    for (const line of lines) {
      const boxY = line.y - boxHeight/2;
      
      for (const process of line.processes) {
        const boxLeft = process.x - process.width/2;
        const boxRight = process.x + process.width/2;
        const textAreaTop = boxY;
        const textAreaBottom = boxY + 30;
        
        if (canvasX >= boxLeft && canvasX <= boxRight && 
            canvasY >= textAreaTop && canvasY <= textAreaBottom) {
          
          const boxCenterX = process.x;
          const boxTopY = textAreaTop;
          const popoverX = rect.left + offsetX + (boxCenterX * scale);
          const popoverY = rect.top + offsetY + (boxTopY * scale);
          
          setPopoverState({
            isOpen: true,
            selectedProcess: process.name,
            selectedRobot: null,
            position: { x: popoverX, y: popoverY }
          });
          return;
        }
      }
    }
    
    setPopoverState(prev => ({ ...prev, isOpen: false }));
    setSelectedProduct(null);
  };

  // 마우스 이동 핸들러 (기존 코드 유지)
  const handleMouseMove = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clientX = event.clientX - rect.left;
    const clientY = event.clientY - rect.top;

    const { scale, offsetX, offsetY } = scaleInfoRef.current;
    const canvasX = (clientX - offsetX) / scale;
    const canvasY = (clientY - offsetY) / scale;

    let isOverClickableArea = false;

    // 제품 위에 마우스가 있는지 확인
    const overProduct = products.some(product => {
      const distance = Math.sqrt(
        Math.pow(canvasX - product.x, 2) + Math.pow(canvasY - product.y, 2)
      );
      return distance <= product.size + 5;
    });

    if (overProduct) {
      isOverClickableArea = true;
    } else {
      // 기존 공정 박스 체크
      for (const line of lines) {
        const boxY = line.y - boxHeight/2;
        
        for (const process of line.processes) {
          const boxLeft = process.x - process.width/2;
          const boxRight = process.x + process.width/2;
          const textAreaTop = boxY;
          const textAreaBottom = boxY + 30;
          
          if (canvasX >= boxLeft && canvasX <= boxRight && 
              canvasY >= textAreaTop && canvasY <= textAreaBottom) {
            isOverClickableArea = true;
            break;
          }
        }
        if (isOverClickableArea) break;
      }
    }

    canvas.style.cursor = isOverClickableArea ? 'pointer' : 'default';
  };

  // 팝오버 핸들러들 (기존 코드 유지)
  const handleRobotSelect = (robot) => {
    setPopoverState(prev => ({
      ...prev,
      selectedRobot: robot
    }));
    
    console.log(`선택된 로봇:`, {
      process: popoverState.selectedProcess,
      robot: robot
    });
  };

  const handleClosePopover = () => {
    setPopoverState({
      isOpen: false,
      selectedProcess: '',
      selectedRobot: null,
      position: { x: 0, y: 0 }
    });
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverState.isOpen && !canvasRef.current?.contains(event.target)) {
        handleClosePopover();
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [popoverState.isOpen]);

  // 🆕 제품들 그리기 함수 (자동차 첫 글자 포함 + 디버깅)
  const drawProducts = (ctx) => {
    console.log(`🎨 제품 그리기 시작 - 총 ${products.length}개 제품`);
    
    if (products.length === 0) {
      console.warn('⚠️ 그릴 제품이 없습니다');
      return;
    }

    products.forEach((product, index) => {
      console.log(`🎨 제품 ${index} 그리기:`, product);
      
      try {
        // 제품 표시 (원형)
        ctx.fillStyle = product.color;
        ctx.beginPath();
        ctx.arc(product.x, product.y, product.size, 0, 2 * Math.PI);
        ctx.fill();

        // 테두리
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 2;
        ctx.stroke();

        // 🆕 자동차 모델 첫 글자 표시 (대문자)
        ctx.fillStyle = 'white';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(product.vehicleInitial, product.x, product.y);

        // 선택된 제품 강조
        if (selectedProduct && selectedProduct.id === product.id) {
          ctx.strokeStyle = '#ff0000';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(product.x, product.y, product.size + 3, 0, 2 * Math.PI);
          ctx.stroke();

          // 🆕 이동 방향 화살표 (진행률이 변하고 있을 때)
          if (product.targetX !== undefined && Math.abs(product.targetX - product.x) > 1) {
            const direction = product.targetX > product.x ? 1 : -1;
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(product.x + (direction * 20), product.y - 20);
            ctx.lineTo(product.x + (direction * 30), product.y - 20);
            ctx.lineTo(product.x + (direction * 25), product.y - 25);
            ctx.moveTo(product.x + (direction * 30), product.y - 20);
            ctx.lineTo(product.x + (direction * 25), product.y - 15);
            ctx.stroke();
          }
        }
        
        console.log(`✅ 제품 ${index} 그리기 완료: (${product.x}, ${product.y})`);
      } catch (error) {
        console.error(`❌ 제품 ${index} 그리기 오류:`, error, product);
      }
    });
    
    console.log(`🎨 제품 그리기 완료 - ${products.length}개 처리됨`);
  };

  // 캔버스 그리기 로직 (실시간 렌더링 강화)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.warn('⚠️ 캔버스가 없음');
      return;
    }

    console.log(`🎨 캔버스 렌더링 시작 - 제품 수: ${products.length}`);

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    canvas.width = containerSize.width * dpr;
    canvas.height = containerSize.height * dpr;
    canvas.style.width = containerSize.width + 'px';
    canvas.style.height = containerSize.height + 'px';
    ctx.scale(dpr, dpr);

    const contentW = 1000, contentH = 900;
    const scale = Math.min(containerSize.width / contentW, containerSize.height / contentH) * 0.95;
    const offsetX = (containerSize.width - contentW * scale) / 2;
    const offsetY = (containerSize.height - contentH * scale) / 2;

    scaleInfoRef.current = { scale, offsetX, offsetY };

    console.log(`🎨 캔버스 설정: ${containerSize.width}x${containerSize.height}, 스케일: ${scale.toFixed(3)}`);

    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    // 배경 클리어
    ctx.clearRect(0, 0, contentW, contentH);
    console.log('🧹 배경 클리어 완료');

    // 컨베이어 시스템 그리기
    ctx.fillStyle = '#444';
    const conveyorPath = new Path2D();
    conveyorPath.rect(0, 120, 1000, beltHeight);
    conveyorPath.rect(940, 180, 60, 140);
    conveyorPath.rect(0, 320, 1000, beltHeight);
    conveyorPath.rect(0, 380, 60, 140);
    conveyorPath.rect(0, 520, 1000, beltHeight);
    conveyorPath.rect(940, 580, 60, 140);
    conveyorPath.rect(0, 720, 1000, beltHeight);
    ctx.fill(conveyorPath);
    console.log('🏭 컨베이어 그리기 완료');

    // 라인 알파벳 표시
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('A', 80, 150 + 7);
    ctx.fillText('B', 80, 350 + 7);
    ctx.fillStyle = '#ffffff';
    ctx.fillText('C', 80, 550 + 7);
    ctx.fillText('D', 80, 750 + 7);

    // 방향 화살표 그리기
    const drawArrow = (x, y, angle, strokeColor = '#ffffff', lineWidth = 3) => {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(-25, -15);
      ctx.lineTo(-25, 15);
      ctx.closePath();
      ctx.stroke();
      ctx.restore();
    };

    drawArrow(30, 150, 0);
    drawArrow(970, 350, Math.PI);
    drawArrow(30, 550, 0);
    drawArrow(970, 750, Math.PI);

    // 🆕 제품들 먼저 그리기 (강화된 렌더링)
    console.log(`🚗 제품 렌더링 시작: ${products.length}개`);
    if (products.length > 0) {
      products.forEach((product, index) => {
        console.log(`🎨 제품 ${index} 렌더링:`, {
          id: product.id,
          x: product.x,
          y: product.y,
          color: product.color,
          size: product.size,
          vehicleInitial: product.vehicleInitial
        });
        
        try {
          // 🆕 제품 렌더링 강화
          // 배경 원 (더 크게)
          ctx.fillStyle = product.color;
          ctx.beginPath();
          ctx.arc(product.x, product.y, product.size + 2, 0, 2 * Math.PI);
          ctx.fill();

          // 메인 제품 원
          ctx.fillStyle = product.color;
          ctx.beginPath();
          ctx.arc(product.x, product.y, product.size, 0, 2 * Math.PI);
          ctx.fill();

          // 강한 테두리
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(product.x, product.y, product.size, 0, 2 * Math.PI);
          ctx.stroke();

          // 🆕 자동차 모델 첫 글자 (더 크고 굵게)
          ctx.fillStyle = 'white';
          ctx.font = 'bold 12px Arial';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1;
          ctx.strokeText(product.vehicleInitial, product.x, product.y);
          ctx.fillText(product.vehicleInitial, product.x, product.y);

          // 🆕 진행률 표시 (제품 위에)
          ctx.fillStyle = '#000000';
          ctx.font = 'bold 8px Arial';
          ctx.fillText(`${product.progress.toFixed(0)}%`, product.x, product.y - product.size - 8);

          console.log(`✅ 제품 ${index} 렌더링 성공`);
        } catch (error) {
          console.error(`❌ 제품 ${index} 렌더링 실패:`, error);
        }
      });
    } else {
      console.warn('⚠️ 렌더링할 제품이 없음');
    }

    // 공정 박스 그리기 (제품 위에 그려서 투명하게)
    lines.forEach(line => {
      const boxY = line.y - boxHeight/2;
      
      line.processes.forEach(process => {
        // 🆕 박스 배경을 투명하게
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'; // 10% 투명도
        ctx.fillRect(process.x - process.width/2, boxY, process.width, boxHeight);
        
        // 테두리는 유지
        ctx.strokeStyle = '#1976d2';
        ctx.lineWidth = 2;
        ctx.strokeRect(process.x - process.width/2, boxY, process.width, boxHeight);
        
        // 텍스트는 유지
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(process.name, process.x, boxY + 25);
      });
    });

    ctx.restore();
    console.log('🎨 캔버스 렌더링 완료');

  }, [containerSize, products]); // products가 변경될 때마다 리렌더링

  // 🆕 실시간 업데이트 표시 함수 (실제 변화 감지)
  const formatLastUpdate = (timestamp) => {
    console.log(`🕐 시간 포맷팅:`, timestamp, typeof timestamp);
    
    if (!timestamp) {
      return '데이터 없음';
    }
    
    try {
      // 🆕 실제 타임스탬프가 있으면 그것을 사용, 없으면 현재 시간
      if (typeof timestamp === 'string' && timestamp !== 'Invalid Date') {
        const updateTime = new Date(timestamp);
        if (!isNaN(updateTime.getTime())) {
          const now = new Date();
          const diffSeconds = Math.floor((now - updateTime) / 1000);
          
          if (diffSeconds < 60) return `${diffSeconds}초 전`;
          if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}분 전`;
          return updateTime.toLocaleTimeString();
        }
      }
      
      // fallback: 현재 시간
      return new Date().toLocaleTimeString();
    } catch (error) {
      console.error('❌ 시간 포맷팅 오류:', error);
      return '시간 오류';
    }
  };

  // 🆕 자동차 모델명 전체 표시 함수
  const getFullVehicleName = (stationId) => {
    const stationIndex = parseInt(stationId.match(/\d+/)?.[0] || '0');
    const modelIndex = stationIndex % vehicleModels.length;
    return vehicleModels[modelIndex];
  };

  return (
    <>
      {/* 연결 상태 표시 */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        zIndex: 1000,
        background: isConnected ? '#4CAF50' : '#f44336',
        color: 'white',
        padding: '6px 12px',
        borderRadius: '4px',
        fontSize: '12px'
      }}>
        {isConnected ? '🟢 MQTT 연결됨' : '🔴 MQTT 연결 끊김'}
      </div>

      {/* 🆕 실시간 제품 정보 패널 (자동차 모델 포함) */}
      {selectedProduct && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 1000,
          background: 'white',
          border: '2px solid #ccc',
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          minWidth: '220px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
            🚗 실시간 제품 정보
          </h4>
          <div><strong>스테이션:</strong> {selectedProduct.stationId}</div>
          <div><strong>차량모델:</strong> {getFullVehicleName(selectedProduct.stationId)}</div>
          <div><strong>진행률:</strong> {selectedProduct.progress.toFixed(1)}%</div>
          <div><strong>상태:</strong> {selectedProduct.status}</div>
          <div><strong>작업:</strong> {selectedProduct.operation}</div>
          {selectedProduct.cycleTime > 0 && (
            <div><strong>사이클타임:</strong> {selectedProduct.cycleTime.toFixed(1)}s</div>
          )}
          {selectedProduct.productionCount > 0 && (
            <div><strong>생산수량:</strong> {selectedProduct.productionCount}대</div>
          )}
          <div><strong>업데이트:</strong> {formatLastUpdate(selectedProduct.lastUpdate)}</div>
          <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
            <div>원본: {String(selectedProduct.lastUpdate).substring(0, 50)}</div>
            <div>현재시간: {new Date().toLocaleTimeString()}</div>
          </div>
          <button 
            onClick={() => setSelectedProduct(null)}
            style={{
              marginTop: '8px',
              padding: '4px 8px',
              border: 'none',
              background: '#f44336',
              color: 'white',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '10px'
            }}
          >
            닫기
          </button>
        </div>
      )}

      {/* 🆕 범례 (자동차 모델별 색상) */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        zIndex: 1000,
        background: 'rgba(255,255,255,0.9)',
        border: '1px solid #ccc',
        borderRadius: '6px',
        padding: '8px',
        fontSize: '11px'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>차량 모델:</div>
        {vehicleModels.map((model, index) => (
          <div key={model} style={{ display: 'flex', alignItems: 'center', marginBottom: '2px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: '#4CAF50',
              marginRight: '6px',
              fontSize: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold'
            }}>
              {model.charAt(0)}
            </div>
            <span>{model}</span>
          </div>
        ))}
      </div>

      {/* 기존 캔버스 및 팝오버 */}
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
          onClick={handleCanvasClick}
          onMouseMove={handleMouseMove}
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