"""
D03 수밀검사 시뮬레이터
최종검사공정 - 방수/배수 테스트
iot.md 기반: 통과/불량 판정
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class D03WaterLeakTestSimulator(BaseStationSimulator):
    """수밀검사 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "D03_WATER_LEAK_TEST", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.test_zones = ["DOOR_SEALS", "WINDSHIELD", "SUNROOF", "TRUNK", "WINDOWS"]
        self.current_zone = 0
        self.operation_phases = ["idle", "water_spray", "pressure_test", "drainage_test", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 950, "y": 180, "line": "D"}
        
        print(f">> D03 수밀검사 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 3, "water_spray": 30, "pressure_test": 20,
            "drainage_test": 15, "inspect": 10
        }
        
        current_duration = phase_durations.get(self.current_phase, 15)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_zone = (self.current_zone + 1) % len(self.test_zones)
                if self.current_zone == 0:
                    self._cycle_complete()
                self.current_phase = "idle"
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f">> 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        if self.current_vehicle and self.vehicle_tracking:
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "line_position": f"D-{self.current_zone + 3}",
                "next_station": "COMPLETE"
            }
        return {}
    
    def generate_telemetry(self) -> Dict[str, Any]:
        self.update_cycle()
        self._update_operation_phase()
        
        if not self.current_vehicle:
            self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        
        # 통과/불량 판정
        test_result = random.choice(["PASS", "PASS", "PASS", "PASS", "FAIL"])  # 80% 통과율
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "rfid": self.current_vehicle.to_dict(),
            "tracking": self.vehicle_tracking.to_dict(),
            "vehicle_position": self._get_vehicle_position(),
            "operation": {
                "phase": self.current_phase,
                "current_zone": self.test_zones[self.current_zone],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "test_result": {
                "overall_result": test_result,
                "water_ingress": random.choice([False, False, False, True]),  # 75% 누수 없음
                "drainage_ok": random.choice([True, True, True, False]),  # 75% 배수 양호
                "pressure_hold": random.choice([True, True, False])  # 66% 압력 유지
            },
            "cycle_info": {
                "cycle_count": self.cycle_count,
                "cycle_time": round(time.time() - self.operation_start_time, 1),
                "target_time": self.current_cycle_time,
                "efficiency": round((self.current_cycle_time / max(1, time.time() - self.operation_start_time)) * 100, 1)
            }
        }
    
    def generate_status(self) -> Dict[str, Any]:
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"{self.current_phase}_{self.test_zones[self.current_zone]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(90, 96), 1),
            "automation_level": "FULLY_AUTO",
            "operator_count": 0
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.current_vehicle.vehicle_id if self.current_vehicle else None,
            "overall_score": quality_score,
            "passed": passed,
            "quality_checks": {
                "water_leak_test": random.uniform(0.85, 0.98)
            },
            "defects": [],
            "inspector": "AUTO_TEST_SYSTEM",
            "rework_required": not passed
        }