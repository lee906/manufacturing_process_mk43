"""
Universal Robots Simulator
UR collaborative robot simulator
"""

import time
import random
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class URRobotModel(Enum):
    """UR Robot Models"""
    UR3e = "UR3e"        # Compact robot (3kg)
    UR5e = "UR5e"        # Medium robot (5kg)
    UR10e = "UR10e"      # Large robot (10kg)
    UR16e = "UR16e"      # Heavy robot (16kg)

@dataclass
class URJointLimits:
    """UR Robot joint angle limits"""
    joint_1: tuple = (-360, 360)
    joint_2: tuple = (-360, 360) 
    joint_3: tuple = (-360, 360)
    joint_4: tuple = (-360, 360)
    joint_5: tuple = (-360, 360)
    joint_6: tuple = (-360, 360)

@dataclass
class URTelemetryData:
    """UR Robot telemetry data structure"""
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
    safety_status: str
    collaborative_mode: bool

class UniversalRobotSimulator:
    """Universal Robot Simulator with realistic telemetry"""
    
    def __init__(self, robot_id: str, model: URRobotModel, station_id: str):
        self.robot_id = robot_id
        self.model = model
        self.station_id = station_id
        self.joint_limits = URJointLimits()
        
        # Robot state
        self.status = "running"
        self.safety_status = "normal"
        self.collaborative_mode = True
        self.current_program = "default.urp"
        self.cycle_count = random.randint(1800, 3500)
        self.joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.tcp_position = {"x": 400.0, "y": 0.0, "z": 500.0, "rx": 0.0, "ry": 0.0, "rz": 0.0}
        
        # Initialize random position
        self._randomize_position()
        
    def _randomize_position(self):
        """Randomize robot position within limits"""
        for i in range(6):
            min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
            self.joint_angles[i] = random.uniform(min_angle * 0.2, max_angle * 0.2)
            
    def _calculate_tcp_from_joints(self) -> Dict[str, float]:
        """Calculate TCP position from joint angles (simplified forward kinematics)"""
        # Simplified calculation for simulation
        base_x = 400 + math.cos(math.radians(self.joint_angles[0])) * 400
        base_y = math.sin(math.radians(self.joint_angles[0])) * 400
        base_z = 500 + math.sin(math.radians(self.joint_angles[1])) * 300
        
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
        base_temp = 38.0
        return {
            "controller": round(base_temp + random.uniform(-2, 16), 1),
            "joint_1": round(base_temp + random.uniform(-1, 8), 1),
            "joint_2": round(base_temp + random.uniform(-1, 8), 1),
            "joint_3": round(base_temp + random.uniform(-1, 8), 1),
            "joint_4": round(base_temp + random.uniform(-1, 5), 1),
            "joint_5": round(base_temp + random.uniform(-1, 5), 1),
            "joint_6": round(base_temp + random.uniform(-1, 5), 1)
        }
        
    def _get_power_consumption(self) -> float:
        """Calculate power consumption based on robot model"""
        base_power = {
            URRobotModel.UR3e: 100.0,
            URRobotModel.UR5e: 200.0,
            URRobotModel.UR10e: 350.0,
            URRobotModel.UR16e: 500.0
        }
        
        power = base_power.get(self.model, 200.0)
        # Add variation based on movement
        movement_factor = (abs(sum(self.joint_angles)) / 180) * 0.2
        collaborative_factor = 0.8 if self.collaborative_mode else 1.0
        
        return round(power * collaborative_factor + movement_factor + random.uniform(-20, 30), 2)
        
    def _simulate_movement(self):
        """Simulate robot movement"""
        if self.status == "running":
            # Simulate joint movement
            for i in range(6):
                # Small random movement
                delta = random.uniform(-1.0, 1.0)
                min_angle, max_angle = getattr(self.joint_limits, f'joint_{i+1}')
                new_angle = self.joint_angles[i] + delta
                
                # Keep within limits
                if min_angle <= new_angle <= max_angle:
                    self.joint_angles[i] = round(new_angle, 2)
                    
            # Update TCP position
            self.tcp_position = self._calculate_tcp_from_joints()
            
            # Simulate safety status changes
            if random.random() < 0.02:  # 2% chance
                safety_statuses = ["normal", "reduced_mode", "protective_stop"]
                self.safety_status = random.choice(safety_statuses)
                
    def _get_error_codes(self) -> List[str]:
        """Generate realistic UR error codes"""
        if random.random() < 0.03:  # 3% chance of errors
            possible_errors = [
                "C201A0", "C100A1", "C161A1", "C162A1", "C300A1"  # Common UR error codes
            ]
            return [random.choice(possible_errors)]
        return []
        
    def get_telemetry_data(self) -> URTelemetryData:
        """Get current telemetry data"""
        self._simulate_movement()
        
        # Increment cycle count occasionally
        if random.random() < 0.2:  # 20% chance
            self.cycle_count += 1
            
        return URTelemetryData(
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
            safety_status=self.safety_status,
            collaborative_mode=self.collaborative_mode
        )
        
    def set_status(self, status: str):
        """Set robot status"""
        valid_statuses = ["running", "stopped", "error", "maintenance", "protective_stop"]
        if status in valid_statuses:
            self.status = status
            
    def set_program(self, program: str):
        """Set current program"""
        self.current_program = program
        
    def set_collaborative_mode(self, enabled: bool):
        """Enable/disable collaborative mode"""
        self.collaborative_mode = enabled