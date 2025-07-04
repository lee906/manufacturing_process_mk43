# 🗄️ 데이터베이스 연동 가이드

remote.it을 통한 InfluxDB & PostgreSQL 연동 설정 가이드

**사용 목적**:
- **InfluxDB**: MQTT 센서 데이터 저장 (mosquitto_MQTT)
- **PostgreSQL**: 재고관리 & 회원관리 데이터

---
remote.it 에 들어가서 회원가입을 하고 로그인에 사용한 메일을 카톡에 올려주세요.


### application.properties 설정
`src/main/resources/application.properties`에 추가:
```properties
# PostgreSQL 설정
spring.datasource.url=jdbc:postgresql://your-remote-it-url/manufacturing_dashboard
spring.datasource.username=postgres
spring.datasource.password=1234
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA 설정
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# InfluxDB 설정 (MQTT 센서 데이터용)
influxdb.url=http://your-remote-it-url
influxdb.token=apiv3_cEbVg1AZ9vV8n6ldeFVBf_ZocFlxa170VAQ4Aq2uUHVUuE63fvdu5VSVhSiQvvPlCUVBSx4TD4b9fl_G334ISw
influxdb.org=factory
influxdb.bucket=sensor


연결 테스트 방법.-- influxdb
remote.it 에 연결 후
cmd에서 
curl -X POST http://주소/api/v3/query/sql -H "Authorization: Bearer apiv3_cEbVg1AZ9vV8n6ldeFVBf_ZocFlxa170VAQ4Aq2uUHVUuE63fvdu5VSVhSiQvvPlCUVBSx4TD4b9fl_G334ISw" -H "Content-Type: application/json" -d '{"sql": "SELECT * factory}'  --안됨
간단 테스트
curl -H "Authorization: Bearer apiv3_cEbVg1AZ9vV8n6ldeFVBf_ZocFlxa170VAQ4Aq2uUHVUuE63fvdu5VSVhSiQvvPlCUVBSx4TD4b9fl_G334ISw" http://리모트주소/ping

postgresql

powershell "try { $tcp = New-Object System.Net.Sockets.TcpClient; $tcp.Connect('리모트주소', 리모트포트); Write-Host 'PostgreSQL 포트 연결 성공!'; $tcp.Close() } catch { Write-Host 'PostgreSQL 포트 연결 실패: ' $_.Exception.Message }"


powershell "$conn = New-Object Npgsql.NpgsqlConnection('Host=proxy151.r3proxy.com,34170;Database=manufacturing_dashboard;Username=postgres;Password=1234'); try { $conn.Open(); Write-Host 'PostgreSQL 연결 성공!' } catch { Write-Host '연결 실패: ' $_.Exception.Message } finally { $conn.Close() }"
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