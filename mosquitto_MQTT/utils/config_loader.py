"""
설정 파일 로더 유틸리티
JSON 설정 파일 로딩 및 검증
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigLoader:
    """설정 파일 로더 및 검증기"""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """JSON 설정 파일 로드"""
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 설정 검증
            ConfigLoader._validate_config(config)
            
            print(f"✅ 설정 파일 로드 완료: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"설정 로드 실패: {e}")
    
    @staticmethod
    def get_station_config(config: Dict[str, Any], station_id: str) -> Dict[str, Any]:
        """특정 스테이션 설정 조회"""
        stations = config.get("assembly_stations", {})
        
        if station_id not in stations:
            print(f"⚠️ 스테이션 설정 없음: {station_id}, 기본값 사용")
            return ConfigLoader._get_default_station_config()
        
        station_config = stations[station_id]
        
        # 기본값 병합
        default_config = ConfigLoader._get_default_station_config()
        merged_config = {**default_config, **station_config}
        
        return merged_config
    
    @staticmethod
    def get_mqtt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """MQTT 설정 조회"""
        mqtt_config = config.get("mqtt", {})
        
        # 기본값 설정
        default_mqtt_config = {
            "broker": "localhost",
            "port": 1883,
            "topic_prefix": "factory",
            "qos": {
                "telemetry": 0,
                "status": 1,
                "quality": 1,
                "sensors": 0
            },
            "retain": {
                "telemetry": False,
                "status": True,
                "quality": False,
                "sensors": False
            }
        }
        
        return {**default_mqtt_config, **mqtt_config}
    
    @staticmethod
    def get_simulation_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """시뮬레이션 설정 조회"""
        sim_config = config.get("simulation", {})
        
        default_sim_config = {
            "interval": 3,
            "anomaly_probability": 0.05,
            "speed_multiplier": 1.0,
            "enable_quality_randomization": True,
            "enable_cycle_time_variance": True
        }
        
        return {**default_sim_config, **sim_config}
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]):
        """설정 파일 검증"""
        required_sections = ["mqtt", "assembly_stations"]
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"필수 설정 섹션 누락: {section}")
        
        # MQTT 설정 검증
        mqtt_config = config["mqtt"]
        if "broker" not in mqtt_config:
            raise ValueError("MQTT 브로커 설정이 누락되었습니다")
        
        # 스테이션 설정 검증
        stations = config["assembly_stations"]
        if not stations:
            raise ValueError("assembly_stations 설정이 비어있습니다")
        
        print("✅ 설정 파일 검증 완료")
    
    @staticmethod
    def _get_default_station_config() -> Dict[str, Any]:
        """기본 스테이션 설정"""
        return {
            "cycle_time_base": 180,
            "cycle_time_variance": 15,
            "quality_params": {
                "base_score": 0.95,
                "variance": 0.05,
                "defect_probability": 0.02
            },
            "sensors": {},
            "robots": []
        }
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str):
        """설정 파일 저장"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 설정 파일 저장 완료: {config_path}")
            
        except Exception as e:
            raise RuntimeError(f"설정 저장 실패: {e}")