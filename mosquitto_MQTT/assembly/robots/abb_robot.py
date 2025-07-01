"""
ABB Robot Simulator
ABB IRB series robot simulator
"""

import time
import random
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ABBRobotModel(Enum):
    """ABB Robot Models"""
    IRB_120 = "IRB 120"      # Small robot (3kg)
    IRB_1600 = "IRB 1600"    # Medium robot (6kg)  
    IRB_6700 = "IRB 6700"    # Large robot (150kg)
    IRB_4600 = "IRB 4600"    # General purpose (20kg)

@dataclass
class ABBJointLimits:
    """ABB Robot joint angle limits"""
    joint_1: tuple = (-180, 180)
    joint_2: tuple = (-90, 150) 
    joint_3: tuple = (-240, 60)
    joint_4: tuple = (-200, 200)
    joint_5: tuple = (-120, 120)
    joint_6: tuple = (-400, 400)

@dataclass
class ABBTelemetryData:
    """ABB Robot telemetry data structure"""
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
    speed_override: float
    payload_weight: float

class ABBRobotSimulator:
    """ABB Robot Simulator with realistic telemetry"""
    
    def __init__(self, robot_id: str, model: ABBRobotModel, station_id: str):
        self.robot_id = robot_id
        self.model = model
        self.station_id = station_id
        self.joint_limits = ABBJointLimits()
        
        # Robot state
        self.status = "running"
        self.current_program = "MainProgram.mod"
        self.cycle_count = random.randint(1500, 3000)
        self.joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.tcp_position = {"x": 500.0, "y": 0.0, "z": 600.0, "rx": 0.0, "ry": 0.0, "rz": 0.0}
        self.speed_override = 100.0
        self.payload_weight = 0.0
        
        # Initialize random position
        self._randomize_position()
        
    def _randomize_position(self):
        """Randomize robot position within limits"""
        for i in range(6):
            min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
            self.joint_angles[i] = random.uniform(min_angle * 0.3, max_angle * 0.3)
            
    def _calculate_tcp_from_joints(self) -> Dict[str, float]:
        """Calculate TCP position from joint angles (simplified forward kinematics)"""
        # Simplified calculation for simulation
        base_x = 500 + math.cos(math.radians(self.joint_angles[0])) * 300
        base_y = math.sin(math.radians(self.joint_angles[0])) * 300
        base_z = 600 + math.sin(math.radians(self.joint_angles[1])) * 200
        
        return {
            "x": round(base_x, 1),
            "y": round(base_y, 1), 
            "z": round(base_z, 1),
            "rx": round(self.joint_angles[3], 1),
            "ry": round(self.joint_angles[4], 1),
            "rz": round(self.joint_angles[5], 1)
        }
        
    def _get_temperature_data(self) -> Dict[str, float]:
        """Get robot temperature readings"""
        base_temp = 45.0
        return {
            "controller": round(base_temp + random.uniform(-5, 15), 1),
            "motor_1": round(base_temp + random.uniform(-3, 12), 1),
            "motor_2": round(base_temp + random.uniform(-3, 12), 1),
            "motor_3": round(base_temp + random.uniform(-3, 12), 1),
            "motor_4": round(base_temp + random.uniform(-2, 8), 1),
            "motor_5": round(base_temp + random.uniform(-2, 8), 1),
            "motor_6": round(base_temp + random.uniform(-2, 8), 1)
        }
        
    def _get_power_consumption(self) -> float:
        """Calculate power consumption based on robot model"""
        base_power = {
            ABBRobotModel.IRB_120: 1.2,
            ABBRobotModel.IRB_1600: 2.5,
            ABBRobotModel.IRB_6700: 8.5,
            ABBRobotModel.IRB_4600: 4.2
        }
        
        power = base_power.get(self.model, 3.0)
        # Add variation based on movement and payload
        movement_factor = (abs(sum(self.joint_angles)) / 100) * 0.1
        payload_factor = self.payload_weight * 0.05
        
        return round(power + movement_factor + payload_factor + random.uniform(-0.2, 0.3), 2)
        
    def _simulate_movement(self):
        """Simulate robot movement"""
        if self.status == "running":
            # Simulate joint movement
            for i in range(6):
                # Small random movement
                delta = random.uniform(-2, 2)
                min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
                new_angle = self.joint_angles[i] + delta
                
                # Keep within limits
                if min_angle <= new_angle <= max_angle:
                    self.joint_angles[i] = round(new_angle, 2)
                    
            # Update TCP position
            self.tcp_position = self._calculate_tcp_from_joints()
            
            # Simulate payload changes
            if random.random() < 0.1:  # 10% chance
                self.payload_weight = random.choice([0.0, 2.5, 5.0, 8.0])
                
    def _get_error_codes(self) -> List[str]:
        """Generate realistic error codes"""
        if random.random() < 0.05:  # 5% chance of errors
            possible_errors = [
                "50074", "50008", "50082", "50083", "50084"  # Common ABB error codes
            ]
            return [random.choice(possible_errors)]
        return []
        
    def get_telemetry_data(self) -> ABBTelemetryData:
        """Get current telemetry data"""
        self._simulate_movement()
        
        # Increment cycle count occasionally
        if random.random() < 0.3:  # 30% chance
            self.cycle_count += 1
            
        return ABBTelemetryData(
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
            speed_override=self.speed_override,
            payload_weight=self.payload_weight
        )
        
    def set_status(self, status: str):
        """Set robot status"""
        valid_statuses = ["running", "stopped", "error", "maintenance"]
        if status in valid_statuses:
            self.status = status
            
    def set_program(self, program: str):
        """Set current program"""
        self.current_program = program
        
    def set_speed_override(self, speed: float):
        """Set speed override (0-100%)"""
        self.speed_override = max(0, min(100, speed))