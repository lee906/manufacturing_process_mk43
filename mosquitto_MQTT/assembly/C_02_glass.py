"""
C02 글라스 조립 시뮬레이터
차체 조립공정 - 글라스 장착
iot.md 기반 핵심 센서: 비전 센서, 레이저 거리 센서, 힘/하중 센서, 근접 센서
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class C02GlassSimulator(BaseStationSimulator):
    """글라스 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "C02_GLASS", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        # 글라스 타입 목록
        self.glass_types = ["WINDSHIELD", "REAR_GLASS", "SIDE_GLASS_FL", "SIDE_GLASS_FR"]
        self.current_glass = 0
        self.operation_phases = ["idle", "surface_prep", "apply_sealant", "position_glass", "laser_check", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 350, "y": 180, "line": "C"}  # C라인 글라스 스테이션 위치
        
        # 글라스 조립 파라미터
        self.sealant_amount = 0  # ml
        self.target_distance = 2.0  # mm (레이저 거리)
        
        print(f">> C02 글라스 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        """작업 단계 업데이트"""
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        # 각 단계별 소요 시간 (초)
        phase_durations = {
            "idle": 4,
            "surface_prep": 20,
            "apply_sealant": 30,
            "position_glass": 25,
            "laser_check": 15,
            "inspect": 15
        }
        
        current_duration = phase_durations.get(self.current_phase, 20)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                # 글라스 완료 - 다음 글라스로
                self.current_glass = (self.current_glass + 1) % len(self.glass_types)
                if self.current_glass == 0:
                    # 모든 글라스 완료 - 새 차량
                    self._cycle_complete()
                self.current_phase = "idle"
                self.sealant_amount = 0
            
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        """사이클 완료 처리"""
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f">> 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_laser_distance_data(self) -> Dict[str, Any]:
        """레이저 거리 센서 데이터 생성"""
        if self.current_phase == "laser_check":
            # 레이저 측정 중 - 정밀 거리 측정
            distance = self.target_distance + random.uniform(-0.3, 0.3)
            accuracy = random.uniform(0.95, 0.99)
        elif self.current_phase == "position_glass":
            # 글라스 포지셔닝 중 - 거리 모니터링
            distance = random.uniform(1.5, 4.0)
            accuracy = random.uniform(0.90, 0.95)
        else:
            distance = random.uniform(5.0, 20.0)
            accuracy = random.uniform(0.80, 0.90)
        
        return {
            "distance": round(distance, 2),
            "target_distance": self.target_distance,
            "unit": "mm",
            "accuracy": round(accuracy, 3),
            "tolerance": "±0.5mm",
            "within_tolerance": abs(distance - self.target_distance) <= 0.5,
            "status": "OK" if abs(distance - self.target_distance) <= 0.5 else "OUT_OF_RANGE"
        }
    
    def _generate_force_load_data(self) -> Dict[str, Any]:
        """힘/하중 센서 데이터 생성"""
        if self.current_phase == "position_glass":
            # 글라스 설치 중 - 하중 모니터링
            applied_force = random.uniform(150, 400)  # N
            max_safe_force = 300  # N
        elif self.current_phase == "laser_check":
            # 검사 중 - 압착력 확인
            applied_force = random.uniform(200, 350)
            max_safe_force = 300
        else:
            applied_force = random.uniform(0, 50)
            max_safe_force = 300
        
        return {
            "applied_force": round(applied_force, 1),
            "max_safe_force": max_safe_force,
            "unit": "N",
            "force_ratio": round(applied_force / max_safe_force, 3),
            "pressure_distribution": random.choice(["UNIFORM", "UNIFORM", "UNEVEN"]),
            "status": "OK" if applied_force <= max_safe_force else "OVERLOAD"
        }
    
    def _generate_proximity_data(self) -> Dict[str, Any]:
        """근접 센서 데이터 생성"""
        if self.current_phase in ["position_glass", "laser_check"]:
            # 글라스 근접 상태
            distance = random.uniform(0.1, 1.5)  # mm
            target_detected = True
        elif self.current_phase == "apply_sealant":
            # 실런트 적용 중
            distance = random.uniform(2.0, 5.0)
            target_detected = distance <= 3.0
        else:
            distance = random.uniform(5.0, 15.0)
            target_detected = False
        
        return {
            "distance": round(distance, 2),
            "unit": "mm",
            "target_detected": target_detected,
            "detection_threshold": 3.0,
            "status": "DETECTED" if target_detected else "NO_TARGET"
        }
    
    def _generate_vision_data(self) -> Dict[str, Any]:
        """비전 센서 데이터 생성"""
        if self.current_phase == "inspect":
            # 최종 검사 중
            optical_clarity = random.uniform(0.90, 0.99)
            defects_detected = random.choice([0, 0, 0, 1])  # 75% 무결함
            surface_quality = random.uniform(0.85, 0.98)
        elif self.current_phase in ["position_glass", "laser_check"]:
            # 위치 확인 중
            optical_clarity = random.uniform(0.85, 0.95)
            defects_detected = 0
            surface_quality = random.uniform(0.80, 0.92)
        else:
            optical_clarity = random.uniform(0.70, 0.90)
            defects_detected = 0
            surface_quality = random.uniform(0.70, 0.85)
        
        defect_types = []
        if defects_detected > 0:
            defect_types = random.sample(["bubble", "scratch", "distortion"], k=defects_detected)
        
        return {
            "optical_clarity": round(optical_clarity, 3),
            "surface_quality": round(surface_quality, 3),
            "defects_count": defects_detected,
            "defect_types": defect_types,
            "alignment_check": random.choice([True, True, False]),  # 66% 정렬
            "sealant_coverage": round(random.uniform(90, 100), 1),
            "status": "OK" if defects_detected == 0 else "DEFECT"
        }
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        """차량 위치 추적 정보"""
        if self.current_vehicle and self.vehicle_tracking:
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "rfid": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "estimated_completion": self.phase_start_time + 109,
                "line_position": f"C-{self.current_glass + 2}",
                "next_station": "C03_SEAT"
            }
        return {}
    
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
            "vehicle_position": self._get_vehicle_position(),
            "operation": {
                "phase": self.current_phase,
                "current_glass": self.glass_types[self.current_glass],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "laser_distance": self._generate_laser_distance_data(),
                "force_load_sensor": self._generate_force_load_data(),
                "proximity_sensor": self._generate_proximity_data(),
                "vision_sensor": self._generate_vision_data()
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
            "current_operation": f"{self.current_phase}_{self.glass_types[self.current_glass]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(87, 93), 1),
            "automation_level": "FULLY_AUTO",  # 100% 로봇
            "operator_count": 0
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        # 글라스별 품질 검사 항목
        quality_checks = {
            "optical_clarity": random.uniform(0.88, 0.98),
            "sealant_integrity": random.uniform(0.85, 0.97),
            "positioning_accuracy": random.uniform(0.90, 0.99),
            "surface_quality": random.uniform(0.87, 0.96),
            "force_distribution": random.uniform(0.89, 0.98)
        }
        
        defects = []
        if quality_score < 0.9:
            defects = random.sample(["optical_distortion", "sealant_gap", "misalignment", "surface_defect"], 
                                  k=random.randint(0, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.current_vehicle.vehicle_id if self.current_vehicle else None,
            "overall_score": quality_score,
            "passed": passed,
            "quality_checks": quality_checks,
            "defects": defects,
            "inspector": "AUTO_OPTICAL_SYSTEM",
            "rework_required": not passed
        }