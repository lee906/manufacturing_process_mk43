"""
현대차 차량 모델 정의 및 RFID 추적 시스템
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

class VehicleModel(Enum):
    """현대차 인기 모델 5종"""
    AVANTE = "AVANTE"           # 준중형 세단
    TUCSON = "TUCSON"           # 중형 SUV
    PALISADE = "PALISADE"       # 대형 SUV
    KONA = "KONA"               # 소형 SUV
    GRANDEUR = "GRANDEUR"       # 대형 세단

class BodyType(Enum):
    """차체 타입"""
    SEDAN = "SEDAN"
    SUV = "SUV"
    HATCHBACK = "HATCHBACK"

@dataclass
class VehicleSpec:
    """차량 사양 정보"""
    model: VehicleModel
    body_type: BodyType
    variants: List[str]
    colors: List[str]
    cycle_time_base: int  # 기본 사이클 타임 (초)
    complexity_factor: float  # 복잡도 (1.0 기준)

# 현대차 모델별 사양 정의
VEHICLE_SPECS = {
    VehicleModel.AVANTE: VehicleSpec(
        model=VehicleModel.AVANTE,
        body_type=BodyType.SEDAN,
        variants=["1.6_MPI", "1.6_TURBO", "1.6_HYBRID"],
        colors=["POLAR_WHITE", "PHANTOM_BLACK", "SHIMMERING_SILVER", "ELECTRIC_SHADOW"],
        cycle_time_base=180,
        complexity_factor=1.0
    ),
    VehicleModel.TUCSON: VehicleSpec(
        model=VehicleModel.TUCSON,
        body_type=BodyType.SUV,
        variants=["2.0_MPI_2WD", "2.0_TURBO_AWD", "1.6_HYBRID_AWD"],
        colors=["PHANTOM_BLACK", "SHIMMERING_SILVER", "AMAZON_GRAY", "CRIMSON_RED"],
        cycle_time_base=220,
        complexity_factor=1.3
    ),
    VehicleModel.PALISADE: VehicleSpec(
        model=VehicleModel.PALISADE,
        body_type=BodyType.SUV,
        variants=["3.8_V6_AWD", "2.2_DIESEL_AWD"],
        colors=["PHANTOM_BLACK", "STEEL_GRAPHITE", "RAINFOREST", "MOON_DUST"],
        cycle_time_base=280,
        complexity_factor=1.8
    ),
    VehicleModel.KONA: VehicleSpec(
        model=VehicleModel.KONA,
        body_type=BodyType.SUV,
        variants=["1.6_TURBO", "1.6_HYBRID", "ELECTRIC"],
        colors=["PULSE_RED", "PHANTOM_BLACK", "CHALK_WHITE", "SONIC_SILVER"],
        cycle_time_base=160,
        complexity_factor=0.8
    ),
    VehicleModel.GRANDEUR: VehicleSpec(
        model=VehicleModel.GRANDEUR,
        body_type=BodyType.SEDAN,
        variants=["2.5_GDI", "3.3_TURBO", "2.0_HYBRID"],
        colors=["PHANTOM_BLACK", "MOONLIGHT_SILVER", "MARBLE_WHITE", "STORMY_SEA"],
        cycle_time_base=240,
        complexity_factor=1.5
    )
}

@dataclass
class VehicleRFID:
    """차량 RFID 정보"""
    vehicle_id: str             # 차량 고유 ID
    model: str                  # 모델명
    variant: str                # 변형 (엔진/구동방식)
    body_type: str             # 차체 타입
    color: str                 # 색상
    production_order: str      # 생산 지시서 번호
    created_at: datetime       # 생성 시간
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class VehicleTracking:
    """차량 추적 정보"""
    vehicle_id: str
    current_station: str
    entry_time: datetime
    estimated_completion: datetime
    progress: float             # 진행률 (0-100)
    total_stations: int
    completed_stations: int
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        data['estimated_completion'] = self.estimated_completion.isoformat()
        return data

class VehicleFactory:
    """차량 생성 팩토리"""
    
    def __init__(self):
        self.vehicle_counter = 1
        self.daily_production_target = 480  # 일일 생산 대수
        
    def generate_vehicle_id(self) -> str:
        """차량 ID 생성 (현대차 형식)"""
        today = datetime.now().strftime("%Y%m%d")
        return f"HMC{today}{self.vehicle_counter:04d}"
    
    def generate_production_order(self) -> str:
        """생산 지시서 번호 생성"""
        today = datetime.now().strftime("%y%m%d")
        return f"PO-{today}-{self.vehicle_counter:03d}"
    
    def create_random_vehicle(self) -> VehicleRFID:
        """랜덤 차량 생성"""
        # 모델 선택 (인기도 가중치 적용)
        model_weights = {
            VehicleModel.TUCSON: 0.3,     # 30% - 가장 인기
            VehicleModel.AVANTE: 0.25,    # 25%
            VehicleModel.PALISADE: 0.2,   # 20%
            VehicleModel.GRANDEUR: 0.15,  # 15%
            VehicleModel.KONA: 0.1        # 10%
        }
        
        model = random.choices(
            list(model_weights.keys()),
            weights=list(model_weights.values())
        )[0]
        
        spec = VEHICLE_SPECS[model]
        
        vehicle = VehicleRFID(
            vehicle_id=self.generate_vehicle_id(),
            model=model.value,
            variant=random.choice(spec.variants),
            body_type=spec.body_type.value,
            color=random.choice(spec.colors),
            production_order=self.generate_production_order(),
            created_at=datetime.now()
        )
        
        self.vehicle_counter += 1
        return vehicle
    
    def get_cycle_time_for_model(self, model: str, station_type: str = "assembly") -> int:
        """모델별 사이클 타임 계산"""
        model_enum = VehicleModel(model)
        spec = VEHICLE_SPECS[model_enum]
        
        base_time = spec.cycle_time_base
        complexity = spec.complexity_factor
        
        # 스테이션 타입별 가중치
        station_weights = {
            "assembly": 1.0,
            "heavy": 1.2,      # B라인 (샤시, 연료탱크)
            "precision": 0.9,   # C라인 (FEM, 글라스)
            "inspection": 0.7   # D라인 (검사)
        }
        
        weight = station_weights.get(station_type, 1.0)
        final_time = int(base_time * complexity * weight)
        
        # 변동성 추가 (±10%)
        variance = random.uniform(-0.1, 0.1)
        return max(60, int(final_time * (1 + variance)))

# 전역 팩토리 인스턴스
vehicle_factory = VehicleFactory()

def create_vehicle_with_tracking(station_id: str) -> tuple[VehicleRFID, VehicleTracking]:
    """차량 생성 및 추적 정보 포함"""
    vehicle = vehicle_factory.create_random_vehicle()
    
    # 전체 공정 순서 정의
    all_stations = [
        "A01_DOOR", "A02_WIRING", "A03_HEADLINER", "A04_CRASH_PAD",
        "B01_FUEL_TANK", "B02_CHASSIS_MERGE", "B03_MUFFLER",
        "C01_FEM", "C02_GLASS", "C03_SEAT", "C04_BUMPER", "C05_TIRE",
        "D01_WHEEL_ALIGNMENT", "D02_HEADLAMP", "D03_WATER_LEAK_TEST"
    ]
    
    # 현재 스테이션 위치 계산
    current_index = all_stations.index(station_id) if station_id in all_stations else 0
    progress = (current_index / len(all_stations)) * 100
    
    # 예상 완료 시간 계산
    cycle_time = vehicle_factory.get_cycle_time_for_model(vehicle.model)
    estimated_completion = datetime.now() + timedelta(seconds=cycle_time)
    
    tracking = VehicleTracking(
        vehicle_id=vehicle.vehicle_id,
        current_station=station_id,
        entry_time=datetime.now(),
        estimated_completion=estimated_completion,
        progress=progress,
        total_stations=len(all_stations),
        completed_stations=current_index
    )
    
    return vehicle, tracking