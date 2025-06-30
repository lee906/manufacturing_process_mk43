package com.u1mobis.dashboard_backend.controller;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.u1mobis.dashboard_backend.service.KPIService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api/kpi")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:3000"})
@RequiredArgsConstructor
@Slf4j
public class KPIController {
    
    private final KPIService kpiService;
    
    /**
     * Data Collector에서 계산된 KPI 데이터 수신
     */
    @PostMapping("/data")
    public ResponseEntity<Map<String, String>> receiveKPIData(@RequestBody Map<String, Object> kpiData) {
        try {
            log.info("KPI 데이터 수신: {}", kpiData.get("station_id"));
            
            kpiService.processKPIData(kpiData);
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "KPI 데이터가 성공적으로 처리되었습니다.",
                "timestamp", java.time.LocalDateTime.now().toString()
            ));
            
        } catch (Exception e) {
            log.error("KPI 데이터 처리 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "status", "error",
                "message", "KPI 데이터 처리 중 오류가 발생했습니다: " + e.getMessage(),
                "timestamp", java.time.LocalDateTime.now().toString()
            ));
        }
    }
    
    /**
     * 최신 KPI 데이터 조회 (React에서 사용)
     */
    @GetMapping("/latest")
    public ResponseEntity<Map<String, Object>> getLatestKPIData() {
        try {
            log.debug("최신 KPI 데이터 요청");
            
            Map<String, Object> kpiData = kpiService.getLatestKPIData();
            
            return ResponseEntity.ok(kpiData);
            
        } catch (Exception e) {
            log.error("KPI 데이터 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "error", "KPI 데이터 조회 실패",
                "message", e.getMessage()
            ));
        }
    }
    
    /**
     * 스테이션별 KPI 조회
     */
    @GetMapping("/station/{stationId}")
    public ResponseEntity<Map<String, Object>> getStationKPI(@PathVariable String stationId) {
        try {
            log.debug("스테이션 {} KPI 요청", stationId);
            
            Map<String, Object> stationKPI = kpiService.getStationKPI(stationId);
            
            return ResponseEntity.ok(stationKPI);
            
        } catch (Exception e) {
            log.error("스테이션 KPI 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "error", "스테이션 KPI 조회 실패",
                "stationId", stationId
            ));
        }
    }
    
    /**
     * 공장 전체 KPI 요약
     */
    @GetMapping("/factory/summary")
    public ResponseEntity<Map<String, Object>> getFactoryKPISummary() {
        try {
            log.debug("공장 전체 KPI 요약 요청");
            
            Map<String, Object> factorySummary = kpiService.getFactoryKPISummary();
            
            return ResponseEntity.ok(factorySummary);
            
        } catch (Exception e) {
            log.error("공장 KPI 요약 조회 중 오류 발생", e);
            
            return ResponseEntity.status(500).body(Map.of(
                "error", "공장 KPI 요약 조회 실패",
                "message", e.getMessage()
            ));
        }
    }
}
