"""
와이어링 공정 시뮬레이터 (A02_WIRE)
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from ..base_simulator import BaseStationSimulator

class WiringSimulator(BaseStationSimulator):
    """와이어링 공정 시뮬레이터"""
    
    def __init__(self, station_id: str):
        config = {
            "cycle_time_base": 200,
            "cycle_time_variance": 20,
            "quality_params": {
                "base_score": 0.93,
                "variance": 0.07,
                "defect_probability": 0.03
            }
        }
        
        super().__init__(station_id, config)
        
        # 와이어링 작업 상태
        self.total_connections = 24
        self.completed_connections = 0
        self.current_harness = 1
        self.total_harnesses = 3
        
        # 작업 단계
        self.work_phases = [
            {"phase": "준비", "duration": 30},
            {"phase": "메인_하네스", "duration": 80},
            {"phase": "보조_하네스", "duration": 60},
            {"phase": "커넥터_결합", "duration": 25},
            {"phase": "검사", "duration": 15}
        ]
        
        self.current_phase_index = 0
        self.phase_start_time = time.time()
        
        print(f"🔌 와이어링 시뮬레이터 초기화: {station_id}")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성"""
        current_phase = self.work_phases[self.current_phase_index]
        phase_elapsed = time.time() - self.phase_start_time
        phase_progress = min(1.0, phase_elapsed / current_phase["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "process": {
                "current_phase": current_phase["phase"],
                "phase_progress": round(phase_progress * 100, 1),
                "total_connections": self.total_connections,
                "completed_connections": self._calculate_completed_connections(phase_progress),
                "current_harness": self.current_harness,
                "total_harnesses": self.total_harnesses
            },
            "robots": self._generate_robot_data(current_phase["phase"], phase_progress),
            "sensors": self._generate_wiring_sensors(current_phase["phase"], phase_progress),
            "cycle_count": self.cycle_count
        }
    
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성"""
        current_phase = self.work_phases[self.current_phase_index]
        phase_elapsed = time.time() - self.phase_start_time
        
        total_elapsed = phase_elapsed + sum(phase["duration"] for phase in self.work_phases[:self.current_phase_index])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "station_status": self.station_status,
            "current_operation": f"와이어링_{current_phase['phase']}",
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
                "접촉_불량", "단선", "절연_불량", "커넥터_불량", "하네스_손상"
            ], k=random.randint(1, 2))
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": quality_score,
            "passed": passed,
            "defects_found": defects,
            "inspection_time": round(time.time() - self.phase_start_time, 1),
            "electrical_tests": {
                "continuity_test": random.choice([True, True, True, False]),
                "insulation_test": random.choice([True, True, False]),
                "load_test": random.choice([True, True, True, False])
            }
        }
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """센서 데이터 생성"""
        current_phase = self.work_phases[self.current_phase_index]
        phase_progress = min(1.0, (time.time() - self.phase_start_time) / current_phase["duration"])
        
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": self._generate_wiring_sensors(current_phase["phase"], phase_progress)
        }
    
    def _calculate_completed_connections(self, phase_progress: float) -> int:
        """완료된 연결 수 계산"""
        if self.current_phase_index >= 1:  # 메인 하네스 단계 이후
            base_connections = int(phase_progress * 8) + (self.current_phase_index - 1) * 8
            return min(self.total_connections, base_connections)
        return 0
    
    def _generate_robot_data(self, current_phase: str, phase_progress: float) -> Dict[str, Any]:
        """로봇 데이터 생성"""
        return {
            "ROB_A02_001": {  # Universal Robots UR10e
                "model": "Universal Robots UR10e",
                "type": "COLLABORATIVE",
                "position":
                  "ROB_A02_001": {  # Universal Robots UR10e
                "model": "Universal Robots UR10e",
                "type": "COLLABORATIVE",
                "position": self._calculate_ur_position(current_phase, phase_progress),
                "joints": [round(15 + 10 * math.sin(phase_progress * math.pi), 1) for _ in range(6)],
                "torques": [round(8 + 3 * phase_progress, 1) for _ in range(6)],
                "tcp_force": [2, 3, 15 + 10 * phase_progress, 1, 1, 2],
                "temperature": 35 + 3 * phase_progress,
                "power": 1.8 + 0.7 * phase_progress
            },
            "ROB_A02_002": {  # FANUC SR-12iA
                "model": "FANUC SR-12iA",
                "type": "SCARA",
                "position": [800 + 50 * math.cos(phase_progress * 2 * math.pi), 
                           600 + 50 * math.sin(phase_progress * 2 * math.pi), 150, 0],
                "joints": [round(phase_progress * 90, 1) for _ in range(4)],
                "torques": [round(5 + 2 * phase_progress, 1) for _ in range(4)],
                "temperature": 32 + 2 * phase_progress,
                "power": 1.2 + 0.5 * phase_progress
            }
        }
    
    def _calculate_ur_position(self, current_phase: str, phase_progress: float) -> List[float]:
        """UR10e 로봇 위치 계산"""
        if current_phase == "메인_하네스":
            return [600 + 100 * phase_progress, 400, 200 + 50 * phase_progress, 0, 0, 45]
        elif current_phase == "커넥터_결합":
            return [700, 500 + 100 * math.sin(phase_progress * 4 * math.pi), 180, 0, -15, 90]
        else:
            return [650, 450, 200, 0, 0, 0]
    
    def _generate_wiring_sensors(self, current_phase: str, phase_progress: float) -> Dict[str, Any]:
        """와이어링 전용 센서 데이터"""
        return {
            "continuity_tester": {
                "voltage": round(12 + 2 * random.random(), 1),
                "resistance": round(0.5 + 0.3 * random.random(), 2),
                "unit": "Ω",
                "status": "OK"
            },
            "insertion_force": {
                "value": round(45 + 10 * phase_progress + 5 * random.random(), 1),
                "unit": "N",
                "status": "OK" if phase_progress < 0.8 else "HIGH"
            },
            "wire_tension": {
                "value": round(25 + 5 * math.sin(phase_progress * 6 * math.pi), 1),
                "unit": "N",
                "status": "OK"
            },
            "position_encoder": {
                "wire_length": round(500 * phase_progress, 1),
                "unit": "mm",
                "accuracy": 0.1
            }
        }
    
    def update_cycle(self):
        """사이클 업데이트"""
        super().update_cycle()
        
        current_time = time.time()
        current_phase = self.work_phases[self.current_phase_index]
        phase_elapsed = current_time - self.phase_start_time
        
        if phase_elapsed >= current_phase["duration"]:
            self.current_phase_index += 1
            
            if self.current_phase_index >= len(self.work_phases):
                self.current_phase_index = 0
                self.completed_connections = 0
                print(f"🔌 와이어링 사이클 #{self.cycle_count} 완료")
            
            self.phase_start_time = current_time