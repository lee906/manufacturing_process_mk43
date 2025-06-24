package com.u1mobis.dashboard_backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "iot_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties(ignoreUnknown = true)
public class IoTData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "station_id", nullable = false)
    private String stationId;
    
    @Column(name = "process_type")
    private String processType;
    
    @Column(name = "location")
    private String location;
    
    @Column(name = "timestamp")
    private LocalDateTime timestamp;
    
    @Column(name = "processed_at")
    private LocalDateTime processedAt;
    
    @Column(name = "topic")
    private String topic;
    
    // JSON 데이터를 저장하기 위한 필드들
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "sensors", columnDefinition = "json")
    private JsonNode sensors;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "production", columnDefinition = "json")
    private JsonNode production;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "quality", columnDefinition = "json")
    private JsonNode quality;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "alerts", columnDefinition = "json")
    private JsonNode alerts;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "robot_data", columnDefinition = "json")
    private JsonNode robotData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "conveyor_data", columnDefinition = "json")
    private JsonNode conveyorData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "quality_data", columnDefinition = "json")
    private JsonNode qualityData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "inventory_data", columnDefinition = "json")
    private JsonNode inventoryData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "derived_metrics", columnDefinition = "json")
    private JsonNode derivedMetrics;
    
    @PrePersist
    protected void onCreate() {
        if (processedAt == null) {
            processedAt = LocalDateTime.now();
        }
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
    }
    
    // Helper methods for JSON manipulation
    public void setSensorsFromObject(Object sensors) {
        ObjectMapper mapper = new ObjectMapper();
        this.sensors = mapper.valueToTree(sensors);
    }
    
    public void setProductionFromObject(Object production) {
        ObjectMapper mapper = new ObjectMapper();
        this.production = mapper.valueToTree(production);
    }
    
    public void setQualityFromObject(Object quality) {
        ObjectMapper mapper = new ObjectMapper();
        this.quality = mapper.valueToTree(quality);
    }
    
    public void setAlertsFromObject(Object alerts) {
        ObjectMapper mapper = new ObjectMapper();
        this.alerts = mapper.valueToTree(alerts);
    }
    
    public void setRobotDataFromObject(Object robotData) {
        ObjectMapper mapper = new ObjectMapper();
        this.robotData = mapper.valueToTree(robotData);
    }
    
    public void setConveyorDataFromObject(Object conveyorData) {
        ObjectMapper mapper = new ObjectMapper();
        this.conveyorData = mapper.valueToTree(conveyorData);
    }
    
    public void setQualityDataFromObject(Object qualityData) {
        ObjectMapper mapper = new ObjectMapper();
        this.qualityData = mapper.valueToTree(qualityData);
    }
    
    public void setInventoryDataFromObject(Object inventoryData) {
        ObjectMapper mapper = new ObjectMapper();
        this.inventoryData = mapper.valueToTree(inventoryData);
    }
    
    public void setDerivedMetricsFromObject(Object derivedMetrics) {
        ObjectMapper mapper = new ObjectMapper();
        this.derivedMetrics = mapper.valueToTree(derivedMetrics);
    }
}