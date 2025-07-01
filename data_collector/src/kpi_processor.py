"""
Data Collector에서 Raw MQTT 데이터를 받아서 KPI로 계산
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict
from dataclasses import dataclass, asdict

@dataclass
class StationMetrics:
    """스테이션별 원시 메트릭 저장"""
    station_id: str
    
    # 생산 메트릭
    total_cycles: int = 0
    total_runtime: float = 0.0  # 분 단위
    cycle_times: List[float] = None
    
    # 품질 메트릭
    total_inspections: int = 0
    passed_first_time: int = 0
    quality_scores: List[float] = None
    defects: List[str] = None
    
    # 시간 추적
    start_time: float = None
    last_update: float = None
    
    def __post_init__(self):
        if self.cycle_times is None:
            self.cycle_times = []
        if self.quality_scores is None:
            self.quality_scores = []
        if self.defects is None:
            self.defects = []
        if self.start_time is None:
            self.start_time = time.time()
        if self.last_update is None:
            self.last_update = time.time()

class KPIProcessor:
    """MQTT Raw 데이터에서 KPI 계산하는 프로세서"""
    
    def __init__(self):
        self.station_metrics = {}  # 스테이션별 메트릭 저장
        self.kpi_targets = {
            "oee": 85.0,
            "fty": 95.0, 
            "otd": 98.0,
            "quality_score": 0.95,
            "throughput": 20.0  # 개/시간
        }
        
        print("🔢 KPI 프로세서 초기화 완료")
    
    def process_mqtt_message(self, topic: str, payload: str) -> Dict[str, Any]:
        """MQTT 메시지를 받아서 KPI 계산"""
        try:
            # 토픽 파싱
            topic_parts = topic.split('/')
            
            # 스테이션별 데이터만 KPI 계산 (factory/A01_DOOR/telemetry)
            if len(topic_parts) < 3:
                return {}
            
            # 시스템 레벨 토픽은 KPI 계산에서 제외
            if topic_parts[1] in ["digital_twin", "production_line", "supply_chain", "robots"]:
                return {}
            
            # 로봇 데이터는 별도 처리 (factory/A01_DOOR/robots/telemetry)
            if len(topic_parts) >= 4 and topic_parts[2] == "robots":
                return {}
            
            # 스테이션 데이터 처리 (factory/A01_DOOR/telemetry)
            if len(topic_parts) >= 3:
                station_id = topic_parts[1]
                data_type = topic_parts[2]
            else:
                return {}
            
            data = json.loads(payload)
            
            # 스테이션 메트릭 초기화
            if station_id not in self.station_metrics:
                self.station_metrics[station_id] = StationMetrics(station_id)
            
            # 데이터 타입별 처리
            if data_type == "status":
                self._process_status_data(station_id, data)
            elif data_type == "quality":
                self._process_quality_data(station_id, data)
            elif data_type == "telemetry":
                self._process_telemetry_data(station_id, data)
            
            # KPI 계산 및 반환
            return self.calculate_station_kpis(station_id)
            
        except Exception as e:
            print(f"❌ KPI 처리 오류: {e}")
            return {}
    
    def _process_status_data(self, station_id: str, data: Dict[str, Any]):
        """상태 데이터 처리"""
        metrics = self.station_metrics[station_id]
        
        # 사이클 완료 체크
        if 'production_count' in data:
            new_cycles = data['production_count'] - metrics.total_cycles
            if new_cycles > 0:
                metrics.total_cycles = data['production_count']
                
                # 사이클 타임 기록
                if 'cycle_time' in data:
                    cycle_time = data['cycle_time']
                    metrics.cycle_times.append(cycle_time)
                    
                    # 최근 100개만 유지
                    if len(metrics.cycle_times) > 100:
                        metrics.cycle_times.pop(0)
        
        # 가동 시간 업데이트
        if data.get('station_status') == 'RUNNING':
            current_time = time.time()
            if metrics.last_update:
                runtime_increment = (current_time - metrics.last_update) / 60  # 분 단위
                metrics.total_runtime += runtime_increment
        
        metrics.last_update = time.time()
    
    def _process_quality_data(self, station_id: str, data: Dict[str, Any]):
        """품질 데이터 처리"""
        metrics = self.station_metrics[station_id]
        
        # 검사 완료 체크
        if 'overall_score' in data:
            metrics.total_inspections += 1
            metrics.quality_scores.append(data['overall_score'])
            
            # 일회 통과 체크
            if data.get('passed', False):
                metrics.passed_first_time += 1
            
            # 불량 기록
            if 'defects_found' in data and data['defects_found']:
                metrics.defects.extend(data['defects_found'])
            
            # 최근 100개만 유지
            if len(metrics.quality_scores) > 100:
                metrics.quality_scores.pop(0)
    
    def _process_telemetry_data(self, station_id: str, data: Dict[str, Any]):
        """텔레메트리 데이터 처리 (필요시)"""
        # 현재는 상태/품질 데이터만 사용하지만, 
        # 향후 센서 데이터 기반 KPI 계산 시 활용
        pass
    
    def calculate_station_kpis(self, station_id: str) -> Dict[str, Any]:
        """스테이션별 모든 KPI 계산"""
        if station_id not in self.station_metrics:
            return {}
        
        metrics = self.station_metrics[station_id]
        current_time = time.time()
        
        # 기본 통계
        runtime_hours = metrics.total_runtime / 60
        planned_time_hours = (current_time - metrics.start_time) / 3600
        
        kpis = {
            "station_id": station_id,
            "timestamp": datetime.now().isoformat(),
            "runtime_hours": round(runtime_hours, 2),
            "total_cycles": metrics.total_cycles
        }
        
        # 1. OEE 계산
        kpis["oee"] = self._calculate_oee(metrics, planned_time_hours)
        
        # 2. FTY 계산  
        kpis["fty"] = self._calculate_fty(metrics)
        
        # 3. OTD 계산
        kpis["otd"] = self._calculate_otd(metrics)
        
        # 4. 품질 점수
        kpis["quality_score"] = self._calculate_quality_score(metrics)
        
        # 5. 시간당 생산량
        kpis["throughput"] = self._calculate_throughput(metrics, runtime_hours)
        
        # 6. 평균 사이클 타임
        kpis["avg_cycle_time"] = self._calculate_avg_cycle_time(metrics)
        
        return kpis
    
    def _calculate_oee(self, metrics: StationMetrics, planned_hours: float) -> Dict[str, float]:
        """OEE = 가동률 × 성능률 × 품질률"""
        
        # 가동률 (Availability)
        runtime_hours = metrics.total_runtime / 60
        availability = (runtime_hours / planned_hours * 100) if planned_hours > 0 else 0
        availability = min(100, availability)
        
        # 성능률 (Performance) 
        if metrics.cycle_times and runtime_hours > 0:
            avg_cycle_time = sum(metrics.cycle_times) / len(metrics.cycle_times)
            target_cycle_time = 180  # 기본 목표 (설정에서 가져와야 함)
            
            # 이론적 최대 생산량
            theoretical_max = (runtime_hours * 3600) / target_cycle_time
            actual_production = metrics.total_cycles
            
            performance = (actual_production / theoretical_max * 100) if theoretical_max > 0 else 0
            performance = min(100, performance)
        else:
            performance = 0
        
        # 품질률 (Quality)
        if metrics.total_inspections > 0:
            quality_rate = (metrics.passed_first_time / metrics.total_inspections * 100)
        else:
            quality_rate = 100
        
        # OEE 종합
        oee = (availability / 100) * (performance / 100) * (quality_rate / 100) * 100
        
        return {
            "value": round(oee, 2),
            "target": self.kpi_targets["oee"],
            "components": {
                "availability": round(availability, 2),
                "performance": round(performance, 2),
                "quality": round(quality_rate, 2)
            }
        }
    
    def _calculate_fty(self, metrics: StationMetrics) -> Dict[str, float]:
        """일회 통과율"""
        if metrics.total_inspections > 0:
            fty = (metrics.passed_first_time / metrics.total_inspections) * 100
        else:
            fty = 100
        
        return {
            "value": round(fty, 2),
            "target": self.kpi_targets["fty"],
            "passed": metrics.passed_first_time,
            "total": metrics.total_inspections
        }
    
    def _calculate_otd(self, metrics: StationMetrics) -> Dict[str, float]:
        """정시 납기율 (사이클 타임 기준)"""
        if metrics.cycle_times:
            avg_cycle_time = sum(metrics.cycle_times) / len(metrics.cycle_times)
            target_cycle_time = 180  # 설정에서 가져와야 함
            
            # 목표 대비 실제 성능
            otd = (target_cycle_time / avg_cycle_time * 100) if avg_cycle_time > 0 else 0
            otd = min(100, otd)  # 100% 넘지 않도록
        else:
            otd = 100
        
        return {
            "value": round(otd, 2),
            "target": self.kpi_targets["otd"],
            "avg_cycle_time": round(sum(metrics.cycle_times) / len(metrics.cycle_times), 1) if metrics.cycle_times else 0
        }
    
    def _calculate_quality_score(self, metrics: StationMetrics) -> Dict[str, float]:
        """평균 품질 점수"""
        if metrics.quality_scores:
            avg_score = sum(metrics.quality_scores) / len(metrics.quality_scores)
        else:
            avg_score = 1.0
        
        return {
            "value": round(avg_score, 3),
            "target": self.kpi_targets["quality_score"],
            "inspections": len(metrics.quality_scores),
            "defects": len(metrics.defects)
        }
    
    def _calculate_throughput(self, metrics: StationMetrics, runtime_hours: float) -> Dict[str, float]:
        """시간당 생산량"""
        if runtime_hours > 0:
            throughput = metrics.total_cycles / runtime_hours
        else:
            throughput = 0
        
        return {
            "value": round(throughput, 1),
            "target": self.kpi_targets["throughput"],
            "unit": "개/시간"
        }
    
    def _calculate_avg_cycle_time(self, metrics: StationMetrics) -> Dict[str, float]:
        """평균 사이클 타임"""
        if metrics.cycle_times:
            avg_time = sum(metrics.cycle_times) / len(metrics.cycle_times)
            # 최근 10개 평균 (트렌드)
            recent_avg = sum(metrics.cycle_times[-10:]) / min(10, len(metrics.cycle_times))
        else:
            avg_time = 0
            recent_avg = 0
        
        return {
            "average": round(avg_time, 1),
            "recent": round(recent_avg, 1),
            "target": 180,  # 설정에서 가져와야 함
            "unit": "초"
        }
    
    def get_factory_kpis(self) -> Dict[str, Any]:
        """전체 공장 KPI 계산"""
        if not self.station_metrics:
            return {}
        
        # 모든 스테이션 KPI 집계
        total_oee = []
        total_fty = []
        total_otd = []
        total_quality = []
        total_throughput = 0
        
        for station_id in self.station_metrics:
            station_kpis = self.calculate_station_kpis(station_id)
            
            if station_kpis:
                total_oee.append(station_kpis["oee"]["value"])
                total_fty.append(station_kpis["fty"]["value"])
                total_otd.append(station_kpis["otd"]["value"])
                total_quality.append(station_kpis["quality_score"]["value"])
                total_throughput += station_kpis["throughput"]["value"]
        
        # 공장 전체 평균
        factory_kpis = {
            "timestamp": datetime.now().isoformat(),
            "factory_oee": round(sum(total_oee) / len(total_oee), 2) if total_oee else 0,
            "factory_fty": round(sum(total_fty) / len(total_fty), 2) if total_fty else 0,
            "factory_otd": round(sum(total_otd) / len(total_otd), 2) if total_otd else 0,
            "factory_quality": round(sum(total_quality) / len(total_quality), 3) if total_quality else 0,
            "factory_throughput": round(total_throughput, 1),
            "active_stations": len(self.station_metrics)
        }
        
        return factory_kpis