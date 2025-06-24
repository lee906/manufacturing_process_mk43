import requests
import logging
from typing import Dict, Any, Optional
import json

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.endpoints = {
            "iot_data": "/api/iot-data",
            "alerts": "/api/alerts"
        }
        self.timeout = 5
        self.logger = logging.getLogger(__name__)
        
        # 세션 설정
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """IoT 데이터를 Spring Boot API로 전송"""
        try:
            url = f"{self.base_url}{self.endpoints['iot_data']}"
            
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.debug(f"✅ API 전송 성공: {data.get('stationId')}")
                return True
            else:
                self.logger.warning(f"⚠️ API 응답 오류: {response.status_code}")
                # Spring Boot가 아직 실행되지 않았을 수 있으므로 에러가 아닌 경고로 처리
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.warning("⚠️ API 서버 연결 실패 (Spring Boot 서버가 실행 중인지 확인)")
            return False
        except requests.exceptions.Timeout:
            self.logger.error("❌ API 요청 타임아웃")
            return False
        except Exception as e:
            self.logger.error(f"❌ API 전송 오류: {e}")
            return False
    
    def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """알림 데이터 전송"""
        try:
            url = f"{self.base_url}{self.endpoints['alerts']}"
            
            response = self.session.post(
                url,
                json=alert_data,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"알림 전송 오류: {e}")
            return False
    
    def health_check(self) -> bool:
        """API 서버 상태 확인"""
        try:
            url = f"{self.base_url}/actuator/health"
            response = self.session.get(url, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
