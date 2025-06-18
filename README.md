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