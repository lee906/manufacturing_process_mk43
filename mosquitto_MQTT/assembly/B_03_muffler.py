"""
B03 머플러 조립 시뮬레이터
배기계통 조립공정 - 머플러 장착
iot.md 기반 핵심 센서: 토크 센서, 비전 센서, 진동 센서, 온도 센서
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class B03MufflerSimulator(BaseStationSimulator):
    """머플러 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "B03_MUFFLER", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.muffler_components = ["MAIN_MUFFLER", "RESONATOR", "EXHAUST_PIPE", "TAIL_PIPE"]
        self.current_component = 0
        self.operation_phases = ["idle", "position_check", "mount_muffler", "torque_apply", "temp_check", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 450, "y": 80, "line": "B"}
        
        self.target_torque = 65.0  # Nm
        self.target_temperature = 80.0  # °C
        
        print(f">> B03 머플러 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 3, "position_check": 12, "mount_muffler": 35,
            "torque_apply": 20, "temp_check": 18, "inspect": 10
        }
        
        current_duration = phase_durations.get(self.current_phase, 15)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_component = (self.current_component + 1) % len(self.muffler_components)
                if self.current_component == 0:
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
                "line_position": f"B-{self.current_component + 3}",
                "next_station": "C01_FEM"
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
                "current_component": self.muffler_components[self.current_component],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": {
                    "applied_torque": round(self.target_torque + random.uniform(-8, 8), 2) if self.current_phase == "torque_apply" else round(random.uniform(0, 10), 2),
                    "target_torque": self.target_torque,
                    "unit": "Nm"
                },
                "temperature_sensor": {
                    "measured_temperature": round(self.target_temperature + random.uniform(-15, 25), 1) if self.current_phase == "temp_check" else round(25 + random.uniform(-5, 20), 1),
                    "target_temperature": self.target_temperature,
                    "unit": "°C"
                },
                "vibration_sensor": {
                    "acceleration": round(random.uniform(0.02, 0.25), 3),
                    "frequency": round(random.uniform(25, 80), 1),
                    "unit": "g"
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
            "current_operation": f"{self.current_phase}_{self.muffler_components[self.current_component]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(88, 95), 1),
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
                "torque_accuracy": random.uniform(0.88, 0.98)
            },
            "defects": [],
            "inspector": "AUTO_SYSTEM",
            "rework_required": not passed
        }