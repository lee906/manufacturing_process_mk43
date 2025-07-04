import paho.mqtt.client as mqtt
import logging
from typing import Callable, List
import json
import os

class MQTTClient:
    def __init__(self, config_path: str = "config.yaml"):
        # 기본 설정
        self.mqtt_config = {
            "broker_host": "localhost",
            "broker_port": 1883,
            "topics": ["factory/assembly/+/data", "factory/assembly/+/alert"],
            "qos": 1
        }
        
        # 설정 파일 로드 시도 (yaml이 없어도 동작)
        try:
            import yaml
            if os.path.exists(config_path):
                with open('config.yaml', 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if 'mqtt' in config:
                        self.mqtt_config.update(config['mqtt'])
        except ImportError:
            logging.info("PyYAML이 설치되지 않음. 기본 설정 사용.")
        except FileNotFoundError:
            logging.info(f"설정 파일 {config_path}를 찾을 수 없음. 기본 설정 사용.")
        
        self.client = mqtt.Client()
        self.message_handlers: List[Callable] = []
        
        # MQTT 이벤트 핸들러 설정
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.logger = logging.getLogger(__name__)
    
    def add_message_handler(self, handler: Callable):
        """메시지 처리 핸들러 추가"""
        self.message_handlers.append(handler)
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("✅ MQTT 브로커 연결 성공")
            # 설정된 토픽들 구독
            for topic in self.mqtt_config['topics']:
                client.subscribe(topic, self.mqtt_config['qos'])
                self.logger.info(f"📡 토픽 구독: {topic}")
        else:
            self.logger.error(f"❌ MQTT 연결 실패: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """메시지 수신 처리"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"📨 메시지 수신: {topic}")
            
            # 등록된 모든 핸들러에게 메시지 전달
            for handler in self.message_handlers:
                handler(topic, payload)
                
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.logger.info("MQTT 연결 해제됨")
    
    def connect(self) -> bool:
        """MQTT 브로커 연결"""
        try:
            self.client.connect(
                self.mqtt_config['broker_host'],
                self.mqtt_config['broker_port'],
                60
            )
            return True
        except Exception as e:
            self.logger.error(f"MQTT 연결 오류: {e}")
            return False
    
    def start_loop(self):
        """MQTT 클라이언트 루프 시작"""
        self.client.loop_forever()
    
    def stop(self):
        """MQTT 클라이언트 중지"""
        try:
            self.logger.info("🛑 MQTT 클라이언트 종료 중...")
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("✅ MQTT 클라이언트 정상 종료")
        except Exception as e:
            self.logger.error(f"❌ MQTT 클라이언트 종료 오류: {e}")
    
    def disconnect(self):
        """MQTT 연결 해제 (별칭)"""
        self.stop()
