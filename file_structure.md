manufacturing_process/
├── dashboard_backend/      # Spring Boot API 서버 (포트: 8080)
│   ├── build.gradle
│   ├── settings.gradle
│   ├── src/
│   │   └── main/
│   │       └── java/
│   │           └── com/
│   │               └── u1mobis/
│   │                   └── dashboard_backend/
│   │                       ├── controller/
│   │                       ├── dto/
│   │                       ├── entity/
│   │                       ├── repository/
│   │                       └── service/
│   └── ...
├── dashboard_frontend/     # React 대시보드 (포트: 5173)
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── components/
│           ├── KPI/
│           ├── Robot/
│           ├── Inventory/
│           ├── Twin/
│           └── ...
├── data_collector/
│   ├── requirements.txt
│   ├── config.yaml
│   ├── main.py                 # 메인 실행 파일
│   ├── src/
│   │   ├── __init__.py
│   │   ├── mqtt_client.py      # MQTT 클라이언트
│   │   ├── data_processor.py   # 데이터 정제/가공
│   │   ├── api_client.py       # Spring Boot API 통신
│   │   └── models/
│   │       ├── __init__.py
│   │       └── sensor_data.py  # 데이터 모델
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_mqtt.py
│   │   └── test_processor.py
│   └── logs/
├── mosquitto_MQTT/
│   ├── requirements.txt
│   ├── config.json          # 의장 공정 전용 설정
│   ├── assembly_simulator.py # 메인 의장 시뮬레이터
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── mqtt_publisher.py
│   │   └── data_generator.py
│   ├── assembly/
│   │   ├── __init__.py
│   │   ├── robot_arm.py      # 로봇팔 시뮬레이터
│   │   ├── conveyor.py       # 컨베이어 시뮬레이터
│   │   ├── quality_check.py  # 품질검사 시뮬레이터
│   │   └── inventory.py      # 재고관리 시뮬레이터
│   ├── test.py
│   └── logs/
├── README.md
└── ...