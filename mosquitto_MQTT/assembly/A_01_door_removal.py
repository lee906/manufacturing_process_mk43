"""
도어 탈거 공정 시뮬레이터 (A01_DOOR)
KPI 계산 제거, Raw 데이터만 생성
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from ..base_simulator import BaseStationSimulator

class DoorRemovalSimulator(BaseStationSimulator):
    """도어 탈거 공정 시뮬레이터"""
    
    def __init__(self, station_id: str):
        # 기본 설정
        config = {
            "cycle_time_base": 180,
            "cycle_time_variance": 15,
            "quality_params": {
                "base_score": 0.95,
                "variance": 0.05,
                "defect_probability": 0.02
            }
        }
        
        super().__init__(station_id, config)
        
        # 도어 탈거 작업 단계
        self.work_sequence = [
            {"step": "검사", "duration": 15, "description": "도어 상태 점검"},
            {"step": "볼트_해체", "duration": 120, "description": "볼트 8개 해체"},
            {"step": "씰_제거", "duration": 25, "description": "도어 씰 제거"},
            {"step": "도어_분리", "duration": 20, "description": "도어 본체 분리"},
            {"step": "완료_검사", "duration": 10, "description": "분리 완료 확인"}
        ]
        
        self.current_step_index = 0
        self.step_start_time = time.time()
        self.total_cycle_time = sum(step["duration"] for step in self.work_sequence)
        
        print(f"🚪 도어 탈거 시뮬레이터 초기화: {station_id}")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """실시간 텔레메트리 데이터 생성"""
        current_step = self.work_sequence[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        step_progress = min(1.0, step_elapsed / current_step["duration"])
        
        # 전체 진행률 계산
        completed_duration = sum(step["duration"] for step in self.work_sequence[:self.current_step_index])
        total_progress = (completed_duration + step_elapsed) / self.total_cycle_time
        total_progress = min(1.0, total_progress)
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "process": {
                "current_step": current_step["step"],
                "step_description": current_step["description"],
                "step_progress": round(step_progress * 100, 1),
                "total_progress": round(total_progress * 100, 1),
                "estimated_remaining": round((self.total_cycle_time - completed_duration - step_elapsed), 1),
                "bolt_status": {
                    "total_bolts": 8,
                    "removed_bolts": self._calculate_removed_bolts(step_progress),
                    "current_torque": self._get_current_torque(current_step["step"], step_progress)
                }
            },
            "robots": self._generate_robot_data(current_step["step"], step_progress),
            "sensors": self._generate_door_sensors(current_step["step"], step_progress),
            "cycle_count": self.cycle_count
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성 (KPI 계산용 Raw 데이터)"""
        current_step = self.work_sequence[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"도어_탈거_{current_step['step']}",
            "cycle_time": step_elapsed + sum(step["duration"] for step in self.work_sequence[:self.current_step_index]),
            "production_count": self.cycle_count,  # 🔥 KPI 계산용 핵심 데이터
            "progress": min(100.0, ((step_elapsed + sum(step["duration"] for step in self.work_sequence[:self.current_step_index])) / self.total_cycle_time) * 100),
            "target_cycle_time": self.total_cycle_time
            # 🚫 KPI 계산 필드 제거: efficiency, oee 등
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성 (KPI 계산용 Raw 데이터)"""
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        # 불량 유형 시뮬레이션
        defects = []
        if not passed:
            defects = random.choices([
                "볼트_손상", "도어_스크래치", "씰_파손", "정렬_불량"
            ], k=random.randint(1, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": quality_score,  # 🔥 KPI 계산용 핵심 데이터
            "passed": passed,                # 🔥 KPI 계산용 핵심 데이터
            "defects_found": defects,        # 🔥 KPI 계산용 핵심 데이터
            "inspection_time": round(time.time() - self.step_start_time, 1),
            "checkpoints": {
                "볼트_해체_확인": random.choice([True, True, False]),
                "도어_손상_검사": random.choice([True, True, True, False]),
                "씰_상태_확인": random.choice([True, True, False])
            }
            # 🚫 KPI 계산 필드 제거: grade, fty 등
        }
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """센서 데이터 생성"""
        current_step = self.work_sequence[self.current_step_index]
        step_progress = min(1.0, (time.time() - self.step_start_time) / current_step["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": self._generate_door_sensors(current_step["step"], step_progress)
        }
    
    def _calculate_removed_bolts(self, step_progress: float) -> int:
        """제거된 볼트 수 계산"""
        if self.work_sequence[self.current_step_index]["step"] == "볼트_해체":
            return min(8, int(step_progress * 8))
        elif self.current_step_index > 1:  # 볼트 해체 완료 후
            return 8
        return 0
    
    def _get_current_torque(self, current_step: str, step_progress: float) -> float:
        """현재 토크값 반환"""
        if current_step == "볼트_해체":
            bolt_torques = [120, 135, 125, 140, 118, 145, 130, 125]  # 8개 볼트
            bolt_index = int(step_progress * 8) % 8
            base_torque = bolt_torques[bolt_index]
            return round(base_torque + 15 * math.sin(step_progress * 20 * math.pi), 1)
        return round(5 + 10 * random.random(), 1)
    
    def _generate_robot_data(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """로봇 데이터 생성"""
        return {
            "ROB_A01_001": {
                "model": "KUKA KR 210 R2700",
                "position": self._calculate_robot_position(current_step, step_progress),
                "joints": self._calculate_joint_angles(current_step, step_progress),
                "torques": self._calculate_joint_torques(current_step, step_progress),
                "tcp_force": self._calculate_tcp_force(current_step, step_progress),
                "temperature": 45 + 5 * (step_progress if current_step == "볼트_해체" else 0),
                "power": 2.8 + 1.2 * (step_progress if current_step in ["볼트_해체", "도어_분리"] else 0)
            }
        }
    
    def _calculate_robot_position(self, current_step: str, step_progress: float) -> List[float]:
        """로봇 위치 계산"""
        if current_step == "검사":
            base_pos = [1200, 800, 1100, 0, 0, 0]
            pos_variation = [50 * math.sin(step_progress * 4 * math.pi), 
                           30 * math.cos(step_progress * 4 * math.pi), 0, 0, 0, 
                           30 * math.sin(step_progress * 2 * math.pi)]
        elif current_step == "볼트_해체":
            bolt_positions = [
                [1150, 750, 1200], [1250, 750, 1200], [1150, 850, 1200], [1250, 850, 1200],
                [1150, 750, 1000], [1250, 750, 1000], [1150, 850, 1000], [1250, 850, 1000]
            ]
            bolt_index = int(step_progress * 8) % 8
            current_bolt_pos = bolt_positions[bolt_index]
            base_pos = current_bolt_pos + [0, -15, 90 + 30 * math.sin(step_progress * 10 * math.pi)]
            pos_variation = [0, 0, 0, 0, 0, 0]
        elif current_step == "도어_분리":
            lift_height = step_progress * 200
            base_pos = [1200, 800, 1100 + lift_height, 0, 0, 0]
            pos_variation = [0, 0, 0, 0, 0, 0]
        else:
            base_pos = [1200, 800, 1100, 0, 0, 0]
            pos_variation = [0, 0, 0, 0, 0, 0]
        
        return [round(base_pos[i] + pos_variation[i], 1) for i in range(6)]
    
    def _calculate_joint_angles(self, current_step: str, step_progress: float) -> List[float]:
        """관절 각도 계산"""
        base_angles = [15 * math.sin(step_progress * math.pi), -45 + 10 * step_progress,
                      90 - 20 * step_progress, 0, 45 + 15 * math.sin(step_progress * 2 * math.pi),
                      step_progress * 180]
        return [round(angle, 1) for angle in base_angles]
    
    def _calculate_joint_torques(self, current_step: str, step_progress: float) -> List[float]:
        """관절 토크 계산"""
        base_torques = [15, 45, 25, 8, 12, 5]
        if current_step == "볼트_해체":
            load_factor = 1.5 + 0.3 * math.sin(step_progress * 20 * math.pi)
        elif current_step == "도어_분리":
            load_factor = 1.3  # 도어 무게 반영
        else:
            load_factor = 1.0
        
        return [round(torque * load_factor, 1) for torque in base_torques]
    
    def _calculate_tcp_force(self, current_step: str, step_progress: float) -> List[float]:
        """TCP 힘 계산"""
        if current_step == "볼트_해체":
            return [5, 8, 150 + 50 * math.sin(step_progress * 15 * math.pi), 2, 3, 10]
        elif current_step == "도어_분리":
            return [10, 15, 155, 1, 2, 5]  # 15.5kg 도어 무게
        else:
            return [2, 3, 15, 0.5, 1, 2]
    
    def _generate_door_sensors(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """도어 탈거 전용 센서 데이터"""
        return {
            "torque_sensor": {
                "value": self._get_current_torque(current_step, step_progress),
                "unit": "Nm",
                "status": "OK",
                "target_torque": 125.0
            },
            "vision_system": {
                "door_detected": current_step != "완료_검사",
                "confidence": round(0.95 + 0.05 * step_progress, 3),
                "position_accuracy": round(0.02 + 0.03 * (1 - step_progress), 3),
                "defects_detected": len(self._generate_quality_score() < 0.85) > 0
            },
            "force_sensor": {
                "force_xyz": self._calculate_tcp_force(current_step, step_progress)[:3],
                "unit": "N",
                "status": "OK"
            },
            "proximity_sensor": {
                "distance": round(1.5 + step_progress * 8 if current_step == "도어_분리" else 1.5 + 0.5 * random.random(), 1),
                "unit": "mm",
                "status": "OK"
            }
        }
    
    def update_cycle(self):
        """사이클 업데이트"""
        super().update_cycle()
        
        # 작업 단계 진행 관리
        current_time = time.time()
        current_step = self.work_sequence[self.current_step_index]
        step_elapsed = current_time - self.step_start_time
        
        if step_elapsed >= current_step["duration"]:
            self.current_step_index += 1
            
            if self.current_step_index >= len(self.work_sequence):
                self.current_step_index = 0
                print(f"🏁 도어 탈거 사이클 #{self.cycle_count} 완료")
            
            self.step_start_time = current_time