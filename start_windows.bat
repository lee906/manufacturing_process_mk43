@echo off
chcp 65001 >nul
REM 현대차 의장공정 디지털 트윈 시스템 - Windows 실행 스크립트
REM 작성자: Claude Code
REM 날짜: 2025-07-03

echo 🏭 현대차 의장공정 디지털 트윈 시스템 - Windows
echo ===============================================

REM 현재 디렉토리 설정
cd /d "%~dp0"
echo 📍 작업 디렉토리: %CD%

REM 로그 디렉토리 생성
if not exist logs mkdir logs

REM 사전 요구사항 확인
echo.
echo 🔍 사전 요구사항 확인

REM Node.js 확인
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js %%i
) else (
    echo ❌ Node.js가 설치되지 않았습니다
    echo https://nodejs.org 에서 다운로드하세요
    pause
    exit /b 1
)

REM Java 확인
java -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Java 설치됨
) else (
    echo ❌ Java가 설치되지 않았습니다
    echo Oracle JDK 또는 OpenJDK를 설치하세요
    pause
    exit /b 1
)

REM Python 확인
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ %%i
    set PYTHON_CMD=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('python3 --version') do echo ✅ %%i
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python이 설치되지 않았습니다
        echo https://python.org 에서 다운로드하세요
        pause
        exit /b 1
    )
)

REM Mosquitto 확인
mosquitto --help >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Mosquitto 설치됨
) else (
    echo ❌ Mosquitto가 설치되지 않았습니다
    echo chocolatey: choco install mosquitto
    echo 또는 https://mosquitto.org/download/ 에서 다운로드
    pause
    exit /b 1
)

REM 포트 사용 확인
echo.
echo 🔌 포트 사용 상태 확인

set PORT_WARNING=0
netstat -an | findstr ":8080 " >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ 포트 8080이 사용 중입니다
    set PORT_WARNING=1
)

netstat -an | findstr ":5173 " >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ 포트 5173이 사용 중입니다
    set PORT_WARNING=1
)

netstat -an | findstr ":1883 " >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ 포트 1883이 사용 중입니다
    set PORT_WARNING=1
)

if %PORT_WARNING% equ 0 (
    echo ✅ 모든 포트^(8080, 5173, 1883^) 사용 가능
) else (
    echo 계속 진행하시겠습니까? ^(y/n^)
    set /p response=
    if /i not "%response%"=="y" exit /b 0
)

REM 1. Python 가상환경 확인
echo.
echo 1️⃣ Python 가상환경 확인

if exist "venv\Scripts\activate.bat" (
    echo ✅ 가상환경 확인 완료
    echo 💡 스크립트 실행 전에 가상환경을 활성화해주세요: venv\Scripts\activate.bat
    
    REM 가상환경 활성화 확인
    if "%VIRTUAL_ENV%"=="" (
        echo ❌ 가상환경이 활성화되지 않았습니다
        echo 다음 명령어를 실행한 후 다시 시도하세요:
        echo venv\Scripts\activate.bat
        echo start_windows.bat
        pause
        exit /b 1
    ) else (
        echo ✅ 가상환경 활성화 상태 확인
    )
) else (
    echo ❌ 가상환경이 없습니다. 'python -m venv venv'로 생성하세요
    pause
    exit /b 1
)

REM 2. Mosquitto 브로커 시작
echo.
echo 2️⃣ Mosquitto MQTT 브로커 시작

start "Mosquitto" /min cmd /c "mosquitto > logs\mosquitto.log 2>&1"
timeout /t 3 /nobreak >nul
echo ✅ Mosquitto 브로커 시작 완료

REM 3. 데이터베이스 연결 확인
echo.
echo 3️⃣ 데이터베이스 연결 확인

echo PostgreSQL 연결 상태 확인 중... ^(proxy151.r3proxy.com:34209^)
powershell -Command "Test-NetConnection -ComputerName proxy151.r3proxy.com -Port 34209 -WarningAction SilentlyContinue" | findstr "TcpTestSucceeded.*True" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL 연결 성공
) else (
    echo.
    echo ❌ 데이터베이스 연결 실패
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo 🔌 PostgreSQL 서버에 연결할 수 없습니다
    echo.
    echo 📋 확인 사항:
    echo   1. remote.it 대시보드에서 PostgreSQL 서비스 상태 확인
    echo      → https://app.remote.it
    echo.
    echo   2. 데이터베이스 엔드포인트 확인:
    echo      • 호스트: proxy151.r3proxy.com
    echo      • 포트: 34209
    echo      • 데이터베이스: manufacturing_dashboard
    echo.
    echo   3. remote.it에서 서비스가 'Connected' 상태인지 확인
    echo   4. 네트워크 연결 상태 확인
    echo.
    echo 📞 조치 방법:
    echo   • remote.it 포털에서 PostgreSQL 서비스 재시작
    echo   • 서비스가 온라인 상태가 된 후 다시 실행
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    goto cleanup
)

