"""
공정 시뮬레이터 베이스 클래스
모든 공정 시뮬레이터의 공통 기능 제공
"""

import time
import random
import math
from datetime import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseStationSimulator(ABC):
    """공정 시뮬레이터 베이스 클래스"""
    
    def __init__(self, station_id: str, config: Dict[str, Any] = None):
        self.station_id = station_id
        self.config = config or {}
        
        # 공통 상태
        self.cycle_count = 0
        self.current_operation = "idle"
        self.operation_start_time = time.time()
        self.station_status = "RUNNING"  # RUNNING, IDLE, ERROR, MAINTENANCE
        
        # 사이클 시간 관리
        self.cycle_time_base = self.config.get("cycle_time_base", 180)
        self.cycle_time_variance = self.config.get("cycle_time_variance", 15)
        self.current_cycle_time = self._generate_cycle_time()
        
        # 품질 파라미터
        quality_params = self.config.get("quality_params", {})
        self.base_quality_score = quality_params.get("base_score", 0.95)
        self.quality_variance = quality_params.get("variance", 0.05)
        self.defect_probability = quality_params.get("defect_probability", 0.02)
        
        # 마지막 품질 검사 시간
        self.last_quality_check = time.time()
        self.quality_check_interval = 30  # 30초마다 품질 검사
        
        print(f"📍 {self.__class__.__name__} 초기화: {station_id}")
    
    def _generate_cycle_time(self) -> float:
        """실제적인 사이클 타임 생성"""
        variance = random.uniform(-self.cycle_time_variance, self.cycle_time_variance)
        return max(self.cycle_time_base * 0.7, self.cycle_time_base + variance)
    
    def _generate_quality_score(self) -> float:
        """실제적인 품질 점수 생성"""
        # 베타 분포를 사용한 품질 점수 (0.8~1.0 범위에 집중)
        if random.random() < self.defect_probability:
            # 불량품 (60~85% 범위)
            score = random.uniform(0.60, 0.85)
        else:
            # 양품 (베타 분포 사용)
            score = random.betavariate(8, 2) * 0.2 + 0.8  # 0.8~1.0 범위
        
        return round(min(1.0, max(0.0, score)), 3)
    
    def _should_quality_pass(self, score: float) -> bool:
        """품질 통과 여부 결정"""
        return score >= 0.85  # 85% 이상이면 통과
    
    def update_cycle(self):
        """사이클 상태 업데이트"""
        current_time = time.time()
        elapsed = current_time - self.operation_start_time
        
        # 사이클 완료 체크
        if elapsed >= self.current_cycle_time:
            self.cycle_count += 1
            self.operation_start_time = current_time
            self.current_cycle_time = self._generate_cycle_time()
            
            # 사이클 완료 시 추가 작업
            self._on_cycle_complete()
    
    def _on_cycle_complete(self):
        """사이클 완료 시 호출되는 메서드 (서브클래스에서 오버라이드)"""
        pass
    
    def should_publish_quality(self) -> bool:
        """품질 데이터 발행 여부 (일정 간격으로)"""
        current_time = time.time()
        if current_time - self.last_quality_check >= self.quality_check_interval:
            self.last_quality_check = current_time
            return True
        return False
    
    @abstractmethod
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성 (서브클래스에서 구현)"""
        pass
    
    @abstractmethod
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성 (서브클래스에서 구현)"""
        pass
    
    @abstractmethod
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성 (서브클래스에서 구현)"""
        pass
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """센서 데이터 생성 (기본 구현)"""
        return {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": {
                "temperature": round(25.0 + random.uniform(-2, 2), 1),
                "humidity": round(50.0 + random.uniform(-5, 5), 1)
            }
        }
