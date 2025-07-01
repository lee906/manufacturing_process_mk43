#!/usr/bin/env python3
"""
현대차 조립라인 MQTT 시뮬레이션 실행 스크립트
RFID 추적 및 실시간 센서 데이터 시뮬레이션
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from mosquitto_MQTT.assembly.assembly_simulator import AssemblyLineSimulator

def main():
    print("🏭 현대차 조립라인 MQTT 시뮬레이터")
    print("=" * 50)
    print("🚗 차량 모델: 아반떼, 투싼, 팰리세이드, 코나, 그랜저")
    print("📍 스테이션: A01(도어탈거), A02(배선), B01(연료탱크)")
    print("📡 MQTT 토픽:")
    print("  - factory/{station_id}/telemetry")
    print("  - factory/{station_id}/status") 
    print("  - factory/{station_id}/quality")
    print("🔧 RFID 추적: 차량별 실시간 위치 및 진행률")
    print("⚙️  센서 데이터: 토크, 전압, 압력, 진동 등")
    print()
    
    # 시뮬레이터 시작
    simulator = AssemblyLineSimulator()
    
    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\n👋 시뮬레이션을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()