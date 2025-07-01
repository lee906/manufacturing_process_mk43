"""
B01 연료탱크 공정 시뮬레이터
현대차 샤시라인 - 연료탱크 장착
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class B01FuelTankSimulator(BaseStationSimulator):
    """연료탱크 공정 시뮬레이터"""
    
    def __init__(self, station_id: str = "B01_FUEL_TANK", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.operation_phases = ["idle", "lift_vehicle", "position_tank", "secure_straps", "connect_lines", "test_leak", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        
        print(f"⛽ B01 연료탱크 공정 시뮬레이터 초기화 완료")
    
    def _update_operation_phase(self):
        """작업 단계 업데이트"""
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 5,
            "lift_vehicle": 20,
            "position_tank": 35,
            "secure_straps": 25,
            "connect_lines": 30,
            "test_leak": 40,
            "inspect": 15
        }
        
        current_duration = phase_durations.get(self.current_phase, 15)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self._cycle_complete()
                self.current_phase = "idle"
            
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        """사이클 완료 처리"""
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f"⛽ 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성"""
        self.update_cycle()
        self._update_operation_phase()
        
        if not self.current_vehicle:
            self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "rfid": self.current_vehicle.to_dict(),
            "tracking": self.vehicle_tracking.to_dict(),
            "operation": {
                "phase": self.current_phase,
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "pressure_sensor": {
                    "value": round(random.uniform(0.0, 0.5), 3),
                    "unit": "bar",
                    "status": "OK"
                },
                "lift_sensor": {
                    "height": round(random.uniform(0, 1200), 1),
                    "load": round(random.uniform(0, 2000), 1),
                    "status": "OK"
                }
            }
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성"""
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": self.current_phase,
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(82, 88), 1)
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.current_vehicle.vehicle_id if self.current_vehicle else None,
            "overall_score": quality_score,
            "passed": passed
        }