"""
생산라인 관리자
스테이션 간 연계성 및 공정 흐름 관리
"""

import time
import random
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class StationStatus(Enum):
    """스테이션 상태"""
    IDLE = "idle"                    # 대기 중
    WORKING = "working"              # 작업 중
    WAITING_PARTS = "waiting_parts"  # 부품 대기
    BLOCKED = "blocked"              # 후속 공정 대기
    MAINTENANCE = "maintenance"      # 정비 중
    ERROR = "error"                  # 오류

class WorkOrder(Enum):
    """작업 지시"""
    NORMAL = "normal"
    PRIORITY = "priority"
    REWORK = "rework"
    HOLD = "hold"

@dataclass
class StationDependency:
    """스테이션 의존성"""
    station_id: str
    prerequisites: List[str] = field(default_factory=list)  # 선행 스테이션
    successors: List[str] = field(default_factory=list)     # 후속 스테이션
    buffer_capacity: int = 3                                # 버퍼 용량
    min_cycle_time: float = 60.0                           # 최소 사이클 타임
    max_cycle_time: float = 180.0                          # 최대 사이클 타임

@dataclass
class WorkInProgress:
    """재공품 정보"""
    wip_id: str
    vehicle_id: str
    current_station: str
    start_time: datetime
    expected_completion: datetime
    work_order: WorkOrder
    quality_status: str = "pending"
    rework_count: int = 0

