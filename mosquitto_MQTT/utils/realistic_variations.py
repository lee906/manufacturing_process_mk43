"""
현실적 공정 변동성 시뮬레이터
실제 제조업 현장의 불확실성과 변동성을 반영
"""

import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from enum import Enum

class OperatorSkillLevel(Enum):
    """작업자 숙련도"""
    TRAINEE = "trainee"      # 신입 (속도 0.7x)
    JUNIOR = "junior"        # 주니어 (속도 0.85x)
    EXPERIENCED = "experienced"  # 숙련 (속도 1.0x)
    EXPERT = "expert"        # 전문가 (속도 1.15x)
    MASTER = "master"        # 마스터 (속도 1.25x)

class EquipmentCondition(Enum):
    """장비 상태"""
    EXCELLENT = "excellent"  # 우수 (속도 1.1x)
    GOOD = "good"           # 양호 (속도 1.0x)
    AVERAGE = "average"     # 보통 (속도 0.95x)
    POOR = "poor"           # 불량 (속도 0.8x)
    MAINTENANCE = "maintenance"  # 정비 필요 (속도 0.6x)

class ShiftType(Enum):
    """근무 시간대"""
    DAY_SHIFT = "day"       # 주간 (06:00-14:00)
    EVENING_SHIFT = "evening"  # 오후 (14:00-22:00)
    NIGHT_SHIFT = "night"   # 야간 (22:00-06:00)

