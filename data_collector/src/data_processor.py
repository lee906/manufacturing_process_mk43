import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class DataProcessor:
    def __init__(self, api_client):
        """데이터 프로세서 초기화"""
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        self.processed_count = 0
        
        self.logger.info("데이터 프로세서 초기화 완료")
    
    def process_message(self, topic: str, payload: str) -> Optional[Dict[str, Any]]:
        """MQTT 메시지 처리 및 API 전송"""
        try:
            # JSON 파싱
            raw_data = json.loads(payload)
            
            # 데이터 정제 및 가공
            processed_data = self._process_iot_data(raw_data, topic)
            
            # Spring Boot API로 전송 (실패해도 계속 진행)
            success = self.api_client.send_data(processed_data)
            
            if success:
                self.processed_count += 1
                self.logger.debug(f"✅ 데이터 처리 완료: {processed_data.get('stationId')}")
            else:
                self.logger.warning(f"⚠️ API 전송 실패: {processed_data.get('stationId')} (Spring Boot 서버 확인)")
            
            return processed_data
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"데이터 처리 오류: {e}")
            return None
    
    def _process_iot_data(self, raw_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """IoT 데이터 정제 및 가공"""
        
        # 토픽에서 스테이션 ID 추출
        topic_parts = topic.split('/')
        station_id = topic_parts[2] if len(topic_parts) > 2 else "UNKNOWN"
        
        # 기본 구조 생성
        processed_data = {
            "stationId": raw_data.get("station_id", station_id),
            "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
            "processType": raw_data.get("process_type", "unknown"),
            "location": raw_data.get("location", "Unknown Location"),
            "sensors": raw_data.get("sensors", {}),
            "production": raw_data.get("production", {}),
            "quality": raw_data.get("quality", {}),
            "alerts": raw_data.get("alerts", {}),
            "processedAt": datetime.now().isoformat(),
            "topic": topic
        }
        
        # 특화 데이터 통합
        if "robot_specific" in raw_data:
            processed_data["robotData"] = raw_data["robot_specific"]
        
        if "conveyor_specific" in raw_data:
            processed_data["conveyorData"] = raw_data["conveyor_specific"]
        
        if "quality_specific" in raw_data:
            processed_data["qualityData"] = raw_data["quality_specific"]
        
        if "inventory_specific" in raw_data:
            processed_data["inventoryData"] = raw_data["inventory_specific"]
        
        # 파생 지표 계산
        processed_data["derivedMetrics"] = self._calculate_derived_metrics(processed_data)
        
        return processed_data
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """파생 지표 계산"""
        metrics = {}
        
        sensors = data.get("sensors", {})
        
        # 효율성 지표
        if "temperature" in sensors:
            temp_efficiency = max(0, 1 - abs(sensors["temperature"] - 35) / 35)
            metrics["efficiency"] = round(temp_efficiency, 3)
        
        # 성능 지표
        production = data.get("production", {})
        if "throughput_per_hour" in production:
            metrics["performanceScore"] = min(1.0, production["throughput_per_hour"] / 100)
        
        # 품질 지표
        quality = data.get("quality", {})
        if "overall_score" in quality:
            metrics["qualityIndex"] = quality["overall_score"]
        
        return metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        return {
            "processedCount": self.processed_count,
            "lastProcessedAt": datetime.now().isoformat()
        }
