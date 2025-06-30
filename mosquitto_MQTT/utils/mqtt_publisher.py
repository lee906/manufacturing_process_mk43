"""
MQTT 데이터 발행 유틸리티
Raw 데이터만 전송 (KPI 계산 제거)
"""

import json
import time
import logging
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

class MQTTPublisher:
    """MQTT 데이터 발행기 - Raw 데이터 전용"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.connected = False
        
        # MQTT 클라이언트 초기화
        self.client = mqtt.Client(client_id=f"assembly_simulator_{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # 통계
        self.published_count = 0
        self.failed_count = 0
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
        print(f"📡 MQTT Publisher 초기화: {broker_host}:{broker_port}")
    
    def connect(self) -> bool:
        """MQTT 브로커에 연결"""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            
            # 연결 대기 (최대 5초)
            timeout = 5.0
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                print(f"✅ MQTT 브로커 연결 성공: {self.broker_host}:{self.broker_port}")
                return True
            else:
                print(f"❌ MQTT 브로커 연결 실패: 타임아웃")
                return False
                
        except Exception as e:
            print(f"❌ MQTT 연결 오류: {e}")
            return False
    
    def disconnect(self):
        """MQTT 브로커 연결 해제"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            
            print(f"📊 MQTT 발행 통계: 성공 {self.published_count}건, 실패 {self.failed_count}건")
            print("🔌 MQTT 연결 해제 완료")
    
    def publish_data(self, topic: str, data: Dict[str, Any], qos: int = 0, retain: bool = False) -> bool:
        """Raw 데이터 발행"""
        if not self.connected:
            self.logger.warning("MQTT 연결이 끊어져 있습니다")
            return False
        
        try:
            # JSON 직렬화
            payload = json.dumps(data, ensure_ascii=False, default=self._json_serializer)
            
            # MQTT 발행
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.published_count += 1
                self.logger.debug(f"📤 발행 성공: {topic}")
                return True
            else:
                self.failed_count += 1
                self.logger.error(f"❌ 발행 실패: {topic}, 코드: {result.rc}")
                return False
                
        except Exception as e:
            self.failed_count += 1
            self.logger.error(f"❌ 발행 오류: {topic}, 오류: {e}")
            return False
    
    def publish_sensor_data(self, station_id: str, data: Dict[str, Any], 
                          topic: Optional[str] = None, qos: int = 0, retain: bool = False) -> bool:
        """센서 데이터 발행 (하위 호환성)"""
        if topic is None:
            topic = f"factory/{station_id}/sensors"
        
        return self.publish_data(topic, data, qos, retain)
    
    def publish_batch_data(self, data_list: list) -> int:
        """배치 데이터 발행"""
        success_count = 0
        
        for data_item in data_list:
            topic = data_item.get('topic')
            payload = data_item.get('data')
            qos = data_item.get('qos', 0)
            retain = data_item.get('retain', False)
            
            if topic and payload:
                if self.publish_data(topic, payload, qos, retain):
                    success_count += 1
        
        print(f"📦 배치 발행 완료: {success_count}/{len(data_list)}건 성공")
        return success_count
    
    def _on_connect(self, client, userdata, flags, rc):
        """연결 콜백"""
        if rc == 0:
            self.connected = True
            self.logger.info(f"MQTT 브로커 연결 성공")
        else:
            self.connected = False
            self.logger.error(f"MQTT 연결 실패: 코드 {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """연결 해제 콜백"""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"MQTT 연결이 예기치 않게 끊어졌습니다: 코드 {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """발행 완료 콜백"""
        self.logger.debug(f"메시지 발행 완료: MID {mid}")
    
    def _json_serializer(self, obj):
        """JSON 직렬화를 위한 기본 변환기"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def get_stats(self) -> Dict[str, Any]:
        """발행 통계 반환"""
        return {
            "connected": self.connected,
            "published_count": self.published_count,
            "failed_count": self.failed_count,
            "success_rate": (self.published_count / (self.published_count + self.failed_count) * 100) 
                           if (self.published_count + self.failed_count) > 0 else 0
        }