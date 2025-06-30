"""
샤시 메리지 공정 시뮬레이터 (B02_CHASSIS)
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from ..base_simulator import BaseStationSimulator

class ChassisMergeSimulator(BaseStationSimulator):
    """샤시 메리지 공정 시뮬레이터"""
    
    def __init__(self, station_id: str):
        config = {
            "cycle_time_base": 300,
            "cycle_time_variance": 30,
            "quality_params": {
                "base_score": 0.94,
                "variance": 0.06,
                "defect_probability": 0.03
            }
        }
        
        super().__init__(station_id, config)
        
        # 샤시 메리지 단계
        self.merge_steps = [
            {"step": "샤시_정렬", "duration": 60},
            {"step": "메인_결합", "duration": 120},
            {"step": "용접_작업", "duration": 80},
            {"step": "강도_검사", "duration": 30},
            {"step": "마무리_정형", "duration": 10}
        ]
        
        self.current_step_index = 0
        self.step_start_time = time.time()
        
        # 샤시 특성
        self.weld_points = 16
        self.completed_welds = 0
        self.alignment_tolerance = 0.5  # mm
        
        print(f"🏗️ 샤시 메리지 시뮬레이터 초기화: {station_id}")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성"""
        current_step = self.merge_steps[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        step_progress = min(1.0, step_elapsed / current_step["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "process": {
                "current_step": current_step["step"],
                "step_progress": round(step_progress * 100, 1),
                "alignment_status": self._get_alignment_status(current_step["step"], step_progress),
                "welding_progress": self._get_welding_progress(current_step["step"], step_progress),
                "structural_integrity": self._assess_structural_integrity(step_progress)
            },
            "robots": self._generate_dual_robot_data(current_step["step"], step_progress),
            "sensors": self._generate_chassis_sensors(current_step["step"], step_progress),
            "cycle_count": self.cycle_count
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성"""
        current_step = self.merge_steps[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        
        total_elapsed = step_elapsed + sum(step["duration"] for step in self.merge_steps[:self.current_step_index])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"샤시메리지_{current_step['step']}",
            "cycle_time": total_elapsed,
            "production_count": self.cycle_count,
            "progress": min(100.0, (total_elapsed / self.cycle_time_base) * 100),
            "target_cycle_time": self.cycle_time_base
        }
    
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성"""
        quality_score = self._generate_quality_score()
        passed = self._should_quality_pass(quality_score)
        
        defects = []
        if not passed:
            defects = random.choices([
                "용접_불량", "정렬_오차", "강도_부족", "치수_편차", "표면_결함"
            ], k=random.randint(1, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": quality_score,
            "passed": passed,
            "defects_found": defects,
            "inspection_time": round(time.time() - self.step_start_time, 1),
            "structural_tests": {
                "정렬_정밀도_확인": random.choice([True, True, True, False]),
                "용접_품질_검사": random.choice([True, True, False]),
                "구조_강도_테스트": random.choice([True, True, True, False])
            }
        }
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """센서 데이터 생성"""
        current_step = self.merge_steps[self.current_step_index]
        step_progress = min(1.0, (time.time() - self.step_start_time) / current_step["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": self._generate_chassis_sensors(current_step["step"], step_progress)
        }
    
    def _get_alignment_status(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """정렬 상태 반환"""
        if current_step == "샤시_정렬":
            deviation = self.alignment_tolerance * (1 - step_progress) + random.uniform(-0.1, 0.1)
        else:
            deviation = random.uniform(-0.05, 0.05)
        
        return {
            "x_deviation": round(deviation, 3),
            "y_deviation": round(deviation * 0.8, 3),
            "z_deviation": round(deviation * 0.6, 3),
            "tolerance": self.alignment_tolerance,
            "status": "OK" if abs(deviation) <= self.alignment_tolerance else "OUT_OF_SPEC"
        }
    
    def _get_welding_progress(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """용접 진행 상태 반환"""
        if current_step == "용접_작업":
            completed = min(self.weld_points, int(step_progress * self.weld_points))
        elif self.current_step_index > 2:
            completed = self.weld_points
        else:
            completed = 0
        
        return {
            "completed_welds": completed,
            "total_welds": self.weld_points,
            "current_weld_quality": random.choice(["EXCELLENT", "GOOD", "FAIR"]),
            "completion_percentage": round((completed / self.weld_points) * 100, 1)
        }
    
    def _assess_structural_integrity(self, step_progress: float) -> str:
        """구조적 무결성 평가"""
        if self.current_step_index < 2:
            return "PREPARING"
        elif step_progress < 0.7:
            return "PARTIAL"
        elif step_progress < 0.95:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def _generate_dual_robot_data(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """듀얼 로봇 데이터 생성"""
        return {
            "ROB_B02_001": {  # ABB IRB 8700 (메인 작업용)
                "model": "ABB IRB 8700",
                "type": "HEAVY_DUTY",
                "position": self._calculate_heavy_duty_position(current_step, step_progress),
                "joints": [round(10 * math.sin(step_progress * math.pi + i), 1) for i in range(6)],
                "torques": [round(100 + 50 * step_progress, 1) for _ in range(6)],
                "tcp_force": [50, 60, 800 + 200 * step_progress, 15, 20, 30],
                "welding_current": 250 + 50 * step_progress if current_step == "용접_작업" else 0,
                "temperature": 65 + 15 * step_progress,
                "power": 12.5 + 5.5 * step_progress
            },
            "ROB_B02_002": {  # FANUC M-900iB/700 (정밀 위치 조정용)
                "model": "FANUC M-900iB/700",
                "type": "PRECISION",
                "position": self._calculate_precision_position(current_step, step_progress),
                "joints": [round(5 * math.cos(step_progress * math.pi + i), 1) for i in range(6)],
                "torques": [round(80 + 30 * step_progress, 1) for _ in range(6)],
                "tcp_force": [30, 35, 600 + 100 * step_progress, 8, 12, 20],
                "positioning_accuracy": round(0.01 + 0.02 * (1 - step_progress), 3),
                "temperature": 58 + 12 * step_progress,
                "power": 9.8 + 4.2 * step_progress
            }
        }
    
    def _calculate_heavy_duty_position(self, current_step: str, step_progress: float) -> List[float]:
        """중작업용 로봇 위치 계산"""
        if current_step == "메인_결합":
            return [2000 - 200 * step_progress, 1200, 1000 - 100 * step_progress, 0, -30, 0]
        elif current_step == "용접_작업":
            # 용접점들을 순차적으로 이동
            weld_angle = step_progress * 2 * math.pi
            return [1800 + 100 * math.cos(weld_angle), 1200 + 100 * math.sin(weld_angle), 900, 0, -45, weld_angle * 180 / math.pi]
        else:
            return [2000, 1200, 1200, 0, 0, 0]
    
    def _calculate_precision_position(self, current_step: str, step_progress: float) -> List[float]:
        """정밀 조정용 로봇 위치 계산"""
        if current_step == "샤시_정렬":
            # 미세 조정 동작
            return [1600 + 10 * math.sin(step_progress * 8 * math.pi), 
                   1000 + 5 * math.cos(step_progress * 8 * math.pi), 
                   1100, 0, -15, step_progress * 360]
        else:
            return [1600, 1000, 1100, 0, -15, 0]
    
    def _generate_chassis_sensors(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """샤시 메리지 전용 센서 데이터"""
        return {
            "alignment_laser": {
                "accuracy": round(0.01 + 0.005 * random.random(), 3),
                "unit": "mm",
                "status": "OK",
                "target_accuracy": 0.01
            },
            "welding_current": {
                "value": round(250 + 100 * step_progress + 25 * random.random() if current_step == "용접_작업" else 0, 1),
                "unit": "A",
                "status": "OK",
                "target_current": 300.0
            },
            "gap_measurement": {
                "gap_size": round(2.0 + 1.0 * random.random(), 2),
                "unit": "mm",
                "status": "OK",
                "tolerance": "±1.0mm"
            },
            "stress_gauge": {
                "stress_level": round(500 + 300 * step_progress + 50 * random.random(), 1),
                "unit": "με",
                "status": "OK",
                "max_allowable": 2000
            }
        }
    
    def update_cycle(self):
        """사이클 업데이트"""
        super().update_cycle()
        
        current_time = time.time()
        current_step = self.merge_steps[self.current_step_index]
        step_elapsed = current_time - self.step_start_time
        
        if step_elapsed >= current_step["duration"]:
            self.current_step_index += 1
            
            if self.current_step_index >= len(self.merge_steps):
                self.current_step_index = 0
                self.completed_welds = 0
                print(f"🏗️ 샤시 메리지 사이클 #{self.cycle_count} 완료")
            
            self.step_start_time = current_time