class ProductionLineManager:
    """생산라인 관리자"""
    
    def __init__(self):
        # 스테이션 의존성 정의 (실제 의장공정 순서)
        self.station_dependencies = self._define_station_dependencies()
        
        # 스테이션별 현재 상태
        self.station_states = {}
        self.station_buffers = {}  # 스테이션별 버퍼 (대기 중인 재공품)
        self.wip_inventory = {}    # 재공품 추적
        
        # 생산 계획
        self.daily_target = 480    # 일일 목표 생산량 (20대/시간 * 24시간)
        self.current_production = 0
        self.shift_start = time.time()
        
        # 초기화
        self._initialize_stations()
        
    def _define_station_dependencies(self) -> Dict[str, StationDependency]:
        """스테이션 의존성 정의"""
        dependencies = {
            # A라인 - 순차적 진행
            "A01_DOOR": StationDependency(
                station_id="A01_DOOR",
                prerequisites=[],  # 시작점
                successors=["A02_WIRING"],
                buffer_capacity=2,
                min_cycle_time=45.0,
                max_cycle_time=75.0
            ),
            "A02_WIRING": StationDependency(
                station_id="A02_WIRING", 
                prerequisites=["A01_DOOR"],
                successors=["A03_HEADLINER"],
                buffer_capacity=3,
                min_cycle_time=60.0,
                max_cycle_time=90.0
            ),
            "A03_HEADLINER": StationDependency(
                station_id="A03_HEADLINER",
                prerequisites=["A02_WIRING"],
                successors=["A04_CRASH_PAD"],
                buffer_capacity=2,
                min_cycle_time=50.0,
                max_cycle_time=80.0
            ),
            "A04_CRASH_PAD": StationDependency(
                station_id="A04_CRASH_PAD",
                prerequisites=["A03_HEADLINER"],
                successors=["B01_FUEL_TANK"],
                buffer_capacity=4,  # A→B 라인 전환점이므로 버퍼 큼
                min_cycle_time=70.0,
                max_cycle_time=110.0
            ),
            
            # B라인 - 중량 작업
            "B01_FUEL_TANK": StationDependency(
                station_id="B01_FUEL_TANK",
                prerequisites=["A04_CRASH_PAD"],
                successors=["B02_CHASSIS_MERGE"],
                buffer_capacity=2,
                min_cycle_time=90.0,
                max_cycle_time=150.0
            ),
            "B02_CHASSIS_MERGE": StationDependency(
                station_id="B02_CHASSIS_MERGE",
                prerequisites=["B01_FUEL_TANK"],
                successors=["B03_MUFFLER"],
                buffer_capacity=1,  # 중요 공정이므로 버퍼 작음
                min_cycle_time=120.0,
                max_cycle_time=180.0
            ),
            "B03_MUFFLER": StationDependency(
                station_id="B03_MUFFLER",
                prerequisites=["B02_CHASSIS_MERGE"],
                successors=["C01_FEM"],
                buffer_capacity=3,
                min_cycle_time=80.0,
                max_cycle_time=120.0
            ),
            
            # C라인 - 부품 조립
            "C01_FEM": StationDependency(
                station_id="C01_FEM",
                prerequisites=["B03_MUFFLER"],
                successors=["C02_GLASS"],
                buffer_capacity=2,
                min_cycle_time=100.0,
                max_cycle_time=160.0
            ),
            "C02_GLASS": StationDependency(
                station_id="C02_GLASS",
                prerequisites=["C01_FEM"],
                successors=["C03_SEAT"],
                buffer_capacity=2,
                min_cycle_time=90.0,
                max_cycle_time=140.0
            ),
            "C03_SEAT": StationDependency(
                station_id="C03_SEAT",
                prerequisites=["C02_GLASS"],
                successors=["C04_BUMPER"],
                buffer_capacity=3,
                min_cycle_time=85.0,
                max_cycle_time=125.0
            ),
            "C04_BUMPER": StationDependency(
                station_id="C04_BUMPER",
                prerequisites=["C03_SEAT"],
                successors=["C05_TIRE"],
                buffer_capacity=2,
                min_cycle_time=75.0,
                max_cycle_time=115.0
            ),
            "C05_TIRE": StationDependency(
                station_id="C05_TIRE",
                prerequisites=["C04_BUMPER"],
                successors=["D01_WHEEL_ALIGNMENT"],
                buffer_capacity=4,  # C→D 라인 전환점
                min_cycle_time=70.0,
                max_cycle_time=100.0
            ),
            
            # D라인 - 검사 및 완료
            "D01_WHEEL_ALIGNMENT": StationDependency(
                station_id="D01_WHEEL_ALIGNMENT",
                prerequisites=["C05_TIRE"],
                successors=["D02_HEADLAMP"],
                buffer_capacity=2,
                min_cycle_time=120.0,
                max_cycle_time=180.0
            ),
            "D02_HEADLAMP": StationDependency(
                station_id="D02_HEADLAMP",
                prerequisites=["D01_WHEEL_ALIGNMENT"],
                successors=["D03_WATER_LEAK_TEST"],
                buffer_capacity=2,
                min_cycle_time=60.0,
                max_cycle_time=90.0
            ),
            "D03_WATER_LEAK_TEST": StationDependency(
                station_id="D03_WATER_LEAK_TEST",
                prerequisites=["D02_HEADLAMP"],
                successors=[],  # 마지막 공정
                buffer_capacity=1,
                min_cycle_time=180.0,
                max_cycle_time=300.0
            )
        }
        return dependencies
    
    def _initialize_stations(self):
        """스테이션 초기화"""
        for station_id, dependency in self.station_dependencies.items():
            self.station_states[station_id] = {
                "status": StationStatus.IDLE,
                "current_wip": None,
                "cycle_start_time": None,
                "expected_cycle_time": dependency.min_cycle_time,
                "efficiency": random.uniform(0.85, 0.95),
                "last_maintenance": time.time() - random.uniform(0, 86400 * 7),  # 지난 주 내 정비
                "downtime_probability": 0.001,  # 0.1% 고장 확률
                "parts_available": True
            }
            self.station_buffers[station_id] = []
    
    def can_start_work(self, station_id: str) -> bool:
        """작업 시작 가능 여부 확인"""
        if station_id not in self.station_dependencies:
            return False
            
        station = self.station_states[station_id]
        dependency = self.station_dependencies[station_id]
        
        # 현재 상태 체크
        if station["status"] != StationStatus.IDLE:
            return False
            
        # 부품 가용성 체크
        if not station["parts_available"]:
            station["status"] = StationStatus.WAITING_PARTS
            return False
            
        # 선행 공정 완료 체크
        for prereq in dependency.prerequisites:
            if not self._is_prerequisite_satisfied(prereq, station_id):
                return False
                
        # 후속 공정 버퍼 체크 (블로킹 방지)
        for successor in dependency.successors:
            if self._is_successor_blocked(successor):
                station["status"] = StationStatus.BLOCKED
                return False
                
        return True
    
    def _is_prerequisite_satisfied(self, prereq_station: str, target_station: str) -> bool:
        """선행 공정 완료 여부 확인"""
        # 선행 공정의 버퍼에 완성품이 있는지 확인
        buffer = self.station_buffers.get(prereq_station, [])
        
        # 버퍼에 완성된 재공품이 있으면 사용 가능
        for wip in buffer:
            if wip.quality_status in ["pass", "conditional_pass"]:
                return True
                
        return False
    
    def _is_successor_blocked(self, successor_station: str) -> bool:
        """후속 공정 블로킹 여부 확인"""
        if successor_station not in self.station_dependencies:
            return False
            
        dependency = self.station_dependencies[successor_station]
        buffer = self.station_buffers.get(successor_station, [])
        
        # 후속 공정 버퍼가 가득 찬 경우 블로킹
        return len(buffer) >= dependency.buffer_capacity
    
    def start_work(self, station_id: str, vehicle_id: str) -> bool:
        """작업 시작"""
        if not self.can_start_work(station_id):
            return False
            
        station = self.station_states[station_id]
        dependency = self.station_dependencies[station_id]
        
        # 선행 공정에서 재공품 가져오기
        wip = self._get_wip_from_predecessor(station_id, vehicle_id)
        if not wip:
            # 새 재공품 생성 (첫 번째 공정인 경우)
            wip = WorkInProgress(
                wip_id=f"WIP_{int(time.time() * 1000)}",
                vehicle_id=vehicle_id,
                current_station=station_id,
                start_time=datetime.now(),
                expected_completion=datetime.now() + timedelta(
                    seconds=dependency.min_cycle_time / station["efficiency"]
                ),
                work_order=WorkOrder.NORMAL
            )
        else:
            # 기존 재공품 업데이트
            wip.current_station = station_id
            wip.start_time = datetime.now()
            wip.expected_completion = datetime.now() + timedelta(
                seconds=dependency.min_cycle_time / station["efficiency"]
            )
        
        # 스테이션 상태 업데이트
        station["status"] = StationStatus.WORKING
        station["current_wip"] = wip.wip_id
        station["cycle_start_time"] = time.time()
        
        # 사이클 타임 계산 (효율성 반영)
        base_cycle_time = random.uniform(dependency.min_cycle_time, dependency.max_cycle_time)
        station["expected_cycle_time"] = base_cycle_time / station["efficiency"]
        
        # 재공품 등록
        self.wip_inventory[wip.wip_id] = wip
        
        return True
    
    def _get_wip_from_predecessor(self, station_id: str, vehicle_id: str) -> Optional[WorkInProgress]:
        """선행 공정에서 재공품 가져오기"""
        dependency = self.station_dependencies[station_id]
        
        for prereq in dependency.prerequisites:
            buffer = self.station_buffers.get(prereq, [])
            for wip in buffer:
                if wip.vehicle_id == vehicle_id and wip.quality_status in ["pass", "conditional_pass"]:
                    buffer.remove(wip)
                    return wip
                    
        return None
    
    def complete_work(self, station_id: str) -> bool:
        """작업 완료"""
        if station_id not in self.station_states:
            return False
            
        station = self.station_states[station_id]
        
        if station["status"] != StationStatus.WORKING or not station["current_wip"]:
            return False
            
        wip_id = station["current_wip"]
        wip = self.wip_inventory.get(wip_id)
        
        if not wip:
            return False
            
        # 품질 검사 시뮬레이션
        quality_result = self._perform_quality_check(station_id)
        wip.quality_status = quality_result["status"]
        
        # 불량일 경우 재작업 처리
        if quality_result["status"] == "fail":
            if wip.rework_count < 2:  # 최대 2회 재작업
                wip.rework_count += 1
                wip.work_order = WorkOrder.REWORK
                wip.quality_status = "pending"
                # 현재 스테이션에서 재작업
                station["cycle_start_time"] = time.time()
                return False
            else:
                # 재작업 한계 초과 시 폐기
                wip.quality_status = "scrap"
        
        # 스테이션 버퍼에 완성품 추가
        self.station_buffers[station_id].append(wip)
        
        # 스테이션 상태 초기화
        station["status"] = StationStatus.IDLE
        station["current_wip"] = None
        station["cycle_start_time"] = None
        
        # 마지막 공정 완료 시 생산량 증가
        if not self.station_dependencies[station_id].successors:
            if wip.quality_status in ["pass", "conditional_pass"]:
                self.current_production += 1
                
        return True
    
    def _perform_quality_check(self, station_id: str) -> Dict:
        """품질 검사 수행"""
        station = self.station_states[station_id]
        
        # 스테이션별 품질 특성
        quality_params = {
            "A01_DOOR": {"pass_rate": 0.98, "critical": False},
            "A02_WIRING": {"pass_rate": 0.95, "critical": True},
            "A03_HEADLINER": {"pass_rate": 0.97, "critical": False},
            "A04_CRASH_PAD": {"pass_rate": 0.96, "critical": False},
            "B01_FUEL_TANK": {"pass_rate": 0.98, "critical": True},
            "B02_CHASSIS_MERGE": {"pass_rate": 0.94, "critical": True},
            "B03_MUFFLER": {"pass_rate": 0.97, "critical": False},
            "C01_FEM": {"pass_rate": 0.96, "critical": True},
            "C02_GLASS": {"pass_rate": 0.99, "critical": False},
            "C03_SEAT": {"pass_rate": 0.98, "critical": False},
            "C04_BUMPER": {"pass_rate": 0.97, "critical": False},
            "C05_TIRE": {"pass_rate": 0.98, "critical": False},
            "D01_WHEEL_ALIGNMENT": {"pass_rate": 0.92, "critical": True},
            "D02_HEADLAMP": {"pass_rate": 0.96, "critical": False},
            "D03_WATER_LEAK_TEST": {"pass_rate": 0.94, "critical": True}
        }
        
        params = quality_params.get(station_id, {"pass_rate": 0.95, "critical": False})
        
        # 효율성이 품질에 영향
        adjusted_pass_rate = params["pass_rate"] * station["efficiency"]
        
        # 품질 판정
        if random.random() < adjusted_pass_rate:
            if params["critical"] and random.random() < 0.05:
                return {"status": "conditional_pass", "score": random.uniform(0.85, 0.89)}
            else:
                return {"status": "pass", "score": random.uniform(0.90, 1.0)}
        else:
            return {"status": "fail", "score": random.uniform(0.60, 0.84)}
    
    def update_station_states(self):
        """스테이션 상태 업데이트"""
        current_time = time.time()
        
        for station_id, station in self.station_states.items():
            # 작업 중인 스테이션의 완료 체크
            if station["status"] == StationStatus.WORKING:
                if station["cycle_start_time"]:
                    elapsed = current_time - station["cycle_start_time"]
                    if elapsed >= station["expected_cycle_time"]:
                        self.complete_work(station_id)
            
            # 고장 시뮬레이션
            self._simulate_equipment_failure(station_id)
            
            # 부품 공급 상태 업데이트
            self._update_parts_availability(station_id)
            
            # 정비 스케줄 체크
            self._check_maintenance_schedule(station_id)
    
    def _simulate_equipment_failure(self, station_id: str):
        """설비 고장 시뮬레이션"""
        station = self.station_states[station_id]
        
        if station["status"] in [StationStatus.WORKING, StationStatus.IDLE]:
            if random.random() < station["downtime_probability"]:
                station["status"] = StationStatus.ERROR
                station["error_start_time"] = time.time()
                station["estimated_repair_time"] = random.uniform(300, 1800)  # 5-30분
        
        elif station["status"] == StationStatus.ERROR:
            # 수리 완료 체크
            elapsed = time.time() - station.get("error_start_time", 0)
            if elapsed >= station.get("estimated_repair_time", 0):
                station["status"] = StationStatus.IDLE
                station["efficiency"] = random.uniform(0.80, 0.95)  # 수리 후 효율성 변화
    
    def _update_parts_availability(self, station_id: str):
        """부품 가용성 업데이트"""
        station = self.station_states[station_id]
        
        # 부품 부족 시뮬레이션 (1% 확률)
        if station["parts_available"] and random.random() < 0.01:
            station["parts_available"] = False
            station["parts_shortage_start"] = time.time()
            station["estimated_resupply_time"] = random.uniform(600, 3600)  # 10분-1시간
        
        elif not station["parts_available"]:
            # 부품 재공급 체크
            elapsed = time.time() - station.get("parts_shortage_start", 0)
            if elapsed >= station.get("estimated_resupply_time", 0):
                station["parts_available"] = True
    
    def _check_maintenance_schedule(self, station_id: str):
        """정비 스케줄 체크"""
        station = self.station_states[station_id]
        
        # 주간 정비 (168시간 = 1주)
        time_since_maintenance = time.time() - station["last_maintenance"]
        if time_since_maintenance > 168 * 3600:  # 1주일
            if station["status"] == StationStatus.IDLE and random.random() < 0.1:
                station["status"] = StationStatus.MAINTENANCE
                station["maintenance_start"] = time.time()
                station["maintenance_duration"] = random.uniform(1800, 7200)  # 30분-2시간
        
        elif station["status"] == StationStatus.MAINTENANCE:
            # 정비 완료 체크
            elapsed = time.time() - station.get("maintenance_start", 0)
            if elapsed >= station.get("maintenance_duration", 0):
                station["status"] = StationStatus.IDLE
                station["last_maintenance"] = time.time()
                station["efficiency"] = random.uniform(0.90, 0.98)  # 정비 후 효율성 향상
    
    def get_line_status(self) -> Dict:
        """생산라인 전체 상태 반환"""
        # 현재 시프트 진행률
        shift_elapsed = time.time() - self.shift_start
        shift_progress = min(100.0, (shift_elapsed / (8 * 3600)) * 100)  # 8시간 기준
        
        # 목표 대비 진행률
        target_progress = (shift_elapsed / (8 * 3600)) * (self.daily_target / 3)  # 8시간당 목표
        achievement_rate = (self.current_production / max(target_progress, 1)) * 100
        
        # 스테이션별 상태 요약
        station_summary = {}
        for station_id, station in self.station_states.items():
            dependency = self.station_dependencies[station_id]
            buffer = self.station_buffers[station_id]
            
            station_summary[station_id] = {
                "status": station["status"].value,
                "efficiency": round(station["efficiency"] * 100, 1),
                "buffer_count": len(buffer),
                "buffer_capacity": dependency.buffer_capacity,
                "current_wip": station["current_wip"],
                "parts_available": station["parts_available"]
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "shift_progress": round(shift_progress, 1),
            "current_production": self.current_production,
            "daily_target": self.daily_target,
            "achievement_rate": round(achievement_rate, 1),
            "total_wip": len(self.wip_inventory),
            "stations": station_summary,
            "line_efficiency": self._calculate_line_efficiency()
        }
    
    def _calculate_line_efficiency(self) -> float:
        """라인 전체 효율성 계산"""
        working_stations = 0
        total_efficiency = 0
        
        for station in self.station_states.values():
            if station["status"] in [StationStatus.WORKING, StationStatus.IDLE]:
                working_stations += 1
                total_efficiency += station["efficiency"]
        
        if working_stations > 0:
            return round((total_efficiency / working_stations) * 100, 1)
        return 0.0