# 🗄️ 데이터베이스 연동 가이드

remote.it을 통한 InfluxDB & PostgreSQL 연동 설정 가이드

**사용 목적**:
- **InfluxDB**: MQTT 센서 데이터 저장 (mosquitto_MQTT)
- **PostgreSQL**: 재고관리 & 회원관리 데이터

---

## 📋 1단계: 환경 설정

### 데이터베이스 서버 설치

#### 🍎 macOS
```bash
# PostgreSQL 설치
brew install postgresql
brew services start postgresql

# InfluxDB 설치
brew install influxdb
brew services start influxdb
```

#### 🪟 Windows
```powershell
# PostgreSQL 설치 (공식 installer 다운로드)
# https://www.postgresql.org/download/windows/

# InfluxDB 설치 (chocolatey 사용)
choco install influxdb
# 또는 공식 installer: https://portal.influxdata.com/downloads/
```

### application.properties 설정
`src/main/resources/application.properties`에 추가:
```properties
# PostgreSQL 설정
spring.datasource.url=jdbc:postgresql://your-remote-it-url:5432/manufacturing_db
spring.datasource.username=your-username
spring.datasource.password=your-password
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA 설정
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# InfluxDB 설정 (MQTT 센서 데이터용)
influxdb.url=http://your-remote-it-url:8086
influxdb.token=your-token
influxdb.org=manufacturing
influxdb.bucket=mqtt_sensor_data
```
---

## ⚠️ 주의사항

- `.env` 파일은 **절대 git에 커밋하지 마세요**
- 사용 후 **반드시 연결 해제**하세요
- remote.it 연결이 **활성화**되어 있는지 확인하세요
- 에러 처리를 위해 **try-catch** 블록 사용하세요

---

## 🆘 문제 해결

| 문제 | 해결방법 |
|------|----------|
| 연결 실패 | remote.it 서비스 상태 확인 |
| 인증 오류 | 토큰/비밀번호 재확인 |
| 패키지 오류 | `pip install --upgrade` 실행 |