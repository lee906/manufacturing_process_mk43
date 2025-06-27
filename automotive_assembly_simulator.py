#!/usr/bin/env python3
"""
자동차 의장공정 시계열 데이터 시뮬레이터
실제 의장공정 흐름을 기반으로 시계열 데이터 생성
"""

import json
import time
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum
import paho.mqtt.client as mqtt
import threading
import queue
import logging

# 의장공정 작업 단계 정의
class AssemblyStage(Enum):
    DOOR_INSTALLATION = "door_installation"      # 도어 설치
    SEAT_INSTALLATION = "seat_installation"      # 시트 설치  
    DASHBOARD_ASSEMBLY = "dashboard_assembly"    # 대시보드 조립
    WIRING_HARNESS = "wiring_harness"           # 와이어링 하네스
    INTERIOR_TRIM = "interior_trim"             # 내장재 부착
    FINAL_INSPECTION = "final_inspection"       # 최종 검사
    QUALITY_CHECK = "quality_check"             # 품질 검증
    COMPLETION = "completion"                   # 완성

class WorkStatus(Enum):
    WAITING = "waiting"                 # 대기
    IN_PROGRESS = "in_progress"        # 작업 중
    COMPLETED = "completed"            # 완료
    ERROR = "error"                    # 오류
    MAINTENANCE = "maintenance"        # 정비

@dataclass
class VehicleUnit:
    """의장공정을 거치는 차량 단위"""
    unit_id: str
    model: str
    color: str
    current_stage: AssemblyStage
    start_time: datetime
    stage_start_time: datetime
    estimated_completion: datetime
    actual_times: Dict[str, float]  # 각 단계별 실제 소요시간
    quality_scores: Dict[str, float]  # 각 단계별 품질 점수
    defects: List[str]  # 발견된 결함 리스트
    worker_id: str
    station_id: str

@dataclass  
class StationStatus:
    """작업 스테이션 상태"""
    station_id: str
    stage: AssemblyStage
    status: WorkStatus
    current_unit: Optional[VehicleUnit]
    worker_count: int
    temperature: float
    humidity: float
    noise_level: float
    tool_status: Dict[str, str]  # 공구 상태
    cycle_time_target: float  # 목표 사이클 타임
    cycle_time_actual: float  # 실제 사이클 타임
    efficiency: float
    last_maintenance: datetime
    error_count: int

