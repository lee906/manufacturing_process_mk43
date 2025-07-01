"""
통합 조립라인 시뮬레이터
현대차 15개 스테이션 조립라인 시뮬레이션
"""

import time
import threading
import signal
import sys
from typing import Dict, List
from ..utils.mqtt_publisher import MQTTPublisher
from ..utils.vehicle_tracker import VehicleTracker
from ..utils.production_line_manager import ProductionLineManager
from ..utils.supply_chain_simulator import SupplyChainSimulator
from ..utils.robot_manager import RobotManager
from .A_01_door_removal import A01DoorRemovalSimulator
from .A_02_wiring import A02WiringSimulator
from .A_03_headliner import A03HeadlinerSimulator
from .A_04_crash_pad import A04CrashPadSimulator
from .B_01_fuel_tank import B01FuelTankSimulator
from .B_02_chassis_merge import B02ChassisMergeSimulator
from .B_03_muffler import B03MufflerSimulator
from .C_01_fem import C01FEMSimulator
from .C_02_glass import C02GlassSimulator
from .C_03_seat import C03SeatSimulator
from .C_04_bumper import C04BumperSimulator
from .C_05_tire import C05TireSimulator
from .D_01_wheel_alignment import D01WheelAlignmentSimulator
from .D_02_headlamp import D02HeadlampSimulator
from .D_03_water_leak_test import D03WaterLeakTestSimulator

