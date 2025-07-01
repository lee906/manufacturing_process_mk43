"""
기본 스테이션 시뮬레이터 클래스
모든 조립 스테이션의 공통 기능 제공
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseStationSimulator(ABC):
    """기본 스테이션 시뮬레이터"""
    
    def __init__(self, station_id: str, config: Dict[str, Any] = None):
        self.station_id = station_id
        self.config = config or {}
        
        # 공통 상태
        self.station_status = "RUNNING"
        self.cycle_count = 0
        self.operation_start_time = time.time()
        self.current_cycle_time = random.randint(120, 300)  # 기본 사이클 타임
        
        # 품질 관련
        self.quality_interval = 5  # 5사이클마다 품질 검사
        self.last_quality_check = 0
        
    def update_cycle(self):
        """사이클 업데이트"""
        current_time = time.time()
        if current_time - self.operation_start_time >= self.current_cycle_time:
            self.cycle_count += 1
            self.operation_start_time = current_time
            self.current_cycle_time = random.randint(120, 300)
    
    def should_publish_quality(self) -> bool:
        """품질 데이터 발행 여부 결정"""
        return (self.cycle_count - self.last_quality_check) >= self.quality_interval
    
    def _generate_quality_score(self) -> float:
        """품질 점수 생성"""
        base_score = random.uniform(0.85, 0.98)
        # 가끔 불량품 발생
        if random.random() < 0.05:  # 5% 확률로 불량
            base_score = random.uniform(0.70, 0.84)
        return round(base_score, 3)
    
    def _should_quality_pass(self, score: float) -> bool:
        """품질 통과 여부 결정"""
        return score >= 0.90
    
    @abstractmethod
    def generate_telemetry(self) -> Dict[str, Any]:
        """텔레메트리 데이터 생성 (하위 클래스에서 구현)"""
        pass
    
    @abstractmethod
    def generate_status(self) -> Dict[str, Any]:
        """상태 데이터 생성 (하위 클래스에서 구현)"""
        pass
    
    @abstractmethod
    def generate_quality(self) -> Dict[str, Any]:
        """품질 데이터 생성 (하위 클래스에서 구현)"""
        pass