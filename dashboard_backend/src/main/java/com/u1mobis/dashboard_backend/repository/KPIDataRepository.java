package com.u1mobis.dashboard_backend.repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.u1mobis.dashboard_backend.entity.KPIData;

@Repository
public interface KPIDataRepository extends JpaRepository<KPIData, Long> {
    
    // 모든 스테이션의 최신 KPI 데이터
    @Query("SELECT k FROM KPIData k WHERE k.timestamp = (SELECT MAX(k2.timestamp) FROM KPIData k2 WHERE k2.stationId = k.stationId)")
    List<KPIData> findLatestKPIByAllStations();
    
    // 특정 스테이션의 최신 KPI
    Optional<KPIData> findTopByStationIdOrderByTimestampDesc(String stationId);
    
    // 특정 시간 범위의 KPI 데이터
    List<KPIData> findByTimestampBetween(LocalDateTime startTime, LocalDateTime endTime);
    
    // 특정 스테이션의 시간 범위 KPI
    List<KPIData> findByStationIdAndTimestampBetween(String stationId, LocalDateTime startTime, LocalDateTime endTime);
    
    // 최근 N개 KPI 데이터 조회
    List<KPIData> findTop10ByOrderByTimestampDesc();
    
    // 특정 스테이션의 최근 N개 KPI
    List<KPIData> findTop10ByStationIdOrderByTimestampDesc(String stationId);
    
    // 오늘 KPI 데이터 개수
    @Query("SELECT COUNT(k) FROM KPIData k WHERE k.timestamp >= :startOfDay AND k.timestamp < :endOfDay")
    Long countTodayKPI(@Param("startOfDay") LocalDateTime startOfDay, @Param("endOfDay") LocalDateTime endOfDay);
}