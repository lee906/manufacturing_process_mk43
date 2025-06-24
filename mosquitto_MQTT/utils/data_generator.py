import random
import time
import math
from typing import Dict, Any, List
from datetime import datetime

class SensorDataGenerator:
    def __init__(self, station_config: Dict[str, Any], variation_range: float = 0.1):
        self.station_id = None
        self.config = station_config
        self.variation_range = variation_range
        self.anomaly_counter = 0
        self.production_count = 0
        self.quality_trend = 1.0
        
        # 시간별 패턴을 위한 시드값
        self.time_seed = random.randint(0, 100)
    
    def generate_realistic_data(self, station_id: str, anomaly_probability: float = 0.05) -> Dict[str, Any]:
        """현실적인 센서 데이터 생성"""
        self.station_id = station_id
        current_time = datetime.now()
        
        # 기본 센서 데이터 생성
        sensor_data = self._generate_sensor_readings(anomaly_probability)
        
        # 생산 정보 생성
        production_data = self._generate_production_data()
        
        # 품질 정보 생성
        quality_data = self._generate_quality_data(sensor_data)
        
        # 알림 정보 생성
        alerts = self._generate_alerts(sensor_data, quality_data)
        
        return {
            "station_id": station_id,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "process_type": self.config["process_type"],
            "location": self.config["location"],
            "sensors": sensor_data,
            "production": production_data,
            "quality": quality_data,
            "alerts": alerts,
            "metadata": {
                "simulation_time": time.time(),
                "cycle_count": self.production_count
            }
        }
    
    def _generate_sensor_readings(self, anomaly_probability: float) -> Dict[str, float]:
        """센서 읽기값 생성"""
        sensors = {}
        
        # 시간 기반 변동 (하루 주기)
        hour_factor = math.sin((time.time() / 3600 + self.time_seed) * 2 * math.pi / 24)
        
        for sensor_name, sensor_config in self.config["sensors"].items():
            # 기본값은 최적값 근처
            base_value = sensor_config["optimal"]
            
            # 정상 변동
            normal_variation = random.uniform(-self.variation_range, self.variation_range)
            
            # 시간별 변동 (±5%)
            time_variation = hour_factor * 0.05
            
            # 이상상황 시뮬레이션
            if random.random() < anomaly_probability:
                anomaly_factor = random.uniform(-0.3, 0.3)  # ±30% 변동
                self.anomaly_counter += 1
            else:
                anomaly_factor = 0
            
            # 최종 값 계산
            final_value = base_value * (1 + normal_variation + time_variation + anomaly_factor)
            
            # 센서 범위 제한
            final_value = max(sensor_config["min"], min(sensor_config["max"], final_value))
            
            sensors[sensor_name] = round(final_value, 3)
        
        return sensors
    
    def _generate_production_data(self) -> Dict[str, Any]:
        """생산 데이터 생성"""
        self.production_count += 1
        
        # 공정별 생산 속도
        process_type = self.config["process_type"]
        base_cycle_time = {
            "robot_assembly": 45,
            "material_transport": 60,
            "quality_inspection": 30,
            "inventory_management": 20
        }.get(process_type, 60)
        
        # 변동이 있는 사이클 타임
        cycle_time = base_cycle_time * random.uniform(0.8, 1.2)
        
        # 처리량 계산 (시간당)
        throughput = 3600 / cycle_time
        
        return {
            "cycle_time": round(cycle_time, 2),
            "throughput_per_hour": round(throughput, 2),
            "total_processed": self.production_count,
            "status": random.choice(["RUNNING", "RUNNING", "RUNNING", "IDLE", "MAINTENANCE"]) if random.random() < 0.1 else "RUNNING"
        }
    
    def _generate_quality_data(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """품질 데이터 생성"""
        # 센서 데이터 기반 품질 점수 계산
        quality_scores = []
        
        for sensor_name, value in sensor_data.items():
            if sensor_name in self.config["sensors"]:
                sensor_config = self.config["sensors"][sensor_name]
                optimal = sensor_config["optimal"]
                range_size = sensor_config["max"] - sensor_config["min"]
                
                # 최적값과의 거리 기반 점수
                distance_from_optimal = abs(value - optimal) / range_size
                score = max(0, 1 - distance_from_optimal * 2)
                quality_scores.append(score)
        
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.8
        
        # 품질 트렌드 적용
        self.quality_trend *= random.uniform(0.98, 1.02)
        self.quality_trend = max(0.7, min(1.0, self.quality_trend))
        
        final_quality = overall_quality * self.quality_trend
        
        # 불량품 확률
        defect_probability = max(0, (1 - final_quality) * 0.1)
        
        return {
            "overall_score": round(final_quality, 3),
            "defect_probability": round(defect_probability, 4),
            "grade": self._get_quality_grade(final_quality),
            "trend": "IMPROVING" if self.quality_trend > 1.001 else "DECLINING" if self.quality_trend < 0.999 else "STABLE"
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """품질 점수를 등급으로 변환"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        else:
            return "D"
    
    def _generate_alerts(self, sensor_data: Dict[str, float], quality_data: Dict[str, Any]) -> Dict[str, bool]:
        """알림 조건 확인"""
        alerts = {
            "temperature_alert": False,
            "pressure_alert": False,
            "quality_alert": False,
            "maintenance_alert": False,
            "efficiency_alert": False
        }
        
        # 센서별 알림 조건
        for sensor_name, value in sensor_data.items():
            if sensor_name in self.config["sensors"]:
                sensor_config = self.config["sensors"][sensor_name]
                
                # 임계값 초과 확인
                if value > sensor_config["max"] * 0.9 or value < sensor_config["min"] * 1.1:
                    if sensor_name == "temperature":
                        alerts["temperature_alert"] = True
                    elif sensor_name == "pressure":
                        alerts["pressure_alert"] = True
        
        # 품질 알림
        if quality_data["overall_score"] < 0.8:
            alerts["quality_alert"] = True
        
        # 유지보수 알림
        if self.anomaly_counter > 3 or quality_data["overall_score"] < 0.7:
            alerts["maintenance_alert"] = True
            
        # 효율성 알림
        if any([alerts["temperature_alert"], alerts["pressure_alert"], alerts["quality_alert"]]):
            alerts["efficiency_alert"] = True
        
        return alerts
    
    def reset_counters(self):
        """카운터 리셋"""
        self.anomaly_counter = 0
        self.production_count = 0
        self.quality_trend = 1.0