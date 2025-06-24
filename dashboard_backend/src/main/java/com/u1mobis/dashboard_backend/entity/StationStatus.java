package com.u1mobis.dashboard_backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import com.fasterxml.jackson.databind.JsonNode;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "station_status")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StationStatus {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "station_id", nullable = false, unique = true)
    private String stationId;
    
    @Column(name = "process_type")
    private String processType;
    
    @Column(name = "status")
    private String status;
    
    @Column(name = "efficiency")
    private Double efficiency;
    
    @Column(name = "temperature")
    private Double temperature;
    
    @Column(name = "alert_count")
    private Integer alertCount;
    
    @Column(name = "last_update")
    private LocalDateTime lastUpdate;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "metrics", columnDefinition = "json")
    private JsonNode metrics;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "current_alerts", columnDefinition = "json")
    private JsonNode currentAlerts;
    
    @PrePersist
    @PreUpdate
    protected void onUpdate() {
        lastUpdate = LocalDateTime.now();
    }
}