class AssemblyLineSimulator:
    """통합 조립라인 시뮬레이터"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.mqtt_publisher = MQTTPublisher(broker_host, broker_port)
        self.vehicle_tracker = VehicleTracker()
        self.production_manager = ProductionLineManager()
        self.supply_chain = SupplyChainSimulator()
        self.robot_manager = RobotManager()
        self.running = False
        self.station_threads = []
        
        # 현대차 5종 기준 전체 스테이션들 (생산품 위치 추적 포함)
        self.stations = {
            # A라인 - 도어 및 내장재
            "A01_DOOR": A01DoorRemovalSimulator(),
            "A02_WIRING": A02WiringSimulator(), 
            "A03_HEADLINER": A03HeadlinerSimulator(),
            "A04_CRASH_PAD": A04CrashPadSimulator(),
            
            # B라인 - 샤시 및 연료계통
            "B01_FUEL_TANK": B01FuelTankSimulator(),
            "B02_CHASSIS_MERGE": B02ChassisMergeSimulator(),
            "B03_MUFFLER": B03MufflerSimulator(),
            
            # C라인 - 주요 부품 조립
            "C01_FEM": C01FEMSimulator(),
            "C02_GLASS": C02GlassSimulator(),
            "C03_SEAT": C03SeatSimulator(),
            "C04_BUMPER": C04BumperSimulator(),
            "C05_TIRE": C05TireSimulator(),
            
            # D라인 - 검사 및 최종점검
            "D01_WHEEL_ALIGNMENT": D01WheelAlignmentSimulator(),
            "D02_HEADLAMP": D02HeadlampSimulator(),
            "D03_WATER_LEAK_TEST": D03WaterLeakTestSimulator()
        }
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print(f"🏭 조립라인 시뮬레이터 초기화 완료")
        print(f"📡 MQTT 브로커: {broker_host}:{broker_port}")
        print(f"🔧 활성 스테이션: {len(self.stations)}개")
    
    def start(self):
        """시뮬레이션 시작"""
        if not self.mqtt_publisher.connect():
            print("❌ MQTT 연결 실패")
            return False
        
        self.running = True
        print("🟢 조립라인 시뮬레이션 시작")
        
        # 각 스테이션별 스레드 시작
        for station_id, simulator in self.stations.items():
            thread = threading.Thread(
                target=self._run_station_simulation,
                args=(station_id, simulator),
                daemon=True
            )
            thread.start()
            self.station_threads.append(thread)
            print(f"🔧 {station_id} 스테이션 시작")
        
        # 차량 추적 스레드 시작
        vehicle_thread = threading.Thread(
            target=self._run_vehicle_tracking,
            daemon=True
        )
        vehicle_thread.start()
        self.station_threads.append(vehicle_thread)
        print(f"🚗 차량 추적 시스템 시작")
        
        # 생산라인 관리 스레드 시작
        production_thread = threading.Thread(
            target=self._run_production_management,
            daemon=True
        )
        production_thread.start()
        self.station_threads.append(production_thread)
        print(f"🏭 생산라인 관리자 시작")
        
        # 공급망 관리 스레드 시작
        supply_thread = threading.Thread(
            target=self._run_supply_chain_management,
            daemon=True
        )
        supply_thread.start()
        self.station_threads.append(supply_thread)
        print(f"📦 공급망 관리자 시작")
        
        # 로봇 관리 스레드 시작
        robot_thread = threading.Thread(
            target=self._run_robot_management,
            daemon=True
        )
        robot_thread.start()
        self.station_threads.append(robot_thread)
        print(f"🤖 로봇 관리자 시작")
        
        # 메인 루프
        try:
            while self.running:
                time.sleep(1)
                self._print_status()
        except KeyboardInterrupt:
            self.stop()
        
        return True
    
    def stop(self):
        """시뮬레이션 중지"""
        print("\\n🔴 조립라인 시뮬레이션 중지 중...")
        self.running = False
        
        # 스레드 종료 대기
        for thread in self.station_threads:
            thread.join(timeout=2)
        
        # MQTT 연결 해제
        self.mqtt_publisher.disconnect()
        print("✅ 조립라인 시뮬레이션 종료 완료")
    
    def _run_station_simulation(self, station_id: str, simulator):
        """개별 스테이션 시뮬레이션 실행"""
        last_telemetry = 0
        last_status = 0
        last_quality = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 텔레메트리 데이터 (2초마다)
                if current_time - last_telemetry >= 2:
                    telemetry = simulator.generate_telemetry()
                    if telemetry:
                        topic = f"factory/{station_id}/telemetry"
                        self.mqtt_publisher.publish_data(topic, telemetry)
                    last_telemetry = current_time
                
                # 상태 데이터 (5초마다)
                if current_time - last_status >= 5:
                    status = simulator.generate_status()
                    if status:
                        topic = f"factory/{station_id}/status"
                        self.mqtt_publisher.publish_data(topic, status)
                    last_status = current_time
                
                # 품질 데이터 (조건에 따라)
                if current_time - last_quality >= 10:
                    quality = simulator.generate_quality()
                    if quality:
                        topic = f"factory/{station_id}/quality"
                        self.mqtt_publisher.publish_data(topic, quality)
                    last_quality = current_time
                
                time.sleep(0.5)  # CPU 사용률 조절
                
            except Exception as e:
                print(f"❌ {station_id} 시뮬레이션 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _run_vehicle_tracking(self):
        """차량 추적 시스템 실행"""
        last_update = 0
        last_stats = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 차량 위치 데이터 (3초마다)
                if current_time - last_update >= 3:
                    tracking_data = self.vehicle_tracker.get_vehicle_tracking_data()
                    if tracking_data:
                        topic = "factory/digital_twin/vehicle_tracking"
                        self.mqtt_publisher.publish_data(topic, tracking_data)
                    last_update = current_time
                
                # 생산 통계 (10초마다)
                if current_time - last_stats >= 10:
                    stats_data = self.vehicle_tracker.get_production_statistics()
                    if stats_data:
                        topic = "factory/digital_twin/production_stats"
                        self.mqtt_publisher.publish_data(topic, stats_data)
                    last_stats = current_time
                
                time.sleep(1)  # CPU 사용률 조절
                
            except Exception as e:
                print(f"❌ 차량 추적 시스템 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _run_production_management(self):
        """생산라인 관리 시스템 실행"""
        last_update = 0
        last_line_status = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 생산라인 상태 업데이트 (1초마다)
                if current_time - last_update >= 1:
                    self.production_manager.update_station_states()
                    
                    # 각 스테이션에서 작업 시작 시도
                    for station_id in self.stations.keys():
                        if self.production_manager.can_start_work(station_id):
                            # 차량 추적에서 해당 스테이션에 도착한 차량 찾기
                            vehicles_at_station = self.vehicle_tracker.get_vehicle_by_station(station_id)
                            for vehicle_data in vehicles_at_station:
                                if vehicle_data.get("status") == "waiting":
                                    vehicle_id = vehicle_data.get("vehicle_id")
                                    if self.production_manager.start_work(station_id, vehicle_id):
                                        break
                    
                    last_update = current_time
                
                # 생산라인 상태 발행 (5초마다)
                if current_time - last_line_status >= 5:
                    line_status = self.production_manager.get_line_status()
                    if line_status:
                        topic = "factory/production_line/status"
                        self.mqtt_publisher.publish_data(topic, line_status)
                    last_line_status = current_time
                
                time.sleep(0.5)  # CPU 사용률 조절
                
            except Exception as e:
                print(f"❌ 생산라인 관리 시스템 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _run_supply_chain_management(self):
        """공급망 관리 시스템 실행"""
        last_update = 0
        last_status_publish = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 공급망 시뮬레이션 업데이트 (5초마다)
                if current_time - last_update >= 5:
                    self.supply_chain.update_simulation()
                    last_update = current_time
                
                # 공급망 상태 발행 (15초마다)
                if current_time - last_status_publish >= 15:
                    supply_status = self.supply_chain.get_supply_status()
                    if supply_status:
                        topic = "factory/supply_chain/status"
                        self.mqtt_publisher.publish_data(topic, supply_status)
                    last_status_publish = current_time
                
                time.sleep(2)  # CPU 사용률 조절
                
            except Exception as e:
                print(f"❌ 공급망 관리 시스템 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _run_robot_management(self):
        """로봇 관리 시스템 실행"""
        last_telemetry = 0
        last_status = 0
        last_summary = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 로봇 텔레메트리 데이터 발행 (3초마다)
                if current_time - last_telemetry >= 3:
                    for station_id in self.stations.keys():
                        robot_telemetry = self.robot_manager.get_robot_telemetry(station_id)
                        if robot_telemetry:
                            topic = f"factory/{station_id}/robots/telemetry"
                            self.mqtt_publisher.publish_data(topic, {
                                "station_id": station_id,
                                "robots": robot_telemetry,
                                "timestamp": time.time()
                            })
                    last_telemetry = current_time
                
                # 로봇 상태 데이터 발행 (8초마다)
                if current_time - last_status >= 8:
                    for station_id in self.stations.keys():
                        robot_status = self.robot_manager.get_robot_status(station_id)
                        collaboration_info = self.robot_manager.simulate_collaborative_work(station_id)
                        
                        if robot_status:
                            topic = f"factory/{station_id}/robots/status"
                            self.mqtt_publisher.publish_data(topic, {
                                "station_id": station_id,
                                "robots": robot_status,
                                "collaboration": collaboration_info,
                                "timestamp": time.time()
                            })
                    last_status = current_time
                
                # 전체 로봇 요약 정보 (20초마다)
                if current_time - last_summary >= 20:
                    robot_summary = self.robot_manager.get_all_robots_summary()
                    if robot_summary:
                        topic = "factory/robots/summary"
                        self.mqtt_publisher.publish_data(topic, robot_summary)
                    last_summary = current_time
                
                time.sleep(1)  # CPU 사용률 조절
                
            except Exception as e:
                print(f"❌ 로봇 관리 시스템 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _print_status(self):
        """시뮬레이션 상태 출력"""
        pass  # 너무 자주 출력하지 않도록 비활성화
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\\n📊 시그널 {signum} 수신, 시뮬레이션 종료 중...")
        self.stop()
        sys.exit(0)
    
    def get_station_stats(self) -> Dict:
        """스테이션별 통계 반환"""
        stats = {}
        for station_id, simulator in self.stations.items():
            stats[station_id] = {
                "cycle_count": simulator.cycle_count,
                "station_status": simulator.station_status,
                "current_phase": getattr(simulator, "current_phase", "unknown")
            }
        return stats

def main():
    """메인 실행"""
    print("🏭 현대차 조립라인 시뮬레이터 v2.0")
    print("=" * 50)
    
    simulator = AssemblyLineSimulator()
    simulator.start()

if __name__ == "__main__":
    main()