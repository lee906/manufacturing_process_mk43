"""
로봇 관리자
스테이션별 로봇 시뮬레이터 관리
"""

import time
from typing import Dict, List
from ..assembly.robots import ABBRobotSimulator, ABBRobotModel, FANUCRobotSimulator, FANUCRobotModel, UniversalRobotSimulator, URRobotModel

class RobotManager:
    """로봇 관리자"""
    
    def __init__(self):
        # 스테이션별 로봇 배치
        self.station_robots = self._initialize_station_robots()
        
    def _initialize_station_robots(self) -> Dict[str, List]:
        """스테이션별 로봇 초기화"""
        return {
            # A라인 - 내장재 작업 (협업로봇 중심)
            "A01_DOOR": [
                UniversalRobotSimulator("UR5e_A01_01", URRobotModel.UR5e, "A01_DOOR"),
                UniversalRobotSimulator("UR5e_A01_02", URRobotModel.UR5e, "A01_DOOR")
            ],
            "A02_WIRING": [
                ABBRobotSimulator("IRB120_A02_01", ABBRobotModel.IRB_120, "A02_WIRING"),
                ABBRobotSimulator("IRB120_A02_02", ABBRobotModel.IRB_120, "A02_WIRING")
            ],
            "A03_HEADLINER": [
                UniversalRobotSimulator("UR3e_A03_01", URRobotModel.UR3e, "A03_HEADLINER")
            ],
            "A04_CRASH_PAD": [
                FANUCRobotSimulator("M10iA_A04_01", FANUCRobotModel.M_10iA, "A04_CRASH_PAD"),
                UniversalRobotSimulator("UR5e_A04_01", URRobotModel.UR5e, "A04_CRASH_PAD")
            ],
            
            # B라인 - 중량 작업 (대형 로봇)
            "B01_FUEL_TANK": [
                ABBRobotSimulator("IRB1600_B01_01", ABBRobotModel.IRB_1600, "B01_FUEL_TANK"),
                FANUCRobotSimulator("M_20iA_B01_01", FANUCRobotModel.M_20iA, "B01_FUEL_TANK")
            ],
            "B02_CHASSIS_MERGE": [
                ABBRobotSimulator("IRB6700_B02_01", ABBRobotModel.IRB_6700, "B02_CHASSIS_MERGE"),
                FANUCRobotSimulator("R_2000iC_B02_01", FANUCRobotModel.R_2000iC, "B02_CHASSIS_MERGE")
            ],
            "B03_MUFFLER": [
                ABBRobotSimulator("IRB1600_B03_01", ABBRobotModel.IRB_1600, "B03_MUFFLER"),
                ABBRobotSimulator("IRB1600_B03_02", ABBRobotModel.IRB_1600, "B03_MUFFLER")
            ],
            
            # C라인 - 정밀 조립 (중형 로봇)
            "C01_FEM": [
                FANUCRobotSimulator("M20iA_C01_01", FANUCRobotModel.M_20iA, "C01_FEM"),
                FANUCRobotSimulator("M20iA_C01_02", FANUCRobotModel.M_20iA, "C01_FEM")
            ],
            "C02_GLASS": [
                ABBRobotSimulator("IRB1600_C02_01", ABBRobotModel.IRB_1600, "C02_GLASS"),
                UniversalRobotSimulator("UR10e_C02_01", URRobotModel.UR10e, "C02_GLASS")
            ],
            "C03_SEAT": [
                UniversalRobotSimulator("UR16e_C03_01", URRobotModel.UR16e, "C03_SEAT"),
                FANUCRobotSimulator("M20iA_C03_01", FANUCRobotModel.M_20iA, "C03_SEAT")
            ],
            "C04_BUMPER": [
                ABBRobotSimulator("IRB1600_C04_01", ABBRobotModel.IRB_1600, "C04_BUMPER"),
                ABBRobotSimulator("IRB1600_C04_02", ABBRobotModel.IRB_1600, "C04_BUMPER")
            ],
            "C05_TIRE": [
                FANUCRobotSimulator("LR_Mate_200iD_C05_01", FANUCRobotModel.LR_Mate_200iD, "C05_TIRE"),
                UniversalRobotSimulator("UR10e_C05_01", URRobotModel.UR10e, "C05_TIRE")
            ],
            
            # D라인 - 검사 및 완료 (정밀 작업)
            "D01_WHEEL_ALIGNMENT": [
                ABBRobotSimulator("IRB120_D01_01", ABBRobotModel.IRB_120, "D01_WHEEL_ALIGNMENT"),
                ABBRobotSimulator("IRB120_D01_02", ABBRobotModel.IRB_120, "D01_WHEEL_ALIGNMENT")
            ],
            "D02_HEADLAMP": [
                UniversalRobotSimulator("UR3e_D02_01", URRobotModel.UR3e, "D02_HEADLAMP"),
                ABBRobotSimulator("IRB120_D02_01", ABBRobotModel.IRB_120, "D02_HEADLAMP")
            ],
            "D03_WATER_LEAK_TEST": [
                # 검사 공정이므로 로봇 최소
                FANUCRobotSimulator("M10iA_D03_01", FANUCRobotModel.M_10iA, "D03_WATER_LEAK_TEST")
            ]
        }
    
    def get_station_robots(self, station_id: str) -> List:
        """특정 스테이션의 로봇 목록 반환"""
        return self.station_robots.get(station_id, [])
    
    def get_robot_telemetry(self, station_id: str) -> List[Dict]:
        """스테이션별 로봇 텔레메트리 데이터"""
        robots = self.get_station_robots(station_id)
        telemetry_data = []
        
        for robot in robots:
            telemetry_data.append(robot.get_telemetry_data())
            
        return telemetry_data
    
    def get_robot_status(self, station_id: str) -> List[Dict]:
        """스테이션별 로봇 상태 데이터"""
        robots = self.get_station_robots(station_id)
        status_data = []
        
        for robot in robots:
            status_data.append(robot.get_status_data())
            
        return status_data
    
    def start_robots_for_station(self, station_id: str, program_name: str = "AUTO_CYCLE"):
        """스테이션의 로봇들 작업 시작"""
        robots = self.get_station_robots(station_id)
        
        for robot in robots:
            if hasattr(robot, 'start_program'):
                robot.start_program(program_name)
            elif hasattr(robot, 'servo_on_off'):
                robot.servo_on_off(True)
                
    def stop_robots_for_station(self, station_id: str):
        """스테이션의 로봇들 작업 정지"""
        robots = self.get_station_robots(station_id)
        
        for robot in robots:
            if hasattr(robot, 'stop_program'):
                robot.stop_program()
            elif hasattr(robot, 'servo_on_off'):
                robot.servo_on_off(False)
                
    def simulate_collaborative_work(self, station_id: str) -> Dict:
        """협업 작업 시뮬레이션"""
        robots = self.get_station_robots(station_id)
        
        if not robots:
            return {"status": "no_robots"}
        
        # 협업 효율성 계산
        ur_robots = [r for r in robots if isinstance(r, UniversalRobotSimulator)]
        collaboration_efficiency = 1.0
        
        if len(ur_robots) > 0:
            # UR 로봇이 있으면 협업 효율성 향상
            collaboration_efficiency = 1.1 + (len(ur_robots) * 0.05)
        
        # 로봇 간 동기화 상태
        sync_status = "synchronized" if len(robots) > 1 else "single_robot"
        
        # 작업 분배
        work_distribution = {}
        for i, robot in enumerate(robots):
            work_distribution[robot.robot_id] = {
                "work_percentage": round(100 / len(robots), 1),
                "current_task": f"task_{i+1}",
                "coordination_mode": "parallel" if len(robots) > 1 else "standalone"
            }
        
        return {
            "station_id": station_id,
            "robot_count": len(robots),
            "collaboration_efficiency": round(collaboration_efficiency, 2),
            "sync_status": sync_status,
            "work_distribution": work_distribution,
            "safety_mode": "collaborative" if len(ur_robots) > 0 else "industrial",
            "timestamp": time.time()
        }
    
    def get_all_robots_summary(self) -> Dict:
        """전체 로봇 요약 정보"""
        total_robots = 0
        robot_brands = {"ABB": 0, "FANUC": 0, "Universal Robots": 0}
        active_robots = 0
        error_robots = 0
        
        for robots in self.station_robots.values():
            total_robots += len(robots)
            
            for robot in robots:
                # 브랜드별 집계
                if isinstance(robot, ABBRobotSimulator):
                    robot_brands["ABB"] += 1
                elif isinstance(robot, FANUCRobotSimulator):
                    robot_brands["FANUC"] += 1
                elif isinstance(robot, UniversalRobotSimulator):
                    robot_brands["Universal Robots"] += 1
                
                # 상태별 집계
                telemetry = robot.get_telemetry_data()
                status = telemetry.get("status", "unknown")
                
                if status in ["running", "working", "moving"]:
                    active_robots += 1
                elif status in ["error", "emergency_stop", "fault"]:
                    error_robots += 1
        
        # 가동률 계산
        uptime_percentage = ((total_robots - error_robots) / max(total_robots, 1)) * 100
        
        return {
            "total_robots": total_robots,
            "robot_brands": robot_brands,
            "active_robots": active_robots,
            "idle_robots": total_robots - active_robots - error_robots,
            "error_robots": error_robots,
            "uptime_percentage": round(uptime_percentage, 1),
            "stations_with_robots": len([s for s, r in self.station_robots.items() if r]),
            "collaborative_stations": len([s for s, r in self.station_robots.items() 
                                         if any(isinstance(robot, UniversalRobotSimulator) for robot in r)]),
            "timestamp": time.time()
        }