"""
B02 샤시 메리지 시뮬레이터
샤시 조립공정 - 차체 결합
iot.md 기반 핵심 센서: 근접 센서, 토크 센서, 비전 센서, 레이저 거리 센서
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class B02ChassisMergeSimulator(BaseStationSimulator):
    """샤시 메리지 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "B02_CHASSIS_MERGE", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.merge_stages = ["FRONT_CHASSIS", "REAR_CHASSIS", "ENGINE_MOUNT", "TRANSMISSION_MOUNT"]
        self.current_stage = 0
        self.operation_phases = ["idle", "position_align", "merge_chassis", "torque_apply", "weight_check", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 350, "y": 80, "line": "B"}
        
        self.target_torque = 180.0  # Nm
        
        print(f">> B02 샤시 메리지 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 5, "position_align": 45, "merge_chassis": 120,
            "torque_apply": 60, "weight_check": 25, "inspect": 20
        }
        
        current_duration = phase_durations.get(self.current_phase, 30)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_stage = (self.current_stage + 1) % len(self.merge_stages)
                if self.current_stage == 0:
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
                "line_position": f"B-{self.current_stage + 2}",
                "next_station": "B03_MUFFLER"
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
                "current_stage": self.merge_stages[self.current_stage],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": {
                    "applied_torque": round(self.target_torque + random.uniform(-15, 15), 2) if self.current_phase == "torque_apply" else round(random.uniform(0, 20), 2),
                    "target_torque": self.target_torque,
                    "unit": "Nm"
                },
                "weight_sensor": {
                    "measured_weight": round(1250 + random.uniform(-50, 50), 1) if self.current_phase == "weight_check" else round(random.uniform(200, 800), 1),
                    "target_weight": 1250.0,
                    "unit": "kg"
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
            "current_operation": f"{self.current_phase}_{self.merge_stages[self.current_stage]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(92, 98), 1),
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
                "chassis_alignment": random.uniform(0.90, 0.99)
            },
            "defects": [],
            "inspector": "AUTO_VISION_SYSTEM",
            "rework_required": not passed
        }