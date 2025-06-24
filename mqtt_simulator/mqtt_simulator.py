#!/usr/bin/env python3
"""
IoT 데이터 MQTT 시뮬레이터
제조 공정의 실제 센서 데이터를 시뮬레이션하여 MQTT로 전송
"""

import json
import time
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any, List
import paho.mqtt.client as mqtt
import threading
import signal
import sys

@dataclass
class StationConfig:
    """스테이션 설정"""
    station_id: str
    process_type: str
    location: str
    base_efficiency: float
    base_temperature: float
    cycle_time_base: float
    production_rate: int  # 시간당 생산량

class IoTDataSimulator:
    def __init__(self):
        self.running = False
        self.mqtt_client = None
        
        # MQTT 설정
        self.broker_host = "localhost"
        self.broker_port = 1883
        self.base_topic = "factory/manufacturing"
        
        # 스테이션 설정
        self.stations = {
            "WELDING_01": StationConfig(
                station_id="WELDING_01",
                process_type="용접",
                location="1호선 용접부",
                base_efficiency=0.85,
                base_temperature=35.0,
                cycle_time_base=18.0,
                production_rate=120
            ),
            "PAINTING_02": StationConfig(
                station_id="PAINTING_02", 
                process_type="도장",
                location="2호선 도장부",
                base_efficiency=0.78,
                base_temperature=28.0,
                cycle_time_base=25.0,
                production_rate=95
            ),
            "ASSEMBLY_03": StationConfig(
                station_id="ASSEMBLY_03",
                process_type="조립",
                location="3호선 조립부", 
                base_efficiency=0.82,
                base_temperature=32.0,
                cycle_time_base=22.0,
                production_rate=110
            ),
            "INSPECTION_04": StationConfig(
                station_id="INSPECTION_04",
                process_type="검사",
                location="4호선 검사부",
                base_efficiency=0.90,
                base_temperature=25.0,
                cycle_time_base=15.0,
                production_rate=150
            ),
            "STAMPING_05": StationConfig(
                station_id="STAMPING_05",
                process_type="프레스",
                location="5호선 프레스부",
                base_efficiency=0.88,
                base_temperature=30.0,
                cycle_time_base=12.0,
                production_rate=180
            )
        }
        
        # 시뮬레이션 상태
        self.simulation_start_time = None
        self.station_states = {}
        self.initialize_station_states()
        
    def initialize_station_states(self):
        """스테이션 초기 상태 설정"""
        for station_id, config in self.stations.items():
            self.station_states[station_id] = {
                "total_production": 0,
                "last_production_time": datetime.now(),
                "maintenance_cycle": 0,
                "quality_trend": 0.95,  # 초기 품질
                "alert_state": {"high_temp": False, "low_efficiency": False, "maintenance_due": False}
            }
    
    def connect_mqtt(self):
        """MQTT 브로커 연결"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            return True
        except Exception as e:
            print(f"❌ MQTT 연결 실패: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ MQTT 브로커 연결 성공 ({self.broker_host}:{self.broker_port})")
        else:
            print(f"❌ MQTT 연결 실패, 코드: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"🔌 MQTT 브로커 연결 해제")
    
    def generate_sensor_data(self, station_config: StationConfig) -> Dict[str, Any]:
        """센서 데이터 생성"""
        now = datetime.now()
        station_state = self.station_states[station_config.station_id]
        
        # 시간에 따른 변화 (하루 주기)
        hour = now.hour
        day_cycle_factor = 0.8 + 0.4 * math.sin(2 * math.pi * hour / 24)
        
        # 온도 시뮬레이션 (외부 온도 + 작업 부하)
        ambient_temp = 20 + 10 * math.sin(2 * math.pi * hour / 24)  # 일일 온도 변화
        work_load_temp = station_config.base_temperature - 20
        temperature = ambient_temp + work_load_temp * day_cycle_factor + random.uniform(-2, 2)
        
        # 효율성 시뮬레이션 (유지보수 주기와 연관)
        maintenance_factor = max(0.6, 1.0 - station_state["maintenance_cycle"] * 0.01)
        efficiency = station_config.base_efficiency * maintenance_factor * day_cycle_factor
        efficiency = max(0.5, min(1.0, efficiency + random.uniform(-0.05, 0.05)))
        
        # 압력, 진동, 전력 등 추가 센서
        pressure = 2.5 + 0.5 * efficiency + random.uniform(-0.2, 0.2)
        vibration = (1.0 - efficiency) * 0.5 + random.uniform(0, 0.1)
        power_consumption = 50 + (1.0 - efficiency) * 30 + random.uniform(-5, 5)
        
        return {
            "temperature": round(temperature, 1),
            "pressure": round(pressure, 2),
            "vibration": round(vibration, 3),
            "power_consumption": round(power_consumption, 1),
            "efficiency_raw": round(efficiency, 3)
        }
    
    def generate_production_data(self, station_config: StationConfig) -> Dict[str, Any]:
        """생산 데이터 생성"""
        now = datetime.now()
        station_state = self.station_states[station_config.station_id]
        
        # 시간당 생산량 계산
        time_diff = (now - station_state["last_production_time"]).total_seconds() / 3600
        expected_production = int(station_config.production_rate * time_diff)
        
        # 효율성에 따른 실제 생산량
        efficiency = station_state.get("current_efficiency", station_config.base_efficiency)
        actual_production = int(expected_production * efficiency * random.uniform(0.9, 1.1))
        
        # 누적 생산량 업데이트
        station_state["total_production"] += actual_production
        station_state["last_production_time"] = now
        
        # 사이클 타임 (효율성에 반비례)
        cycle_time = station_config.cycle_time_base / efficiency
        cycle_time += random.uniform(-2, 2)
        
        # 처리량 
        throughput_per_hour = max(0, 3600 / cycle_time if cycle_time > 0 else 0)
        
        return {
            "count": actual_production,
            "total_count": station_state["total_production"],
            "cycle_time": round(cycle_time, 1),
            "throughput_per_hour": round(throughput_per_hour, 1),
            "status": "RUNNING" if efficiency > 0.6 else "SLOW",
            "target_rate": station_config.production_rate
        }
    
    def generate_quality_data(self, station_config: StationConfig) -> Dict[str, Any]:
        """품질 데이터 생성"""
        station_state = self.station_states[station_config.station_id]
        
        # 품질 트렌드 (시간이 지나면서 서서히 변화)
        trend_change = random.uniform(-0.002, 0.001)  # 품질은 보통 서서히 악화
        station_state["quality_trend"] = max(0.8, min(0.99, 
            station_state["quality_trend"] + trend_change))
        
        # 현재 품질 점수
        quality_score = station_state["quality_trend"] + random.uniform(-0.02, 0.02)
        quality_score = max(0.8, min(1.0, quality_score))
        
        # 불량률
        defect_rate = 1.0 - quality_score
        
        # 품질 등급
        if quality_score >= 0.98:
            grade = "A+"
        elif quality_score >= 0.95:
            grade = "A"
        elif quality_score >= 0.90:
            grade = "B+"
        elif quality_score >= 0.85:
            grade = "B"
        else:
            grade = "C"
        
        return {
            "score": round(quality_score, 3),
            "defect_rate": round(defect_rate, 3),
            "grade": grade,
            "overall_score": round(quality_score, 3)
        }
    
    def generate_alerts(self, station_config: StationConfig, sensor_data: Dict, production_data: Dict) -> Dict[str, Any]:
        """알림 데이터 생성"""
        station_state = self.station_states[station_config.station_id]
        alerts = station_state["alert_state"]
        
        # 온도 알림
        alerts["high_temperature"] = sensor_data["temperature"] > 40
        
        # 효율성 알림  
        alerts["low_efficiency"] = sensor_data["efficiency_raw"] < 0.7
        
        # 유지보수 알림
        station_state["maintenance_cycle"] += 1
        alerts["maintenance_due"] = station_state["maintenance_cycle"] > 100
        
        # 진동 알림
        alerts["high_vibration"] = sensor_data["vibration"] > 0.3
        
        # 생산 지연 알림
        alerts["production_delay"] = production_data["status"] == "SLOW"
        
        return alerts
    
    def generate_station_specific_data(self, station_config: StationConfig) -> Dict[str, Any]:
        """스테이션별 특화 데이터 생성"""
        if station_config.process_type == "용접":
            return {
                "welding_current": round(150 + random.uniform(-20, 20), 1),
                "welding_voltage": round(24 + random.uniform(-2, 2), 1),
                "wire_feed_rate": round(8.5 + random.uniform(-0.5, 0.5), 1),
                "shielding_gas_flow": round(15 + random.uniform(-1, 1), 1)
            }
        elif station_config.process_type == "도장":
            return {
                "paint_pressure": round(3.5 + random.uniform(-0.3, 0.3), 1),
                "spray_pattern": random.choice(["NORMAL", "WIDE", "NARROW"]),
                "paint_consumption": round(2.5 + random.uniform(-0.2, 0.2), 1),
                "booth_humidity": round(45 + random.uniform(-5, 5), 1)
            }
        elif station_config.process_type == "조립":
            return {
                "torque_applied": round(45 + random.uniform(-5, 5), 1),
                "assembly_sequence": random.randint(1, 12),
                "tool_wear": round(random.uniform(0.1, 0.9), 2),
                "fastener_count": random.randint(8, 12)
            }
        elif station_config.process_type == "검사":
            return {
                "inspection_points": random.randint(15, 25),
                "pass_count": random.randint(14, 25),
                "measurement_accuracy": round(random.uniform(0.95, 0.99), 3),
                "scan_duration": round(random.uniform(8, 15), 1)
            }
        elif station_config.process_type == "프레스":
            return {
                "press_force": round(800 + random.uniform(-50, 50), 1),
                "stroke_count": random.randint(180, 220),
                "die_temperature": round(150 + random.uniform(-10, 10), 1),
                "material_thickness": round(2.5 + random.uniform(-0.1, 0.1), 2)
            }
        
        return {}
    
    def create_iot_message(self, station_config: StationConfig) -> Dict[str, Any]:
        """완전한 IoT 메시지 생성"""
        now = datetime.now()
        
        # 각 데이터 카테고리 생성
        sensor_data = self.generate_sensor_data(station_config)
        production_data = self.generate_production_data(station_config)
        quality_data = self.generate_quality_data(station_config)
        alerts = self.generate_alerts(station_config, sensor_data, production_data)
        station_specific = self.generate_station_specific_data(station_config)
        
        # 현재 효율성을 스테이션 상태에 저장
        self.station_states[station_config.station_id]["current_efficiency"] = sensor_data["efficiency_raw"]
        
        # 파생 메트릭 계산
        derived_metrics = {
            "efficiency": sensor_data["efficiency_raw"],
            "performance_score": min(1.0, production_data["throughput_per_hour"] / 100),
            "quality_index": quality_data["score"],
            "overall_equipment_effectiveness": round(
                sensor_data["efficiency_raw"] * 
                (production_data["throughput_per_hour"] / station_config.production_rate) * 
                quality_data["score"], 3
            )
        }
        
        # 최종 메시지 구성
        message = {
            "station_id": station_config.station_id,
            "timestamp": now.isoformat(),
            "process_type": station_config.process_type,
            "location": station_config.location,
            "sensors": sensor_data,
            "production": production_data,
            "quality": quality_data,
            "alerts": alerts,
            "derived_metrics": derived_metrics,
            "processedAt": now.isoformat()
        }
        
        # 스테이션별 특화 데이터 추가
        if station_specific:
            message[f"{station_config.process_type.lower()}_specific"] = station_specific
            
        return message
    
    def publish_station_data(self, station_id: str):
        """특정 스테이션 데이터 발송"""
        if station_id not in self.stations:
            return
            
        station_config = self.stations[station_id]
        message = self.create_iot_message(station_config)
        
        topic = f"{self.base_topic}/{station_id}/data"
        payload = json.dumps(message, ensure_ascii=False, indent=None)
        
        try:
            result = self.mqtt_client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📤 [{station_id}] 데이터 전송 완료 - 효율성: {message['sensors']['efficiency_raw']:.3f}")
            else:
                print(f"❌ [{station_id}] 데이터 전송 실패")
        except Exception as e:
            print(f"❌ [{station_id}] 전송 오류: {e}")
    
    def simulation_loop(self):
        """시뮬레이션 메인 루프"""
        print("🚀 IoT 데이터 시뮬레이션 시작!")
        print(f"📡 MQTT 토픽: {self.base_topic}/{{STATION_ID}}/data")
        print(f"🏭 시뮬레이션 스테이션: {list(self.stations.keys())}")
        print("🛑 종료하려면 Ctrl+C를 누르세요\n")
        
        self.simulation_start_time = datetime.now()
        
        while self.running:
            try:
                # 모든 스테이션 데이터 전송
                for station_id in self.stations.keys():
                    if self.running:  # 중간에 종료 신호가 올 수 있음
                        self.publish_station_data(station_id)
                        time.sleep(0.5)  # 스테이션 간 간격
                
                # 다음 전송까지 대기 (5초 간격)
                if self.running:
                    time.sleep(4.5)  # 0.5 * 5개 스테이션 = 2.5초 + 4.5초 = 7초 총 간격
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 시뮬레이션 오류: {e}")
                time.sleep(1)
    
    def start(self):
        """시뮬레이션 시작"""
        if not self.connect_mqtt():
            return False
            
        self.running = True
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.simulation_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            
        return True
    
    def stop(self):
        """시뮬레이션 중지"""
        print("\n🛑 IoT 시뮬레이션 중지 중...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
        if self.simulation_start_time:
            runtime = datetime.now() - self.simulation_start_time
            print(f"⏱️  총 실행 시간: {str(runtime).split('.')[0]}")
            
        print("✅ IoT 시뮬레이션 종료 완료")
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\n🛑 종료 신호 감지 (Signal: {signum})")
        self.running = False

def main():
    """메인 함수"""
    print("🏭 제조 공정 IoT 데이터 시뮬레이터 v1.0")
    print("=" * 50)
    
    simulator = IoTDataSimulator()
    simulator.start()

if __name__ == "__main__":
    main()