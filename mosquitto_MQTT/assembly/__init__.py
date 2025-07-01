"""
Assembly Process Simulators Package
자동차 의장공정 시뮬레이터 패키지 - Flat Structure with Line Sequence
"""

__version__ = "2.0.0"
__author__ = "Manufacturing IoT Team"

from .base_simulator import BaseStationSimulator

# Line A Simulators (도어 및 내장재)
from .A_01_door_removal import A01DoorRemovalSimulator
from .A_02_wiring import A02WiringSimulator
from .A_03_headliner import A03HeadlinerSimulator
from .A_04_crash_pad import A04CrashPadSimulator

# Line B Simulators (샤시 및 연료계통)
from .B_01_fuel_tank import B01FuelTankSimulator
from .B_02_chassis_merge import B02ChassisMergeSimulator
from .B_03_muffler import B03MufflerSimulator

# Line C Simulators (주요 부품 조립)
from .C_01_fem import C01FEMSimulator
from .C_02_glass import C02GlassSimulator
from .C_03_seat import C03SeatSimulator
from .C_04_bumper import C04BumperSimulator
from .C_05_tire import C05TireSimulator

# Line D Simulators (검사 및 최종점검)
from .D_01_wheel_alignment import D01WheelAlignmentSimulator
from .D_02_headlamp import D02HeadlampSimulator
from .D_03_water_leak_test import D03WaterLeakTestSimulator

# Main Simulator
from .assembly_simulator import AssemblyLineSimulator

__all__ = [
    'BaseStationSimulator',
    'A01DoorRemovalSimulator', 
    'A02WiringSimulator',
    'A03HeadlinerSimulator',
    'A04CrashPadSimulator',
    'B01FuelTankSimulator',
    'B02ChassisMergeSimulator',
    'B03MufflerSimulator',
    'C01FEMSimulator',
    'C02GlassSimulator', 
    'C03SeatSimulator',
    'C04BumperSimulator',
    'C05TireSimulator',
    'D01WheelAlignmentSimulator',
    'D02HeadlampSimulator',
    'D03WaterLeakTestSimulator',
    'AssemblyLineSimulator'
]
