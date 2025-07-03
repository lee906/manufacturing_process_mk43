"""
차량 위치 추적 시스템 (현대차 의장공정 방식)
센서 기반 실시간 차량 위치 및 컨베이어 제어
"""

import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from .sensor_system import ProductionLineController, SensorReading

class VehicleStatus(Enum):
    """차량 상태"""
    WAITING = "waiting"          # 대기 중
    IN_PROCESS = "in_process"    # 작업 중
    MOVING = "moving"            # 이동 중
    COMPLETED = "completed"      # 완료
    FAILED = "failed"           # 실패/불량

@dataclass
class VehiclePosition:
    """차량 위치 정보"""
    x: float                    # X 좌표 (0-1000)
    y: float                    # Y 좌표 (0-600)
    station_id: str             # 현재 스테이션 ID
    station_progress: float     # 스테이션 내 진행률 (0-100%)
    
@dataclass 
class Vehicle:
    """차량 정보"""
    vehicle_id: str            # 차량 고유 ID
    rfid_tag: str              # RFID 태그
    model: str                 # 차량 모델
    color: str                 # 차량 색상
    status: VehicleStatus      # 현재 상태
    position: VehiclePosition  # 현재 위치
    created_time: datetime     # 생성 시간
    current_station_index: int # 현재 스테이션 인덱스
    total_stations: int        # 전체 스테이션 수
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "vehicle_id": self.vehicle_id,
            "rfid_tag": self.rfid_tag,
            "model": self.model,
            "color": self.color,
            "status": self.status.value,
            "position": asdict(self.position),
            "created_time": self.created_time.isoformat(),
            "current_station_index": self.current_station_index,
            "total_stations": self.total_stations,
            "progress_percentage": round((self.current_station_index / self.total_stations) * 100, 1)
        }

