"""
센서 기반 차량 감지 및 제어 시스템
현대차 의장공정 실제 방식 모방
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class SensorType(Enum):
    """센서 타입"""
    PHOTO_SENSOR = "photo_sensor"          # 포토센서 (차량 감지)
    RFID_READER = "rfid_reader"           # RFID 리더 (차량 식별)
    PRESSURE_SENSOR = "pressure_sensor"    # 압력센서 (작업자 안전)
    PROXIMITY_SENSOR = "proximity_sensor"  # 근접센서 (정밀 위치)
    BARCODE_SCANNER = "barcode_scanner"    # 바코드 스캐너 (작업지시)

@dataclass
class SensorReading:
    """센서 판독값"""
    sensor_id: str
    sensor_type: SensorType
    station_id: str
    timestamp: float
    value: bool
    vehicle_id: Optional[str] = None
    signal_strength: float = 100.0
    error_code: Optional[str] = None

class StationSensorSet:
    """스테이션별 센서 세트"""
    
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.sensors = {
            "entry_photo": SensorType.PHOTO_SENSOR,      # 진입 감지
            "position_proximity": SensorType.PROXIMITY_SENSOR,  # 정확한 위치
            "rfid_reader": SensorType.RFID_READER,       # 차량 식별
            "work_pressure": SensorType.PRESSURE_SENSOR,  # 작업 감지
            "exit_photo": SensorType.PHOTO_SENSOR,       # 출구 감지
            "barcode_scanner": SensorType.BARCODE_SCANNER # 작업지시 확인
        }
        
        # 센서 상태
        self.sensor_states = {sensor: False for sensor in self.sensors.keys()}
        self.last_readings = {}
        
    def detect_vehicle_entry(self, vehicle_id: str) -> SensorReading:
        """차량 진입 감지"""
        sensor_id = f"{self.station_id}_entry_photo"
        
        # 실제 센서 정확도 모사 (99% 정확도)
        detection_success = random.random() < 0.99
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=SensorType.PHOTO_SENSOR,
            station_id=self.station_id,
            timestamp=time.time(),
            value=detection_success,
            vehicle_id=vehicle_id if detection_success else None,
            signal_strength=random.uniform(95.0, 100.0),
            error_code=None if detection_success else "DETECTION_FAILED"
        )
        
        self.sensor_states["entry_photo"] = detection_success
        self.last_readings["entry_photo"] = reading
        return reading
    
    def verify_vehicle_position(self, vehicle_id: str) -> SensorReading:
        """차량 정확한 위치 확인"""
        sensor_id = f"{self.station_id}_position_proximity"
        
        # 근접센서 정밀도 (±2mm 이내)
        position_accuracy = random.random() < 0.95
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=SensorType.PROXIMITY_SENSOR,
            station_id=self.station_id,
            timestamp=time.time(),
            value=position_accuracy,
            vehicle_id=vehicle_id,
            signal_strength=random.uniform(90.0, 100.0),
            error_code=None if position_accuracy else "POSITION_MISALIGNMENT"
        )
        
        self.sensor_states["position_proximity"] = position_accuracy
        self.last_readings["position_proximity"] = reading
        return reading
    
    def read_vehicle_id(self, vehicle_id: str) -> SensorReading:
        """RFID로 차량 ID 읽기"""
        sensor_id = f"{self.station_id}_rfid_reader"
        
        # RFID 읽기 성공률 (98%)
        read_success = random.random() < 0.98
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=SensorType.RFID_READER,
            station_id=self.station_id,
            timestamp=time.time(),
            value=read_success,
            vehicle_id=vehicle_id if read_success else None,
            signal_strength=random.uniform(85.0, 100.0),
            error_code=None if read_success else "RFID_READ_ERROR"
        )
        
        self.sensor_states["rfid_reader"] = read_success
        self.last_readings["rfid_reader"] = reading
        return reading
    
    def detect_work_completion(self, vehicle_id: str) -> SensorReading:
        """작업 완료 감지 (압력센서 + 시간)"""
        sensor_id = f"{self.station_id}_work_pressure"
        
        # 작업 완료 확인 (작업자 안전센서 해제)
        work_completed = random.random() < 0.97
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=SensorType.PRESSURE_SENSOR,
            station_id=self.station_id,
            timestamp=time.time(),
            value=work_completed,
            vehicle_id=vehicle_id,
            signal_strength=random.uniform(92.0, 100.0),
            error_code=None if work_completed else "WORK_INCOMPLETE"
        )
        
        self.sensor_states["work_pressure"] = work_completed
        self.last_readings["work_pressure"] = reading
        return reading
    
    def detect_vehicle_exit(self, vehicle_id: str) -> SensorReading:
        """차량 출구 감지"""
        sensor_id = f"{self.station_id}_exit_photo"
        
        # 출구 감지 성공률 (99.5%)
        exit_detected = random.random() < 0.995
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=SensorType.PHOTO_SENSOR,
            station_id=self.station_id,
            timestamp=time.time(),
            value=exit_detected,
            vehicle_id=vehicle_id if exit_detected else None,
            signal_strength=random.uniform(96.0, 100.0),
            error_code=None if exit_detected else "EXIT_DETECTION_FAILED"
        )
        
        self.sensor_states["exit_photo"] = exit_detected
        self.last_readings["exit_photo"] = reading
        
        # 출구 감지 시 모든 센서 리셋
        if exit_detected:
            self._reset_sensors()
        
        return reading
    
    def _reset_sensors(self):
        """센서 상태 리셋"""
        self.sensor_states = {sensor: False for sensor in self.sensors.keys()}
    
    def get_sensor_status(self) -> Dict:
        """센서 상태 정보"""
        return {
            "station_id": self.station_id,
            "sensors": self.sensor_states,
            "last_readings": {k: {
                "sensor_id": v.sensor_id,
                "timestamp": v.timestamp,
                "value": v.value,
                "vehicle_id": v.vehicle_id,
                "signal_strength": v.signal_strength,
                "error_code": v.error_code
            } for k, v in self.last_readings.items()},
            "all_sensors_ready": all(self.sensor_states.values()),
            "timestamp": time.time()
        }

class ConveyorController:
    """컨베이어 제어 시스템"""
    
    def __init__(self):
        self.conveyor_speed = 3.0  # m/min (현대차 실제 속도)
        self.station_distance = 15.0  # 스테이션 간 거리 (m)
        self.is_moving = False
        self.current_position = 0.0
        
    def calculate_travel_time(self) -> float:
        """스테이션 간 이동시간 계산"""
        return (self.station_distance / self.conveyor_speed) * 60  # 초 단위
    
    def start_conveyor(self):
        """컨베이어 시작"""
        self.is_moving = True
        
    def stop_conveyor(self):
        """컨베이어 정지"""
        self.is_moving = False
        
    def get_conveyor_status(self) -> Dict:
        """컨베이어 상태"""
        return {
            "speed": self.conveyor_speed,
            "is_moving": self.is_moving,
            "current_position": self.current_position,
            "travel_time_per_station": self.calculate_travel_time(),
            "timestamp": time.time()
        }

class ProductionLineController:
    """생산라인 통합 제어 시스템"""
    
    def __init__(self, station_ids: List[str]):
        self.station_sensors = {
            station_id: StationSensorSet(station_id) 
            for station_id in station_ids
        }
        self.conveyor = ConveyorController()
        self.cycle_time = 90  # 통일된 90초 사이클
        
    def process_vehicle_at_station(self, vehicle_id: str, station_id: str) -> Dict:
        """스테이션에서 차량 처리 프로세스"""
        if station_id not in self.station_sensors:
            return {"error": "Invalid station ID"}
        
        sensor_set = self.station_sensors[station_id]
        process_log = []
        
        # 1. 차량 진입 감지
        entry_reading = sensor_set.detect_vehicle_entry(vehicle_id)
        process_log.append(("vehicle_entry", entry_reading))
        
        if not entry_reading.value:
            return {"status": "entry_failed", "log": process_log}
        
        # 2. 정확한 위치 확인
        position_reading = sensor_set.verify_vehicle_position(vehicle_id)
        process_log.append(("position_verify", position_reading))
        
        if not position_reading.value:
            return {"status": "positioning_failed", "log": process_log}
        
        # 3. 차량 ID 확인
        rfid_reading = sensor_set.read_vehicle_id(vehicle_id)
        process_log.append(("vehicle_id_read", rfid_reading))
        
        # 4. 작업 시작 (컨베이어 정지)
        self.conveyor.stop_conveyor()
        work_start_time = time.time()
        
        # 5. 작업 완료 대기 (90초 사이클)
        time.sleep(0.1)  # 시뮬레이션용 짧은 대기
        
        # 6. 작업 완료 감지
        work_reading = sensor_set.detect_work_completion(vehicle_id)
        process_log.append(("work_completion", work_reading))
        
        # 7. 차량 출구 감지
        exit_reading = sensor_set.detect_vehicle_exit(vehicle_id)
        process_log.append(("vehicle_exit", exit_reading))
        
        # 8. 컨베이어 재시작
        self.conveyor.start_conveyor()
        
        return {
            "status": "completed",
            "vehicle_id": vehicle_id,
            "station_id": station_id,
            "work_duration": self.cycle_time,
            "process_log": process_log,
            "sensor_status": sensor_set.get_sensor_status(),
            "conveyor_status": self.conveyor.get_conveyor_status(),
            "timestamp": time.time()
        }
    
    def get_system_status(self) -> Dict:
        """전체 시스템 상태"""
        return {
            "conveyor": self.conveyor.get_conveyor_status(),
            "stations": {
                station_id: sensors.get_sensor_status() 
                for station_id, sensors in self.station_sensors.items()
            },
            "cycle_time": self.cycle_time,
            "timestamp": time.time()
        }