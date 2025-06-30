"""
Assembly Process Simulators Package
자동차 의장공정 시뮬레이터 패키지 - Flat Structure with Line Sequence
"""

__version__ = "2.0.0"
__author__ = "Manufacturing IoT Team"

from .base_simulator import BaseStationSimulator
from .shared_conveyor import ConveyorSimulator

# Line A Simulators (도어 탈거 → 와이어링 → 헤드라이너 → 크래쉬 패드)
from .A_01_door_removal import A01DoorRemovalSimulator
from .A_02_wiring import A02WiringSimulator
from .A_03_headliner import A03HeadlinerSimulator
from .A_04_crash_pad import A04CrashPadSimulator

# Line B Simulators (연료탱크 → 샤시 메리지 → 머플러)
from .B_01_fuel_tank import B01FuelTankSimulator
from .B_02_chassis_merge import B02ChassisMergeSimulator
from .B_03_muffler import B03MufflerSimulator

# Line C Simulators (FEM → 글라스 → 시트 → 범퍼 → 타이어)
from .C_01_fem import C01FEMSimulator
from .C_02_glass import C02GlassSimulator
from .C_03_seat import C03SeatSimulator
from .C_04_bumper import C04BumperSimulator
from .C_05_tire import C05TireSimulator

# Line D Simulators (휠 얼라이언트 → 헤드램프 → 수밀 검사)
from .D_01_wheel_alignment import D01WheelAlignmentSimulator
from .D_02_headlamp import D02HeadlampSimulator
from .D_03_water_leak_test import D03WaterLeakTestSimulator

# Robot Simulators
from .robots.abb_robot import ABBRobotSimulator
from .robots.fanuc_robot import FANUCRobotSimulator
from .robots.universal_robot import UniversalRobotSimulator

__all__ = [
    'BaseStationSimulator',
    'ConveyorSimulator',
    # Line A (A01 → A02 → A03 → A04)
    'A01DoorRemovalSimulator', 'A02WiringSimulator', 'A03HeadlinerSimulator', 'A04CrashPadSimulator',
    # Line B (B01 → B02 → B03)
    'B01FuelTankSimulator', 'B02ChassisMergeSimulator', 'B03MufflerSimulator',
    # Line C (C01 → C02 → C03 → C04 → C05)
    'C01FEMSimulator', 'C02GlassSimulator', 'C03SeatSimulator', 'C04BumperSimulator', 'C05TireSimulator',
    # Line D (D01 → D02 → D03)
    'D01WheelAlignmentSimulator', 'D02HeadlampSimulator', 'D03WaterLeakTestSimulator',
    # Robots
    'ABBRobotSimulator', 'FANUCRobotSimulator', 'UniversalRobotSimulator'
]
