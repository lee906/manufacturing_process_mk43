"""
헤드라이너 공정 시뮬레이터 (A03_HEAD)
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from ..base_simulator import BaseStationSimulator

class HeadlinerSimulator(BaseStationSimulator):
    """헤드라이너 공정 시뮬레이터"""
    
    def __init__(self, station_id: str):
        config = {
            "cycle_time_base": 150,
            "cycle_time_variance": 12,
            "quality_params": {
                "base_score": 0.97,
                "variance": 0.03,
                "defect_probability": 0.01
            }
        }
        
        super().__init__(station_id, config)
        
        # 헤드라이너 설치 단계
        self.installation_steps = [
            {"step": "위치_확인", "duration": 20},
            {"step": "접착제_도포", "duration": 40},
            {"step": "헤드라이너_설치", "duration": 60},
            {"step": "압착_및_정형", "duration": 25},
            {"step": "마무리_검사", "duration": 15}
        ]
        
        self.current_step_index = 0
        self.step_start_time = time.time()
        
        # 헤드라이너 특성
        self.headliner_thickness = 8.5  # mm
        self.coverage_area = 2.1  # m²
        self.adhesive_temperature = 85.0  # °C
        
        print(f"🏠 헤드라이너 시뮬레이터 초기화: {station_id}")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성"""
        current_step = self.installation_steps[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        step_progress = min(1.0, step_elapsed / current_step["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "process": {
                "current_step": current_step["step"],
                "step_progress": round(step_progress * 100, 1),
                "coverage_percentage": self._calculate_coverage(step_progress),
                "adhesive_status": self._get_adhesive_status(current_step["step"]),
                "headliner_thickness": self.headliner_thickness,
                "installation_quality": self._assess_installation_quality(step_progress)
            },
            "robots": self._generate_gantry_robot_data(current_step["step"], step_progress),
            "sensors": self._generate_headliner_sensors(current_step["step"], step_progress),
            "cycle_count": self.cycle_count
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성"""
        current_step = self.installation_steps[self.current_step_index]
        step_elapsed = time.time() - self.step_start_time
        
        total_elapsed = step_elapsed + sum(step["duration"] for step in self.installation_steps[:self.current_step_index])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"헤드라이너_{current_step['step']}",
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
                "접착_불량", "기포_발생", "주름_형성", "두께_편차", "외관_불량"
            ], k=random.randint(1, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": quality_score,
            "passed": passed,
            "defects_found": defects,
            "inspection_time": round(time.time() - self.step_start_time, 1),
            "quality_checks": {
                "접착_상태_확인": random.choice([True, True, True, False]),
                "평면# 📁 mosquitto_MQTT/assembly/ 폴더 모든 파일 코드