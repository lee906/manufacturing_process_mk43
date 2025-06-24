# src/models/sensor_data.py
from dataclasses import dataclass
from typing import Dict, Optional, Any
from datetime import datetime
import json

@dataclass
class SensorReading:
    station_id: str
    timestamp: str
    process_type: str
    sensors: Dict[str, float]
    production: Optional[Dict[str, Any]] = None
    quality: Optional[Dict[str, Any]] = None
    alerts: Optional[Dict[str, bool]] = None
    
    @classmethod
    def from_mqtt_payload(cls, payload: str) -> 'SensorReading':
        """MQTT 페이로드에서 센서 데이터 생성"""
        data = json.loads(payload)
        return cls(
            station_id=data.get('station_id'),
            timestamp=data.get('timestamp'),
            process_type=data.get('process_type'),
            sensors=data.get('sensors', {}),
            production=data.get('production'),
            quality=data.get('quality'),
            alerts=data.get('alerts')
        )
    
    def to_api_format(self) -> Dict[str, Any]:
        """Spring Boot API 형식으로 변환"""
        return {
            "stationId": self.station_id,
            "timestamp": self.timestamp,
            "processType": self.process_type,
            "sensors": self.sensors,
            "production": self.production,
            "quality": self.quality,
            "alerts": self.alerts,
            "processedAt": datetime.now().isoformat()
        }