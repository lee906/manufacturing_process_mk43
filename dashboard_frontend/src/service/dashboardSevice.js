const API_BASE_URL = 'http://localhost:8080/api';

class DashboardService {
  constructor() {
    this.cache = new Map();
    this.listeners = new Set();
  }

  // 실시간 대시보드 데이터 조회
  async getLatestDashboardData() {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/latest`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.updateCache('dashboard', data);
      this.notifyListeners('dashboard', data);
      return data;
    } catch (error) {
      console.error('대시보드 데이터 조회 실패:', error);
      // 실패 시 더미 데이터 반환
      return this.getDummyDashboardData();
    }
  }

  // 스테이션 상태 데이터 조회
  async getStationsStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/stations/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.updateCache('stations', data);
      this.notifyListeners('stations', data);
      return data;
    } catch (error) {
      console.error('스테이션 데이터 조회 실패:', error);
      return this.getDummyStationsData();
    }
  }

  // 실시간 데이터 구독
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  // 리스너들에게 데이터 변경 알림
  notifyListeners(type, data) {
    this.listeners.forEach(callback => {
      try {
        callback(type, data);
      } catch (error) {
        console.error('리스너 콜백 오류:', error);
      }
    });
  }

  // 캐시 업데이트
  updateCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: new Date().getTime()
    });
  }

  // 캐시된 데이터 조회
  getCachedData(key) {
    const cached = this.cache.get(key);
    if (cached && (new Date().getTime() - cached.timestamp) < 10000) { // 10초 캐시
      return cached.data;
    }
    return null;
  }

  // 더미 대시보드 데이터 (Spring Boot 연결 전 테스트용)
  getDummyDashboardData() {
    const now = new Date();
    return {
      production: {
        current: Math.floor(Math.random() * 50) + 800, // 800-850
        target: 1000,
        hourlyRate: Math.floor(Math.random() * 10) + 40, // 40-50
        cycleTime: (Math.random() * 10 + 80).toFixed(1) // 80-90초
      },
      kpi: {
        oee: (Math.random() * 10 + 55).toFixed(1), // 55-65%
        otd: (Math.random() * 10 + 85).toFixed(1), // 85-95%
        fty: (Math.random() * 10 + 90).toFixed(1)  // 90-100%
      },
      quality: {
        overallScore: (Math.random() * 0.2 + 0.8).toFixed(3), // 0.8-1.0
        defectRate: (Math.random() * 0.05).toFixed(3), // 0-5%
        grade: ['A+', 'A', 'B+'][Math.floor(Math.random() * 3)]
      },
      efficiency: {
        powerEfficiency: (Math.random() * 10 + 70).toFixed(1), // 70-80%
        energyConsumption: Math.floor(Math.random() * 100) + 200 // 200-300kW
      },
      timestamp: now.toISOString(),
      lastUpdated: now.toLocaleTimeString()
    };
  }

  // 더미 스테이션 데이터
  getDummyStationsData() {
    const stations = ['ROBOT_ARM_01', 'CONVEYOR_01', 'QUALITY_CHECK_01', 'INVENTORY_01'];
    const statuses = ['RUNNING', 'IDLE', 'MAINTENANCE'];
    
    return stations.map(stationId => ({
      stationId,
      processType: this.getProcessType(stationId),
      status: statuses[Math.floor(Math.random() * statuses.length)],
      efficiency: (Math.random() * 0.3 + 0.7).toFixed(3), // 70-100%
      temperature: (Math.random() * 15 + 25).toFixed(1), // 25-40°C
      alertCount: Math.floor(Math.random() * 3),
      lastUpdate: new Date().toLocaleTimeString(),
      metrics: this.generateStationMetrics(stationId)
    }));
  }

  getProcessType(stationId) {
    const types = {
      'ROBOT_ARM_01': '로봇 조립',
      'CONVEYOR_01': '부품 이송',
      'QUALITY_CHECK_01': '품질 검사',
      'INVENTORY_01': '재고 관리'
    };
    return types[stationId] || '의장 공정';
  }

  generateStationMetrics(stationId) {
    switch (stationId) {
      case 'ROBOT_ARM_01':
        return {
          assemblies: Math.floor(Math.random() * 20) + 100,
          errors: Math.floor(Math.random() * 3),
          gripper_force: (Math.random() * 20 + 40).toFixed(1),
          positioning_accuracy: (Math.random() * 0.1 + 0.05).toFixed(3)
        };
      case 'CONVEYOR_01':
        return {
          parts_transported: Math.floor(Math.random() * 50) + 200,
          belt_speed: (Math.random() * 0.5 + 1.0).toFixed(1),
          jam_count: Math.floor(Math.random() * 2)
        };
      case 'QUALITY_CHECK_01':
        return {
          inspections: Math.floor(Math.random() * 30) + 150,
          pass_rate: (Math.random() * 10 + 90).toFixed(1),
          defect_detection: (Math.random() * 0.1 + 0.9).toFixed(2)
        };
      case 'INVENTORY_01':
        return {
          stock_level: Math.floor(Math.random() * 200) + 400,
          retrievals: Math.floor(Math.random() * 20) + 50,
          storage_efficiency: (Math.random() * 0.2 + 0.8).toFixed(2)
        };
      default:
        return {};
    }
  }

  // 폴링 시작 (실시간 업데이트)
  startPolling(interval = 5000) {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    this.pollingInterval = setInterval(async () => {
      try {
        await Promise.all([
          this.getLatestDashboardData(),
          this.getStationsStatus()
        ]);
      } catch (error) {
        console.error('폴링 중 오류:', error);
      }
    }, interval);

    // 초기 데이터 로드
    this.getLatestDashboardData();
    this.getStationsStatus();
  }

  // 폴링 중지
  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }
}

// 싱글톤 인스턴스 생성
const dashboardService = new DashboardService();

export default dashboardService;