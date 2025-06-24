package com.u1mobis.dashboard_backend.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.u1mobis.dashboard_backend.dto.DashboardDto;
import com.u1mobis.dashboard_backend.service.IoTDataService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:3000"})
@RequiredArgsConstructor
@Slf4j
public class IoTDataController {
    
    private final IoTDataService iotDataService;
    
    /**
     * IoT 데이터 수신 엔드포인트
     * Python 데이터 수집기에서 POST 요청으로 데이터 전송
     */
    @PostMapping("/iot-data")
    public ResponseEntity<Map<String, String>> receiveIoTData(@RequestBody Map<String, Object> data) {
        try {
            log.info("IoT 데이터 수신: {}", data.get("stationId"));
            
            iotDataService.processIoTData(data);
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "데이터가 성공적으로 처리되었습니다.",
                "timestamp", java.time.LocalDateTime.now().toString()
            ));
            
        } catch (Exception e) {
            log.error("IoT 데이터 처리 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "status", "error",
                "message", "데이터 처리 중 오류가 발생했습니다: " + e.getMessage(),
                "timestamp", java.time.LocalDateTime.now().toString()
            ));
        }
    }
    
    /**
     * 대시보드 최신 데이터 조회
     * React 프론트엔드에서 실시간 데이터 요청
     */
    @GetMapping("/dashboard/latest")
    public ResponseEntity<DashboardDto> getLatestDashboardData() {
        try {
            log.debug("대시보드 최신 데이터 요청");
            
            DashboardDto dashboardData = iotDataService.getLatestDashboardData();
            
            return ResponseEntity.ok(dashboardData);
            
        } catch (Exception e) {
            log.error("대시보드 데이터 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(null);
        }
    }
    
    /**
     * 스테이션 상태 정보 조회
     * 로봇 테이블에 표시할 스테이션별 상태 데이터
     */
    @GetMapping("/stations/status")
    public ResponseEntity<List<Map<String, Object>>> getStationsStatus() {
        try {
            log.debug("스테이션 상태 정보 요청");
            
            List<Map<String, Object>> stationsData = iotDataService.getStationsStatus();
            
            return ResponseEntity.ok(stationsData);
            
        } catch (Exception e) {
            log.error("스테이션 상태 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(List.of());
        }
    }
    
    /**
     * 시스템 통계 정보 조회
     */
    @GetMapping("/system/statistics")
    public ResponseEntity<Map<String, Object>> getSystemStatistics() {
        try {
            log.debug("시스템 통계 정보 요청");
            
            Map<String, Object> statistics = iotDataService.getSystemStatistics();
            
            return ResponseEntity.ok(statistics);
            
        } catch (Exception e) {
            log.error("시스템 통계 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "error", "통계 데이터 조회 실패",
                "message", e.getMessage()
            ));
        }
    }
    
    /**
     * 최근 데이터 조회
     */
    @GetMapping("/data/recent")
    public ResponseEntity<List<Map<String, Object>>> getRecentData(
            @RequestParam(defaultValue = "10") int limit) {
        try {
            log.debug("최근 데이터 요청, limit: {}", limit);
            
            List<Map<String, Object>> recentData = iotDataService.getRecentData(limit);
            
            return ResponseEntity.ok(recentData);
            
        } catch (Exception e) {
            log.error("최근 데이터 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(List.of());
        }
    }
    
    /**
     * 특정 스테이션 데이터 조회
     */
    @GetMapping("/stations/{stationId}/latest")
    public ResponseEntity<Map<String, Object>> getStationLatestData(
            @PathVariable String stationId) {
        try {
            log.debug("스테이션 {} 최신 데이터 요청", stationId);
            
            // 구현 예정: 특정 스테이션의 최신 데이터 조회
            Map<String, Object> stationData = Map.of(
                "stationId", stationId,
                "message", "해당 스테이션의 최신 데이터",
                "timestamp", java.time.LocalDateTime.now().toString()
            );
            
            return ResponseEntity.ok(stationData);
            
        } catch (Exception e) {
            log.error("스테이션 데이터 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "error", "스테이션 데이터 조회 실패",
                "stationId", stationId
            ));
        }
    }
    
    /**
     * 헬스 체크 엔드포인트
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of(
            "status", "UP",
            "service", "IoT Dashboard Backend",
            "timestamp", java.time.LocalDateTime.now().toString(),
            "version", "1.0.0"
        ));
    }
    
    /**
     * 연결 테스트 엔드포인트 (React에서 연결 확인용)
     */
    @GetMapping("/test")
    public ResponseEntity<Map<String, String>> connectionTest() {
        return ResponseEntity.ok(Map.of(
            "message", "Spring Boot 백엔드 연결 성공!",
            "timestamp", java.time.LocalDateTime.now().toString(),
            "status", "connected"
        ));
    }
}