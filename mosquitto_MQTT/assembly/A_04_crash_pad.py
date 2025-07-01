"""
A04 크래쉬패드 조립 시뮬레이터  
내장재 조립공정 - 크래쉬패드 장착
iot.md 기반 핵심 센서: 토크 센서, 비전 센서, 근접 센서, 압력 센서
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class A04CrashPadSimulator(BaseStationSimulator):
    """크래쉬패드 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "A04_CRASH_PAD", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.crash_pad_components = ["MAIN_PANEL", "AIRBAG_MODULE", "DISPLAY_UNIT", "HVAC_CONTROL"]
        self.current_component = 0
        self.operation_phases = ["idle", "position_check", "mount_component", "torque_apply", "pressure_test", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 150, "y": 120, "line": "A"}
        
        self.target_torque = 25.0
        
        print(f">> A04 크래쉬패드 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 4, "position_check": 18, "mount_component": 40,
            "torque_apply": 22, "pressure_test": 15, "inspect": 12
        }
        
        current_duration = phase_durations.get(self.current_phase, 18)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_component = (self.current_component + 1) % len(self.crash_pad_components)
                if self.current_component == 0:
                    self._cycle_complete()
                self.current_phase = "idle"
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        if self.current_vehicle and self.vehicle_tracking:
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "line_position": f"A-{self.current_component + 4}",
                "next_station": "B01_FUEL_TANK"
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
                "current_component": self.crash_pad_components[self.current_component],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": {
                    "applied_torque": round(self.target_torque + random.uniform(-3, 3), 2) if self.current_phase == "torque_apply" else round(random.uniform(0, 5), 2),
                    "target_torque": self.target_torque,
                    "unit": "Nm"
                }
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
            "current_operation": f"{self.current_phase}_{self.crash_pad_components[self.current_component]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(85, 92), 1),
            "automation_level": "SEMI_AUTO",
            "operator_count": 2
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
                "mounting_torque": random.uniform(0.88, 0.98)
            },
            "defects": [],
            "inspector": "HUMAN_OPERATOR",
            "rework_required": not passed
        }