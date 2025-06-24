"""
데이터 수집기 메인 실행 파일
MQTT로부터 IoT 데이터를 수집하여 Spring Boot API로 전송
"""

import logging
import signal
import sys
import time
from datetime import datetime
from colorama import init, Fore, Style
from src.mqtt_client import MQTTClient
from src.data_processor import DataProcessor
from src.api_client import APIClient

# 컬러 출력 초기화
init(autoreset=True)

class DataCollectorMain:
    def __init__(self):
        self.running = False
        self.mqtt_client = None
        self.data_processor = None
        self.api_client = None
        
        # 로깅 설정
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 통계
        self.stats = {
            "start_time": None,
            "messages_received": 0,
            "messages_processed": 0,
            "api_calls_success": 0,
            "api_calls_failed": 0
        }
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_collector.log'),
                logging.StreamHandler()
            ]
        )
        
        # logs 디렉토리 생성
        import os
        os.makedirs('logs', exist_ok=True)
    
    def initialize(self):
        """데이터 수집기 초기화"""
        try:
            print(f"{Fore.CYAN}🔧 데이터 수집기 초기화 중...{Style.RESET_ALL}")
            
            # API 클라이언트 초기화
            self.api_client = APIClient("http://localhost:8080")
            print(f"{Fore.GREEN}✅ API 클라이언트 초기화 완료{Style.RESET_ALL}")
            
            # 데이터 프로세서 초기화
            self.data_processor = DataProcessor(self.api_client)
            print(f"{Fore.GREEN}✅ 데이터 프로세서 초기화 완료{Style.RESET_ALL}")
            
            # MQTT 클라이언트 초기화
            self.mqtt_client = MQTTClient()
            self.mqtt_client.add_message_handler(self._handle_mqtt_message)
            
            if self.mqtt_client.connect():
                print(f"{Fore.GREEN}✅ MQTT 클라이언트 연결 성공{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ MQTT 클라이언트 연결 실패{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ 초기화 실패: {e}{Style.RESET_ALL}")
            self.logger.error(f"초기화 실패: {e}")
            return False
    
    def start(self):
        """데이터 수집 시작"""
        if not self.initialize():
            return
        
        try:
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            print(f"\n{Fore.GREEN}🚀 데이터 수집기 시작!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📡 MQTT 구독: factory/manufacturing/+/data{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🔗 API 엔드포인트: http://localhost:8080/api/iot-data{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🛑 종료하려면 Ctrl+C를 누르세요{Style.RESET_ALL}\n")
            
            # MQTT 클라이언트 시작
            self.mqtt_client.start_loop()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  사용자 종료 요청{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ 데이터 수집 오류: {e}{Style.RESET_ALL}")
            self.logger.error(f"데이터 수집 오류: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """데이터 수집 중지"""
        print(f"{Fore.YELLOW}🛑 데이터 수집기 중지 중...{Style.RESET_ALL}")
        
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.stop()
            print(f"{Fore.GREEN}✅ MQTT 클라이언트 중지 완료{Style.RESET_ALL}")
        
        # 최종 통계 출력
        self._print_final_statistics()
        
        print(f"{Fore.GREEN}✅ 데이터 수집기 종료 완료{Style.RESET_ALL}")
        self.logger.info("데이터 수집기 종료")
    
    def _handle_mqtt_message(self, topic: str, payload: str):
        """MQTT 메시지 처리"""
        try:
            self.stats["messages_received"] += 1
            
            # 데이터 처리
            processed_data = self.data_processor.process_message(topic, payload)
            
            if processed_data:
                self.stats["messages_processed"] += 1
                self.stats["api_calls_success"] += 1
            else:
                self.stats["api_calls_failed"] += 1
                
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
            self.stats["api_calls_failed"] += 1
    
    def _print_final_statistics(self):
        """최종 통계 출력"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        
        print(f"\n{Fore.CYAN}📊 === 최종 데이터 수집 통계 ==={Style.RESET_ALL}")
        print(f"⏱️  총 실행 시간: {str(runtime).split('.')[0]}")
        print(f"📨 수신 메시지: {self.stats['messages_received']}")
        print(f"⚙️  처리된 메시지: {self.stats['messages_processed']}")
        print(f"✅ API 호출 성공: {self.stats['api_calls_success']}")
        print(f"❌ API 호출 실패: {self.stats['api_calls_failed']}")
        
        if self.stats["messages_received"] > 0:
            success_rate = (self.stats["api_calls_success"] / self.stats["messages_received"]) * 100
            print(f"📈 성공률: {success_rate:.1f}%")
        
        print(f"{Fore.CYAN}=============================={Style.RESET_ALL}\n")
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\n{Fore.YELLOW}🛑 종료 신호 감지 (Signal: {signum}){Style.RESET_ALL}")
        self.running = False


def main():
    """메인 함수"""
    print(f"{Fore.CYAN}🔧 IoT 데이터 수집기 v1.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Manufacturing Process Data Collector{Style.RESET_ALL}\n")
    
    collector = DataCollectorMain()
    collector.start()


if __name__ == "__main__":
    main()