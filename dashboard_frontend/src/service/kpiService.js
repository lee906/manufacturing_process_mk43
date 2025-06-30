const API_BASE_URL = 'http://localhost:8080/api/kpi';

export const kpiService = {
  // 최신 KPI 데이터 조회
  getLatestKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/latest`);
    return response.json();
  },
  
  // 스테이션별 KPI 조회
  getStationKPI: async (stationId) => {
    const response = await fetch(`${API_BASE_URL}/station/${stationId}`);
    return response.json();
  },
  
  // 공장 전체 KPI 요약
  getFactorySummary: async () => {
    const response = await fetch(`${API_BASE_URL}/factory/summary`);
    return response.json();
  }
};