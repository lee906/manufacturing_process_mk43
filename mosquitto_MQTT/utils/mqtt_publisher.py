import paho.mqtt.client as mqtt
import json
import logging
from typing import Dict, Any
import time

class MQTTPublisher:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.connected = False
        
        # MQTT 이벤트 핸들러
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        self.logger = logging.getLogger(__name__)
        
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.logger.info("✅ MQTT 브로커 연결 성공")
        else:
            self.connected = False
            self.logger.error(f"❌ MQTT 연결 실패: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.logger.info("🔌 MQTT 브로커 연결 해제")
    
    def _on_publish(self, client, userdata, mid):
        self.logger.debug(f"📤 메시지 발행 완료: {mid}")
    
    def connect(self) -> bool:
        """MQTT 브로커에 연결"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # 연결 대기
            timeout = time.time() + 5
            while not self.connected and time.time() < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            self.logger.error(f"MQTT 연결 오류: {e}")
            return False
    
    def publish_sensor_data(self, station_id: str, data: Dict[str, Any], topic_prefix: str = "factory/manufacturing") -> bool:
        """센서 데이터 발행"""
        if not self.connected:
            self.logger.warning("MQTT 연결이 끊어져 있습니다.")
            return False
        
        try:
            topic = f"{topic_prefix}/{station_id}/data"
            payload = json.dumps(data, ensure_ascii=False)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"📡 데이터 발행: {station_id}")
                return True
            else:
                self.logger.error(f"발행 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"데이터 발행 오류: {e}")
            return False
    
    def publish_alert(self, station_id: str, alert_type: str, message: str, topic_prefix: str = "factory/manufacturing") -> bool:
        """알림 메시지 발행"""
        alert_data = {
            "station_id": station_id,
            "alert_type": alert_type,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        topic = f"{topic_prefix}/{station_id}/alert"
        return self._publish_json(topic, alert_data)
    
    def _publish_json(self, topic: str, data: Dict[str, Any]) -> bool:
        """JSON 데이터 발행"""
        try:
            payload = json.dumps(data, ensure_ascii=False)
            result = self.client.publish(topic, payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self.logger.error(f"JSON 발행 오류: {e}")
            return False
    
    def disconnect(self):
        """MQTT 연결 해제"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("MQTT 연결 해제됨")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()