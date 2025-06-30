package com.u1mobis.dashboard_backend.entity;

import java.time.LocalDateTime;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "kpi_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KPIData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "station_id", nullable = false)
    private String stationId;
    
    @Column(name = "timestamp")
    private LocalDateTime timestamp;
    
    @Column(name = "total_cycles")
    private Integer totalCycles;
    
    @Column(name = "runtime_hours")
    private Double runtimeHours;
    
    // KPI JSON 데이터 저장
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "oee_data", columnDefinition = "json")
    private JsonNode oeeData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "fty_data", columnDefinition = "json")
    private JsonNode ftyData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "otd_data", columnDefinition = "json")
    private JsonNode otdData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "quality_data", columnDefinition = "json")
    private JsonNode qualityData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "throughput_data", columnDefinition = "json")
    private JsonNode throughputData;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "cycle_time_data", columnDefinition = "json")
    private JsonNode cycleTimeData;
    
    @PrePersist
    protected void onCreate() {
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
    }
    
    // Helper methods for JSON manipulation
    public void setOeeDataFromObject(Object oeeData) {
        ObjectMapper mapper = new ObjectMapper();
        this.oeeData = mapper.valueToTree(oeeData);
    }
    
    public void setFtyDataFromObject(Object ftyData) {
        ObjectMapper mapper = new ObjectMapper();
        this.ftyData = mapper.valueToTree(ftyData);
    }
    
    public void setOtdDataFromObject(Object otdData) {
        ObjectMapper mapper = new ObjectMapper();
        this.otdData = mapper.valueToTree(otdData);
    }
    
    public void setQualityDataFromObject(Object qualityData) {
        ObjectMapper mapper = new ObjectMapper();
        this.qualityData = mapper.valueToTree(qualityData);
    }
    
    public void setThroughputDataFromObject(Object throughputData) {
        ObjectMapper mapper = new ObjectMapper();
        this.throughputData = mapper.valueToTree(throughputData);
    }
    
    public void setCycleTimeDataFromObject(Object cycleTimeData) {
        ObjectMapper mapper = new ObjectMapper();
        this.cycleTimeData = mapper.valueToTree(cycleTimeData);
    }
}