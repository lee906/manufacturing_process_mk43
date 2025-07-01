"""
Data Collector 메인 - KPI 계산 통합
"""
import signal
import sys
import yaml
from src.mqtt_client import MQTTClient
from src.api_client import APIClient  
from src.data_processor import DataProcessor
from src.kpi_processor import KPIProcessor  # 🆕 추가

class DataCollector:
    def __init__(self, config_path: str = "config.yaml"):
        # 설정 로드
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # API 설정 업데이트 (KPI 엔드포인트 추가)
        if 'kpi_data' not in self.config['api']['endpoints']:
            self.config['api']['endpoints']['kpi_data'] = '/api/kpi/data'
        
        self.mqtt_client = MQTTClient()
        self.api_client = APIClient(self.config)
        self.data_processor = DataProcessor(self.api_client)
        self.kpi_processor = KPIProcessor()  # 🆕 KPI 프로세서 추가
        
        # MQTT 메시지 핸들러 등록
        self.mqtt_client.add_message_handler(self.handle_mqtt_message)
        
        # 시그널 핸들러
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def handle_mqtt_message(self, topic: str, payload: str):
        """MQTT 메시지 처리 - 통합 데이터 라우팅"""
        try:
            # 1. 모든 데이터 처리 (데이터 타입별 분류 및 가공)
            processed_data = self.data_processor.process_message(topic, payload)
            
            # 2. 데이터 타입별 특화 처리
            if processed_data:
                data_category = processed_data.get("dataCategory")
                
                # 스테이션 데이터 → KPI 계산
                if data_category == "station_data" and topic.endswith(('/status', '/quality')):
                    kpi_data = self.kpi_processor.process_mqtt_message(topic, payload)
                    if kpi_data:
                        self._send_kpi_data(kpi_data)
                
                # 차량 추적 데이터 → 전용 엔드포인트
                elif data_category == "vehicle_tracking":
                    self._send_vehicle_tracking_data(processed_data)
                
                # 로봇 데이터 → 전용 엔드포인트  
                elif data_category == "robot_data":
                    self._send_robot_data(processed_data)
                
                # 생산라인 상태 → 전용 엔드포인트
                elif data_category == "production_line":
                    self._send_production_status(processed_data)
                
                # 공급망 데이터 → 전용 엔드포인트
                elif data_category == "supply_chain":
                    self._send_supply_chain_data(processed_data)
                    
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
    
    def _send_vehicle_tracking_data(self, data: dict):
        """차량 추적 데이터 전송"""
        try:
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/api/digital-twin/vehicles",
                json=data,
                timeout=self.api_client.timeout
            )
            if response.status_code == 200:
                vehicle_count = data.get('vehicleTracking', {}).get('totalVehicles', 0)
                print(f"🚗 차량 추적 데이터 전송 성공: {vehicle_count}대")
        except Exception as e:
            print(f"❌ 차량 추적 데이터 전송 오류: {e}")
    
    def _send_robot_data(self, data: dict):
        """로봇 데이터 전송"""
        try:
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/api/robots/data",
                json=data,
                timeout=self.api_client.timeout
            )
            if response.status_code == 200:
                robot_count = len(data.get('robotData', {}).get('robots', []))
                station_id = data.get('stationId', 'Unknown')
                print(f"🤖 로봇 데이터 전송 성공: {station_id} ({robot_count}대)")
        except Exception as e:
            print(f"❌ 로봇 데이터 전송 오류: {e}")
    
    def _send_production_status(self, data: dict):
        """생산라인 상태 데이터 전송"""
        try:
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/api/production/status",
                json=data,
                timeout=self.api_client.timeout
            )
            if response.status_code == 200:
                efficiency = data.get('productionLine', {}).get('lineEfficiency', 0)
                print(f"🏭 생산라인 상태 전송 성공: 라인효율 {efficiency}%")
        except Exception as e:
            print(f"❌ 생산라인 상태 전송 오류: {e}")
    
    def _send_supply_chain_data(self, data: dict):
        """공급망 데이터 전송"""
        try:
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/api/supply-chain/status",
                json=data,
                timeout=self.api_client.timeout
            )
            if response.status_code == 200:
                total_parts = data.get('supplyChain', {}).get('totalParts', 0)
                print(f"📦 공급망 데이터 전송 성공: {total_parts}개 부품")
        except Exception as e:
            print(f"❌ 공급망 데이터 전송 오류: {e}")
    
    def _signal_handler(self, signum, frame):
        """종료 시그널 처리"""
        print(f"\n📊 KPI 프로세서 종료 중...")
        
        # 최종 KPI 요약 출력
        for station_id, metrics in self.kpi_processor.station_metrics.items():
            print(f"📈 {station_id}: {metrics.total_cycles}사이클, {metrics.total_inspections}검사")
        
        self.mqtt_client.stop()
        sys.exit(0)

def main():
    print("🔢 Data Collector with Digital Twin Support v3.0")
    print("=" * 60)
    print("📡 지원 토픽:")
    print("  • factory/{station}/telemetry|status|quality")
    print("  • factory/{station}/robots/telemetry|status")  
    print("  • factory/digital_twin/vehicle_tracking")
    print("  • factory/production_line/status")
    print("  • factory/supply_chain/status")
    print("  • factory/robots/summary")
    print("📤 API 엔드포인트:")
    print("  • /api/iot-data (스테이션 센서)")
    print("  • /api/kpi/data (KPI 지표)")
    print("  • /api/digital-twin/vehicles (차량 추적)")
    print("  • /api/robots/data (로봇 데이터)")
    print("  • /api/production/status (생산라인)")
    print("  • /api/supply-chain/status (공급망)")
    print("=" * 60)
    
    collector = DataCollector()
    
    if collector.mqtt_client.connect():
        print("✅ MQTT 연결 성공")
        print("🔢 실시간 데이터 수집 및 KPI 계산 시작!")
        print("🛑 종료하려면 Ctrl+C\n")
        
        collector.mqtt_client.start_loop()
    else:
        print("❌ MQTT 연결 실패")

if __name__ == "__main__":
    main()