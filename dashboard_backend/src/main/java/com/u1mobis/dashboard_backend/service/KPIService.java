package com.u1mobis.dashboard_backend.service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.u1mobis.dashboard_backend.entity.KPIData;
import com.u1mobis.dashboard_backend.repository.KPIDataRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class KPIService {
    
    private final KPIDataRepository kpiDataRepository;
    private final ObjectMapper objectMapper;
    
    @Transactional
    public void processKPIData(Map<String, Object> rawData) {
        try {
            // KPI 데이터를 Entity로 변환 및 저장
            KPIData kpiData = convertToEntity(rawData);
            kpiDataRepository.save(kpiData);
            
            log.info("KPI 데이터 저장 완료 - Station: {}, OEE: {}", 
                kpiData.getStationId(), 
                extractOEEValue(rawData));
            
        } catch (Exception e) {
            log.error("KPI 데이터 처리 중 오류 발생", e);
            throw new RuntimeException("KPI 데이터 처리 실패", e);
        }
    }
    
    public Map<String, Object> getLatestKPIData() {
        try {
            List<KPIData> latestKPIs = kpiDataRepository.findLatestKPIByAllStations();
            
            return buildKPIResponse(latestKPIs);
            
        } catch (Exception e) {
            log.error("최신 KPI 데이터 조회 중 오류 발생", e);
            return getDefaultKPIData();
        }
    }
    
    public Map<String, Object> getStationKPI(String stationId) {
        try {
            Optional<KPIData> latestKPI = kpiDataRepository.findTopByStationIdOrderByTimestampDesc(stationId);
            
            if (latestKPI.isPresent()) {
                return convertKPIToMap(latestKPI.get());
            } else {
                return Map.of(
                    "stationId", stationId,
                    "message", "해당 스테이션의 KPI 데이터가 없습니다."
                );
            }
            
        } catch (Exception e) {
            log.error("스테이션 KPI 조회 중 오류 발생", e);
            return Map.of("error", "스테이션 KPI 조회 실패");
        }
    }
    
    public Map<String, Object> getFactoryKPISummary() {
        try {
            List<KPIData> allStationKPIs = kpiDataRepository.findLatestKPIByAllStations();
            
            if (allStationKPIs.isEmpty()) {
                return getDefaultFactorySummary();
            }
            
            // 공장 전체 KPI 계산
            double avgOEE = allStationKPIs.stream()
                .mapToDouble(kpi -> extractDoubleFromJson(kpi.getOeeData(), "value"))
                .average()
                .orElse(0.0);
                
            double avgFTY = allStationKPIs.stream()
                .mapToDouble(kpi -> extractDoubleFromJson(kpi.getFtyData(), "value"))
                .average()
                .orElse(0.0);
                
            double avgOTD = allStationKPIs.stream()
                .mapToDouble(kpi -> extractDoubleFromJson(kpi.getOtdData(), "value"))
                .average()
                .orElse(0.0);
            
            double totalThroughput = allStationKPIs.stream()
                .mapToDouble(kpi -> extractDoubleFromJson(kpi.getThroughputData(), "value"))
                .sum();
            
            return Map.of(
                "timestamp", LocalDateTime.now().toString(),
                "factory_oee", Math.round(avgOEE * 100.0) / 100.0,
                "factory_fty", Math.round(avgFTY * 100.0) / 100.0,
                "factory_otd", Math.round(avgOTD * 100.0) / 100.0,
                "factory_throughput", Math.round(totalThroughput * 10.0) / 10.0,
                "active_stations", allStationKPIs.size(),
                "last_updated", LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"))
            );
            
        } catch (Exception e) {
            log.error("공장 KPI 요약 조회 중 오류 발생", e);
            return getDefaultFactorySummary();
        }
    }
    
    private KPIData convertToEntity(Map<String, Object> rawData) {
        KPIData entity = KPIData.builder()
            .stationId((String) rawData.get("station_id"))
            .timestamp(parseTimestamp((String) rawData.get("timestamp")))
            .totalCycles((Integer) rawData.getOrDefault("total_cycles", 0))
            .runtimeHours(((Number) rawData.getOrDefault("runtime_hours", 0.0)).doubleValue())
            .build();
        
        // JSON 데이터 저장
        if (rawData.containsKey("oee")) {
            entity.setOeeDataFromObject(rawData.get("oee"));
        }
        if (rawData.containsKey("fty")) {
            entity.setFtyDataFromObject(rawData.get("fty"));
        }
        if (rawData.containsKey("otd")) {
            entity.setOtdDataFromObject(rawData.get("otd"));
        }
        if (rawData.containsKey("quality_score")) {
            entity.setQualityDataFromObject(rawData.get("quality_score"));
        }
        if (rawData.containsKey("throughput")) {
            entity.setThroughputDataFromObject(rawData.get("throughput"));
        }
        if (rawData.containsKey("avg_cycle_time")) {
            entity.setCycleTimeDataFromObject(rawData.get("avg_cycle_time"));
        }
        
        return entity;
    }
    
    private Map<String, Object> buildKPIResponse(List<KPIData> kpiList) {
        Map<String, Object> response = new HashMap<>();
        
        if (kpiList.isEmpty()) {
            return getDefaultKPIData();
        }
        
        // 각 스테이션별 KPI 데이터
        Map<String, Object> stationKPIs = new HashMap<>();
        for (KPIData kpi : kpiList) {
            stationKPIs.put(kpi.getStationId(), convertKPIToMap(kpi));
        }
        
        // 전체 요약
        double avgOEE = kpiList.stream()
            .mapToDouble(kpi -> extractDoubleFromJson(kpi.getOeeData(), "value"))
            .average()
            .orElse(0.0);
            
        double avgFTY = kpiList.stream()
            .mapToDouble(kpi -> extractDoubleFromJson(kpi.getFtyData(), "value"))
            .average()
            .orElse(0.0);
            
        response.put("stations", stationKPIs);
        response.put("summary", Map.of(
            "avg_oee", Math.round(avgOEE * 100.0) / 100.0,
            "avg_fty", Math.round(avgFTY * 100.0) / 100.0,
            "total_stations", kpiList.size(),
            "timestamp", LocalDateTime.now().toString()
        ));
        
        return response;
    }
    
    private Map<String, Object> convertKPIToMap(KPIData kpiData) {
        Map<String, Object> result = new HashMap<>();
        
        result.put("stationId", kpiData.getStationId());
        result.put("timestamp", kpiData.getTimestamp().toString());
        result.put("totalCycles", kpiData.getTotalCycles());
        result.put("runtimeHours", kpiData.getRuntimeHours());
        
        // JSON 데이터를 Map으로 변환
        try {
            if (kpiData.getOeeData() != null) {
                result.put("oee", objectMapper.convertValue(kpiData.getOeeData(), Map.class));
            }
            if (kpiData.getFtyData() != null) {
                result.put("fty", objectMapper.convertValue(kpiData.getFtyData(), Map.class));
            }
            if (kpiData.getOtdData() != null) {
                result.put("otd", objectMapper.convertValue(kpiData.getOtdData(), Map.class));
            }
            if (kpiData.getQualityData() != null) {
                result.put("quality_score", objectMapper.convertValue(kpiData.getQualityData(), Map.class));
            }
            if (kpiData.getThroughputData() != null) {
                result.put("throughput", objectMapper.convertValue(kpiData.getThroughputData(), Map.class));
            }
        } catch (Exception e) {
            log.warn("JSON 데이터 변환 중 오류 발생", e);
        }
        
        return result;
    }
    
    private double extractDoubleFromJson(com.fasterxml.jackson.databind.JsonNode jsonNode, String key) {
        if (jsonNode != null && jsonNode.has(key)) {
            return jsonNode.get(key).asDouble();
        }
        return 0.0;
    }
    
    private double extractOEEValue(Map<String, Object> rawData) {
        if (rawData.containsKey("oee")) {
            Object oeeData = rawData.get("oee");
            if (oeeData instanceof Number) {
                return ((Number) oeeData).doubleValue();
            } else if (oeeData instanceof Map) {
                Map<String, Object> oeeMap = (Map<String, Object>) oeeData;
                if (oeeMap.containsKey("value")) {
                    return ((Number) oeeMap.get("value")).doubleValue();
                }
            }
        }
        return 0.0;
    }
    
    private LocalDateTime parseTimestamp(String timestamp) {
        try {
            return LocalDateTime.parse(timestamp.replace("Z", ""));
        } catch (Exception e) {
            log.warn("타임스탬프 파싱 실패: {}", timestamp);
            return LocalDateTime.now();
        }
    }
    
    private Map<String, Object> getDefaultKPIData() {
        return Map.of(
            "stations", Map.of(),
            "summary", Map.of(
                "avg_oee", 0.0,
                "avg_fty", 0.0,
                "total_stations", 0,
                "timestamp", LocalDateTime.now().toString()
            ),
            "message", "KPI 데이터가 없습니다 (시뮬레이션 모드)"
        );
    }
    
    private Map<String, Object> getDefaultFactorySummary() {
        return Map.of(
            "factory_oee", 0.0,
            "factory_fty", 0.0,
            "factory_otd", 0.0,
            "factory_throughput", 0.0,
            "active_stations", 0,
            "timestamp", LocalDateTime.now().toString(),
            "message", "공장 KPI 데이터가 없습니다"
        );
    }
}