class AutomotiveAssemblySimulator:
    def __init__(self):
        self.running = False
        self.mqtt_client = None
        
        # MQTT 설정
        self.broker_host = "localhost"
        self.broker_port = 1883
        self.base_topic = "automotive/assembly"
        
        # 시뮬레이션 설정
        self.simulation_speed = 1.0  # 1.0 = 실시간, 10.0 = 10배속
        self.shift_start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        
        # 차량 모델별 설정
        self.vehicle_models = {
            "SEDAN_A": {"cycle_time": 180, "complexity": 1.0},    # 3분
            "SUV_B": {"cycle_time": 240, "complexity": 1.2},     # 4분
            "TRUCK_C": {"cycle_time": 300, "complexity": 1.5}    # 5분
        }
        
        # 작업 스테이션 초기화
        self.stations = self._initialize_stations()
        
        # 진행 중인 차량들
        self.vehicles_in_process = queue.Queue()
        self.completed_vehicles = []
        
        # 통계
        self.daily_stats = {
            "total_completed": 0,
            "total_defects": 0,
            "avg_cycle_time": 0,
            "efficiency": 0,
            "shift_start": self.shift_start_time
        }
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _initialize_stations(self) -> Dict[str, StationStatus]:
        """작업 스테이션 초기화"""
        stations = {}
        
        station_configs = [
            {"id": "DOOR_01", "stage": AssemblyStage.DOOR_INSTALLATION, "target_time": 180},
            {"id": "SEAT_01", "stage": AssemblyStage.SEAT_INSTALLATION, "target_time": 150},
            {"id": "DASH_01", "stage": AssemblyStage.DASHBOARD_ASSEMBLY, "target_time": 240},
            {"id": "WIRE_01", "stage": AssemblyStage.WIRING_HARNESS, "target_time": 200},
            {"id": "TRIM_01", "stage": AssemblyStage.INTERIOR_TRIM, "target_time": 120},
            {"id": "INSP_01", "stage": AssemblyStage.FINAL_INSPECTION, "target_time": 90},
            {"id": "QUAL_01", "stage": AssemblyStage.QUALITY_CHECK, "target_time": 60}
        ]
        
        for config in station_configs:
            stations[config["id"]] = StationStatus(
                station_id=config["id"],
                stage=config["stage"],
                status=WorkStatus.WAITING,
                current_unit=None,
                worker_count=2,
                temperature=22.0 + (hash(config["id"]) % 10),  # 22-32도
                humidity=45.0 + (hash(config["id"]) % 20),     # 45-65%
                noise_level=60.0 + (hash(config["id"]) % 20), # 60-80dB
                tool_status=self._generate_tool_status(config["stage"]),
                cycle_time_target=config["target_time"],
                cycle_time_actual=config["target_time"],
                efficiency=0.85,
                last_maintenance=datetime.now() - timedelta(hours=hash(config["id"]) % 24),
                error_count=0
            )
        
        return stations
    
    def _generate_tool_status(self, stage: AssemblyStage) -> Dict[str, str]:
        """단계별 공구 상태 생성"""
        tools = {
            AssemblyStage.DOOR_INSTALLATION: ["pneumatic_gun", "torque_wrench", "door_lift"],
            AssemblyStage.SEAT_INSTALLATION: ["seat_lift", "bolt_gun", "alignment_jig"],
            AssemblyStage.DASHBOARD_ASSEMBLY: ["screwdriver", "clip_gun", "wire_tester"],
            AssemblyStage.WIRING_HARNESS: ["wire_tester", "crimping_tool", "multimeter"],
            AssemblyStage.INTERIOR_TRIM: ["trim_gun", "adhesive_gun", "trim_knife"],
            AssemblyStage.FINAL_INSPECTION: ["inspection_camera", "torque_meter", "leak_tester"],
            AssemblyStage.QUALITY_CHECK: ["quality_scanner", "defect_detector", "measurement_tool"]
        }
        
        stage_tools = tools.get(stage, ["generic_tool"])
        return {tool: "operational" for tool in stage_tools}
    
    def create_new_vehicle(self) -> VehicleUnit:
        """새 차량 생성"""
        now = datetime.now()
        vehicle_id = f"VIN_{now.strftime('%Y%m%d_%H%M%S')}_{hash(str(now)) % 1000:03d}"
        
        models = list(self.vehicle_models.keys())
        model = models[hash(vehicle_id) % len(models)]
        
        colors = ["WHITE", "BLACK", "SILVER", "RED", "BLUE"]
        color = colors[hash(vehicle_id) % len(colors)]
        
        # 예상 완료 시간 계산 (모든 단계 사이클 타임 합계)
        total_cycle_time = sum(s.cycle_time_target for s in self.stations.values())
        estimated_completion = now + timedelta(seconds=total_cycle_time)
        
        return VehicleUnit(
            unit_id=vehicle_id,
            model=model,
            color=color,
            current_stage=AssemblyStage.DOOR_INSTALLATION,
            start_time=now,
            stage_start_time=now,
            estimated_completion=estimated_completion,
            actual_times={},
            quality_scores={},
            defects=[],
            worker_id=f"WORKER_{hash(vehicle_id) % 50 + 1:03d}",
            station_id="DOOR_01"
        )
    
    def simulate_work_progress(self, station: StationStatus, vehicle: VehicleUnit) -> bool:
        """작업 진행 시뮬레이션"""
        now = datetime.now()
        stage_duration = (now - vehicle.stage_start_time).total_seconds()
        
        # 실제 작업 시간은 목표 시간 기준으로 변동 (±20%)
        base_time = station.cycle_time_target
        actual_time = base_time * (0.8 + 0.4 * (hash(vehicle.unit_id) % 100) / 100)
        
        # 작업 완료 여부 확인
        if stage_duration >= actual_time:
            # 작업 완료
            station.cycle_time_actual = stage_duration
            vehicle.actual_times[station.stage.value] = stage_duration
            
            # 품질 점수 생성 (90-100점)
            quality_score = 90 + 10 * (hash(f"{vehicle.unit_id}_{station.stage.value}") % 100) / 100
            vehicle.quality_scores[station.stage.value] = quality_score
            
            # 결함 발생 확인 (5% 확률)
            if hash(f"{vehicle.unit_id}_{station.stage.value}") % 100 < 5:
                defect_types = {
                    AssemblyStage.DOOR_INSTALLATION: "door_alignment_issue",
                    AssemblyStage.SEAT_INSTALLATION: "seat_bolt_loose",
                    AssemblyStage.DASHBOARD_ASSEMBLY: "dashboard_gap",
                    AssemblyStage.WIRING_HARNESS: "wire_connection_loose",
                    AssemblyStage.INTERIOR_TRIM: "trim_bubble",
                    AssemblyStage.FINAL_INSPECTION: "assembly_tolerance_out",
                    AssemblyStage.QUALITY_CHECK: "quality_standard_fail"
                }
                vehicle.defects.append(defect_types[station.stage])
            
            return True  # 작업 완료
        
        return False  # 작업 진행 중
    
    def move_to_next_stage(self, vehicle: VehicleUnit) -> Optional[str]:
        """다음 단계로 차량 이동"""
        stages = list(AssemblyStage)
        current_index = stages.index(vehicle.current_stage)
        
        if current_index < len(stages) - 1:
            # 다음 단계로 이동
            vehicle.current_stage = stages[current_index + 1]
            vehicle.stage_start_time = datetime.now()
            
            # 다음 스테이션 찾기
            for station_id, station in self.stations.items():
                if station.stage == vehicle.current_stage and station.status == WorkStatus.WAITING:
                    vehicle.station_id = station_id
                    return station_id
        else:
            # 모든 단계 완료
            vehicle.current_stage = AssemblyStage.COMPLETION
            return "COMPLETED"
        
        return None
    
    def generate_station_telemetry(self, station: StationStatus) -> Dict[str, Any]:
        """스테이션 텔레메트리 데이터 생성"""
        now = datetime.now()
        
        # 시간대별 변동 요인
        hour = now.hour
        shift_factor = 1.0
        if 8 <= hour <= 16:  # 주간 근무
            shift_factor = 1.0
        elif 16 <= hour <= 24:  # 저녁 근무  
            shift_factor = 0.95
        else:  # 야간 근무
            shift_factor = 0.90
        
        # 환경 데이터 (실제적인 변동)
        base_temp = station.temperature
        temp_variation = 2 * math.sin(2 * math.pi * hour / 24)  # 일일 온도 변화
        current_temp = base_temp + temp_variation + (hash(str(now)) % 20 - 10) / 10
        
        # 습도는 온도와 반비례
        current_humidity = station.humidity - temp_variation + (hash(str(now)) % 10 - 5) / 10
        
        # 소음 레벨 (작업 중일 때 증가)
        noise_base = station.noise_level
        if station.status == WorkStatus.IN_PROGRESS:
            noise_base += 10  # 작업 중 소음 증가
        current_noise = noise_base + (hash(str(now)) % 10 - 5)
        
        # 효율성 계산 (목표 대비 실제 성능)
        if station.cycle_time_target > 0:
            efficiency = min(1.0, station.cycle_time_target / station.cycle_time_actual) * shift_factor
        else:
            efficiency = station.efficiency * shift_factor
        
        # 진동 데이터 (공구 사용 시 증가)
        vibration = 0.1
        if station.status == WorkStatus.IN_PROGRESS:
            vibration += 0.3 + (hash(str(now)) % 20) / 100
        
        return {
            "station_id": station.station_id,
            "timestamp": now.isoformat(),
            "stage": station.stage.value,
            "status": station.status.value,
            "environmental": {
                "temperature": round(current_temp, 1),
                "humidity": round(current_humidity, 1),
                "noise_level": round(current_noise, 1),
                "vibration": round(vibration, 3)
            },
            "performance": {
                "cycle_time_target": station.cycle_time_target,
                "cycle_time_actual": round(station.cycle_time_actual, 1),
                "efficiency": round(efficiency, 3),
                "worker_count": station.worker_count
            },
            "tools": station.tool_statusㄹ,
            "maintenance": {
                "last_maintenance": station.last_maintenance.isoformat(),
                "next_maintenance": (station.last_maintenance + timedelta(hours=168)).isoformat(),  # 주간 정비
                "error_count": station.error_count
            },
            "current_unit": {
                "unit_id": station.current_unit.unit_id if station.current_unit else None,
                "model": station.current_unit.model if station.current_unit else None,
                "color": station.current_unit.color if station.current_unit else None,
                "progress": self._calculate_stage_progress(station) if station.current_unit else 0
            }
        }
    
    def _calculate_stage_progress(self, station: StationStatus) -> float:
        """현재 단계 진행률 계산"""
        if not station.current_unit:
            return 0.0
        
        now = datetime.now()
        elapsed = (now - station.current_unit.stage_start_time).total_seconds()
        target_time = station.cycle_time_target
        
        return min(1.0, elapsed / target_time)
    
    def connect_mqtt(self):
        """MQTT 브로커 연결"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"MQTT 연결 실패: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info(f"MQTT 브로커 연결 성공 ({self.broker_host}:{self.broker_port})")
        else:
            self.logger.error(f"MQTT 연결 실패, 코드: {rc}")
    
    def publish_telemetry(self, station_id: str, data: Dict[str, Any]):
        """텔레메트리 데이터 발송"""
        topic = f"{self.base_topic}/{station_id}/telemetry"
        payload = json.dumps(data, ensure_ascii=False, indent=None)
        
        try:
            result = self.mqtt_client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"📤 [{station_id}] 텔레메트리 전송")
        except Exception as e:
            self.logger.error(f"❌ [{station_id}] 전송 실패: {e}")
    
    def simulation_loop(self):
        """메인 시뮬레이션 루프"""
        self.logger.info("🚗 자동차 의장공정 시뮬레이션 시작!")
        self.logger.info(f"📍 시프트 시작: {self.shift_start_time.strftime('%H:%M')}")
        
        vehicle_spawn_interval = 300  # 5분마다 새 차량 투입
        last_vehicle_spawn = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 새 차량 투입
                if current_time - last_vehicle_spawn >= vehicle_spawn_interval:
                    new_vehicle = self.create_new_vehicle()
                    self.vehicles_in_process.put(new_vehicle)
                    
                    # 첫 번째 스테이션에 배정
                    first_station = self.stations["DOOR_01"]
                    if first_station.status == WorkStatus.WAITING:
                        first_station.current_unit = new_vehicle
                        first_station.status = WorkStatus.IN_PROGRESS
                        self.logger.info(f"🆕 새 차량 투입: {new_vehicle.unit_id} ({new_vehicle.model})")
                    
                    last_vehicle_spawn = current_time
                
                # 각 스테이션 처리
                for station_id, station in self.stations.items():
                    if station.current_unit and station.status == WorkStatus.IN_PROGRESS:
                        # 작업 진행 시뮬레이션
                        work_completed = self.simulate_work_progress(station, station.current_unit)
                        
                        if work_completed:
                            self.logger.info(f"✅ [{station_id}] {station.current_unit.unit_id} 작업 완료")
                            
                            # 다음 단계로 이동
                            next_station_id = self.move_to_next_stage(station.current_unit)
                            
                            if next_station_id == "COMPLETED":
                                # 전체 공정 완료
                                self.completed_vehicles.append(station.current_unit)
                                self.daily_stats["total_completed"] += 1
                                self.logger.info(f"🏁 차량 완성: {station.current_unit.unit_id}")
                                
                                station.current_unit = None
                                station.status = WorkStatus.WAITING
                            elif next_station_id:
                                # 다음 스테이션으로 이동
                                next_station = self.stations[next_station_id]
                                if next_station.status == WorkStatus.WAITING:
                                    next_station.current_unit = station.current_unit
                                    next_station.status = WorkStatus.IN_PROGRESS
                                    
                                    station.current_unit = None
                                    station.status = WorkStatus.WAITING
                    
                    # 텔레메트리 데이터 전송
                    telemetry = self.generate_station_telemetry(station)
                    self.publish_telemetry(station_id, telemetry)
                
                # 시뮬레이션 속도 조절
                time.sleep(5.0 / self.simulation_speed)  # 5초 간격
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"시뮬레이션 오류: {e}")
                time.sleep(1)
    
    def start(self):
        """시뮬레이션 시작"""
        if not self.connect_mqtt():
            return False
        
        self.running = True
        
        try:
            self.simulation_loop()
        except KeyboardInterrupt:
            self.logger.info("사용자 종료 요청")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """시뮬레이션 중지"""
        self.logger.info("🛑 의장공정 시뮬레이션 중지")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        # 최종 통계 출력
        self.logger.info(f"📊 완성된 차량: {self.daily_stats['total_completed']}대")
        self.logger.info("✅ 시뮬레이션 종료")

def main():
    """메인 함수"""
    print("🚗 자동차 의장공정 시계열 데이터 시뮬레이터 v2.0")
    print("=" * 60)
    
    simulator = AutomotiveAssemblySimulator()
    simulator.start()

if __name__ == "__main__":
    main()