"""
공통 데이터 생성 유틸리티
센서값, 로봇 데이터, 품질 데이터 등 생성
"""

import random
import math
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

class DataGenerator:
    """공통 데이터 생성 함수들"""
    
    @staticmethod
    def generate_sensor_value(optimal: float, variance_percent: float = 10.0, 
                            min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
        """센서값 생성 (정규분포 기반)"""
        variance = optimal * (variance_percent / 100.0)
        
        # 정규분포 기반 값 생성
        value = random.gauss(optimal, variance / 3)  # 99.7%가 ±variance 범위 내
        
        # 범위 제한
        if min_val is not None:
            value = max(min_val, value)
        if max_val is not None:
            value = min(max_val, value)
        
        return round(value, 3)
    
    @staticmethod
    def generate_robot_position(base_pos: List[float], movement_range: float = 50.0, 
                              smooth_motion: bool = True) -> List[float]:
        """로봇 위치 생성 (부드러운 동작 시뮬레이션)"""
        if smooth_motion:
            # 시간 기반 부드러운 움직임
            t = time.time()
            positions = []
            
            for i, pos in enumerate(base_pos):
                # 각 축마다 다른 주기로 진동
                frequency = 0.1 + (i * 0.05)  # 0.1Hz ~ 0.35Hz
                amplitude = movement_range * (0.3 + 0.1 * i)  # 점진적으로 증가
                
                offset = amplitude * math.sin(2 * math.pi * frequency * t + i)
                positions.append(round(pos + offset, 2))
                
            return positions
        else:
            # 랜덤 움직임
            return [
                round(pos + random.uniform(-movement_range, movement_range), 2)
                for pos in base_pos
            ]
    
    @staticmethod
    def generate_joint_angles(current_angles: List[float], target_angles: List[float], 
                            interpolation_factor: float = 0.1) -> List[float]:
        """로봇 관절각 생성 (보간 동작)"""
        new_angles = []
        
        for current, target in zip(current_angles, target_angles):
            # 선형 보간
            new_angle = current + (target - current) * interpolation_factor
            
            # 각도 제한 (-180 ~ 180)
            new_angle = ((new_angle + 180) % 360) - 180
            new_angles.append(round(new_angle, 2))
        
        return new_angles
    
    @staticmethod
    def generate_joint_torques(joint_angles: List[float], payload: float = 0.0, 
                             max_torques: List[float] = None) -> List[float]:
        """관절 토크 계산 (물리 기반)"""
        if max_torques is None:
            max_torques = [100, 150, 80, 40, 40, 20]  # 기본 최대 토크
        
        torques = []
        
        for i, (angle, max_torque) in enumerate(zip(joint_angles, max_torques)):
            # 중력 영향 (수직 관절만)
            gravity_effect = 0
            if i < 3:  # 주요 관절들
                gravity_effect = math.cos(math.radians(angle)) * (payload / 10)
            
            # 기본 토크 + 중력 보상 + 노이즈
            base_torque = max_torque * 0.1  # 기본 10% 부하
            torque = base_torque + gravity_effect + random.gauss(0, max_torque * 0.02)
            
            # 토크 제한
            torque = max(0, min(max_torque * 0.8, abs(torque)))
            torques.append(round(torque, 1))
        
        return torques
    
    @staticmethod
    def generate_quality_score(base_score: float = 0.95, defect_probability: float = 0.02,
                             station_type: str = "general") -> float:
        """품질 점수 생성 (스테이션별 특성 반영)"""
        
        # 스테이션별 품질 특성
        station_params = {
            "precision": {"alpha": 10, "beta": 1.5},  # 정밀 작업 (높은 품질)
            "assembly": {"alpha": 8, "beta": 2},      # 조립 작업 (일반 품질)
            "welding": {"alpha": 6, "beta": 2.5},     # 용접 작업 (변동 큰 품질)
            "general": {"alpha": 8, "beta": 2}        # 일반 작업
        }
        
        params = station_params.get(station_type, station_params["general"])
        
        # 베타 분포로 품질 점수 생성 (0.8~1.0 범위에 집중)
        if random.random() < defect_probability:
            # 불량품 (60~85% 범위)
            score = random.uniform(0.60, 0.85)
        else:
            # 양품 (베타 분포 사용)
            beta_sample = np.random.beta(params["alpha"], params["beta"])
            score = 0.8 + (beta_sample * 0.2)  # 0.8~1.0 범위로 변환
        
        return round(min(1.0, max(0.0, score)), 3)
    
    @staticmethod
    def generate_cycle_time(base_time: float, variance: float = 15.0, 
                          efficiency_factor: float = 1.0) -> float:
        """사이클 타임 생성 (현실적인 변동)"""
        
        # 정규분포 기반 변동
        time_variance = random.gauss(0, variance / 3)
        
        # 효율성 요인 적용
        actual_time = (base_time + time_variance) / efficiency_factor
        
        # 최소/최대 제한 (기본 시간의 70%~150%)
        min_time = base_time * 0.7
        max_time = base_time * 1.5
        
        return round(max(min_time, min(max_time, actual_time)), 1)
    
    @staticmethod
    def simulate_vibration(amplitude: float = 1.0, frequency: float = 50.0, 
                         noise_level: float = 0.1, wear_factor: float = 1.0,
                         imbalance_factor: float = 0.0) -> Dict[str, float]:
        """진동 시뮬레이션 (3축 진동 + 설비 마모도 반영)"""
        t = time.time()
        
        # 기본 진동 (설비 마모도 반영)
        worn_amplitude = amplitude * (1 + wear_factor * 0.5)
        
        # 불균형으로 인한 주파수 변조
        freq_modulation = frequency * (1 + imbalance_factor * 0.1 * math.sin(2 * math.pi * t * 0.1))
        
        # 3축 진동 (각축마다 다른 특성)
        base_vibration_x = worn_amplitude * math.sin(2 * math.pi * freq_modulation * t)
        base_vibration_y = worn_amplitude * math.cos(2 * math.pi * freq_modulation * t * 1.1)
        base_vibration_z = worn_amplitude * 0.5 * math.sin(4 * math.pi * freq_modulation * t)
        
        # 마모로 인한 하모닉 성분 추가
        if wear_factor > 0.5:
            harmonic_x = worn_amplitude * 0.2 * math.sin(4 * math.pi * freq_modulation * t)
            harmonic_y = worn_amplitude * 0.2 * math.cos(4 * math.pi * freq_modulation * t)
            base_vibration_x += harmonic_x
            base_vibration_y += harmonic_y
        
        # 노이즈 추가 (마모도에 비례)
        enhanced_noise = noise_level * (1 + wear_factor)
        noise_x = random.gauss(0, enhanced_noise)
        noise_y = random.gauss(0, enhanced_noise)
        noise_z = random.gauss(0, enhanced_noise)
        
        return {
            "x_axis": round(base_vibration_x + noise_x, 3),
            "y_axis": round(base_vibration_y + noise_y, 3),
            "z_axis": round(base_vibration_z + noise_z, 3),
            "frequency": round(freq_modulation + random.uniform(-2, 2), 1),
            "amplitude": round(worn_amplitude, 3),
            "wear_indicator": round(wear_factor, 2),
            "imbalance_indicator": round(imbalance_factor, 2)
        }
    
    @staticmethod
    def generate_temperature_profile(base_temp: float = 25.0, operation_heat: float = 15.0,
                                   ambient_variation: float = 3.0, time_constant: float = 300.0,
                                   workload_factor: float = 1.0) -> float:
        """온도 프로파일 생성 (열역학 기반)"""
        
        # 주변 온도 변동 (시간에 따른 변화)
        t = time.time()
        daily_variation = 5 * math.sin(2 * math.pi * t / 86400)  # 24시간 주기
        hourly_variation = 2 * math.sin(2 * math.pi * t / 3600)  # 1시간 주기 미세 변동
        ambient_noise = random.gauss(0, ambient_variation / 3)
        
        # 작업 부하에 따른 온도 상승 (지수적 증가)
        operating_time = (t % time_constant) / time_constant
        heat_buildup = operation_heat * workload_factor * (1 - math.exp(-operating_time * 3))
        
        # 열 방출 (Newton의 냉각 법칙)
        heat_dissipation = heat_buildup * 0.1 * operating_time
        
        total_temp = base_temp + daily_variation + hourly_variation + ambient_noise + heat_buildup - heat_dissipation
        
        return round(max(15.0, total_temp), 1)  # 최소 15도
    
    @staticmethod
    def generate_power_consumption(base_power: float = 2.0, load_factor: float = 1.0,
                                 efficiency: float = 0.85, operating_mode: str = "normal") -> float:
        """전력 소비 생성 (부하 기반 + 운전 모드 반영)"""
        
        # 운전 모드별 전력 계수
        mode_multipliers = {
            "idle": 0.2,      # 대기 모드
            "normal": 1.0,    # 정상 운전
            "high_load": 1.5, # 고부하
            "startup": 2.0,   # 기동 시
            "shutdown": 0.1   # 정지 중
        }
        
        mode_multiplier = mode_multipliers.get(operating_mode, 1.0)
        
        # 기본 소비 + 부하 기반 추가 + 효율성 반영
        load_power = base_power * load_factor * (2 - efficiency) * mode_multiplier
        
        # 전력 변동 (모드에 따라 다름)
        if operating_mode == "startup":
            variation = load_power * random.uniform(-0.1, 0.3)  # 기동 시 큰 변동
        else:
            variation = load_power * random.uniform(-0.05, 0.05)
        
        total_power = load_power + variation
        
        return round(max(0.05, total_power), 2)
    
    @staticmethod
    def generate_defect_list(defect_probability: float = 0.02, 
                           station_type: str = "general") -> List[str]:
        """불량 유형 리스트 생성"""
        
        # 스테이션별 불량 유형
        defect_types = {
            "precision": [
                "dimension_out_of_tolerance",
                "surface_roughness_exceeded", 
                "positioning_accuracy_error",
                "alignment_deviation"
            ],
            "assembly": [
                "loose_connection",
                "missing_component",
                "incorrect_orientation",
                "fastener_issue"
            ],
            "welding": [
                "weld_penetration_insufficient",
                "porosity_detected",
                "crack_formation",
                "heat_affected_zone_excessive"
            ],
            "inspection": [
                "visual_defect_detected",
                "measurement_out_of_range",
                "functional_test_failed",
                "calibration_drift"
            ],
            "general": [
                "quality_check_failed",
                "specification_deviation",
                "process_parameter_violation",
                "material_defect"
            ]
        }
        
        available_defects = defect_types.get(station_type, defect_types["general"])
        
        defects = []
        if random.random() < defect_probability:
            # 1-3개의 불량 선택
            num_defects = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
            defects = random.sample(available_defects, min(num_defects, len(available_defects)))
        
        return defects
    
    @staticmethod
    def generate_timestamp_with_jitter(base_time: Optional[datetime] = None, 
                                     jitter_seconds: float = 0.5) -> str:
        """지터가 있는 타임스탬프 생성"""
        if base_time is None:
            base_time = datetime.now()
        
        # ±지터 범위에서 랜덤 오프셋
        jitter = random.uniform(-jitter_seconds, jitter_seconds)
        actual_time = base_time + timedelta(seconds=jitter)
        
        return actual_time.isoformat()
    
    @staticmethod
    def apply_anomaly(value: float, anomaly_probability: float = 0.01, 
                     anomaly_factor: float = 2.0) -> float:
        """이상치 시뮬레이션"""
        if random.random() < anomaly_probability:
            # 이상치 생성 (정상값의 anomaly_factor배 또는 1/anomaly_factor배)
            if random.random() < 0.5:
                value *= anomaly_factor
            else:
                value /= anomaly_factor
        
        return value
    
    @staticmethod
    def generate_pressure_profile(base_pressure: float = 6.0, target_pressure: float = 8.0,
                                buildup_rate: float = 0.5, release_rate: float = 1.2,
                                system_state: str = "building") -> float:
        """압력 프로파일 생성 (유압/공압 시스템)"""
        
        # 시스템 상태별 압력 변화
        if system_state == "building":
            # 압력 상승 (지수적 접근)
            pressure_diff = target_pressure - base_pressure
            buildup_factor = 1 - math.exp(-buildup_rate * time.time() % 60)
            current_pressure = base_pressure + pressure_diff * buildup_factor
            
        elif system_state == "holding":
            # 압력 유지 (약간의 변동)
            current_pressure = target_pressure + random.gauss(0, 0.1)
            
        elif system_state == "releasing":
            # 압력 해제 (지수적 감소)
            pressure_diff = target_pressure - base_pressure
            release_factor = math.exp(-release_rate * time.time() % 30)
            current_pressure = base_pressure + pressure_diff * release_factor
            
        elif system_state == "cycling":
            # 주기적 압력 변화 (작업 사이클)
            cycle_time = time.time() % 120  # 2분 주기
            if cycle_time < 30:
                # 압력 상승
                progress = cycle_time / 30
                current_pressure = base_pressure + (target_pressure - base_pressure) * progress
            elif cycle_time < 90:
                # 압력 유지
                current_pressure = target_pressure + random.gauss(0, 0.05)
            else:
                # 압력 감소
                progress = (cycle_time - 90) / 30
                current_pressure = target_pressure - (target_pressure - base_pressure) * progress
        else:
            current_pressure = base_pressure
        
        # 압력 센서 노이즈 및 드리프트
        sensor_noise = random.gauss(0, 0.02)
        sensor_drift = 0.01 * math.sin(time.time() / 3600)  # 시간당 드리프트
        
        final_pressure = current_pressure + sensor_noise + sensor_drift
        
        return round(max(0.0, final_pressure), 2)
    
    @staticmethod
    def generate_hydraulic_pressure(nominal_pressure: float = 250.0, 
                                  load_condition: str = "normal",
                                  pump_efficiency: float = 0.9) -> Dict[str, float]:
        """유압 시스템 압력 생성"""
        
        # 부하 조건별 압력 요구량
        load_factors = {
            "no_load": 0.3,
            "light": 0.6,
            "normal": 1.0,
            "heavy": 1.4,
            "maximum": 1.8
        }
        
        load_factor = load_factors.get(load_condition, 1.0)
        target_pressure = nominal_pressure * load_factor
        
        # 펌프 효율성 반영
        actual_pressure = target_pressure * pump_efficiency
        
        # 압력 리플 (펌프 맥동)
        ripple_frequency = 25  # Hz
        pressure_ripple = actual_pressure * 0.02 * math.sin(2 * math.pi * ripple_frequency * time.time())
        
        # 시스템 압력
        system_pressure = actual_pressure + pressure_ripple
        
        # 압력 강하 (배관 손실)
        pressure_drop = system_pressure * 0.05 * random.uniform(0.8, 1.2)
        working_pressure = system_pressure - pressure_drop
        
        # 온도 보상 (온도에 따른 압력 변화)
        ambient_temp = DataGenerator.generate_temperature_profile()
        temp_compensation = (ambient_temp - 20) * 0.002  # 온도당 0.2% 변화
        compensated_pressure = working_pressure * (1 + temp_compensation)
        
        return {
            "system_pressure": round(system_pressure, 1),
            "working_pressure": round(working_pressure, 1),
            "compensated_pressure": round(compensated_pressure, 1),
            "pressure_ripple": round(pressure_ripple, 2),
            "pump_efficiency": round(pump_efficiency * 100, 1),
            "load_condition": load_condition
        }