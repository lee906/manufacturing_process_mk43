"""
머플러 공정 시뮬레이터 (B03_MUFFLER)
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from ..base_simulator import BaseStationSimulator

class MufflerSimulator(BaseStationSimulator):
    """머플러 공정 시뮬레이터"""
    
    def __init__(self, station_id: str):
        config = {
            "cycle_time_base": 100,
            "cycle_time_variance": 8,
            "quality_params": {
                "base_score": 0.94,
                "variance": 0.06,
                "defect_probability": 0.03
            }
        }
        
        super().__init__(station_id, config)
        
        # 머플러 장착 단계
        self.installation_steps = [
            {"step": "위치_조정", "duration": 15},
            {"step": "머플러_장착", "duration": 40},
            {"step": "클램프_체결", "duration": 25},
            {"step": "배기_테스트", "duration": 15},
            {"step": "최종_점검", "duration": 5}
        ]
        
        self.current_step_index = 0
        self.step_start_time = time.time()
        
        # 머플러 특성
        self.muffler_weight = 12.8  # kg
        self.clamp_count = 4
        self.secured_clamps = 0
        
        print(f"🔇 머플러 시뮬레이터 초기화: {station_id}")
    
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
                "muffler_weight": self.muffler_weight,
                "clamp_status": self._get_clamp_status(current_step["step"], step_progress),
                "exhaust_flow": self._get_exhaust_flow(current_step["step"], step_progress),
                "noise_reduction": self._calculate_noise_reduction(step_progress)
            },
            "robots": self._generate_articulated_robot_data(current_step["step"], step_progress),
            "sensors": self._generate_muffler_sensors(current_step["step"], step_progress),
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
            "current_operation": f"머플러_{current_step['step']}",
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
                "배기_누출", "진동_과다", "클램프_불량", "소음_기준_초과", "부식_발견"
            ], k=random.randint(1, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": quality_score,
            "passed": passed,
            "defects_found": defects,
            "inspection_time": round(time.time() - self.step_start_time, 1),
            "performance_tests": {
                "배기_기밀성_확인": random.choice([True, True, True, False]),
                "진동_레벨_측정": random.choice([True, True, False]),
                "고정_강도_확인": random.choice([True, True, True, False])
            }
        }
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """센서 데이터 생성"""
        current_step = self.installation_steps[self.current_step_index]
        step_progress = min(1.0, (time.time() - self.step_start_time) / current_step["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": self._generate_muffler_sensors(current_step["step"], step_progress)
        }
    
    def _get_clamp_status(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """클램프 상태 반환"""
        if current_step == "클램프_체결":
            secured = min(self.clamp_count, int(step_progress * self.clamp_count))
        elif self.current_step_index >= 3:
            secured = self.clamp_count
        else:
            secured = 0
        
        return {
            "secured_clamps": secured,
            "total_clamps": self.clamp_count,
            "clamp_torque": round(50 + 25 * step_progress if current_step == "클램프_체결" else 0, 1)
        }
    
    def _get_exhaust_flow(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """배기 흐름 상태 반환"""
        if current_step == "배기_테스트":
            flow_rate = 150 + 50 * step_progress  # L/min
            back_pressure = 1.5 + 0.5 * step_progress  # bar
        else:
            flow_rate = random.uniform(100, 120)
            back_pressure = random.uniform(1.0, 1.3)
        
        return {
            "flow_rate": round(flow_rate, 1),
            "back_pressure": round(back_pressure, 2),
            "flow_efficiency": round((flow_rate / 200) * 100, 1)
        }
    
    def _calculate_noise_reduction(self, step_progress: float) -> Dict[str, Any]:
        """소음 감소 계산"""
        if self.current_step_index >= 1:  # 머플러 장착 후
            baseline_noise = 85  # dB
            reduction = 15 + 5 * step_progress  # dB 감소
            final_noise = baseline_noise - reduction
        else:
            final_noise = 85  # 머플러 없을 때
            reduction = 0
        
        return {
            "noise_level": round(final_noise + random.uniform(-2, 2), 1),
            "noise_reduction": round(reduction, 1),
            "meets_standard": final_noise <= 70  # 70dB 이하 기준
        }
    
    def _generate_articulated_robot_data(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """관절형 로봇 데이터 생성"""
        return {
            "ROB_B03_001": {
                "model": "KAWASAKI RS010L",
                "type": "ARTICULATED",
                "position": self._calculate_kawasaki_position(current_step, step_progress),
                "joints": [round(15 * math.sin(step_progress * math.pi + i * 0.5), 1) for i in range(6)],
                "torques": [round(25 + 15 * step_progress, 1) for _ in range(6)],
                "tcp_force": [8, 10, 125 + 25 * step_progress, 3, 4, 8],  # 머플러 무게 반영
                "gripper_force": 80 + 20 * step_progress if current_step == "머플러_장착" else 10,
                "temperature": 45 + 8 * step_progress,
                "power": 3.8 + 1.8 * step_progress
            }
        }
    
    def _calculate_kawasaki_position(self, current_step: str, step_progress: float) -> List[float]:
        """KAWASAKI 로봇 위치 계산"""
        if current_step == "머플러_장착":
            # 머플러를 차량 하부로 이동
            start_pos = [1800, 600, 1200]
            end_pos = [1800, 600, 400]  # 차량 하부
            current_pos = [
                start_pos[0],
                start_pos[1], 
                start_pos[2] - (start_pos[2] - end_pos[2]) * step_progress
            ]
            return current_pos + [0, 90, 0]  # 수직으로 작업
        elif current_step == "클램프_체결":
            # 각 클램프 위치로 이동
            clamp_positions = [
                [1750, 600, 450], [1850, 600, 450], 
                [1750, 600, 350], [1850, 600, 350]
            ]
            clamp_index = int(step_progress * len(clamp_positions)) % len(clamp_positions)
            pos = clamp_positions[clamp_index]
            return pos + [0, 90, step_progress * 180]
        else:
            return [1800, 600, 800, 0, 45, 0]  # 대기 위치
    
    def _generate_muffler_sensors(self, current_step: str, step_progress: float) -> Dict[str, Any]:
        """머플러 전용 센서 데이터"""
        return {
            "exhaust_pressure": {
                "value": round(1.5 + 0.5 * step_progress + 0.2 * random.random(), 2),
                "unit": "bar",
                "status": "OK",
                "max_allowable": 3.0
            },
            "temperature_monitor": {
                "value": round(200 + 100 * step_progress + 20 * random.random(), 1),
                "unit": "°C",
                "status": "OK" if 150 <= 300 else "HIGH",
                "max_operating": 400.0
            },
            "clamp_force": {
                "value": round(50 + 25 * step_progress if current_step == "클램프_체결" else random.uniform(0, 10), 1),
                "unit": "bar",
                "status": "OK",
                "target_pressure": 75.0
            },
            "vibration_analysis": {
                "x_axis": round(10 + 5 * step_progress + 2 * random.random(), 1),
                "y_axis": round(8 + 4 * step_progress + 2 * random.random(), 1),
                "z_axis": round(12 + 6 * step_progress + 3 * random.random(), 1),
                "frequency": round(30 + 20 * step_progress + 5 * random.random(), 1),
                "unit": "g",
                "status": "OK"
            }
        }
    
    def update_cycle(self):
        """사이클 업데이트"""
        super().update_cycle()
        
        current_time = time.time()
        current_step = self.installation_steps[self.current_step_index]
        step_elapsed = current_time - self.step_start_time
        
        if step_elapsed >= current_step["duration"]:
            self.current_step_index += 1
            
            if self.current_step_index >= len(self.installation_steps):
                self.current_step_index = 0
                self.secured_clamps = 0
                print(f"🔇 머플러 사이클 #{self.cycle_count} 완료")
            
            self.step_start_time = current_time
