package com.u1mobis.dashboard_backend.service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.u1mobis.dashboard_backend.dto.DashboardDto;
import com.u1mobis.dashboard_backend.dto.IoTDataDto;
import com.u1mobis.dashboard_backend.entity.IoTData;
import com.u1mobis.dashboard_backend.entity.StationStatus;
import com.u1mobis.dashboard_backend.repository.IoTDataRepository;
import com.u1mobis.dashboard_backend.repository.StationStatusRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class IoTDataService {
    
    private final IoTDataRepository iotDataRepository;
    private final StationStatusRepository stationStatusRepository;
    private final ObjectMapper objectMapper;
    
    @Transactional
    public void processIoTData(Map<String, Object> rawData) {
        try {
            // DTO로 변환
            IoTDataDto dto = objectMapper.convertValue(rawData, IoTDataDto.class);
            
            // Entity로 변환 및 저장
            IoTData iotData = convertToEntity(dto);
            iotDataRepository.save(iotData);
            
            // Station Status 업데이트
            updateStationStatus(dto);
            
            log.info("IoT 데이터 처리 완료 - Station: {}, Time: {}", 
                dto.getStationId(), dto.getTimestamp());
            
        } catch (Exception e) {
            log.error("IoT 데이터 처리 중 오류 발생", e);
            throw new RuntimeException("IoT 데이터 처리 실패", e);
        }
    }
    
    private IoTData convertToEntity(IoTDataDto dto) {
        IoTData entity = IoTData.builder()
            .stationId(dto.getStationId())
            .processType(dto.getProcessType())
            .location(dto.getLocation())
            .topic(dto.getTopic())
            .build();
        
        // 타임스탬프 변환
        if (dto.getTimestamp() != null) {
            entity.setTimestamp(parseTimestamp(dto.getTimestamp()));
        }
        if (dto.getProcessedAt() != null) {
            entity.setProcessedAt(parseTimestamp(dto.getProcessedAt()));
        }
        
        // JSON 데이터 설정
        if (dto.getSensors() != null) {
            entity.setSensorsFromObject(dto.getSensors());
        }
        if (dto.getProduction() != null) {
            entity.setProductionFromObject(dto.getProduction());
        }
        if (dto.getQuality() != null) {
            entity.setQualityFromObject(dto.getQuality());
        }
        if (dto.getAlerts() != null) {
            entity.setAlertsFromObject(dto.getAlerts());
        }
        if (dto.getRobotData() != null) {
            entity.setRobotDataFromObject(dto.getRobotData());
        }
        if (dto.getConveyorData() != null) {
            entity.setConveyorDataFromObject(dto.getConveyorData());
        }
        if (dto.getQualityData() != null) {
            entity.setQualityDataFromObject(dto.getQualityData());
        }
        if (dto.getInventoryData() != null) {
            entity.setInventoryDataFromObject(dto.getInventoryData());
        }
        if (dto.getDerivedMetrics() != null) {
            entity.setDerivedMetricsFromObject(dto.getDerivedMetrics());
        }
        
        return entity;
    }
    
    private void updateStationStatus(IoTDataDto dto) {
        Optional<StationStatus> existingStatus = stationStatusRepository.findByStationId(dto.getStationId());
        
        StationStatus status;
        if (existingStatus.isPresent()) {
            status = existingStatus.get();
        } else {
            status = new StationStatus();
            status.setStationId(dto.getStationId());
        }
        
        // 기본 정보 업데이트
        status.setProcessType(dto.getProcessType());
        
        // 센서 데이터에서 상태 정보 추출
        if (dto.getSensors() != null) {
            Object tempObj = dto.getSensors().get("temperature");
            if (tempObj != null) {
                status.setTemperature(Double.valueOf(tempObj.toString()));
            }
        }
        
        // 생산 데이터에서 상태 추출
        if (dto.getProduction() != null) {
            Object statusObj = dto.getProduction().get("status");
            if (statusObj != null) {
                status.setStatus(statusObj.toString());
            }
        }
        
        // 파생 메트릭에서 효율성 추출
        if (dto.getDerivedMetrics() != null) {
            Object efficiencyObj = dto.getDerivedMetrics().get("efficiency");
            if (efficiencyObj != null) {
                status.setEfficiency(Double.valueOf(efficiencyObj.toString()));
            }
        }
        
        // 알림 개수 계산
        if (dto.getAlerts() != null) {
            long alertCount = dto.getAlerts().values().stream()
                .mapToLong(alert -> Boolean.TRUE.equals(alert) ? 1 : 0)
                .sum();
            status.setAlertCount((int) alertCount);
        }
        
        // 메트릭 저장
        if (dto.getRobotData() != null || dto.getConveyorData() != null || 
            dto.getQualityData() != null || dto.getInventoryData() != null) {
            
            Map<String, Object> metrics = new HashMap<>();
            if (dto.getRobotData() != null) metrics.putAll(dto.getRobotData());
            if (dto.getConveyorData() != null) metrics.putAll(dto.getConveyorData());
            if (dto.getQualityData() != null) metrics.putAll(dto.getQualityData());
            if (dto.getInventoryData() != null) metrics.putAll(dto.getInventoryData());
            
            status.setMetrics(objectMapper.valueToTree(metrics));
        }
        
        // 현재 알림 저장
        if (dto.getAlerts() != null) {
            status.setCurrentAlerts(objectMapper.valueToTree(dto.getAlerts()));
        }
        
        stationStatusRepository.save(status);
    }
    
    public DashboardDto getLatestDashboardData() {
        try {
            // 최신 IoT 데이터 조회
            List<IoTData> latestData = iotDataRepository.findLatestDataByAllStations();
            
            // 대시보드 데이터 계산
            return calculateDashboardMetrics(latestData);
            
        } catch (Exception e) {
            log.error("대시보드 데이터 조회 중 오류 발생", e);
            // 기본값 반환
            return getDefaultDashboardData();
        }
    }
    
    public List<Map<String, Object>> getStationsStatus() {
        try {
            List<StationStatus> stations = stationStatusRepository.findAllByOrderByLastUpdateDesc();
            
            return stations.stream()
                .map(this::convertStationToMap)
                .collect(Collectors.toList());
                
        } catch (Exception e) {
            log.error("스테이션 상태 조회 중 오류 발생", e);
            return Collections.emptyList();
        }
    }
    
    private DashboardDto calculateDashboardMetrics(List<IoTData> latestData) {
        if (latestData.isEmpty()) {
            return getDefaultDashboardData();
        }
        
        // 생산 데이터 계산
        int totalProduction = latestData.stream()
            .mapToInt(this::extractProductionCount)
            .sum();
        
        double avgCycleTime = latestData.stream()
            .mapToDouble(this::extractCycleTime)
            .average()
            .orElse(85.0);
        
        double hourlyRate = latestData.size() * 12.0; // 예시 계산
        
        // KPI 계산
        double avgEfficiency = latestData.stream()
            .mapToDouble(this::extractEfficiency)
            .average()
            .orElse(0.8);
        
        double avgQuality = latestData.stream()
            .mapToDouble(this::extractQuality)
            .average()
            .orElse(0.95);
        
        // OEE = 가동률 × 성능률 × 품질률 (실제 계산)
        double availability = 0.90; // 가동률 (실제로는 다운타임 데이터에서 계산)
        double performance = Math.min(1.0, hourlyRate / 100.0); // 성능률
        double oee = availability * performance * avgQuality * 100;
        double otd = Math.min(100.0, avgEfficiency * 100); // 정시 납기율
        double fty = avgQuality * 100; // 일회통과율
        
        return DashboardDto.builder()
            .production(DashboardDto.ProductionInfo.builder()
                .current(totalProduction)
                .target(1000)
                .hourlyRate(hourlyRate)
                .cycleTime(String.format("%.1f", avgCycleTime))
                .build())
            .kpi(DashboardDto.KpiInfo.builder()
                .oee(String.format("%.1f", oee))
                .otd(String.format("%.1f", otd))
                .fty(String.format("%.1f", fty))
                .build())
            .quality(DashboardDto.QualityInfo.builder()
                .overallScore(String.format("%.3f", avgQuality))
                .defectRate(String.format("%.3f", 1.0 - avgQuality))
                .grade(getQualityGrade(avgQuality))
                .build())
            .efficiency(DashboardDto.EfficiencyInfo.builder()
                .powerEfficiency(String.format("%.1f", avgEfficiency * 100))
                .energyConsumption(calculateEnergyConsumption(latestData))
                .build())
            .timestamp(LocalDateTime.now().toString())
            .lastUpdated(LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")))
            .build();
    }
    
    private DashboardDto getDefaultDashboardData() {
        return DashboardDto.builder()
            .production(DashboardDto.ProductionInfo.builder()
                .current(0)
                .target(1000)
                .hourlyRate(0.0)
                .cycleTime("0.0")
                .build())
            .kpi(DashboardDto.KpiInfo.builder()
                .oee("0.0")
                .otd("0.0")
                .fty("0.0")
                .build())
            .quality(DashboardDto.QualityInfo.builder()
                .overallScore("0.000")
                .defectRate("0.000")
                .grade("N/A")
                .build())
            .efficiency(DashboardDto.EfficiencyInfo.builder()
                .powerEfficiency("0.0")
                .energyConsumption(0)
                .build())
            .timestamp(LocalDateTime.now().toString())
            .lastUpdated(LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")))
            .build();
    }
    
    private Map<String, Object> convertStationToMap(StationStatus station) {
        Map<String, Object> result = new HashMap<>();
        result.put("stationId", station.getStationId());
        result.put("processType", station.getProcessType());
        result.put("status", station.getStatus());
        result.put("efficiency", station.getEfficiency());
        result.put("temperature", station.getTemperature());
        result.put("alertCount", station.getAlertCount());
        result.put("lastUpdate", station.getLastUpdate().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
        
        // JSON 메트릭을 Map으로 변환
        if (station.getMetrics() != null) {
            try {
                Map<String, Object> metrics = objectMapper.convertValue(station.getMetrics(), Map.class);
                result.put("metrics", metrics);
            } catch (Exception e) {
                result.put("metrics", new HashMap<>());
            }
        } else {
            result.put("metrics", new HashMap<>());
        }
        
        return result;
    }
    
    private int extractProductionCount(IoTData data) {
        try {
            if (data.getProduction() != null && data.getProduction().has("count")) {
                return data.getProduction().get("count").asInt();
            }
            // 실제 데이터가 없을 때 기본값 (랜덤 제거)
            return 0;
        } catch (Exception e) {
            return 0;
        }
    }
    
    private double extractCycleTime(IoTData data) {
        try {
            if (data.getProduction() != null && data.getProduction().has("cycle_time")) {
                return data.getProduction().get("cycle_time").asDouble();
            }
            // 스테이션별 기본 사이클 타임 (실제 데이터)
            String stationId = data.getStationId();
            if ("WELDING_01".equals(stationId)) return 18.0;
            if ("PAINTING_02".equals(stationId)) return 25.0;
            if ("ASSEMBLY_03".equals(stationId)) return 22.0;
            if ("INSPECTION_04".equals(stationId)) return 15.0;
            if ("STAMPING_05".equals(stationId)) return 12.0;
            return 20.0; // 기본값
        } catch (Exception e) {
            return 20.0;
        }
    }
    
    private double extractEfficiency(IoTData data) {
        try {
            if (data.getDerivedMetrics() != null && data.getDerivedMetrics().has("efficiency")) {
                return data.getDerivedMetrics().get("efficiency").asDouble();
            }
            // 센서 데이터에서 효율성 추출
            if (data.getSensors() != null && data.getSensors().has("efficiency_raw")) {
                return data.getSensors().get("efficiency_raw").asDouble();
            }
            // 실제 데이터가 없을 때 기본값
            return 0.85;
        } catch (Exception e) {
            return 0.85;
        }
    }
    
    private double extractQuality(IoTData data) {
        try {
            if (data.getQuality() != null && data.getQuality().has("score")) {
                return data.getQuality().get("score").asDouble();
            }
            // overall_score 확인
            if (data.getQuality() != null && data.getQuality().has("overall_score")) {
                return data.getQuality().get("overall_score").asDouble();
            }
            // 실제 데이터가 없을 때 기본값
            return 0.95;
        } catch (Exception e) {
            return 0.95;
        }
    }
    
    private String getQualityGrade(double quality) {
        if (quality >= 0.98) return "A+";
        if (quality >= 0.95) return "A";
        if (quality >= 0.90) return "B+";
        if (quality >= 0.85) return "B";
        return "C";
    }
    
    private LocalDateTime parseTimestamp(String timestamp) {
        try {
            // ISO 형식 타임스탬프 파싱
            return LocalDateTime.parse(timestamp.replace("Z", ""));
        } catch (Exception e) {
            // 파싱 실패시 현재 시간 반환
            log.warn("타임스탬프 파싱 실패: {}", timestamp);
            return LocalDateTime.now();
        }
    }
    
    private int calculateEnergyConsumption(List<IoTData> latestData) {
        // 실제 센서 데이터에서 전력 소비량 계산
        int totalConsumption = 0;
        for (IoTData data : latestData) {
            try {
                if (data.getSensors() != null && data.getSensors().has("power_consumption")) {
                    totalConsumption += data.getSensors().get("power_consumption").asInt();
                }
            } catch (Exception e) {
                // 기본값 추가
                totalConsumption += 250;
            }
        }
        return totalConsumption > 0 ? totalConsumption : 250;
    }
    
    // 통계 메서드들
    public Map<String, Object> getSystemStatistics() {
    Map<String, Object> stats = new HashMap<>();
    
    try {
        Long totalRecords = iotDataRepository.count();
        
        // 오늘 데이터 조회를 위한 시간 범위 설정
        LocalDateTime startOfDay = LocalDateTime.now().toLocalDate().atStartOfDay();
        LocalDateTime endOfDay = startOfDay.plusDays(1);
        Long todayRecords = iotDataRepository.countTodayData(startOfDay, endOfDay);
        
        Long runningStations = stationStatusRepository.countRunningStations();
        Double avgEfficiency = stationStatusRepository.getAverageEfficiency();
        Long totalAlerts = stationStatusRepository.getTotalAlertCount();
        
        stats.put("totalRecords", totalRecords);
        stats.put("todayRecords", todayRecords);
        stats.put("runningStations", runningStations);
        stats.put("averageEfficiency", avgEfficiency);
        stats.put("totalAlerts", totalAlerts);
        stats.put("lastUpdate", LocalDateTime.now().toString());
        
    } catch (Exception e) {
        log.error("시스템 통계 조회 중 오류 발생", e);
        stats.put("error", "통계 데이터 조회 실패");
    }
    
    return stats;
}
    
    // 최근 데이터 조회
    public List<Map<String, Object>> getRecentData(int limit) {
        try {
            List<IoTData> recentData = iotDataRepository.findTop10ByOrderByTimestampDesc();
            
            return recentData.stream()
                .limit(limit)
                .map(this::convertIoTDataToMap)
                .collect(Collectors.toList());
                
        } catch (Exception e) {
            log.error("최근 데이터 조회 중 오류 발생", e);
            return Collections.emptyList();
        }
    }
    
    private Map<String, Object> convertIoTDataToMap(IoTData data) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", data.getId());
        result.put("stationId", data.getStationId());
        result.put("processType", data.getProcessType());
        result.put("timestamp", data.getTimestamp().toString());
        result.put("processedAt", data.getProcessedAt().toString());
        
        // JSON 데이터들을 Map으로 변환
        try {
            if (data.getSensors() != null) {
                result.put("sensors", objectMapper.convertValue(data.getSensors(), Map.class));
            }
            if (data.getProduction() != null) {
                result.put("production", objectMapper.convertValue(data.getProduction(), Map.class));
            }
            if (data.getDerivedMetrics() != null) {
                result.put("derivedMetrics", objectMapper.convertValue(data.getDerivedMetrics(), Map.class));
            }
        } catch (Exception e) {
            log.warn("JSON 데이터 변환 중 오류 발생", e);
        }
        
        return result;
    }
}