#!/usr/bin/env python3
"""
의장 공정 IoT 시뮬레이터
Author: Manufacturing Process Team
"""

import json
import time
import logging
import threading
import signal
import sys
from pathlib import Path
from colorama import init, Fore, Style
from datetime import datetime

# 프로젝트 모듈
from utils.mqtt_publisher import MQTTPublisher
from mosquitto_MQTT.assembly.robot import RobotArmSimulator
from assembly.conveyor import ConveyorSimulator
from assembly.quality_check import QualityCheckSimulator
from assembly.inventory import InventorySimulator

# 컬러 출력 초기화
init(autoreset=True)

class AssemblyProcessSimulator:
    def __init__(self, config_path: str = "config.json"):
        """의장 공정 시뮬레이터 초기화"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # 로깅 설정
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # MQTT 클라이언트
        self.mqtt_publisher = None
        
        # 시뮬레이터 인스턴스들
        self.simulators = {}
        self.running = False
        
        # 통계 정보
        self.stats = {
            "start_time": None,
            "total_assemblies": 0,
            "quality_passed": 0,
            "alerts_generated": 0
        }
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> dict:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 설정 파일을 찾을 수 없습니다: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 설정 파일 파싱 오류: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """로깅 설정"""
        # logs 디렉토리 생성
        Path("logs").mkdir(exist_ok=True)
        
        # 로그 포맷 설정
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # 파일 핸들러
        file_handler = logging.FileHandler(
            f"logs/assembly_simulator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def initialize(self) -> bool:
        """시뮬레이터 초기화"""
        try:
            print(f"{Fore.CYAN}🏭 의장 공정 IoT 시뮬레이터 초기화 중...{Style.RESET_ALL}")
            
            # MQTT 클라이언트 초기화
            mqtt_config = self.config["mqtt"]
            self.mqtt_publisher = MQTTPublisher(
                mqtt_config["broker"], 
                mqtt_config["port"]
            )
            
            if not self.mqtt_publisher.connect():
                print(f"{Fore.RED}❌ MQTT 브로커 연결 실패{Style.RESET_ALL}")
                return False
            
            print(f"{Fore.GREEN}✅ MQTT 브로커 연결 성공{Style.RESET_ALL}")
            
            # 각 스테이션 시뮬레이터 초기화
            assembly_stations = self.config["assembly_stations"]
            simulation_config = self.config["simulation"]
            
            # 로봇팔 시뮬레이터
            if "ROBOT_ARM_01" in assembly_stations:
                self.simulators["robot_arm"] = RobotArmSimulator(
                    "ROBOT_ARM_01",
                    assembly_stations["ROBOT_ARM_01"],
                    self.mqtt_publisher,
                    self.config["assembly_process"]
                )
                print(f"{Fore.BLUE}🤖 로봇팔 시뮬레이터 초기화 완료{Style.RESET_ALL}")
            
            # 컨베이어 시뮬레이터
            if "CONVEYOR_01" in assembly_stations:
                self.simulators["conveyor"] = ConveyorSimulator(
                    "CONVEYOR_01",
                    assembly_stations["CONVEYOR_01"], 
                    self.mqtt_publisher
                )
                print(f"{Fore.YELLOW}🏭 컨베이어 시뮬레이터 초기화 완료{Style.RESET_ALL}")
            
            # 품질검사 시뮬레이터
            if "QUALITY_CHECK_01" in assembly_stations:
                self.simulators["quality_check"] = QualityCheckSimulator(
                    "QUALITY_CHECK_01",
                    assembly_stations["QUALITY_CHECK_01"],
                    self.mqtt_publisher,
                    self.config["assembly_process"]["quality_standards"]
                )
                print(f"{Fore.MAGENTA}🔍 품질검사 시뮬레이터 초기화 완료{Style.RESET_ALL}")
            
            # 재고관리 시뮬레이터
            if "INVENTORY_01" in assembly_stations:
                self.simulators["inventory"] = InventorySimulator(
                    "INVENTORY_01",
                    assembly_stations["INVENTORY_01"],
                    self.mqtt_publisher,
                    self.config["assembly_process"]["parts_catalog"]
                )
                print(f"{Fore.GREEN}📦 재고관리 시뮬레이터 초기화 완료{Style.RESET_ALL}")
            
            self.logger.info("의장 공정 시뮬레이터 초기화 완료")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ 초기화 실패: {e}{Style.RESET_ALL}")
            self.logger.error(f"초기화 실패: {e}")
            return False
    
    def start_simulation(self):
        """시뮬레이션 시작"""
        if not self.initialize():
            return
        
        try:
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            print(f"\n{Fore.GREEN}🚀 의장 공정 시뮬레이션 시작!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 실시간 모니터링: http://localhost:5173{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📡 MQTT 토픽: {self.config['mqtt']['topic_prefix']}/+/data{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🛑 종료하려면 Ctrl+C를 누르세요{Style.RESET_ALL}\n")
            
            # 시뮬레이션 설정
            interval = self.config["simulation"]["interval"]
            anomaly_prob = self.config["simulation"]["anomaly_probability"]
            
            # 모든 시뮬레이터 시작
            for name, simulator in self.simulators.items():
                simulator.start(interval, anomaly_prob)
                time.sleep(0.5)  # 순차적 시작
            
            # 통계 출력 스레드 시작
            stats_thread = threading.Thread(target=self._statistics_reporter, daemon=True)
            stats_thread.start()
            
            # 메인 루프
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  사용자 종료 요청{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ 시뮬레이션 오류: {e}{Style.RESET_ALL}")
            self.logger.error(f"시뮬레이션 오류: {e}")
        finally:
            self.stop_simulation()
    
    def stop_simulation(self):
        """시뮬레이션 중지"""
        print(f"{Fore.YELLOW}🛑 의장 공정 시뮬레이션 중지 중...{Style.RESET_ALL}")
        
        self.running = False
        
        # 모든 시뮬레이터 중지
        for name, simulator in self.simulators.items():
            try:
                simulator.stop()
                print(f"{Fore.GREEN}✅ {name} 시뮬레이터 중지 완료{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ {name} 시뮬레이터 중지 실패: {e}{Style.RESET_ALL}")
        
        # MQTT 연결 해제
        if self.mqtt_publisher:
            self.mqtt_publisher.disconnect()
            print(f"{Fore.GREEN}✅ MQTT 연결 해제 완료{Style.RESET_ALL}")
        
        # 최종 통계 출력
        self._print_final_statistics()
        
        print(f"{Fore.GREEN}✅ 의장 공정 시뮬레이션 종료 완료{Style.RESET_ALL}")
        self.logger.info("의장 공정 시뮬레이션 종료")
    
    def _statistics_reporter(self):
        """주기적 통계 리포트"""
        while self.running:
            try:
                time.sleep(30)  # 30초마다 통계 출력
                if self.running:
                    self._print_runtime_statistics()
            except Exception as e:
                self.logger.error(f"통계 리포트 오류: {e}")
    
    def _print_runtime_statistics(self):
        """실행 중 통계 출력"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        
        print(f"\n{Fore.CYAN}📊 === 의장 공정 실시간 통계 ==={Style.RESET_ALL}")
        print(f"⏱️  실행 시간: {str(runtime).split('.')[0]}")
        print(f"🏭 총 조립 건수: {self.stats['total_assemblies']}")
        print(f"✅ 품질 통과: {self.stats['quality_passed']}")
        print(f"⚠️  알림 발생: {self.stats['alerts_generated']}")
        
        # 각 시뮬레이터 상태
        for name, simulator in self.simulators.items():
            if hasattr(simulator, 'get_status'):
                status = simulator.get_status()
                print(f"📋 {name}: {status}")
        
        print(f"{Fore.CYAN}================================{Style.RESET_ALL}\n")
    
    def _print_final_statistics(self):
        """최종 통계 출력"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        
        print(f"\n{Fore.CYAN}📊 === 최종 시뮬레이션 통계 ==={Style.RESET_ALL}")
        print(f"⏱️  총 실행 시간: {str(runtime).split('.')[0]}")
        print(f"🏭 총 조립 건수: {self.stats['total_assemblies']}")
        print(f"✅ 품질 통과율: {(self.stats['quality_passed']/max(1, self.stats['total_assemblies'])*100):.1f}%")
        print(f"⚠️  총 알림 수: {self.stats['alerts_generated']}")
        print(f"{Fore.CYAN}=============================={Style.RESET_ALL}\n")
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\n{Fore.YELLOW}🛑 종료 신호 감지 (Signal: {signum}){Style.RESET_ALL}")
        self.running = False


def main():
    """메인 함수"""
    print(f"{Fore.CYAN}🏭 의장 공정 IoT 시뮬레이터 v1.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Manufacturing Process Simulator{Style.RESET_ALL}\n")
    
    # 시뮬레이터 생성 및 실행
    simulator = AssemblyProcessSimulator()
    simulator.start_simulation()


if __name__ == "__main__":
    main()