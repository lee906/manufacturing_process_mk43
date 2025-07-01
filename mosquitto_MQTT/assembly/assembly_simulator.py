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