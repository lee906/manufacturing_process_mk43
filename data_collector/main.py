"""
Data Collector 메인 - KPI 계산 통합
"""
import signal
import sys
from src.mqtt_client import MQTTClient
from src.api_client import APIClient  
from src.data_processor import DataProcessor
from src.kpi_processor import KPIProcessor  # 🆕 추가

class DataCollector:
    def __init__(self):
        self.mqtt_client = MQTTClient()
        self.api_client = APIClient()
        self.data_processor = DataProcessor(self.api_client)
        self.kpi_processor = KPIProcessor()  # 🆕 KPI 프로세서 추가
        
        # MQTT 메시지 핸들러 등록
        self.mqtt_client.add_message_handler(self.handle_mqtt_message)
        
        # 시그널 핸들러
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def handle_mqtt_message(self, topic: str, payload: str):
        """MQTT 메시지 처리 - 기존 + KPI 계산"""
        try:
            # 1. 기존 데이터 처리 (원시 데이터 → Spring Boot)
            processed_data = self.data_processor.process_message(topic, payload)
            
            # 2. 🆕 KPI 계산 (원시 데이터 → KPI → Spring Boot)
            if topic.endswith(('/status', '/quality')):  # KPI 관련 토픽만
                kpi_data = self.kpi_processor.process_mqtt_data(topic, payload)
                if kpi_data:
                    self._send_kpi_data(kpi_data)
                    
        except Exception as e:
            print(f"❌ 메시지 처리 오류: {e}")
    
    def _send_kpi_data(self, kpi_data: dict):
        """계산된 KPI 데이터를 Spring Boot로 전송"""
        try:
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/api/kpi/data",  # 🆕 KPI 전용 엔드포인트
                json=kpi_data,
                timeout=self.api_client.timeout
            )
            
            if response.status_code == 200:
                station_id = kpi_data.get('station_id', 'Unknown')
                oee_value = kpi_data.get('oee', {}).get('value', 0)
                print(f"✅ KPI 전송 성공: {station_id} (OEE: {oee_value}%)")
            else:
                print(f"⚠️ KPI 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ KPI 전송 오류: {e}")
    
    def _signal_handler(self, signum, frame):
        """종료 시그널 처리"""
        print(f"\n📊 KPI 프로세서 종료 중...")
        
        # 최종 KPI 요약 출력
        for station_id, metrics in self.kpi_processor.station_metrics.items():
            print(f"📈 {station_id}: {metrics.total_cycles}사이클, {metrics.total_inspections}검사")
        
        self.mqtt_client.disconnect()
        sys.exit(0)

def main():
    print("🔢 Data Collector with KPI Processing v2.0")
    print("=" * 50)
    
    collector = DataCollector()
    
    if collector.mqtt_client.connect():
        print("✅ MQTT 연결 성공")
        print("🔢 KPI 실시간 계산 시작!")
        print("📊 KPI 엔드포인트: /api/kpi/data")
        print("🛑 종료하려면 Ctrl+C\n")
        
        collector.mqtt_client.start_loop()
    else:
        print("❌ MQTT 연결 실패")

if __name__ == "__main__":
    main()