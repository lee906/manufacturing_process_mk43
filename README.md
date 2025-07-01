# 자동차 의장공장 디지털 트윈 시스템

## 프로젝트 개요
자동차 제조 의장공장의 실시간 모니터링 및 관리를 위한 디지털 트윈 시스템

## 시스템 구성
digital-twin-project/
├── dashboard-backend/    # Spring Boot API 서버 (포트: 8080)
├── data-collector/      # Python 데이터 수집 서버 (포트: 8082)
└── dashboard-frontend/  # React 대시보드 (포트: 5173)

## 기술 스택
- **Backend**: Spring Boot 3.1.5, Java 17, Gradle, node v22.16.0
- **Data Collector**: Python 3.8+
- **Frontend**: React 18, Vite, Tabler.io
- **Database**: H2 (개발), MySQL (운영)

## 사용방법
- **Node.js 설치**: [Node.js 공식 사이트](https://nodejs.org/)에서 LTS 버전 다운로드 및 설치
- 터미널에서 설치 확인 : node --version / npm --version

- **의존성 패키지 설치**
- dashboard_frontend에서 npm install
- npm install react-router-dom
- npm install apexcharts react-apexcharts

- **개발 서버 실행**
- npm run dev


- **IoT 신호 데이터**
- mosquitto MQTT는 브로커 역할
- mosquitto version 2.0.21
- brew install mosquitto - 모스키토 설치
- brew services start mosquitto - 모스키토를 서비스로 등록

# 작업 시작할 때마다
cd manufacturing_process/
source venv/bin/activate - 가상환경 설치 후 실행

# MQTT 시뮬레이터 실행
cd mosquitto_MQTT/
pip install -r requirements.txt - 한번만 진행
python run_simulation.py

# 데이터 수집기 실행 (다른 터미널)
cd ../data_collector/
pip install -r requirements.txt - 한번만 진행
python main.py

# 대시보드 백엔드 (다른 터미널)
cd dashboard_backend
./gradlew bootRun

# 대시보드 프론트엔데 (다른 터미널)
cd dashboard_frontend
npm run dev

# 작업 완료 후
deactivate