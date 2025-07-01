"""
C04 범퍼 조립 시뮬레이터
차체 조립공정 - 범퍼 장착
iot.md 기반 핵심 센서: 토크 센서, 비전 센서, 근접 센서, 압력 센서
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class C04BumperSimulator(BaseStationSimulator):
    """범퍼 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "C04_BUMPER", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.bumper_types = ["FRONT_BUMPER", "REAR_BUMPER"]
        self.current_bumper = 0
        self.operation_phases = ["idle", "position_check", "mount_bumper", "torque_apply", "pressure_test", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 550, "y": 180, "line": "C"}
        
        # 범퍼 조립 파라미터
        self.target_torque = 40.0  # Nm
        self.torque_tolerance = 4.0
        
        print(f">> C04 범퍼 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 3, "position_check": 10, "mount_bumper": 20,
            "torque_apply": 15, "pressure_test": 12, "inspect": 8
        }
        
        current_duration = phase_durations.get(self.current_phase, 12)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_bumper = (self.current_bumper + 1) % len(self.bumper_types)
                if self.current_bumper == 0:
                    self._cycle_complete()
                self.current_phase = "idle"
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f">> 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_torque_data(self) -> Dict[str, Any]:
        if self.current_phase == "torque_apply":
            applied_torque = self.target_torque + random.uniform(-self.torque_tolerance, self.torque_tolerance)
        else:
            applied_torque = random.uniform(0, 5.0)
        
        return {
            "applied_torque": round(applied_torque, 2),
            "target_torque": self.target_torque,
            "unit": "Nm",
            "status": "OK" if abs(applied_torque - self.target_torque) <= self.torque_tolerance else "WARNING"
        }
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        if self.current_vehicle and self.vehicle_tracking:
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "line_position": f"C-{self.current_bumper + 4}",
                "next_station": "C05_TIRE"
            }
        return {}
    
    def generate_telemetry(self) -> Dict[str, Any]:
        self.update_cycle()
        self._update_operation_phase()
        
        if not self.current_vehicle:
            self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "rfid": self.current_vehicle.to_dict(),
            "tracking": self.vehicle_tracking.to_dict(),
            "vehicle_position": self._get_vehicle_position(),
            "operation": {
                "phase": self.current_phase,
                "current_bumper": self.bumper_types[self.current_bumper],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": self._generate_torque_data()
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
            "current_operation": f"{self.current_phase}_{self.bumper_types[self.current_bumper]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(85, 91), 1),
            "automation_level": "SEMI_AUTO",
            "operator_count": 1
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
                "mounting_torque": random.uniform(0.88, 0.98),
                "bumper_alignment": random.uniform(0.90, 0.99)
            },
            "defects": [],
            "inspector": "HUMAN_OPERATOR",
            "rework_required": not passed
        }