echo InfluxDB 연결 상태 확인 중... ^(proxy151.r3proxy.com:34200^)
powershell -Command "Test-NetConnection -ComputerName proxy151.r3proxy.com -Port 34200 -WarningAction SilentlyContinue" | findstr "TcpTestSucceeded.*True" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ InfluxDB 연결 성공
) else (
    echo.
    echo ❌ InfluxDB 연결 실패
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo 🔌 InfluxDB 서버에 연결할 수 없습니다
    echo.
    echo 📋 확인 사항:
    echo   1. remote.it 대시보드에서 InfluxDB 서비스 상태 확인
    echo      → https://app.remote.it
    echo.
    echo   2. 데이터베이스 엔드포인트 확인:
    echo      • 호스트: proxy151.r3proxy.com
    echo      • 포트: 34200
    echo      • 데이터베이스: IOT-sensor
    echo.
    echo 📞 조치 방법:
    echo   • remote.it 포털에서 InfluxDB 서비스 재시작
    echo   • 서비스가 온라인 상태가 된 후 다시 실행
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    goto cleanup
)

REM 4. Spring Boot 백엔드 시작
echo.
echo 4️⃣ Spring Boot 백엔드 시작
echo 백엔드 컴파일 및 시작 중... ^(약 30초 소요^)

cd dashboard_backend
start "Backend" /min cmd /c "gradlew.bat bootRun > ..\logs\backend.log 2>&1"
cd ..

echo ✅ Spring Boot 백엔드 시작 완료

REM 백엔드 준비 대기
echo 백엔드 서버 준비 대기 중...
set /a attempts=0
:wait_backend
set /a attempts+=1
curl -s http://localhost:8080/api/kpi/factory/summary >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 백엔드 서버 준비 완료
    goto backend_ready
)
if %attempts% lss 30 (
    echo|set /p="."
    timeout /t 2 /nobreak >nul
    goto wait_backend
)
echo ❌ 백엔드 서버가 60초 내에 시작되지 않았습니다
goto cleanup

:backend_ready

REM 5. 데이터 수집기 시작
echo.
echo 5️⃣ 데이터 수집기 시작

cd data_collector
start "DataCollector" /min cmd /c "%PYTHON_CMD% main.py > ..\logs\data_collector.log 2>&1"
cd ..
echo ✅ 데이터 수집기 시작 완료
timeout /t 3 /nobreak >nul

REM 6. MQTT 시뮬레이터 시작
echo.
echo 6️⃣ MQTT 시뮬레이터 시작 ^(15개 스테이션^)

cd mosquitto_MQTT
start "MQTTSimulator" /min cmd /c "%PYTHON_CMD% run_simulation.py > ..\logs\mqtt_simulator.log 2>&1"
cd ..
echo ✅ MQTT 시뮬레이터 시작 완료
timeout /t 5 /nobreak >nul

REM 7. React 프론트엔드 시작
echo.
echo 7️⃣ React 프론트엔드 시작

cd dashboard_frontend
start "Frontend" /min cmd /c "npm run dev > ..\logs\frontend.log 2>&1"
cd ..
echo ✅ React 프론트엔드 시작 완료

REM 프론트엔드 준비 대기
echo 프론트엔드 서버 준비 대기 중...
set /a attempts=0
:wait_frontend
set /a attempts+=1
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 프론트엔드 서버 준비 완료
    goto frontend_ready
)
if %attempts% lss 15 (
    echo|set /p="."
    timeout /t 2 /nobreak >nul
    goto wait_frontend
)
echo ⚠️ 프론트엔드가 30초 내에 준비되지 않았지만 계속 진행합니다

:frontend_ready

REM 8. 시스템 상태 확인
echo.
echo 8️⃣ 시스템 상태 확인
echo 백엔드 API 테스트 중...

%PYTHON_CMD% dashboard_backend\test_api.py > logs\api_test.log 2>&1
if %errorlevel% equ 0 (
    echo ✅ API 테스트 통과
) else (
    echo ⚠️ API 테스트 실패 - 로그 확인: logs\api_test.log
)

REM 9. 브라우저 열기
echo.
echo 🌐 웹 브라우저에서 대시보드를 열까요? ^(y/n^)
set /p response=
if /i "%response%"=="y" start http://localhost:5173

REM 최종 상태 출력
echo.
echo 🎉 시스템 시작 완료!
echo ===============================================
echo 📊 접속 주소:
echo   • 대시보드: http://localhost:5173
echo   • 백엔드 API: http://localhost:8080/api/kpi/factory/summary
echo.
echo 📁 로그 파일:
echo   • 백엔드: logs\backend.log
echo   • 데이터수집: logs\data_collector.log
echo   • 시뮬레이터: logs\mqtt_simulator.log
echo   • 프론트엔드: logs\frontend.log
echo   • API테스트: logs\api_test.log
echo.
echo 🛑 종료하려면 아무 키나 누르세요
echo 💡 로그 실시간 보기: type logs\[파일명]
echo 💡 종료 후 가상환경 비활성화: deactivate

REM 사용자 입력 대기
pause >nul

:cleanup
echo.
echo 🛑 시스템 정리 중...

REM 프로세스 종료
taskkill /f /im "mosquitto.exe" >nul 2>&1
taskkill /f /im "java.exe" >nul 2>&1
taskkill /f /im "python.exe" >nul 2>&1
taskkill /f /im "python3.exe" >nul 2>&1
taskkill /f /im "node.exe" >nul 2>&1

echo ✓ 모든 프로세스 종료 완료
echo 정리 완료
echo 💡 가상환경은 터미널을 종료하거나 'deactivate' 명령어로 비활성화하세요

pause