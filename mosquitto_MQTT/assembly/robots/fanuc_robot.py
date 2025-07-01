"""
FANUC Robot Simulator
FANUC R-30iB series robot simulator
"""

import time
import random
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class FANUCRobotModel(Enum):
    """FANUC Robot Models"""
    M_10iA = "M-10iA"       # Compact robot (10kg)
    M_20iA = "M-20iA"       # Medium robot (20kg)
    R_2000iC = "R-2000iC"   # Heavy robot (210kg)
    LR_Mate_200iD = "LR Mate 200iD"  # Small robot (7kg)

@dataclass
class FANUCJointLimits:
    """FANUC Robot joint angle limits"""
    joint_1: tuple = (-170, 170)
    joint_2: tuple = (-120, 120) 
    joint_3: tuple = (-210, 210)
    joint_4: tuple = (-200, 200)
    joint_5: tuple = (-125, 125)
    joint_6: tuple = (-360, 360)

@dataclass
class FANUCTelemetryData:
    """FANUC Robot telemetry data structure"""
    timestamp: str
    robot_id: str
    model: str
    status: str
    position: Dict[str, float]
    joint_angles: List[float]
    tcp_coordinates: Dict[str, float]
    temperature: Dict[str, float]
    current_program: str
    cycle_count: int
    error_codes: List[str]
    power_consumption: float
    override_speed: float
    load_percentage: float

class FANUCRobotSimulator:
    """FANUC Robot Simulator with realistic telemetry"""
    
    def __init__(self, robot_id: str, model: FANUCRobotModel, station_id: str):
        self.robot_id = robot_id
        self.model = model
        self.station_id = station_id
        self.joint_limits = FANUCJointLimits()
        
        # Robot state
        self.status = "running"
        self.current_program = "MAIN.TP"
        self.cycle_count = random.randint(2000, 4000)
        self.joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.tcp_position = {"x": 450.0, "y": 0.0, "z": 550.0, "w": 0.0, "p": 0.0, "r": 0.0}
        self.override_speed = 100.0
        self.load_percentage = 0.0
        
        # Initialize random position
        self._randomize_position()
        
    def _randomize_position(self):
        """Randomize robot position within limits"""
        for i in range(6):
            min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
            self.joint_angles[i] = random.uniform(min_angle * 0.25, max_angle * 0.25)
            
    def _calculate_tcp_from_joints(self) -> Dict[str, float]:
        """Calculate TCP position from joint angles (simplified forward kinematics)"""
        # Simplified calculation for simulation
        base_x = 450 + math.cos(math.radians(self.joint_angles[0])) * 350
        base_y = math.sin(math.radians(self.joint_angles[0])) * 350
        base_z = 550 + math.sin(math.radians(self.joint_angles[1])) * 250
        
        return {
            "x": round(base_x, 1),
            "y": round(base_y, 1), 
            "z": round(base_z, 1),
            "w": round(self.joint_angles[3], 1),
            "p": round(self.joint_angles[4], 1),
            "r": round(self.joint_angles[5], 1)
        }
        
    def _get_temperature_data(self) -> Dict[str, float]:
        """Get robot temperature readings"""
        base_temp = 42.0
        return {
            "controller": round(base_temp + random.uniform(-3, 18), 1),
            "servo_1": round(base_temp + random.uniform(-2, 10), 1),
            "servo_2": round(base_temp + random.uniform(-2, 10), 1),
            "servo_3": round(base_temp + random.uniform(-2, 10), 1),
            "servo_4": round(base_temp + random.uniform(-1, 6), 1),
            "servo_5": round(base_temp + random.uniform(-1, 6), 1),
            "servo_6": round(base_temp + random.uniform(-1, 6), 1)
        }
        
    def _get_power_consumption(self) -> float:
        """Calculate power consumption based on robot model"""
        base_power = {
            FANUCRobotModel.M_10iA: 1.8,
            FANUCRobotModel.M_20iA: 3.2,
            FANUCRobotModel.R_2000iC: 12.5,
            FANUCRobotModel.LR_Mate_200iD: 0.9
        }
        
        power = base_power.get(self.model, 2.5)
        # Add variation based on movement and load
        movement_factor = (abs(sum(self.joint_angles)) / 120) * 0.15
        load_factor = self.load_percentage * 0.01
        
        return round(power + movement_factor + load_factor + random.uniform(-0.3, 0.4), 2)
        
    def _simulate_movement(self):
        """Simulate robot movement"""
        if self.status == "running":
            # Simulate joint movement
            for i in range(6):
                # Small random movement
                delta = random.uniform(-1.5, 1.5)
                min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
                new_angle = self.joint_angles[i] + delta
                
                # Keep within limits
                if min_angle <= new_angle <= max_angle:
                    self.joint_angles[i] = round(new_angle, 2)
                    
            # Update TCP position
            self.tcp_position = self._calculate_tcp_from_joints()
            
            # Simulate load changes
            if random.random() < 0.12:  # 12% chance
                self.load_percentage = random.uniform(0, 85)
                
    def _get_error_codes(self) -> List[str]:
        """Generate realistic FANUC error codes"""
        if random.random() < 0.04:  # 4% chance of errors
            possible_errors = [
                "SRVO-001", "SRVO-062", "SRVO-065", "DCS-001", "MOTN-023"  # Common FANUC error codes
            ]
            return [random.choice(possible_errors)]
        return []
        
    def get_telemetry_data(self) -> FANUCTelemetryData:
        """Get current telemetry data"""
        self._simulate_movement()
        
        # Increment cycle count occasionally
        if random.random() < 0.25:  # 25% chance
            self.cycle_count += 1
            
        return FANUCTelemetryData(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            robot_id=self.robot_id,
            model=self.model.value,
            status=self.status,
            position=self.tcp_position.copy(),
            joint_angles=self.joint_angles.copy(),
            tcp_coordinates=self.tcp_position.copy(),
            temperature=self._get_temperature_data(),
            current_program=self.current_program,
            cycle_count=self.cycle_count,
            error_codes=self._get_error_codes(),
            power_consumption=self._get_power_consumption(),
            override_speed=self.override_speed,
            load_percentage=round(self.load_percentage, 1)
        )
        
    def set_status(self, status: str):
        """Set robot status"""
        valid_statuses = ["running", "stopped", "error", "maintenance", "hold"]
        if status in valid_statuses:
            self.status = status
            
    def set_program(self, program: str):
        """Set current program"""
        self.current_program = program
        
    def set_override_speed(self, speed: float):
        """Set speed override (0-100%)"""
        self.override_speed = max(0, min(100, speed))