"""
A01 도어 탈거 공정 시뮬레이터
현대차 의장공정 - 협업로봇 + 사람
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class A01DoorRemovalSimulator(BaseStationSimulator):
    """도어 탈거 공정 시뮬레이터"""
    
    def __init__(self, station_id: str = "A01_DOOR", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        # 도어 탈거 특화 설정
        self.door_positions = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.current_door = 0
        self.operation_phases = ["idle", "approach", "unlock", "lift", "remove", "place", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 현재 작업 중인 차량
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        
        # 센서 시뮬레이션을 위한 기준값
        self.baseline_torque = 125.0  # Nm
        self.baseline_magnetic = True
        self.baseline_proximity = 2.0  # mm
        
        print(f"🚪 A01 도어 탈거 공정 시뮬레이터 초기화 완료")
    
    def _update_operation_phase(self):
        """작업 단계 업데이트"""
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        # 각 단계별 소요 시간 (초)
        phase_durations = {
            "idle": 5,
            "approach": 8,
            "unlock": 12,
            "lift": 15,
            "remove": 20,
            "place": 10,
            "inspect": 8
        }
        
        current_duration = phase_durations.get(self.current_phase, 10)
        
        if phase_duration >= current_duration:
            # 다음 단계로 진행
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                # 사이클 완료 - 다음 도어로
                self.current_door = (self.current_door + 1) % len(self.door_positions)
                if self.current_door == 0:
                    # 모든 도어 완료 - 새 차량
                    self._cycle_complete()
                self.current_phase = "idle"
            
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        """사이클 완료 처리"""
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f"🚪 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_torque_data(self) -> Dict[str, Any]:
        """토크 센서 데이터 생성"""
        # 작업 단계에 따른 토크 변화
        phase_torque_multipliers = {
            "idle": 0.1,
            "approach": 0.3,
            "unlock": 1.5,  # 높은 토크 필요
            "lift": 1.2,
            "remove": 0.8,
            "place": 0.6,
            "inspect": 0.2
        }
        
        multiplier = phase_torque_multipliers.get(self.current_phase, 1.0)
        base_torque = self.baseline_torque * multiplier
        
        # 차량 모델별 토크 차이 (대형 차량일수록 높은 토크)
        model_multipliers = {
            "PALISADE": 1.4,
            "GRANDEUR": 1.2,
            "TUCSON": 1.1,
            "AVANTE": 1.0,
            "KONA": 0.9
        }
        
        if self.current_vehicle:
            model_mult = model_multipliers.get(self.current_vehicle.model, 1.0)
            base_torque *= model_mult
        
        # 노이즈 및 변동성 추가
        noise = random.gauss(0, base_torque * 0.05)  # 5% 노이즈
        torque_value = max(0, base_torque + noise)
        
        return {
            "value": round(torque_value, 2),
            "unit": "Nm",
            "status": "OK" if torque_value < 200 else "WARNING",
            "phase": self.current_phase
        }
    
    def _generate_magnetic_sensor_data(self) -> Dict[str, Any]:
        """마그네틱 센서 데이터 생성 (힌지 상태)"""
        # 작업 단계에 따른 도어 상태
        if self.current_phase in ["idle", "approach"]:
            door_closed = True
            hinge_angle = random.uniform(85, 90)  # 거의 닫힌 상태
        elif self.current_phase in ["unlock", "lift"]:
            door_closed = False
            hinge_angle = random.uniform(15, 45)  # 부분 열림
        elif self.current_phase in ["remove", "place"]:
            door_closed = False
            hinge_angle = random.uniform(85, 95)  # 완전 열림
        else:  # inspect
            door_closed = True
            hinge_angle = random.uniform(87, 90)
        
        return {
            "door_closed": door_closed,
            "hinge_angle": round(hinge_angle, 1),
            "door_position": self.door_positions[self.current_door],
            "magnetic_field_strength": round(random.uniform(0.8, 1.2), 3)
        }
    
    def _generate_vision_data(self) -> Dict[str, Any]:
        """비전 센서 데이터 생성"""
        # 작업 단계별 비전 검사 결과
        if self.current_phase == "inspect":
            confidence = random.uniform(0.92, 0.99)
            passed = confidence > 0.95
        elif self.current_phase in ["remove", "place"]:
            confidence = random.uniform(0.85, 0.95)
            passed = True
        else:
            confidence = random.uniform(0.7, 0.9)
            passed = True
        
        return {
            "passed": passed,
            "confidence": round(confidence, 3),
            "detected_objects": ["door", "hinge", "handle"],
            "alignment_score": round(random.uniform(0.88, 0.98), 3)
        }
    
    def _generate_proximity_data(self) -> Dict[str, Any]:
        """근접 센서 데이터 생성"""
        # 작업 단계별 거리 변화
        phase_distances = {
            "idle": random.uniform(50, 100),
            "approach": random.uniform(10, 30),
            "unlock": random.uniform(2, 8),
            "lift": random.uniform(5, 15),
            "remove": random.uniform(20, 50),
            "place": random.uniform(3, 10),
            "inspect": random.uniform(1, 5)
        }
        
        distance = phase_distances.get(self.current_phase, 10)
        
        return {
            "distance": round(distance, 1),
            "unit": "mm",
            "target_detected": distance < 30,
            "sensor_status": "OK"
        }
    
    def _generate_vibration_data(self) -> Dict[str, Any]:
        """진동 센서 데이터 생성"""
        # 작업 강도에 따른 진동
        phase_vibrations = {
            "idle": 0.02,
            "approach": 0.05,
            "unlock": 0.15,  # 높은 진동
            "lift": 0.12,
            "remove": 0.08,
            "place": 0.06,
            "inspect": 0.03
        }
        
        base_vibration = phase_vibrations.get(self.current_phase, 0.05)
        vibration = base_vibration + random.gauss(0, base_vibration * 0.2)
        vibration = max(0, vibration)
        
        return {
            "value": round(vibration, 3),
            "unit": "g",
            "frequency": round(random.uniform(40, 120), 1),
            "status": "OK" if vibration < 0.3 else "WARNING"
        }
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성"""
        self.update_cycle()
        self._update_operation_phase()
        
        # 차량이 없으면 새로 생성
        if not self.current_vehicle:
            self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "rfid": self.current_vehicle.to_dict(),
            "tracking": self.vehicle_tracking.to_dict(),
            "operation": {
                "phase": self.current_phase,
                "current_door": self.door_positions[self.current_door],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": self._generate_torque_data(),
                "magnetic_sensor": self._generate_magnetic_sensor_data(),
                "vision_sensor": self._generate_vision_data(),
                "proximity_sensor": self._generate_proximity_data(),
                "vibration_sensor": self._generate_vibration_data()
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
            "current_operation": f"{self.current_phase}_{self.door_positions[self.current_door]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(85, 95), 1),
            "automation_level": "COLLABORATIVE",  # 협업로봇
            "operator_count": 1
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        # 도어별 품질 검사 항목
        quality_checks = {
            "door_alignment": random.uniform(0.85, 0.98),
            "hinge_operation": random.uniform(0.88, 0.99),
            "handle_function": random.uniform(0.90, 0.99),
            "seal_integrity": random.uniform(0.87, 0.97),
            "surface_condition": random.uniform(0.85, 0.95)
        }
        
        defects = []
        if quality_score < 0.9:
            defects = random.sample(["minor_scratch", "alignment_deviation", "hinge_stiffness"], 
                                  k=random.randint(0, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.current_vehicle.vehicle_id if self.current_vehicle else None,
            "overall_score": quality_score,
            "passed": passed,
            "quality_checks": quality_checks,
            "defects": defects,
            "inspector": "AUTO_VISION_SYSTEM",
            "rework_required": not passed
        }