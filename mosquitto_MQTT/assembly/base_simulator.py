"""
기본 스테이션 시뮬레이터 클래스
모든 조립 스테이션의 공통 기능 제공
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
from ..utils.realistic_variations import variation_manager


class BaseStationSimulator(ABC):
    """기본 스테이션 시뮬레이터"""
    
    def __init__(self, station_id: str, config: Dict[str, Any] = None):
        self.station_id = station_id
        self.config = config or {}
        
        # 공통 상태
        self.station_status = "RUNNING"
        self.cycle_count = 0
        self.operation_start_time = time.time()
        
        # 통일된 사이클 타임 (현대차 의장공정 방식 - 90초 기준)
        base_cycle_time = random.randint(85, 95)
        self.current_cycle_time = variation_manager.calculate_variable_cycle_time(
            station_id, base_cycle_time
        )
        
        # 품질 관련
        self.quality_interval = 5  # 5사이클마다 품질 검사
        self.last_quality_check = 0
        
        # 현실적 변동성 초기화
        variation_manager.initialize_station(station_id)
        
    def update_cycle(self):
        """사이클 업데이트 (현실적 변동성 적용)"""
        current_time = time.time()
        if current_time - self.operation_start_time >= self.current_cycle_time:
            self.cycle_count += 1
            self.operation_start_time = current_time
            
            # 다음 사이클 타임을 현실적 변동성으로 계산
            base_cycle_time = random.randint(120, 300)
            self.current_cycle_time = variation_manager.calculate_variable_cycle_time(
                self.station_id, base_cycle_time
            )
            
            # 작업자 피로도 업데이트
            variation_manager.update_operator_fatigue(self.station_id)
    
    def should_publish_quality(self) -> bool:
        """품질 데이터 발행 여부 결정"""
        return (self.cycle_count - self.last_quality_check) >= self.quality_interval
    
    def _generate_quality_score(self) -> float:
        """품질 점수 생성 (현실적 변동성 적용)"""
        # 기존의 높은 품질률을 현실적으로 조정
        base_score = random.uniform(0.85, 0.98)
        
        # 현실적 품질률로 변환 (70-90% 범위)
        realistic_score = variation_manager.get_realistic_quality_score(
            self.station_id, base_score
        )
        
        return round(realistic_score, 3)
    
    def _should_quality_pass(self, score: float) -> bool:
        """품질 통과 여부 결정 (현실적 기준)"""
        # 현실적 품질 기준 (85% 이상 통과)
        return score >= 0.85
    
    def get_station_variation_status(self) -> Dict[str, Any]:
        """스테이션 변동성 상태 조회"""
        return variation_manager.get_station_status_summary(self.station_id)
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """장비 예열 상태 조회"""
        return variation_manager.simulate_equipment_warmup(self.station_id)
    
    def get_shift_status(self) -> Dict[str, Any]:
        """교대 상태 조회"""
        return variation_manager.simulate_shift_change(self.station_id)
    
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