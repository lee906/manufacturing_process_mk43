"""
컨베이어 경로 계산 시스템
Factory2DTwin.jsx의 좌표계를 기반으로 한 실제 이동 경로 구현
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class PathSegment:
    """경로 구간"""
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    segment_type: str  # 'horizontal', 'vertical'
    line_name: str     # 'A', 'B', 'C', 'D', 'A→B', 'B→C', 'C→D'

class ConveyorPathCalculator:
    """컨베이어 경로 계산기 (Factory2DTwin.jsx 좌표계 기반)"""
    
    def __init__(self):
        # Factory2DTwin.jsx의 컨베이어 경로 좌표 (288-307라인)
        self.belt_height = 60
        
        # 컨베이어 경로 정의
        self.conveyor_segments = [
            # A라인 (0~1000, 120~180) - 좌→우
            PathSegment(0, 150, 1000, 150, 'horizontal', 'A'),
            
            # A→B 수직 연결 (940~1000, 180~320) - 하향
            PathSegment(970, 180, 970, 320, 'vertical', 'A→B'),
            
            # B라인 (0~1000, 320~380) - 우→좌
            PathSegment(1000, 350, 0, 350, 'horizontal', 'B'),
            
            # B→C 수직 연결 (0~60, 380~520) - 하향
            PathSegment(30, 380, 30, 520, 'vertical', 'B→C'),
            
            # C라인 (0~1000, 520~580) - 좌→우
            PathSegment(0, 550, 1000, 550, 'horizontal', 'C'),
            
            # C→D 수직 연결 (940~1000, 580~720) - 하향
            PathSegment(970, 580, 970, 720, 'vertical', 'C→D'),
            
            # D라인 (0~1000, 720~780) - 우→좌
            PathSegment(1000, 750, 0, 750, 'horizontal', 'D')
        ]
        
        # 스테이션별 경로 매핑 (vehicle_tracker.py의 좌표와 일치)
        self.station_to_path_mapping = {
            # A라인 스테이션들
            "A01_DOOR": ("A", 150),
            "A02_WIRING": ("A", 300),
            "A03_HEADLINER": ("A", 450),
            "A04_CRASH_PAD": ("A", 750),
            
            # A→B 연결
            "A_TO_B": ("A→B", 970),
            
            # B라인 스테이션들
            "B01_FUEL_TANK": ("B", 850),
            "B02_CHASSIS_MERGE": ("B", 500),
            "B03_MUFFLER": ("B", 150),
            
            # B→C 연결
            "B_TO_C": ("B→C", 30),
            
            # C라인 스테이션들
            "C01_FEM": ("C", 150),
            "C02_GLASS": ("C", 300),
            "C03_SEAT": ("C", 450),
            "C04_BUMPER": ("C", 600),
            "C05_TIRE": ("C", 750),
            
            # C→D 연결
            "C_TO_D": ("C→D", 970),
            
            # D라인 스테이션들
            "D01_WHEEL_ALIGNMENT": ("D", 800),
            "D02_HEADLAMP": ("D", 650),
            "D03_WATER_LEAK_TEST": ("D", 320)
        }
        
        # 스테이션 순서 (vehicle_tracker.py와 동일)
        self.station_sequence = [
            "A01_DOOR", "A02_WIRING", "A03_HEADLINER", "A04_CRASH_PAD",
            "B01_FUEL_TANK", "B02_CHASSIS_MERGE", "B03_MUFFLER",
            "C01_FEM", "C02_GLASS", "C03_SEAT", "C04_BUMPER", "C05_TIRE",
            "D01_WHEEL_ALIGNMENT", "D02_HEADLAMP", "D03_WATER_LEAK_TEST"
        ]
    
    def get_station_position(self, station_id: str) -> Tuple[float, float]:
        """스테이션의 실제 좌표 반환"""
        if station_id not in self.station_to_path_mapping:
            return (0, 0)
        
        line_name, x_pos = self.station_to_path_mapping[station_id]
        
        # 라인별 Y 좌표
        line_y_positions = {
            'A': 150,
            'B': 350,
            'C': 550,
            'D': 750
        }
        
        y_pos = line_y_positions.get(line_name, 0)
        return (float(x_pos), float(y_pos))
    
    def calculate_movement_path(self, from_station: str, to_station: str) -> List[Tuple[float, float]]:
        """두 스테이션 간의 이동 경로 계산"""
        from_idx = self.station_sequence.index(from_station) if from_station in self.station_sequence else -1
        to_idx = self.station_sequence.index(to_station) if to_station in self.station_sequence else -1
        
        if from_idx == -1 or to_idx == -1 or from_idx >= to_idx:
            return []
        
        from_pos = self.get_station_position(from_station)
        to_pos = self.get_station_position(to_station)
        
        # 같은 라인 내 이동
        if from_pos[1] == to_pos[1]:
            return self._calculate_same_line_path(from_pos, to_pos)
        
        # 다른 라인 간 이동 (연결 구간 포함)
        return self._calculate_cross_line_path(from_station, to_station)
    
    def _calculate_same_line_path(self, from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> List[Tuple[float, float]]:
        """같은 라인 내에서의 경로 계산"""
        path_points = []
        
        # 직선 경로 생성 (10픽셀 간격)
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        distance = abs(x2 - x1)
        steps = max(1, int(distance / 10))  # 10픽셀 간격
        
        for i in range(steps + 1):
            progress = i / steps
            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress
            path_points.append((x, y))
        
        return path_points
    
    def _calculate_cross_line_path(self, from_station: str, to_station: str) -> List[Tuple[float, float]]:
        """라인 간 이동 경로 계산 (연결 구간 포함)"""
        path_points = []
        
        from_pos = self.get_station_position(from_station)
        to_pos = self.get_station_position(to_station)
        
        from_line = self.station_to_path_mapping[from_station][0]
        to_line = self.station_to_path_mapping[to_station][0]
        
        # A라인에서 시작하는 경우
        if from_line == 'A':
            # A라인 끝까지 이동 (x=1000)
            path_points.extend(self._calculate_same_line_path(from_pos, (1000, 150)))
            
            if to_line == 'B':
                # A→B 연결 구간
                path_points.extend(self._calculate_vertical_path((970, 180), (970, 320)))
                # B라인 시작점으로
                path_points.extend(self._calculate_same_line_path((1000, 350), to_pos))
        
        # B라인에서 시작하는 경우
        elif from_line == 'B':
            # B라인 시작까지 이동 (x=0)
            path_points.extend(self._calculate_same_line_path(from_pos, (0, 350)))
            
            if to_line == 'C':
                # B→C 연결 구간
                path_points.extend(self._calculate_vertical_path((30, 380), (30, 520)))
                # C라인에서 목표 위치까지
                path_points.extend(self._calculate_same_line_path((0, 550), to_pos))
        
        # C라인에서 시작하는 경우
        elif from_line == 'C':
            # C라인 끝까지 이동 (x=1000)
            path_points.extend(self._calculate_same_line_path(from_pos, (1000, 550)))
            
            if to_line == 'D':
                # C→D 연결 구간
                path_points.extend(self._calculate_vertical_path((970, 580), (970, 720)))
                # D라인에서 목표 위치까지
                path_points.extend(self._calculate_same_line_path((1000, 750), to_pos))
        
        return path_points
    
    def _calculate_vertical_path(self, from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> List[Tuple[float, float]]:
        """수직 경로 계산"""
        path_points = []
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        distance = abs(y2 - y1)
        steps = max(1, int(distance / 10))  # 10픽셀 간격
        
        for i in range(steps + 1):
            progress = i / steps
            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress
            path_points.append((x, y))
        
        return path_points
    
    def interpolate_position(self, path_points: List[Tuple[float, float]], progress: float) -> Tuple[float, float]:
        """경로상의 특정 진행률에 해당하는 위치 계산"""
        if not path_points:
            return (0, 0)
        
        if progress <= 0:
            return path_points[0]
        if progress >= 1:
            return path_points[-1]
        
        # 전체 경로 길이 계산
        total_distance = 0
        segment_distances = []
        
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            segment_distances.append(distance)
            total_distance += distance
        
        # 진행률에 해당하는 거리 계산
        target_distance = progress * total_distance
        current_distance = 0
        
        # 해당 구간 찾기
        for i, segment_distance in enumerate(segment_distances):
            if current_distance + segment_distance >= target_distance:
                # 구간 내 위치 계산
                segment_progress = (target_distance - current_distance) / segment_distance
                x1, y1 = path_points[i]
                x2, y2 = path_points[i + 1]
                
                x = x1 + (x2 - x1) * segment_progress
                y = y1 + (y2 - y1) * segment_progress
                return (x, y)
            
            current_distance += segment_distance
        
        return path_points[-1]
    
    def get_next_station_in_sequence(self, current_station: str) -> Optional[str]:
        """다음 스테이션 반환"""
        try:
            current_idx = self.station_sequence.index(current_station)
            if current_idx < len(self.station_sequence) - 1:
                return self.station_sequence[current_idx + 1]
        except ValueError:
            pass
        return None