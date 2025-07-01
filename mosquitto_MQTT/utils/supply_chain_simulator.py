"""
공급망 시뮬레이터
부품 공급, 재고 관리, 물류 시뮬레이션
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class SupplyStatus(Enum):
    """공급 상태"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DELAYED = "delayed"
    IN_TRANSIT = "in_transit"

class PartCategory(Enum):
    """부품 카테고리"""
    ENGINE = "engine"           # 엔진 부품
    ELECTRICAL = "electrical"   # 전장 부품
    INTERIOR = "interior"       # 내장재
    EXTERIOR = "exterior"       # 외장재
    CHASSIS = "chassis"         # 샤시 부품
    SAFETY = "safety"          # 안전 부품

@dataclass
class PartDefinition:
    """부품 정의"""
    part_id: str
    part_name: str
    category: PartCategory
    supplier: str
    unit_price: float
    lead_time_hours: int       # 리드타임 (시간)
    min_stock_level: int       # 최소 재고
    max_stock_level: int       # 최대 재고
    reorder_point: int         # 재주문점
    usage_per_vehicle: int     # 차량당 사용량
    critical: bool = False     # 중요 부품 여부

@dataclass
class Inventory:
    """재고 정보"""
    part_id: str
    current_stock: int
    reserved_stock: int        # 예약된 재고
    available_stock: int       # 사용 가능한 재고
    last_received: datetime
    next_delivery: Optional[datetime] = None
    pending_orders: List[str] = field(default_factory=list)

@dataclass
class SupplyOrder:
    """공급 주문"""
    order_id: str
    part_id: str
    quantity: int
    order_date: datetime
    expected_delivery: datetime
    supplier: str
    status: str = "ordered"
    actual_delivery: Optional[datetime] = None

