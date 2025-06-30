const API_BASE_URL = 'http://localhost:8080/api/kpi';

class DashboardService {
  constructor() {
    this.subscribers = [];
    this.pollingInterval = null;
    this.isPolling = false;
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(sub => sub !== callback);
    };
  }

  notify(type, data) {
    this.subscribers.forEach(callback => callback(type, data));
  }

  startPolling(interval = 3000) {
    if (this.isPolling) return;
    
    this.isPolling = true;
    this.fetchData();
    
    this.pollingInterval = setInterval(() => {
      this.fetchData();
    }, interval);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
      this.isPolling = false;
    }
  }

  async fetchData() {
    try {
      // 5초 타임아웃으로 빠른 응답 보장
      const dashboardPromise = Promise.race([
        this.getFactorySummary(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('API Timeout')), 5000))
      ]);
      
      const stationsPromise = Promise.race([
        this.getLatestKPIs(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('API Timeout')), 5000))
      ]);

      const dashboardData = await dashboardPromise;
      this.notify('dashboard', dashboardData);
      
      const stationsData = await stationsPromise;
      this.notify('stations', stationsData);
      
    } catch (error) {
      console.error('Backend connection failed, using mock data:', error);
      // 빠른 fallback
      this.notify('dashboard', this.getMockDashboardData());
      this.notify('stations', this.getMockStationsData());
    }
  }

  async getLatestKPIs() {
    const response = await fetch(`${API_BASE_URL}/latest`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }
  
  async getStationKPI(stationId) {
    const response = await fetch(`${API_BASE_URL}/station/${stationId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }
  
  async getFactorySummary() {
    const response = await fetch(`${API_BASE_URL}/factory/summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  getMockDashboardData() {
    return {
      production: {
        current: Math.floor(Math.random() * 200) + 650,
        target: 1000,
        hourlyRate: Math.floor(Math.random() * 20) + 35,
        cycleTime: Math.floor(Math.random() * 20) + 45
      },
      kpi: {
        oee: Math.floor(Math.random() * 15) + 80,
        otd: Math.floor(Math.random() * 10) + 88,
        fty: Math.floor(Math.random() * 12) + 85
      },
      quality: {
        overallScore: (Math.random() * 0.15 + 0.82)
      }
    };
  }

  getMockStationsData() {
    const stations = ['A', 'B', 'C', 'D'];
    return stations.map((station, index) => ({
      id: index + 1,
      name: `Station ${station}`,
      stationId: `ST00${index + 1}`,
      status: Math.random() > 0.2 ? 'running' : 'maintenance',
      efficiency: Math.floor(Math.random() * 25) + 75,
      temperature: Math.floor(Math.random() * 15) + 65,
      vibration: (Math.random() * 0.5 + 0.1).toFixed(2),
      oee: Math.floor(Math.random() * 20) + 75,
      cycleTime: Math.floor(Math.random() * 30) + 45,
      lastUpdated: new Date().toISOString()
    }));
  }
}

const dashboardService = new DashboardService();
export default dashboardService;