class VehicleTracker:
    """차량 추적 시스템"""
    
    def __init__(self):
        # 현대차 모델 및 색상
        self.vehicle_models = ["아반떼", "투싼", "팰리세이드", "코나", "그랜저"]
        self.vehicle_colors = ["화이트", "블랙", "실버", "레드", "블루", "그레이"]
        
        # 공정 스테이션 순서 (실제 의장공정 순서)
        self.station_sequence = [
            "A01_DOOR",          # 도어 탈거
            "A02_WIRING",        # 와이어링
            "A03_HEADLINER",     # 헤드라이너
            "A04_CRASH_PAD",     # 크래쉬 패드
            "B01_FUEL_TANK",     # 연료탱크
            "B02_CHASSIS_MERGE", # 샤시 메리지
            "B03_MUFFLER",       # 머플러
            "C01_FEM",           # FEM 모듈
            "C02_GLASS",         # 글라스
            "C03_SEAT",          # 시트
            "C04_BUMPER",        # 범퍼
            "C05_TIRE",          # 타이어
            "D01_WHEEL_ALIGNMENT", # 휠 얼라이언트
            "D02_HEADLAMP",      # 헤드램프
            "D03_WATER_LEAK_TEST" # 수밀 검사
        ]
        
        # Factory2DTwin.jsx 좌표계와 일치시킨 스테이션 위치
        self.station_positions = {
            # A라인 (y=150, 좌측에서 우측으로)
            "A01_DOOR": (150, 150),          # 도어탈거 x=150
            "A02_WIRING": (300, 150),        # 와이어링 x=300
            "A03_HEADLINER": (450, 150),     # 헤드라이너 x=450
            "A04_CRASH_PAD": (750, 150),     # 크래쉬패드 x=750 (width=350 중앙)
            
            # B라인 (y=350, 우측에서 좌측으로)
            "B01_FUEL_TANK": (850, 350),     # 연료탱크 x=850
            "B02_CHASSIS_MERGE": (500, 350), # 샤시메리지 x=500 (width=500 중앙)
            "B03_MUFFLER": (150, 350),       # 머플러 x=150
            
            # C라인 (y=550, 좌측에서 우측으로)
            "C01_FEM": (150, 550),           # FEM x=150
            "C02_GLASS": (300, 550),         # 글라스 x=300
            "C03_SEAT": (450, 550),          # 시트 x=450
            "C04_BUMPER": (600, 550),        # 범퍼 x=600
            "C05_TIRE": (750, 550),          # 타이어 x=750
            
            # D라인 (y=750, 우측에서 좌측으로)
            "D01_WHEEL_ALIGNMENT": (800, 750), # 휠 얼라이언트 x=800
            "D02_HEADLAMP": (650, 750),        # 헤드램프 x=650
            "D03_WATER_LEAK_TEST": (320, 750) # 수밀검사 x=320 (width=450 중앙)
        }
        
        # 활성 차량 목록
        self.active_vehicles: Dict[str, Vehicle] = {}
        
        # 차량 생성 설정
        self.vehicle_creation_interval = 90  # 90초마다 새 차량 생성 (사이클타임과 동일)
        self.last_vehicle_creation = 0
        self.max_concurrent_vehicles = 8     # 최대 동시 생산 차량 수 (버퍼 고려)
        
        # 센서 기반 생산라인 제어 시스템
        self.production_controller = ProductionLineController(self.station_sequence)
        
        # 컨베이어 이동 시간 (실제 현대차 기준: 5초)
        self.conveyor_travel_time = 5.0
        
    def create_new_vehicle(self) -> Vehicle:
        """새 차량 생성"""
        vehicle_id = f"VH_{int(time.time() * 1000)}"
        rfid_tag = f"RFID_{uuid.uuid4().hex[:8].upper()}"
        model = random.choice(self.vehicle_models)
        color = random.choice(self.vehicle_colors)
        
        # 첫 번째 스테이션 위치에서 시작
        first_station = self.station_sequence[0]
        x, y = self.station_positions[first_station]
        
        position = VehiclePosition(
            x=float(x),
            y=float(y),
            station_id=first_station,
            station_progress=0.0
        )
        
        vehicle = Vehicle(
            vehicle_id=vehicle_id,
            rfid_tag=rfid_tag,
            model=model,
            color=color,
            status=VehicleStatus.WAITING,
            position=position,
            created_time=datetime.now(),
            current_station_index=0,
            total_stations=len(self.station_sequence)
        )
        
        return vehicle
    
    def move_vehicle_to_next_station(self, vehicle: Vehicle) -> bool:
        """차량을 다음 스테이션으로 이동"""
        if vehicle.current_station_index >= len(self.station_sequence) - 1:
            # 마지막 스테이션 완료
            vehicle.status = VehicleStatus.COMPLETED
            return True
        
        # 다음 스테이션으로 이동
        vehicle.current_station_index += 1
        next_station = self.station_sequence[vehicle.current_station_index]
        x, y = self.station_positions[next_station]
        
        vehicle.position.x = float(x)
        vehicle.position.y = float(y)
        vehicle.position.station_id = next_station
        vehicle.position.station_progress = 0.0
        vehicle.status = VehicleStatus.WAITING
        
        return False
    
    def update_vehicle_progress(self, vehicle: Vehicle, progress_delta: float):
        """차량의 스테이션 내 진행률 업데이트"""
        vehicle.position.station_progress = min(100.0, 
            vehicle.position.station_progress + progress_delta)
        
        if vehicle.position.station_progress >= 100.0:
            # 현재 스테이션 작업 완료
            completed = self.move_vehicle_to_next_station(vehicle)
            if completed:
                # 전체 공정 완료
                pass
    
    def simulate_vehicle_movement(self, vehicle: Vehicle) -> Dict:
        """센서 기반 차량 이동 시뮬레이션 (현대차 의장공정 방식)"""
        current_time = time.time()
        
        # 차량이 스테이션에 새로 도착한 경우
        if vehicle.position.station_progress == 0.0:
            # 센서 기반 차량 처리 시작
            processing_result = self.production_controller.process_vehicle_at_station(
                vehicle.vehicle_id, 
                vehicle.position.station_id
            )
            
            vehicle.sensor_data = processing_result
            vehicle.work_start_time = current_time
            vehicle.status = VehicleStatus.IN_PROCESS
            
        # 90초 사이클 타임 기준으로 진행률 계산
        elif vehicle.status == VehicleStatus.IN_PROCESS:
            elapsed_time = current_time - getattr(vehicle, 'work_start_time', current_time)
            cycle_time = 90.0  # 통일된 90초 사이클
            
            # 차량 모델별 작업 속도 조정
            speed_multiplier = {
                "아반떼": 1.0,
                "투싼": 0.95,
                "팰리세이드": 0.85,  # 대형차는 작업이 조금 더 오래 걸림
                "코나": 0.98,
                "그랜저": 0.90
            }.get(vehicle.model, 1.0)
            
            adjusted_cycle_time = cycle_time / speed_multiplier
            progress_percentage = (elapsed_time / adjusted_cycle_time) * 100.0
            
            vehicle.position.station_progress = min(100.0, progress_percentage)
            
            # 작업 완료 시
            if vehicle.position.station_progress >= 100.0:
                vehicle.status = VehicleStatus.MOVING
                vehicle.conveyor_start_time = current_time
        
        # 컨베이어 이동 중 (5초)
        elif vehicle.status == VehicleStatus.MOVING:
            elapsed_move_time = current_time - getattr(vehicle, 'conveyor_start_time', current_time)
            
            if elapsed_move_time >= self.conveyor_travel_time:
                # 다음 스테이션으로 이동
                completed = self.move_vehicle_to_next_station(vehicle)
                if not completed:
                    vehicle.status = VehicleStatus.WAITING
                    vehicle.position.station_progress = 0.0
        
        # 불량 발생 시뮬레이션 (1% 확률)
        if random.random() < 0.01:
            vehicle.status = VehicleStatus.FAILED
        
        return vehicle.to_dict()
    
    def should_create_new_vehicle(self) -> bool:
        """새 차량 생성 여부 결정"""
        current_time = time.time()
        
        # 시간 간격 체크
        if current_time - self.last_vehicle_creation < self.vehicle_creation_interval:
            return False
        
        # 최대 동시 생산 차량 수 체크
        active_count = len([v for v in self.active_vehicles.values() 
                          if v.status != VehicleStatus.COMPLETED])
        
        if active_count >= self.max_concurrent_vehicles:
            return False
        
        return True
    
    def cleanup_completed_vehicles(self):
        """완료된 차량 정리"""
        # 완료된 차량은 30분 후 제거
        cutoff_time = datetime.now() - timedelta(minutes=30)
        
        to_remove = []
        for vehicle_id, vehicle in self.active_vehicles.items():
            if (vehicle.status == VehicleStatus.COMPLETED and 
                vehicle.created_time < cutoff_time):
                to_remove.append(vehicle_id)
        
        for vehicle_id in to_remove:
            del self.active_vehicles[vehicle_id]
    
    def get_vehicle_tracking_data(self) -> Dict:
        """전체 차량 추적 데이터 반환"""
        current_time = datetime.now()
        
        # 새 차량 생성 체크
        if self.should_create_new_vehicle():
            new_vehicle = self.create_new_vehicle()
            self.active_vehicles[new_vehicle.vehicle_id] = new_vehicle
            self.last_vehicle_creation = time.time()
        
        # 완료된 차량 정리
        self.cleanup_completed_vehicles()
        
        # 모든 차량 상태 업데이트
        vehicle_data = []
        for vehicle in self.active_vehicles.values():
            if vehicle.status != VehicleStatus.COMPLETED:
                updated_data = self.simulate_vehicle_movement(vehicle)
                vehicle_data.append(updated_data)
            else:
                vehicle_data.append(vehicle.to_dict())
        
        return {
            "timestamp": current_time.isoformat(),
            "total_vehicles": len(vehicle_data),
            "active_vehicles": len([v for v in vehicle_data 
                                  if v["status"] not in ["completed", "failed"]]),
            "vehicles": vehicle_data,
            "station_sequence": self.station_sequence,
            "station_positions": self.station_positions
        }
    
    def get_vehicle_by_station(self, station_id: str) -> List[Dict]:
        """특정 스테이션의 차량 목록 반환"""
        vehicles_at_station = []
        
        for vehicle in self.active_vehicles.values():
            if vehicle.position.station_id == station_id:
                vehicles_at_station.append(vehicle.to_dict())
        
        return vehicles_at_station
    
    def get_production_statistics(self) -> Dict:
        """생산 통계 반환"""
        total_vehicles = len(self.active_vehicles)
        completed_vehicles = len([v for v in self.active_vehicles.values() 
                                if v.status == VehicleStatus.COMPLETED])
        failed_vehicles = len([v for v in self.active_vehicles.values() 
                             if v.status == VehicleStatus.FAILED])
        
        # 스테이션별 차량 수
        station_counts = {}
        for station in self.station_sequence:
            station_counts[station] = len(self.get_vehicle_by_station(station))
        
        return {
            "total_vehicles": total_vehicles,
            "completed_vehicles": completed_vehicles,
            "failed_vehicles": failed_vehicles,
            "completion_rate": round((completed_vehicles / max(total_vehicles, 1)) * 100, 1),
            "station_vehicle_counts": station_counts,
            "average_cycle_time": self.vehicle_creation_interval
        }