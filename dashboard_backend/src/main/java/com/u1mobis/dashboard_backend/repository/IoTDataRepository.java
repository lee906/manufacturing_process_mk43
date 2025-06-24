package com.u1mobis.dashboard_backend.repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.u1mobis.dashboard_backend.entity.IoTData;

@Repository
public interface IoTDataRepository extends JpaRepository<IoTData, Long> {
    
    // 최신 데이터 조회
    @Query("SELECT i FROM IoTData i WHERE i.timestamp = (SELECT MAX(i2.timestamp) FROM IoTData i2 WHERE i2.stationId = i.stationId)")
    List<IoTData> findLatestDataByAllStations();
    
    // 특정 스테이션의 최신 데이터
    Optional<IoTData> findTopByStationIdOrderByTimestampDesc(String stationId);
    
    // 특정 시간 범위의 데이터
    List<IoTData> findByTimestampBetween(LocalDateTime startTime, LocalDateTime endTime);
    
    // 특정 스테이션의 시간 범위 데이터
    List<IoTData> findByStationIdAndTimestampBetween(String stationId, LocalDateTime startTime, LocalDateTime endTime);
    
    // 최근 N개 데이터 조회
    List<IoTData> findTop10ByOrderByTimestampDesc();
    
    // 특정 스테이션의 최근 N개 데이터
    List<IoTData> findTop10ByStationIdOrderByTimestampDesc(String stationId);
    
    // 스테이션별 데이터 개수
    @Query("SELECT COUNT(i) FROM IoTData i WHERE i.stationId = :stationId")
    Long countByStationId(@Param("stationId") String stationId);
    
    // 전체 스테이션 목록
    @Query("SELECT DISTINCT i.stationId FROM IoTData i")
    List<String> findDistinctStationIds();
    
    // 특정 프로세스 타입별 최신 데이터
    @Query("SELECT i FROM IoTData i WHERE i.processType = :processType AND i.timestamp = (SELECT MAX(i2.timestamp) FROM IoTData i2 WHERE i2.processType = :processType)")
    List<IoTData> findLatestDataByProcessType(@Param("processType") String processType);
    
    // 최근 1시간 데이터
    @Query("SELECT i FROM IoTData i WHERE i.timestamp >= :oneHourAgo ORDER BY i.timestamp DESC")
    List<IoTData> findRecentHourData(@Param("oneHourAgo") LocalDateTime oneHourAgo);
    
    // 오늘 데이터 개수 (수정된 쿼리)
    @Query("SELECT COUNT(i) FROM IoTData i WHERE i.timestamp >= :startOfDay AND i.timestamp < :endOfDay")
    Long countTodayData(@Param("startOfDay") LocalDateTime startOfDay, @Param("endOfDay") LocalDateTime endOfDay);
}