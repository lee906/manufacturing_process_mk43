package com.u1mobis.dashboard_backend.repository;

import com.u1mobis.dashboard_backend.entity.StationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface StationStatusRepository extends JpaRepository<StationStatus, Long> {
    
    // 스테이션 ID로 조회
    Optional<StationStatus> findByStationId(String stationId);
    
    // 모든 스테이션 상태 조회 (최신 업데이트 순)
    List<StationStatus> findAllByOrderByLastUpdateDesc();
    
    // 특정 상태의 스테이션들 조회
    List<StationStatus> findByStatus(String status);
    
    // 알림이 있는 스테이션들 조회
    @Query("SELECT s FROM StationStatus s WHERE s.alertCount > 0 ORDER BY s.alertCount DESC")
    List<StationStatus> findStationsWithAlerts();
    
    // 효율성이 특정 값 이하인 스테이션들
    @Query("SELECT s FROM StationStatus s WHERE s.efficiency < :threshold ORDER BY s.efficiency ASC")
    List<StationStatus> findStationsWithLowEfficiency(@Param("threshold") Double threshold);
    
    // 온도가 특정 값 이상인 스테이션들
    @Query("SELECT s FROM StationStatus s WHERE s.temperature > :threshold ORDER BY s.temperature DESC")
    List<StationStatus> findStationsWithHighTemperature(@Param("threshold") Double threshold);
    
    // 최근 업데이트된 스테이션들 (특정 시간 이후)
    @Query("SELECT s FROM StationStatus s WHERE s.lastUpdate >= :since ORDER BY s.lastUpdate DESC")
    List<StationStatus> findRecentlyUpdatedStations(@Param("since") LocalDateTime since);
    
    // 프로세스 타입별 스테이션들
    List<StationStatus> findByProcessType(String processType);
    
    // 가동 중인 스테이션 개수
    @Query("SELECT COUNT(s) FROM StationStatus s WHERE s.status = 'RUNNING'")
    Long countRunningStations();
    
    // 평균 효율성
    @Query("SELECT AVG(s.efficiency) FROM StationStatus s WHERE s.efficiency IS NOT NULL")
    Double getAverageEfficiency();
    
    // 총 알림 개수
    @Query("SELECT COALESCE(SUM(s.alertCount), 0) FROM StationStatus s")
    Long getTotalAlertCount();
}