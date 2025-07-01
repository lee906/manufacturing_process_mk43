import requests
import json
import time
import logging
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['api'].get('base_url', config['api'].get('backend_url'))
        self.endpoints = config['api']['endpoints']
        self.timeout = config['api']['timeout']
        self.retry_count = config['api'].get('retry_count', 3)
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DataCollector-KPI/2.0'
        })
    
    def send_iot_data(self, data: Dict[str, Any]) -> bool:
        """기존 IoT 데이터 전송"""
        return self._send_data(self.endpoints['iot_data'], data)
    
    def send_kpi_data(self, kpi_data: Dict[str, Any]) -> bool:
        """🆕 KPI 데이터 전송"""
        return self._send_data(self.endpoints['kpi_data'], kpi_data)
    
    def _send_data(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """데이터 전송 (재시도 로직 포함)"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_count):
            try:
                response = self.session.post(
                    url, 
                    json=data, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return True
                else:
                    self.logger.warning(f"⚠️ API 오류 ({attempt+1}/{self.retry_count}): {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.logger.warning("⚠️ API 서버 연결 실패 (Spring Boot 서버가 실행 중인지 확인)")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ 네트워크 오류 ({attempt+1}/{self.retry_count}): {e}")
            
            if attempt < self.retry_count - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
        
        return False
    
    def health_check(self) -> bool:
        """API 서버 상태 확인"""
        try:
            response = self.session.get(
                f"{self.base_url}/actuator/health", 
                timeout=5
            )
            return response.status_code == 200
        except:
            return False