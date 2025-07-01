"""
A02 배선 공정 시뮬레이터
현대차 의장공정 - 전기 배선 설치
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class A02WiringSimulator(BaseStationSimulator):
    """배선 공정 시뮬레이터"""
    
    def __init__(self, station_id: str = "A02_WIRING", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        # 배선 특화 설정
        self.wiring_sections = ["DASHBOARD", "ENGINE_BAY", "DOOR_HARNESS", "TRUNK"]
        self.current_section = 0
        self.operation_phases = ["idle", "route_check", "pull_wire", "connect", "test", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 현재 작업 중인 차량
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        
        print(f"⚡ A02 배선 공정 시뮬레이터 초기화 완료")
    
    def _update_operation_phase(self):
        """작업 단계 업데이트"""
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        phase_durations = {
            "idle": 3,
            "route_check": 10,
            "pull_wire": 25,
            "connect": 30,
            "test": 15,
            "inspect": 12
        }
        
        current_duration = phase_durations.get(self.current_phase, 10)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                self.current_section = (self.current_section + 1) % len(self.wiring_sections)
                if self.current_section == 0:
                    self._cycle_complete()
                self.current_phase = "idle"
            
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        """사이클 완료 처리"""
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f"⚡ 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_current_data(self) -> Dict[str, Any]:
        """전류 센서 데이터 생성"""
        phase_currents = {
            "idle": 0.1,
            "route_check": 0.2,
            "pull_wire": 1.5,
            "connect": 3.2,
            "test": 12.5,  # 높은 전류
            "inspect": 0.5
        }
        
        base_current = phase_currents.get(self.current_phase, 1.0)
        noise = random.gauss(0, base_current * 0.1)
        current_value = max(0, base_current + noise)
        
        return {
            "value": round(current_value, 2),
            "unit": "A",
            "status": "OK" if current_value < 15 else "WARNING",
            "phase": self.current_phase
        }
    
    def _generate_voltage_data(self) -> Dict[str, Any]:
        """전압 센서 데이터 생성"""
        nominal_voltage = 12.0
        
        if self.current_phase == "test":
            voltage = random.uniform(11.8, 12.4)
        elif self.current_phase in ["connect", "inspect"]:
            voltage = random.uniform(11.9, 12.2)
        else:
            voltage = random.uniform(11.5, 12.5)
        
        return {
            "value": round(voltage, 2),
            "unit": "V",
            "nominal": nominal_voltage,
            "status": "OK" if 11.0 <= voltage <= 13.0 else "WARNING"
        }
    
    def _generate_resistance_data(self) -> Dict[str, Any]:
        """저항 센서 데이터 생성"""
        section_resistances = {
            "DASHBOARD": random.uniform(0.8, 1.2),
            "ENGINE_BAY": random.uniform(0.5, 0.9),
            "DOOR_HARNESS": random.uniform(1.0, 1.5),
            "TRUNK": random.uniform(0.6, 1.1)
        }
        
        resistance = section_resistances.get(self.wiring_sections[self.current_section], 1.0)
        
        return {
            "value": round(resistance, 3),
            "unit": "Ω",
            "section": self.wiring_sections[self.current_section],
            "status": "OK" if resistance < 2.0 else "WARNING"
        }
    
    def _generate_continuity_data(self) -> Dict[str, Any]:
        """도통 센서 데이터 생성"""
        if self.current_phase in ["connect", "test", "inspect"]:
            continuity = random.choice([True, True, True, False])  # 75% 성공률
        else:
            continuity = False
        
        return {
            "continuity": continuity,
            "test_points": random.randint(8, 24),
            "passed_points": random.randint(6, 24) if continuity else random.randint(0, 8),
            "insulation_resistance": round(random.uniform(10, 50), 1)
        }
    
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
                "current_section": self.wiring_sections[self.current_section],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "current_sensor": self._generate_current_data(),
                "voltage_sensor": self._generate_voltage_data(),
                "resistance_sensor": self._generate_resistance_data(),
                "continuity_sensor": self._generate_continuity_data()
            },
            "cycle_info": {
                "cycle_count": self.cycle_count,
                "cycle_time": round(time.time() - self.operation_start_time, 1),
                "target_time": self.current_cycle_time,
                "efficiency": round((self.current_cycle_time / max(1, time.time() - self.operation_start_time)) * 100, 1)
            }
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성"""
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"{self.current_phase}_{self.wiring_sections[self.current_section]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(88, 94), 1),
            "automation_level": "SEMI_AUTO",
            "operator_count": 2
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        quality_checks = {
            "wire_routing": random.uniform(0.85, 0.98),
            "connection_quality": random.uniform(0.88, 0.99),
            "insulation_test": random.uniform(0.90, 0.99),
            "continuity_test": random.uniform(0.87, 0.97)
        }
        
        defects = []
        if quality_score < 0.9:
            defects = random.sample(["loose_connection", "wire_damage", "routing_error"], 
                                  k=random.randint(0, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.current_vehicle.vehicle_id if self.current_vehicle else None,
            "overall_score": quality_score,
            "passed": passed,
            "quality_checks": quality_checks,
            "defects": defects,
            "inspector": "AUTO_TEST_SYSTEM",
            "rework_required": not passed
        }