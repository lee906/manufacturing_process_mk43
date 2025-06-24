package com.u1mobis.dashboard_backend.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DashboardDto {
    
    @JsonProperty("production")
    private ProductionInfo production;
    
    @JsonProperty("kpi")
    private KpiInfo kpi;
    
    @JsonProperty("quality")
    private QualityInfo quality;
    
    @JsonProperty("efficiency")
    private EfficiencyInfo efficiency;
    
    @JsonProperty("timestamp")
    private String timestamp;
    
    @JsonProperty("lastUpdated")
    private String lastUpdated;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ProductionInfo {
        private Integer current;
        private Integer target;
        private Double hourlyRate;
        private String cycleTime;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class KpiInfo {
        private String oee;
        private String otd;
        private String fty;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class QualityInfo {
        private String overallScore;
        private String defectRate;
        private String grade;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class EfficiencyInfo {
        private String powerEfficiency;
        private Integer energyConsumption;
    }
}