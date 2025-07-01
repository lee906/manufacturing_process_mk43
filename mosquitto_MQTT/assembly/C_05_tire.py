"""
C05 타이어 조립 시뮬레이터
차체 조립공정 - 타이어 장착
iot.md 기반 핵심 센서: 토크 센서, 비전 센서, 압력 센서, 근접 센서
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class C05TireSimulator(BaseStationSimulator):
    """타이어 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "C05_TIRE", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        self.tire_positions = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.current_tire = 0
        self.operation_phases = ["idle", "position_check", "mount_tire", "torque_apply", "pressure_check", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 650, "y": 180, "line": "C"}
        
        # 타이어 조립 파라미터
        self.target_torque = 110.0  # Nm (휠 너트)
        self.target_pressure = 2.3  # bar
        
        print(f">> C05 타이어 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 2, "position_check": 8, "mount_tire": 15,
            "torque_apply": 12, "pressure_check": 10, "inspect": 6
        }
        
        current_duration = phase_durations.get(self.current_phase, 10)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_tire = (self.current_tire + 1) % len(self.tire_positions)
                if self.current_tire == 0:
                    self._cycle_complete()
                self.current_phase = "idle"
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f">> 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_pressure_data(self) -> Dict[str, Any]:
        if self.current_phase == "pressure_check":
            pressure = self.target_pressure + random.uniform(-0.1, 0.1)
        else:
            pressure = random.uniform(0.5, 1.0)
        
        return {
            "tire_pressure": round(pressure, 2),
            "target_pressure": self.target_pressure,
            "unit": "bar",
            "status": "OK" if abs(pressure - self.target_pressure) <= 0.15 else "WARNING"
        }
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        if self.current_vehicle and self.vehicle_tracking:
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "line_position": f"C-{self.current_tire + 5}",
                "next_station": "D01_WHEEL_ALIGNMENT"
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
                "current_tire": self.tire_positions[self.current_tire],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "pressure_sensor": self._generate_pressure_data()
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
            "current_operation": f"{self.current_phase}_{self.tire_positions[self.current_tire]}",
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
                "tire_pressure": random.uniform(0.90, 0.99),
                "wheel_torque": random.uniform(0.88, 0.98)
            },
            "defects": [],
            "inspector": "AUTO_SYSTEM",
            "rework_required": not passed
        }