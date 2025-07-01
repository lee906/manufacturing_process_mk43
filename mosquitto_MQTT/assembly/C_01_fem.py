"""
C01 FEM(Front End Module) 조립 시뮬레이터
차체 조립공정 - 프론트 엔드 모듈 장착
iot.md 기반 핵심 센서: 토크 센서, 비전 센서, 근접 센서, 힘/하중 센서
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any
from ..models.vehicle_models import create_vehicle_with_tracking, VehicleRFID, VehicleTracking
from .base_simulator import BaseStationSimulator

class C01FEMSimulator(BaseStationSimulator):
    """FEM 조립 시뮬레이터 - 현대차 5종 기준"""
    
    def __init__(self, station_id: str = "C01_FEM", config: Dict[str, Any] = None):
        super().__init__(station_id, config)
        
        # FEM 구성 요소 목록
        self.fem_components = ["RADIATOR", "CONDENSER", "HEADLAMP_BRACKET", "BUMPER_SUPPORT"]
        self.current_component = 0
        self.operation_phases = ["idle", "position_check", "mount_component", "torque_apply", "force_check", "inspect"]
        self.current_phase = "idle"
        self.phase_start_time = time.time()
        
        # 차량 정보 및 위치 추적
        self.current_vehicle: VehicleRFID = None
        self.vehicle_tracking: VehicleTracking = None
        self.station_position = {"x": 250, "y": 180, "line": "C"}  # C라인 FEM 스테이션 위치
        
        # FEM 조립 파라미터
        self.target_torque = 45.0  # Nm
        self.torque_tolerance = 5.0  # ±5Nm
        self.mounting_points = 8
        self.completed_mounts = 0
        
        print(f">> C01 FEM 조립 시뮬레이터 시작됨")
    
    def _update_operation_phase(self):
        """작업 단계 업데이트"""
        current_time = time.time()
        phase_duration = current_time - self.phase_start_time
        
        # 각 단계별 소요 시간 (초)
        phase_durations = {
            "idle": 3,
            "position_check": 15,
            "mount_component": 35,
            "torque_apply": 25,
            "force_check": 20,
            "inspect": 12
        }
        
        current_duration = phase_durations.get(self.current_phase, 15)
        
        if phase_duration >= current_duration:
            current_idx = self.operation_phases.index(self.current_phase)
            if current_idx < len(self.operation_phases) - 1:
                self.current_phase = self.operation_phases[current_idx + 1]
            else:
                # 컴포넌트 완료 - 다음 컴포넌트로
                self.current_component = (self.current_component + 1) % len(self.fem_components)
                if self.current_component == 0:
                    # 모든 컴포넌트 완료 - 새 차량
                    self._cycle_complete()
                self.current_phase = "idle"
                self.completed_mounts = 0
            
            self.phase_start_time = current_time
    
    def _cycle_complete(self):
        """사이클 완료 처리"""
        self.cycle_count += 1
        self.current_vehicle, self.vehicle_tracking = create_vehicle_with_tracking(self.station_id)
        print(f">> 새 차량 진입: {self.current_vehicle.model} {self.current_vehicle.color}")
    
    def _generate_torque_data(self) -> Dict[str, Any]:
        """토크 센서 데이터 생성"""
        if self.current_phase == "torque_apply":
            # 토크 적용 중 - 실제 토크 측정
            applied_torque = self.target_torque + random.uniform(-self.torque_tolerance, self.torque_tolerance)
            self.completed_mounts = min(self.mounting_points, int((time.time() - self.phase_start_time) / 3))
        elif self.current_phase == "inspect":
            # 검사 단계 - 최종 토크 확인
            applied_torque = self.target_torque + random.uniform(-2.0, 2.0)
        else:
            applied_torque = random.uniform(0, 5.0)  # 대기 상태
        
        return {
            "applied_torque": round(applied_torque, 2),
            "target_torque": self.target_torque,
            "unit": "Nm",
            "tolerance": f"±{self.torque_tolerance}",
            "mounting_points": self.completed_mounts,
            "total_points": self.mounting_points,
            "status": "OK" if abs(applied_torque - self.target_torque) <= self.torque_tolerance else "WARNING"
        }
    
    def _generate_force_load_data(self) -> Dict[str, Any]:
        """힘/하중 센서 데이터 생성"""
        if self.current_phase == "force_check":
            # 하중 검사 중
            applied_force = random.uniform(800, 1200)  # N
            max_safe_force = 1000  # N
        elif self.current_phase == "mount_component":
            # 부품 장착 중
            applied_force = random.uniform(200, 600)
            max_safe_force = 1000
        else:
            applied_force = random.uniform(0, 50)
            max_safe_force = 1000
        
        return {
            "applied_force": round(applied_force, 1),
            "max_safe_force": max_safe_force,
            "unit": "N",
            "force_ratio": round(applied_force / max_safe_force, 3),
            "status": "OK" if applied_force <= max_safe_force else "OVERLOAD"
        }
    
    def _generate_proximity_data(self) -> Dict[str, Any]:
        """근접 센서 데이터 생성"""
        if self.current_phase in ["position_check", "mount_component"]:
            # 위치 확인 중
            distance = random.uniform(0.5, 3.0)  # mm
            target_detected = distance <= 2.0
        elif self.current_phase in ["torque_apply", "force_check"]:
            # 작업 중 - 부품이 근접한 상태
            distance = random.uniform(0.1, 0.8)
            target_detected = True
        else:
            distance = random.uniform(3.0, 10.0)
            target_detected = False
        
        return {
            "distance": round(distance, 2),
            "unit": "mm",
            "target_detected": target_detected,
            "detection_threshold": 2.0,
            "status": "DETECTED" if target_detected else "NO_TARGET"
        }
    
    def _generate_vision_data(self) -> Dict[str, Any]:
        """비전 센서 데이터 생성"""
        if self.current_phase == "inspect":
            # 최종 검사 중
            component_present = random.choice([True, True, True, False])  # 75% 정상
            alignment_ok = random.choice([True, True, False])  # 66% 정렬
            surface_quality = random.uniform(0.85, 0.98)
        elif self.current_phase in ["position_check", "mount_component"]:
            # 위치 확인 및 장착 중
            component_present = True
            alignment_ok = random.choice([True, False])
            surface_quality = random.uniform(0.7, 0.9)
        else:
            component_present = False
            alignment_ok = False
            surface_quality = random.uniform(0.5, 0.8)
        
        defects = []
        if not component_present:
            defects.append("missing_component")
        if not alignment_ok:
            defects.append("misalignment")
        if surface_quality < 0.8:
            defects.append("surface_defect")
        
        return {
            "component_present": component_present,
            "alignment_ok": alignment_ok,
            "surface_quality": round(surface_quality, 3),
            "defects": defects,
            "defect_count": len(defects),
            "status": "OK" if len(defects) == 0 else "DEFECT"
        }
    
    def _get_vehicle_position(self) -> Dict[str, Any]:
        """차량 위치 추적 정보"""
        if self.current_vehicle and self.vehicle_tracking:
            # 실제 생산 라인에서의 위치 계산
            progress = (self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100
            
            return {
                "station_position": self.station_position,
                "vehicle_id": self.current_vehicle.vehicle_id,
                "rfid": self.current_vehicle.vehicle_id,
                "progress_in_station": round(progress, 1),
                "estimated_completion": self.phase_start_time + 110,  # 예상 완료 시간
                "line_position": f"C-{self.current_component + 1}",
                "next_station": "C02_GLASS"
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
                "current_component": self.fem_components[self.current_component],
                "progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1)
            },
            "sensors": {
                "torque_sensor": self._generate_torque_data(),
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
            "current_operation": f"{self.current_phase}_{self.fem_components[self.current_component]}",
            "cycle_progress": round((self.operation_phases.index(self.current_phase) / len(self.operation_phases)) * 100, 1),
            "production_count": self.cycle_count,
            "efficiency": round(random.uniform(90, 96), 1),
            "automation_level": "SEMI_AUTO",  # 협업 로봇
            "operator_count": 1
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        if not self.should_publish_quality():
            return None
            
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        # FEM별 품질 검사 항목
        quality_checks = {
            "mounting_torque": random.uniform(0.88, 0.98),
            "component_alignment": random.uniform(0.90, 0.99),
            "surface_finish": random.uniform(0.87, 0.96),
            "force_distribution": random.uniform(0.89, 0.98),
            "visual_inspection": random.uniform(0.85, 0.97)
        }
        
        defects = []
        if quality_score < 0.9:
            defects = random.sample(["torque_deviation", "misalignment", "surface_damage", "force_overload"], 
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