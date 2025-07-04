#!/usr/bin/env python3
"""
StationStatus 간단 테스트 스크립트
"""

import json
import time
import random
import requests
from datetime import datetime, timezone

class SimpleStationStatusTester:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.test_stations = ["A01_DOOR", "A02_WIRE", "A03_HEAD"]
        
    def generate_status_data(self, station_id):
        """상태 데이터 생성"""
        station_names = {
            "A01_DOOR": "도어 탈거",
            "A02_WIRE": "와이어링", 
            "A03_HEAD": "헤드라이너"
        }
        
        return {
            "station_id": station_id,
            "station_name": station_names.get(station_id, station_id),
            "station_status": random.choice(["RUNNING", "IDLE", "RUNNING", "RUNNING"]),
            "current_operation": f"{station_names.get(station_id, '')}_작업중",
            "cycle_time": round(random.uniform(150, 250), 1),
            "target_cycle_time": 200.0,
            "production_count": random.randint(50, 200),
            "progress": round(random.uniform(10, 100), 1),
            "efficiency": round(random.uniform(75, 95), 1),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            print("🔍 데이터베이스 연결 테스트...")
            response = requests.get(f"{self.backend_url}/api/station/test", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 데이터베이스 연결: {result.get('database_connected')}")
                print(f"📊 총 레코드 수: {result.get('total_records')}")
                return True
            else:
                print(f"❌ 테스트 API 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 연결 테스트 실패: {e}")
            return False
    
    def send_status_data(self, station_id):
        """상태 데이터 전송"""
        try:
            data = self.generate_status_data(station_id)
            print(f"📤 데이터 전송: {station_id}")
            
            response = requests.post(
                f"{self.backend_url}/api/station/status",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ 전송 성공: {station_id}")
                    print(f"   - 저장 ID: {result.get('statusId')}")
                    return True
                else:
                    print(f"❌ 전송 실패: {result.get('message')}")
                    return False
            else:
                print(f"❌ API 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 전송 오류: {e}")
            return False
    
    def get_latest_status(self, station_id):
        """최신 상태 조회"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/station/{station_id}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 {station_id} 최신 상태:")
                print(f"   - 상태: {data.get('status')}")
                print(f"   - 작업: {data.get('currentOperation')}")
                print(f"   - 효율: {data.get('efficiency')}%")
                print(f"   - 시간: {data.get('timestamp')}")
                return True
            elif response.status_code == 404:
                print(f"❌ {station_id} 데이터 없음")
                return False
            else:
                print(f"❌ 조회 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 조회 실패: {e}")
            return False
    
    def get_all_stations_status(self):
        """모든 스테이션 상태 조회"""
        try:
            print("\n📊 전체 스테이션 상태 조회...")
            response = requests.get(
                f"{self.backend_url}/api/station/status/all",
                timeout=10
            )
            
            if response.status_code == 200:
                stations = response.json()
                print(f"✅ 총 {len(stations)}개 스테이션 발견:")
                for station in stations:
                    print(f"   - {station.get('stationId')}: {station.get('status')} ({station.get('efficiency')}%)")
                return True
            else:
                print(f"❌ 전체 조회 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 전체 조회 실패: {e}")
            return False
    
    def get_running_stations(self):
        """실행 중인 스테이션 조회"""
        try:
            print("\n🏃 실행 중인 스테이션 조회...")
            response = requests.get(
                f"{self.backend_url}/api/station/running",
                timeout=10
            )
            
            if response.status_code == 200:
                stations = response.json()
                print(f"✅ 실행 중인 스테이션: {len(stations)}개")
                for station in stations:
                    print(f"   - {station.get('stationId')}: {station.get('currentOperation')}")
                return True
            else:
                print(f"❌ 실행 중인 스테이션 조회 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 실행 중인 스테이션 조회 실패: {e}")
            return False
    
    def run_test(self):
        """테스트 실행"""
        print("🏭 StationStatus 테스트 시작")
        print("=" * 50)
        
        # 1. 데이터베이스 연결 확인
        if not self.test_database_connection():
            print("❌ 데이터베이스 연결 실패 - 테스트 중단")
            return False
        
        print("\n" + "=" * 50)
        
        # 2. 각 스테이션별 데이터 전송 테스트
        success_count = 0
        for station_id in self.test_stations:
            print(f"\n2️⃣ 스테이션 {station_id} 테스트")
            if self.send_status_data(station_id):
                success_count += 1
                time.sleep(1)  # 잠시 대기
                self.get_latest_status(station_id)
            time.sleep(1)
        
        print("\n" + "=" * 50)
        
        # 3. 전체 조회 테스트
        self.get_all_stations_status()
        
        # 4. 실행 중인 스테이션 조회
        self.get_running_stations()
        
        # 5. 결과 출력
        print("\n" + "=" * 50)
        print(f"📊 테스트 결과:")
        print(f"   - 총 테스트: {len(self.test_stations)}")
        print(f"   - 성공: {success_count}")
        print(f"   - 실패: {len(self.test_stations) - success_count}")
        print(f"   - 성공률: {(success_count/len(self.test_stations)*100):.1f}%")
        
        return success_count == len(self.test_stations)
    
    def run_continuous_test(self, minutes=2):
        """연속 테스트 (기본 2분)"""
        print(f"🔄 {minutes}분간 연속 테스트 시작")
        start_time = time.time()
        end_time = start_time + (minutes * 60)
        test_count = 0
        success_count = 0
        
        while time.time() < end_time:
            station_id = random.choice(self.test_stations)
            print(f"\n⏰ 연속 테스트 #{test_count + 1} - {station_id}")
            
            if self.send_status_data(station_id):
                success_count += 1
            
            test_count += 1
            time.sleep(10)  # 10초 간격
        
        print(f"\n✅ 연속 테스트 완료")
        print(f"   - 총 테스트: {test_count}")
        print(f"   - 성공: {success_count}")
        print(f"   - 실패: {test_count - success_count}")

def main():
    """메인 함수"""
    print("🏭 StationStatus 간단 테스트 도구")
    print("=" * 50)
    
    tester = SimpleStationStatusTester()
    
    print("\n테스트 모드를 선택하세요:")
    print("1. 기본 테스트 (각 스테이션 1회)")
    print("2. 연속 테스트 (2분간)")
    print("3. 데이터베이스 연결 확인만")
    print("4. 현재 상태 조회만")
    
    try:
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            success = tester.run_test()
            if success:
                print("\n🎉 기본 테스트 성공!")
            else:
                print("\n❌ 기본 테스트 실패")
        
        elif choice == "2":
            if tester.test_database_connection():
                tester.run_continuous_test(2)
            else:
                print("❌ 데이터베이스 연결 실패")
        
        elif choice == "3":
            tester.test_database_connection()
        
        elif choice == "4":
            print("\n📊 현재 상태 조회:")
            tester.get_all_stations_status()
            tester.get_running_stations()
        
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n👋 테스트가 사용자에 의해 중단되었습니다.")
    
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()