class RealisticVariationManager:
    """현실적 변동성 관리자"""
    
    def __init__(self):
        # 작업자 정보 (스테이션별로 다른 작업자)
        self.operators = {}
        self.equipment_conditions = {}
        self.warmup_status = {}  # 장비 예열 상태
        self.shift_change_effects = {}  # 교대 변경 효과
        
        # 시간 기반 효과
        self.start_time = time.time()
        self.last_shift_change = time.time()
        
        # 글로벌 팩터들
        self.weather_effect = 1.0  # 날씨 영향
        self.material_quality_effect = 1.0  # 자재 품질 영향
        
        print("🎯 현실적 변동성 관리자 초기화 완료")
    
    def initialize_station(self, station_id: str):
        """스테이션별 초기 설정"""
        if station_id not in self.operators:
            # 랜덤한 작업자 할당
            skill_levels = list(OperatorSkillLevel)
            weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # 정규분포 형태
            
            self.operators[station_id] = {
                "skill_level": random.choices(skill_levels, weights=weights)[0],
                "fatigue_level": random.uniform(0.0, 0.2),  # 초기 피로도
                "experience_hours": random.randint(100, 5000),  # 경험 시간
                "last_break": time.time() - random.randint(0, 3600)  # 마지막 휴식
            }
            
            # 장비 상태 할당
            condition_levels = list(EquipmentCondition)
            condition_weights = [0.15, 0.35, 0.35, 0.1, 0.05]  # 대부분 좋은 상태
            
            self.equipment_conditions[station_id] = {
                "condition": random.choices(condition_levels, weights=condition_weights)[0],
                "wear_level": random.uniform(0.0, 0.8),  # 마모 수준
                "last_maintenance": time.time() - random.randint(0, 86400 * 7),  # 마지막 정비
                "operating_hours": random.randint(0, 2000)  # 가동 시간
            }
            
            # 예열 상태 초기화
            self.warmup_status[station_id] = {
                "is_warmed_up": random.choice([True, False]),
                "warmup_start": None,
                "target_temp": random.uniform(35, 45),  # 목표 온도
                "current_temp": random.uniform(20, 30)  # 현재 온도
            }
            
            print(f"📊 {station_id} 초기화: {self.operators[station_id]['skill_level'].value} 작업자, "
                  f"{self.equipment_conditions[station_id]['condition'].value} 장비")
    
    def get_current_shift(self) -> ShiftType:
        """현재 시간대 기반 근무 시간 반환"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 14:
            return ShiftType.DAY_SHIFT
        elif 14 <= current_hour < 22:
            return ShiftType.EVENING_SHIFT
        else:
            return ShiftType.NIGHT_SHIFT
    
    def calculate_variable_cycle_time(self, station_id: str, base_time: float) -> float:
        """가변 사이클 타임 계산"""
        self.initialize_station(station_id)
        
        # 기본 변동성 (±20%)
        base_variation = random.uniform(0.8, 1.2)
        
        # 작업자 숙련도 효과
        operator = self.operators[station_id]
        skill_multipliers = {
            OperatorSkillLevel.TRAINEE: 1.43,      # 신입 (30% 느림)
            OperatorSkillLevel.JUNIOR: 1.18,       # 주니어 (15% 느림)
            OperatorSkillLevel.EXPERIENCED: 1.0,   # 기준
            OperatorSkillLevel.EXPERT: 0.87,       # 전문가 (13% 빠름)
            OperatorSkillLevel.MASTER: 0.8         # 마스터 (20% 빠름)
        }
        skill_factor = skill_multipliers[operator["skill_level"]]
        
        # 장비 상태 효과
        equipment = self.equipment_conditions[station_id]
        condition_multipliers = {
            EquipmentCondition.EXCELLENT: 0.9,     # 우수 (10% 빠름)
            EquipmentCondition.GOOD: 1.0,          # 기준
            EquipmentCondition.AVERAGE: 1.05,      # 평균 (5% 느림)
            EquipmentCondition.POOR: 1.25,         # 불량 (25% 느림)
            EquipmentCondition.MAINTENANCE: 1.67   # 정비 필요 (67% 느림)
        }
        equipment_factor = condition_multipliers[equipment["condition"]]
        
        # 피로도 효과 (시간이 지날수록 증가)
        elapsed_hours = (time.time() - operator["last_break"]) / 3600
        fatigue_factor = 1.0 + min(0.3, elapsed_hours * 0.02)  # 시간당 2% 증가, 최대 30%
        
        # 교대 시간 효과
        shift = self.get_current_shift()
        shift_multipliers = {
            ShiftType.DAY_SHIFT: 1.0,      # 주간 기준
            ShiftType.EVENING_SHIFT: 1.05, # 오후 5% 느림
            ShiftType.NIGHT_SHIFT: 1.15    # 야간 15% 느림
        }
        shift_factor = shift_multipliers[shift]
        
        # 예열 상태 효과
        warmup_factor = self._get_warmup_factor(station_id)
        
        # 최종 사이클 타임 계산
        final_time = (base_time * base_variation * skill_factor * equipment_factor * 
                     fatigue_factor * shift_factor * warmup_factor)
        
        # 극단값 제한 (기본 시간의 50% ~ 200%)
        final_time = max(base_time * 0.5, min(base_time * 2.0, final_time))
        
        return round(final_time, 1)
    
    def _get_warmup_factor(self, station_id: str) -> float:
        """장비 예열 상태에 따른 팩터 계산"""
        warmup = self.warmup_status[station_id]
        
        if not warmup["is_warmed_up"]:
            # 예열 중이면 느려짐
            return 1.3
        
        # 온도에 따른 효율성
        temp_efficiency = min(1.0, warmup["current_temp"] / warmup["target_temp"])
        return 1.0 + (1.0 - temp_efficiency) * 0.2  # 최대 20% 느려짐
    
    def simulate_equipment_warmup(self, station_id: str) -> Dict[str, Any]:
        """장비 예열 시뮬레이션"""
        self.initialize_station(station_id)
        warmup = self.warmup_status[station_id]
        
        if not warmup["is_warmed_up"] and warmup["warmup_start"] is None:
            # 예열 시작
            warmup["warmup_start"] = time.time()
            warmup["current_temp"] = 20.0  # 초기 온도
        
        if warmup["warmup_start"]:
            # 예열 진행
            elapsed_time = time.time() - warmup["warmup_start"]
            
            # 지수적 온도 상승 (15-30분 예열 시간)
            warmup_duration = random.uniform(900, 1800)  # 15-30분
            temp_progress = 1 - math.exp(-elapsed_time / (warmup_duration / 3))
            
            warmup["current_temp"] = 20 + (warmup["target_temp"] - 20) * temp_progress
            
            # 예열 완료 체크
            if warmup["current_temp"] >= warmup["target_temp"] * 0.95:
                warmup["is_warmed_up"] = True
                warmup["warmup_start"] = None
        
        return {
            "is_warmed_up": warmup["is_warmed_up"],
            "current_temp": round(warmup["current_temp"], 1),
            "target_temp": round(warmup["target_temp"], 1),
            "warmup_progress": min(100, (warmup["current_temp"] / warmup["target_temp"]) * 100)
        }
    
    def update_operator_fatigue(self, station_id: str):
        """작업자 피로도 업데이트"""
        if station_id not in self.operators:
            return
        
        operator = self.operators[station_id]
        
        # 시간 경과에 따른 피로도 증가
        elapsed_hours = (time.time() - operator["last_break"]) / 3600
        
        # 4시간마다 자동 휴식 (현실적)
        if elapsed_hours >= 4:
            operator["last_break"] = time.time()
            operator["fatigue_level"] = 0.0
            print(f"😴 {station_id} 작업자 휴식 완료")
        else:
            # 점진적 피로도 증가
            operator["fatigue_level"] = min(1.0, elapsed_hours / 8)  # 8시간에 최대 피로
    
    def simulate_shift_change(self, station_id: str) -> Dict[str, Any]:
        """교대 변경 시뮬레이션"""
        current_time = time.time()
        current_hour = datetime.now().hour
        
        # 교대 시간 체크 (6시, 14시, 22시)
        shift_hours = [6, 14, 22]
        is_shift_change = any(abs(current_hour - h) < 0.5 for h in shift_hours)
        
        if is_shift_change and station_id not in self.shift_change_effects:
            # 교대 변경 효과 시작
            self.shift_change_effects[station_id] = {
                "start_time": current_time,
                "duration": random.uniform(1800, 3600),  # 30-60분 효과
                "productivity_impact": random.uniform(0.7, 0.85)  # 15-30% 생산성 저하
            }
            
            # 새 작업자 할당
            skill_levels = list(OperatorSkillLevel)
            weights = [0.1, 0.2, 0.4, 0.2, 0.1]
            
            self.operators[station_id] = {
                "skill_level": random.choices(skill_levels, weights=weights)[0],
                "fatigue_level": 0.0,  # 새 작업자는 피로하지 않음
                "experience_hours": random.randint(100, 5000),
                "last_break": current_time
            }
            
            print(f"🔄 {station_id} 교대 변경: 새로운 {self.operators[station_id]['skill_level'].value} 작업자")
        
        # 교대 변경 효과 해제
        if station_id in self.shift_change_effects:
            effect = self.shift_change_effects[station_id]
            if current_time - effect["start_time"] >= effect["duration"]:
                del self.shift_change_effects[station_id]
                print(f"✅ {station_id} 교대 변경 효과 종료")
        
        return {
            "current_shift": self.get_current_shift().value,
            "is_shift_change": is_shift_change,
            "shift_change_active": station_id in self.shift_change_effects,
            "operator_skill": self.operators[station_id]["skill_level"].value if station_id in self.operators else "unknown"
        }
    
    def get_realistic_quality_score(self, station_id: str, base_score: float) -> float:
        """현실적 품질 점수 계산"""
        self.initialize_station(station_id)
        
        # 기본 품질을 70-90% 범위로 조정
        realistic_base = 0.7 + (base_score - 0.85) * 0.2 / 0.14  # 0.85-0.99 → 0.7-0.9 매핑
        realistic_base = max(0.7, min(0.9, realistic_base))
        
        # 작업자 숙련도 영향
        operator = self.operators[station_id]
        skill_quality_impact = {
            OperatorSkillLevel.TRAINEE: -0.15,
            OperatorSkillLevel.JUNIOR: -0.08,
            OperatorSkillLevel.EXPERIENCED: 0.0,
            OperatorSkillLevel.EXPERT: +0.05,
            OperatorSkillLevel.MASTER: +0.08
        }
        quality_adjustment = skill_quality_impact[operator["skill_level"]]
        
        # 장비 상태 영향
        equipment = self.equipment_conditions[station_id]
        condition_quality_impact = {
            EquipmentCondition.EXCELLENT: +0.05,
            EquipmentCondition.GOOD: 0.0,
            EquipmentCondition.AVERAGE: -0.03,
            EquipmentCondition.POOR: -0.08,
            EquipmentCondition.MAINTENANCE: -0.15
        }
        quality_adjustment += condition_quality_impact[equipment["condition"]]
        
        # 피로도 영향
        fatigue_impact = -operator["fatigue_level"] * 0.1  # 최대 10% 감소
        
        # 교대 변경 영향
        shift_impact = 0
        if station_id in self.shift_change_effects:
            shift_impact = -0.05  # 교대 변경 시 5% 품질 저하
        
        final_score = realistic_base + quality_adjustment + fatigue_impact + shift_impact
        return max(0.5, min(0.95, final_score))  # 50-95% 범위로 제한
    
    def get_station_status_summary(self, station_id: str) -> Dict[str, Any]:
        """스테이션 상태 요약"""
        self.initialize_station(station_id)
        
        operator = self.operators[station_id]
        equipment = self.equipment_conditions[station_id]
        warmup = self.warmup_status[station_id]
        
        return {
            "operator": {
                "skill_level": operator["skill_level"].value,
                "fatigue_level": round(operator["fatigue_level"], 2),
                "experience_hours": operator["experience_hours"]
            },
            "equipment": {
                "condition": equipment["condition"].value,
                "wear_level": round(equipment["wear_level"], 2),
                "operating_hours": equipment["operating_hours"]
            },
            "warmup": {
                "is_warmed_up": warmup["is_warmed_up"],
                "temperature": round(warmup["current_temp"], 1)
            },
            "shift": {
                "current_shift": self.get_current_shift().value,
                "shift_change_active": station_id in self.shift_change_effects
            }
        }

# 글로벌 인스턴스
variation_manager = RealisticVariationManager()