class SupplyChainSimulator:
    """공급망 시뮬레이터"""
    
    def __init__(self):
        # 부품 정의
        self.part_definitions = self._define_parts()
        
        # 재고 관리
        self.inventory = {}
        self.supply_orders = {}
        
        # 공급업체 성능
        self.supplier_performance = self._initialize_supplier_performance()
        
        # 일일 생산 계획
        self.daily_production_target = 480  # 일일 480대
        self.vehicle_mix = {
            "아반떼": 0.30,
            "투싼": 0.25, 
            "팰리세이드": 0.15,
            "코나": 0.20,
            "그랜저": 0.10
        }
        
        # 시뮬레이션 설정
        self.start_time = time.time()
        self.last_inventory_check = 0
        self.last_usage_update = 0
        
        # 초기 재고 설정
        self._initialize_inventory()
        
    def _define_parts(self) -> Dict[str, PartDefinition]:
        """부품 정의"""
        parts = {
            # A라인 부품 (도어 및 내장재)
            "DOOR_ASSY_FR": PartDefinition(
                part_id="DOOR_ASSY_FR",
                part_name="Front Door Assembly",
                category=PartCategory.EXTERIOR,
                supplier="Mobis",
                unit_price=85000.0,
                lead_time_hours=24,
                min_stock_level=100,
                max_stock_level=500,
                reorder_point=150,
                usage_per_vehicle=2,
                critical=True
            ),
            "WIRE_HARNESS_MAIN": PartDefinition(
                part_id="WIRE_HARNESS_MAIN",
                part_name="Main Wire Harness",
                category=PartCategory.ELECTRICAL,
                supplier="Kyungshin",
                unit_price=45000.0,
                lead_time_hours=48,
                min_stock_level=200,
                max_stock_level=800,
                reorder_point=300,
                usage_per_vehicle=1,
                critical=True
            ),
            "HEADLINER": PartDefinition(
                part_id="HEADLINER",
                part_name="Roof Headliner",
                category=PartCategory.INTERIOR,
                supplier="Hyundai Wia",
                unit_price=25000.0,
                lead_time_hours=12,
                min_stock_level=150,
                max_stock_level=600,
                reorder_point=200,
                usage_per_vehicle=1
            ),
            "CRASH_PAD": PartDefinition(
                part_id="CRASH_PAD",
                part_name="Dashboard Crash Pad",
                category=PartCategory.INTERIOR,
                supplier="Mobis",
                unit_price=65000.0,
                lead_time_hours=36,
                min_stock_level=80,
                max_stock_level=400,
                reorder_point=120,
                usage_per_vehicle=1,
                critical=True
            ),
            
            # B라인 부품 (샤시 및 연료계통)
            "FUEL_TANK": PartDefinition(
                part_id="FUEL_TANK",
                part_name="Fuel Tank Assembly",
                category=PartCategory.CHASSIS,
                supplier="Yapp",
                unit_price=120000.0,
                lead_time_hours=72,
                min_stock_level=50,
                max_stock_level=300,
                reorder_point=80,
                usage_per_vehicle=1,
                critical=True
            ),
            "CHASSIS_FRAME": PartDefinition(
                part_id="CHASSIS_FRAME",
                part_name="Main Chassis Frame",
                category=PartCategory.CHASSIS,
                supplier="Hyundai Steel",
                unit_price=180000.0,
                lead_time_hours=96,
                min_stock_level=30,
                max_stock_level=200,
                reorder_point=50,
                usage_per_vehicle=1,
                critical=True
            ),
            "MUFFLER_ASSY": PartDefinition(
                part_id="MUFFLER_ASSY", 
                part_name="Exhaust Muffler Assembly",
                category=PartCategory.ENGINE,
                supplier="Sejong Industrial",
                unit_price=75000.0,
                lead_time_hours=24,
                min_stock_level=120,
                max_stock_level=500,
                reorder_point=180,
                usage_per_vehicle=1
            ),
            
            # C라인 부품 (주요 부품 조립)
            "FEM_MODULE": PartDefinition(
                part_id="FEM_MODULE",
                part_name="Front End Module",
                category=PartCategory.EXTERIOR,
                supplier="Mobis",
                unit_price=150000.0,
                lead_time_hours=48,
                min_stock_level=60,
                max_stock_level=350,
                reorder_point=100,
                usage_per_vehicle=1,
                critical=True
            ),
            "WINDSHIELD": PartDefinition(
                part_id="WINDSHIELD",
                part_name="Front Windshield",
                category=PartCategory.SAFETY,
                supplier="Hyundai Mobis Glass",
                unit_price=85000.0,
                lead_time_hours=36,
                min_stock_level=100,
                max_stock_level=400,
                reorder_point=150,
                usage_per_vehicle=1,
                critical=True
            ),
            "SEAT_ASSY_FR": PartDefinition(
                part_id="SEAT_ASSY_FR",
                part_name="Front Seat Assembly",
                category=PartCategory.INTERIOR,
                supplier="Hyundai Dymos",
                unit_price=195000.0,
                lead_time_hours=48,
                min_stock_level=80,
                max_stock_level=400,
                reorder_point=120,
                usage_per_vehicle=2,
                critical=True
            ),
            "BUMPER_FR": PartDefinition(
                part_id="BUMPER_FR",
                part_name="Front Bumper",
                category=PartCategory.EXTERIOR,
                supplier="Mobis",
                unit_price=55000.0,
                lead_time_hours=24,
                min_stock_level=150,
                max_stock_level=600,
                reorder_point=200,
                usage_per_vehicle=1
            ),
            "TIRE_SET": PartDefinition(
                part_id="TIRE_SET",
                part_name="Tire Set (4pcs)",
                category=PartCategory.CHASSIS,
                supplier="Hankook Tire",
                unit_price=320000.0,
                lead_time_hours=24,
                min_stock_level=200,
                max_stock_level=1000,
                reorder_point=300,
                usage_per_vehicle=1,
                critical=True
            ),
            
            # D라인 부품 (검사 및 완료)
            "HEADLAMP_SET": PartDefinition(
                part_id="HEADLAMP_SET",
                part_name="Headlamp Set",
                category=PartCategory.ELECTRICAL,
                supplier="Mobis Lighting",
                unit_price=125000.0,
                lead_time_hours=36,
                min_stock_level=100,
                max_stock_level=500,
                reorder_point=150,
                usage_per_vehicle=1,
                critical=True
            )
        }
        return parts
    
    def _initialize_supplier_performance(self) -> Dict[str, Dict]:
        """공급업체 성능 초기화"""
        return {
            "Mobis": {
                "on_time_delivery": 0.95,
                "quality_rate": 0.98,
                "lead_time_variance": 0.1
            },
            "Kyungshin": {
                "on_time_delivery": 0.92,
                "quality_rate": 0.96,
                "lead_time_variance": 0.15
            },
            "Hyundai Wia": {
                "on_time_delivery": 0.98,
                "quality_rate": 0.99,
                "lead_time_variance": 0.05
            },
            "Yapp": {
                "on_time_delivery": 0.90,
                "quality_rate": 0.95,
                "lead_time_variance": 0.2
            },
            "Hyundai Steel": {
                "on_time_delivery": 0.94,
                "quality_rate": 0.97,
                "lead_time_variance": 0.12
            },
            "Sejong Industrial": {
                "on_time_delivery": 0.88,
                "quality_rate": 0.94,
                "lead_time_variance": 0.25
            },
            "Hyundai Mobis Glass": {
                "on_time_delivery": 0.93,
                "quality_rate": 0.98,
                "lead_time_variance": 0.1
            },
            "Hyundai Dymos": {
                "on_time_delivery": 0.96,
                "quality_rate": 0.97,
                "lead_time_variance": 0.08
            },
            "Hankook Tire": {
                "on_time_delivery": 0.97,
                "quality_rate": 0.99,
                "lead_time_variance": 0.05
            },
            "Mobis Lighting": {
                "on_time_delivery": 0.91,
                "quality_rate": 0.96,
                "lead_time_variance": 0.18
            }
        }
    
    def _initialize_inventory(self):
        """초기 재고 설정"""
        for part_id, part_def in self.part_definitions.items():
            # 초기 재고를 재주문점과 최대 재고 사이의 랜덤 값으로 설정
            initial_stock = random.randint(part_def.reorder_point, part_def.max_stock_level)
            
            self.inventory[part_id] = Inventory(
                part_id=part_id,
                current_stock=initial_stock,
                reserved_stock=0,
                available_stock=initial_stock,
                last_received=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
    
    def consume_parts(self, station_id: str, vehicle_model: str) -> bool:
        """부품 소모 (생산 시)"""
        # 스테이션별 필요 부품 매핑
        station_parts = {
            "A01_DOOR": ["DOOR_ASSY_FR"],
            "A02_WIRING": ["WIRE_HARNESS_MAIN"],
            "A03_HEADLINER": ["HEADLINER"],
            "A04_CRASH_PAD": ["CRASH_PAD"],
            "B01_FUEL_TANK": ["FUEL_TANK"],
            "B02_CHASSIS_MERGE": ["CHASSIS_FRAME"],
            "B03_MUFFLER": ["MUFFLER_ASSY"],
            "C01_FEM": ["FEM_MODULE"],
            "C02_GLASS": ["WINDSHIELD"],
            "C03_SEAT": ["SEAT_ASSY_FR"],
            "C04_BUMPER": ["BUMPER_FR"],
            "C05_TIRE": ["TIRE_SET"],
            "D01_WHEEL_ALIGNMENT": [],  # 검사만
            "D02_HEADLAMP": ["HEADLAMP_SET"],
            "D03_WATER_LEAK_TEST": []   # 검사만
        }
        
        required_parts = station_parts.get(station_id, [])
        
        # 모든 필요 부품이 있는지 확인
        for part_id in required_parts:
            inventory = self.inventory.get(part_id)
            if not inventory:
                return False
                
            part_def = self.part_definitions[part_id]
            
            # 차량 모델별 사용량 조정
            usage_multiplier = {
                "아반떼": 1.0,
                "투싼": 1.1,
                "팰리세이드": 1.3,
                "코나": 0.9,
                "그랜저": 1.2
            }.get(vehicle_model, 1.0)
            
            required_qty = int(part_def.usage_per_vehicle * usage_multiplier)
            
            if inventory.available_stock < required_qty:
                return False
        
        # 부품 소모 실행
        for part_id in required_parts:
            inventory = self.inventory[part_id]
            part_def = self.part_definitions[part_id]
            
            usage_multiplier = {
                "아반떼": 1.0,
                "투싼": 1.1,
                "팰리세이드": 1.3,
                "코나": 0.9,
                "그랜저": 1.2
            }.get(vehicle_model, 1.0)
            
            required_qty = int(part_def.usage_per_vehicle * usage_multiplier)
            
            inventory.current_stock -= required_qty
            inventory.available_stock = inventory.current_stock - inventory.reserved_stock
            
            # 재주문점 체크
            self._check_reorder_point(part_id)
        
        return True
    
    def _check_reorder_point(self, part_id: str):
        """재주문점 체크 및 자동 주문"""
        inventory = self.inventory.get(part_id)
        part_def = self.part_definitions.get(part_id)
        
        if not inventory or not part_def:
            return
            
        if inventory.current_stock <= part_def.reorder_point:
            # 이미 주문 중인 것이 있는지 확인
            pending_orders = [order for order in self.supply_orders.values() 
                            if order.part_id == part_id and order.status in ["ordered", "in_transit"]]
            
            if not pending_orders:
                self._place_order(part_id)
    
    def _place_order(self, part_id: str):
        """주문 생성"""
        part_def = self.part_definitions.get(part_id)
        inventory = self.inventory.get(part_id)
        
        if not part_def or not inventory:
            return
            
        # 주문 수량 계산 (최대 재고 - 현재 재고)
        order_qty = part_def.max_stock_level - inventory.current_stock
        
        # 공급업체 성능 반영
        supplier_perf = self.supplier_performance.get(part_def.supplier, {})
        lead_time_variance = supplier_perf.get("lead_time_variance", 0.1)
        
        # 실제 리드타임 (변동성 반영)
        actual_lead_time = part_def.lead_time_hours * (1 + random.uniform(-lead_time_variance, lead_time_variance))
        
        order_id = f"PO_{part_id}_{int(time.time() * 1000)}"
        order = SupplyOrder(
            order_id=order_id,
            part_id=part_id,
            quantity=order_qty,
            order_date=datetime.now(),
            expected_delivery=datetime.now() + timedelta(hours=actual_lead_time),
            supplier=part_def.supplier
        )
        
        self.supply_orders[order_id] = order
        inventory.pending_orders.append(order_id)
    
    def process_deliveries(self):
        """배송 처리"""
        current_time = datetime.now()
        
        for order_id, order in self.supply_orders.items():
            if order.status == "ordered" and current_time >= order.expected_delivery:
                # 배송 도착
                supplier_perf = self.supplier_performance.get(order.supplier, {})
                on_time_delivery = supplier_perf.get("on_time_delivery", 0.9)
                quality_rate = supplier_perf.get("quality_rate", 0.95)
                
                # 정시 배송 여부
                if random.random() < on_time_delivery:
                    # 품질 검사
                    if random.random() < quality_rate:
                        # 정상 입고
                        self._receive_parts(order_id, order.quantity)
                        order.status = "completed"
                        order.actual_delivery = current_time
                    else:
                        # 품질 불량으로 반품
                        order.status = "quality_rejected"
                        self._place_order(order.part_id)  # 재주문
                else:
                    # 지연 배송
                    delay_hours = random.uniform(2, 24)
                    order.expected_delivery = current_time + timedelta(hours=delay_hours)
                    order.status = "delayed"
    
    def _receive_parts(self, order_id: str, quantity: int):
        """부품 입고"""
        order = self.supply_orders.get(order_id)
        if not order:
            return
            
        inventory = self.inventory.get(order.part_id)
        if not inventory:
            return
            
        inventory.current_stock += quantity
        inventory.available_stock = inventory.current_stock - inventory.reserved_stock
        inventory.last_received = datetime.now()
        
        # 주문 목록에서 제거
        if order_id in inventory.pending_orders:
            inventory.pending_orders.remove(order_id)
    
    def get_supply_status(self) -> Dict:
        """공급 상태 반환"""
        current_time = datetime.now()
        
        # 재고 상태별 분류
        inventory_status = {
            "in_stock": 0,
            "low_stock": 0,
            "out_of_stock": 0,
            "critical_shortage": 0
        }
        
        part_details = []
        
        for part_id, inventory in self.inventory.items():
            part_def = self.part_definitions[part_id]
            
            # 재고 상태 판정
            if inventory.current_stock <= 0:
                status = SupplyStatus.OUT_OF_STOCK
                inventory_status["out_of_stock"] += 1
                if part_def.critical:
                    inventory_status["critical_shortage"] += 1
            elif inventory.current_stock <= part_def.min_stock_level:
                status = SupplyStatus.LOW_STOCK
                inventory_status["low_stock"] += 1
            else:
                status = SupplyStatus.IN_STOCK
                inventory_status["in_stock"] += 1
            
            # 진행 중인 주문 정보
            pending_deliveries = []
            for order_id in inventory.pending_orders:
                order = self.supply_orders.get(order_id)
                if order:
                    pending_deliveries.append({
                        "order_id": order_id,
                        "quantity": order.quantity,
                        "expected_delivery": order.expected_delivery.isoformat(),
                        "status": order.status
                    })
            
            part_details.append({
                "part_id": part_id,
                "part_name": part_def.part_name,
                "category": part_def.category.value,
                "supplier": part_def.supplier,
                "current_stock": inventory.current_stock,
                "available_stock": inventory.available_stock,
                "min_stock_level": part_def.min_stock_level,
                "reorder_point": part_def.reorder_point,
                "status": status.value,
                "critical": part_def.critical,
                "last_received": inventory.last_received.isoformat(),
                "pending_deliveries": pending_deliveries
            })
        
        # 공급업체별 성능
        supplier_summary = {}
        for supplier, perf in self.supplier_performance.items():
            recent_orders = [order for order in self.supply_orders.values() 
                           if order.supplier == supplier and order.status == "completed"]
            
            supplier_summary[supplier] = {
                "on_time_delivery": perf["on_time_delivery"],
                "quality_rate": perf["quality_rate"],
                "recent_orders": len(recent_orders),
                "lead_time_variance": perf["lead_time_variance"]
            }
        
        return {
            "timestamp": current_time.isoformat(),
            "inventory_summary": inventory_status,
            "total_parts": len(self.part_definitions),
            "active_orders": len([o for o in self.supply_orders.values() 
                                if o.status in ["ordered", "in_transit", "delayed"]]),
            "parts": part_details,
            "suppliers": supplier_summary
        }
    
    def simulate_supply_disruption(self, supplier: str, duration_hours: int = 24):
        """공급 중단 시뮬레이션"""
        if supplier in self.supplier_performance:
            # 임시로 성능 저하
            original_perf = self.supplier_performance[supplier].copy()
            self.supplier_performance[supplier]["on_time_delivery"] = 0.1
            self.supplier_performance[supplier]["lead_time_variance"] = 0.8
            
            # 일정 시간 후 복구 (실제로는 스케줄러 필요)
            # 여기서는 시뮬레이션용으로 간단히 구현
            
    def update_simulation(self):
        """시뮬레이션 업데이트"""
        current_time = time.time()
        
        # 배송 처리 (10초마다)
        if current_time - self.last_inventory_check >= 10:
            self.process_deliveries()
            self.last_inventory_check = current_time
        
        # 생산 기반 부품 소모 시뮬레이션 (30초마다)
        if current_time - self.last_usage_update >= 30:
            # 랜덤하게 일부 스테이션에서 부품 소모
            stations = ["A01_DOOR", "A02_WIRING", "C03_SEAT", "C05_TIRE"]
            models = list(self.vehicle_mix.keys())
            
            for _ in range(random.randint(1, 3)):
                station = random.choice(stations)
                model = random.choice(models)
                self.consume_parts(station, model)
            
            self.last_usage_update = current_time