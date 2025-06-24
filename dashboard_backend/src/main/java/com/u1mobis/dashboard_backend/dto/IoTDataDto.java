package com.u1mobis.dashboard_backend.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties(ignoreUnknown = true)
public class IoTDataDto {
    
    @JsonProperty("stationId")
    private String stationId;
    
    @JsonProperty("timestamp")
    private String timestamp;
    
    @JsonProperty("processType")
    private String processType;
    
    @JsonProperty("location")
    private String location;
    
    @JsonProperty("sensors")
    private Map<String, Object> sensors;
    
    @JsonProperty("production")
    private Map<String, Object> production;
    
    @JsonProperty("quality")
    private Map<String, Object> quality;
    
    @JsonProperty("alerts")
    private Map<String, Object> alerts;
    
    @JsonProperty("robotData")
    private Map<String, Object> robotData;
    
    @JsonProperty("conveyorData")
    private Map<String, Object> conveyorData;
    
    @JsonProperty("qualityData")
    private Map<String, Object> qualityData;
    
    @JsonProperty("inventoryData")
    private Map<String, Object> inventoryData;
    
    @JsonProperty("derivedMetrics")
    private Map<String, Object> derivedMetrics;
    
    @JsonProperty("processedAt")
    private String processedAt;
    
    @JsonProperty("topic")
    private String topic;
}