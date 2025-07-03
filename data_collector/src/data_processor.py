import json
import logging
from typing import Dict, Any, Optional, List
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
            success = self.api_client.send_iot_data(processed_data)
            
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
        
        # 토픽 파싱 및 데이터 타입 식별
        topic_parts = topic.split('/')
        data_category = self._identify_data_category(topic_parts)
        
        # 토픽에서 스테이션 ID 추출
        if len(topic_parts) >= 3 and topic_parts[1] not in ["digital_twin", "production_line", "supply_chain", "robots"]:
            station_id = topic_parts[1]  # factory/A01_DOOR/telemetry
        else:
            station_id = raw_data.get("station_id", "SYSTEM")
        
        # 기본 구조 생성
        processed_data = {
            "stationId": raw_data.get("station_id", station_id),
            "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
            "dataCategory": data_category,
            "topic": topic,
            "processedAt": datetime.now().isoformat()
        }
        
        # 데이터 카테고리별 처리
        if data_category == "station_data":
            self._process_station_data(processed_data, raw_data)
        elif data_category == "vehicle_tracking":
            self._process_vehicle_tracking_data(processed_data, raw_data)
        elif data_category == "robot_data":
            self._process_robot_data(processed_data, raw_data)
        elif data_category == "production_line":
            self._process_production_line_data(processed_data, raw_data)
        elif data_category == "supply_chain":
            self._process_supply_chain_data(processed_data, raw_data)
        else:
            # 기본 처리 (기존 로직)
            self._process_legacy_data(processed_data, raw_data)
        
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
    
    def _identify_data_category(self, topic_parts: List[str]) -> str:
        """토픽 기반 데이터 카테고리 식별"""
        if len(topic_parts) < 2:
            return "unknown"
        
        # factory/digital_twin/vehicle_tracking
        if len(topic_parts) >= 3 and topic_parts[1] == "digital_twin":
            return "vehicle_tracking"
        
        # factory/production_line/status
        elif len(topic_parts) >= 3 and topic_parts[1] == "production_line":
            return "production_line"
        
        # factory/supply_chain/status
        elif len(topic_parts) >= 3 and topic_parts[1] == "supply_chain":
            return "supply_chain"
        
        # factory/robots/summary
        elif len(topic_parts) >= 3 and topic_parts[1] == "robots":
            return "robot_summary"
        
        # factory/A01_DOOR/robots/telemetry
        elif len(topic_parts) >= 4 and topic_parts[2] == "robots":
            return "robot_data"
        
        # factory/A01_DOOR/telemetry (기존 스테이션 데이터)
        elif len(topic_parts) >= 3:
            return "station_data"
        
        return "unknown"
    
    def _process_station_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """스테이션 센서 데이터 처리"""
        processed_data.update({
            "processType": raw_data.get("process_type", "assembly"),
            "location": raw_data.get("location", "Assembly Line"),
            "sensors": raw_data.get("sensors", {}),
            "production": raw_data.get("production", {}),
            "quality": raw_data.get("quality", {}),
            "alerts": raw_data.get("alerts", {})
        })
    
    def _process_vehicle_tracking_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """차량 추적 데이터 처리"""
        # 차량 추적 데이터는 별도 API로 전송
        vehicle_data = {
            "total_vehicles": raw_data.get("total_vehicles", 0),
            "active_vehicles": raw_data.get("active_vehicles", 0),
            "vehicles": raw_data.get("vehicles", []),
            "station_sequence": raw_data.get("station_sequence", []),
            "station_positions": raw_data.get("station_positions", {}),
            "timestamp": raw_data.get("timestamp", processed_data.get("timestamp"))
        }
        
        # 차량 추적 전용 API로 전송
        vehicle_success = self.api_client.send_vehicle_tracking_data(vehicle_data)
        
        if vehicle_success:
            self.logger.debug("✅ 차량 추적 데이터 전송 완료")
        else:
            self.logger.warning("⚠️ 차량 추적 데이터 전송 실패")
        
        # 기존 구조도 유지 (하위 호환성)
        processed_data.update({
            "vehicleTracking": vehicle_data
        })
    
    def _process_robot_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """로봇 데이터 처리"""
        processed_data.update({
            "robotData": {
                "robots": raw_data.get("robots", []),
                "collaboration": raw_data.get("collaboration", {}),
                "stationId": raw_data.get("station_id")
            }
        })
    
    def _process_production_line_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """생산라인 데이터 처리"""
        processed_data.update({
            "productionLine": {
                "shiftProgress": raw_data.get("shift_progress", 0),
                "currentProduction": raw_data.get("current_production", 0),
                "dailyTarget": raw_data.get("daily_target", 0),
                "achievementRate": raw_data.get("achievement_rate", 0),
                "totalWip": raw_data.get("total_wip", 0),
                "stations": raw_data.get("stations", {}),
                "lineEfficiency": raw_data.get("line_efficiency", 0)
            }
        })
    
    def _process_supply_chain_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """공급망 데이터 처리"""
        processed_data.update({
            "supplyChain": {
                "inventorySummary": raw_data.get("inventory_summary", {}),
                "totalParts": raw_data.get("total_parts", 0),
                "activeOrders": raw_data.get("active_orders", 0),
                "parts": raw_data.get("parts", []),
                "suppliers": raw_data.get("suppliers", {})
            }
        })
    
    def _process_legacy_data(self, processed_data: Dict[str, Any], raw_data: Dict[str, Any]):
        """기존 데이터 구조 처리 (하위 호환성)"""
        processed_data.update({
            "processType": raw_data.get("process_type", "unknown"),
            "location": raw_data.get("location", "Unknown Location"),
            "sensors": raw_data.get("sensors", {}),
            "production": raw_data.get("production", {}),
            "quality": raw_data.get("quality", {}),
            "alerts": raw_data.get("alerts", {})
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        return {
            "processedCount": self.processed_count,
            "lastProcessedAt": datetime.now().isoformat()
        }
