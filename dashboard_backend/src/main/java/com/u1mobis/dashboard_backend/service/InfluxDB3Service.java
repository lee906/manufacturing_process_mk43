package com.u1mobis.dashboard_backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.u1mobis.dashboard_backend.config.InfluxDB3Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
public class InfluxDB3Service {
    
    private static final Logger logger = LoggerFactory.getLogger(InfluxDB3Service.class);
    
    private final WebClient sqlClient;
    private final WebClient writeClient;
    private final InfluxDB3Config config;
    private final ObjectMapper objectMapper;
    
    @Autowired
    public InfluxDB3Service(WebClient influxDb3SqlClient, 
                           WebClient influxDb3WriteClient,
                           InfluxDB3Config config) {
        this.sqlClient = influxDb3SqlClient;
        this.writeClient = influxDb3WriteClient;
        this.config = config;
        this.objectMapper = new ObjectMapper();
        logger.info("InfluxDB3Service 초기화 완료 - URL: {}, Database: {}", 
                   config.getUrl(), config.getDatabase());
    }
    
    /**
     * InfluxDB 3.x SQL API를 사용한 데이터 조회
     */
    public Mono<List<Map<String, Object>>> queryBySql(String sql) {
        Map<String, Object> requestBody = Map.of(
            "query", sql,
            "format", "json"
        );
        
        logger.debug("InfluxDB SQL 쿼리 실행: {}", sql);
        
        return sqlClient.post()
            .uri(config.getSqlApiUrl())
            .bodyValue(requestBody)
            .retrieve()
            .bodyToMono(String.class)  // bodyToString() 대신 bodyToMono(String.class) 사용
            .timeout(Duration.ofMillis(config.getQueryTimeout()))
            .map(this::parseJsonResponse)
            .doOnSuccess(result -> logger.debug("SQL 쿼리 성공: {} rows", result.size()))
            .doOnError(error -> logger.error("SQL 쿼리 실행 실패 [{}]: {}", sql, error.getMessage()))
            .onErrorReturn(Collections.emptyList());
    }
    
    /**
     * Line Protocol을 사용한 단일 데이터 입력
     */
    public Mono<Boolean> writeLineProtocol(String lineProtocol) {
        return writeClient.post()
            .uri(config.getWriteApiUrl())
            .bodyValue(lineProtocol)
            .retrieve()
            .bodyToMono(String.class)  // bodyToString() 대신 bodyToMono(String.class) 사용
            .timeout(Duration.ofMillis(config.getWriteTimeout()))
            .map(response -> true)
            .doOnSuccess(result -> logger.debug("데이터 입력 성공: {}", lineProtocol))
            .doOnError(error -> logger.error("데이터 입력 실패: {}", error.getMessage()))
            .onErrorReturn(false);
    }
    
    /**
     * 구조화된 데이터 입력
     */
    public Mono<Boolean> writeData(String measurement, Map<String, String> tags, 
                                  Map<String, Object> fields, Instant timestamp) {
        String lineProtocol = buildLineProtocol(measurement, tags, fields, timestamp);
        return writeLineProtocol(lineProtocol);
    }
    
    /**
     * 배치 데이터 입력
     */
    public Mono<Boolean> writeBatchData(List<String> lineProtocols) {
        if (lineProtocols.isEmpty()) {
            return Mono.just(true);
        }
        
        String batchData = String.join("\n", lineProtocols);
        
        return writeClient.post()
            .uri(config.getWriteApiUrl())
            .bodyValue(batchData)
            .retrieve()
            .bodyToMono(String.class)  // bodyToString() 대신 bodyToMono(String.class) 사용
            .timeout(Duration.ofMillis(config.getWriteTimeout() * 2))
            .map(response -> true)
            .doOnSuccess(result -> logger.debug("배치 데이터 입력 성공: {} lines", lineProtocols.size()))
            .doOnError(error -> logger.error("배치 데이터 입력 실패: {}", error.getMessage()))
            .onErrorReturn(false);
    }
    
    /**
     * 최근 센서 데이터 조회
     */
    public Mono<List<Map<String, Object>>> getRecentSensorData(String stationId, int limit) {
        String sql = String.format("""
            SELECT time, station_id, temperature, humidity, pressure, status
            FROM %s 
            WHERE station_id = '%s'
            ORDER BY time DESC 
            LIMIT %d
            """, config.getDatabase(), stationId, limit);
        
        return queryBySql(sql);
    }
    
    /**
     * 시간 범위별 센서 데이터 조회
     */
    public Mono<List<Map<String, Object>>> getSensorDataByTimeRange(String stationId, 
                                                                   Instant startTime, 
                                                                   Instant endTime) {
        String sql = String.format("""
            SELECT time, station_id, temperature, humidity, pressure, status
            FROM %s 
            WHERE station_id = '%s' 
                AND time >= '%s' 
                AND time <= '%s'
            ORDER BY time ASC
            """, config.getDatabase(), stationId, 
            formatTimestamp(startTime), formatTimestamp(endTime));
        
        return queryBySql(sql);
    }
    
    /**
     * 테이블 목록 조회
     */
    public Mono<List<Map<String, Object>>> getTables() {
        String sql = "SHOW TABLES";
        return queryBySql(sql);
    }
    
    /**
     * InfluxDB 3.x 연결 상태 확인
     */
    public Mono<Boolean> checkConnection() {
        return sqlClient.get()
            .uri(config.getHealthApiUrl())
            .retrieve()
            .bodyToMono(String.class)  // bodyToString() 대신 bodyToMono(String.class) 사용
            .timeout(Duration.ofSeconds(5))
            .map(response -> {
                // InfluxDB 3.x health response 확인
                return response.contains("pass") || 
                       response.contains("healthy") || 
                       response.contains("ok") ||
                       response.length() > 0; // 응답이 있으면 연결됨
            })
            .doOnSuccess(result -> logger.info("InfluxDB 3.x 연결 상태: {}", result ? "정상" : "실패"))
            .doOnError(error -> logger.error("InfluxDB 3.x 연결 확인 실패: {}", error.getMessage()))
            .onErrorReturn(false);
    }
    
    /**
     * InfluxDB 3.x 버전 정보 조회
     */
    public Mono<Map<String, Object>> getVersionInfo() {
        String sql = "SELECT version() as version";
        
        return queryBySql(sql)
            .map(result -> {
                if (!result.isEmpty()) {
                    return result.get(0);
                }
                return Map.of("version", "InfluxDB 3.x", "status", "connected");
            });
    }
    
    /**
     * Line Protocol 문자열 생성
     */
    private String buildLineProtocol(String measurement, Map<String, String> tags, 
                                   Map<String, Object> fields, Instant timestamp) {
        StringBuilder sb = new StringBuilder();
        sb.append(escapeValue(measurement));
        
        // 태그 추가
        if (tags != null && !tags.isEmpty()) {
            for (Map.Entry<String, String> tag : tags.entrySet()) {
                sb.append(",")
                  .append(escapeKey(tag.getKey()))
                  .append("=")
                  .append(escapeValue(tag.getValue()));
            }
        }
        
        sb.append(" ");
        
        // 필드 추가
        if (fields != null && !fields.isEmpty()) {
            List<String> fieldStrings = new ArrayList<>();
            for (Map.Entry<String, Object> field : fields.entrySet()) {
                String key = escapeKey(field.getKey());
                String value = formatFieldValue(field.getValue());
                fieldStrings.add(key + "=" + value);
            }
            sb.append(String.join(",", fieldStrings));
        }
        
        // 타임스탬프 추가
        if (timestamp != null) {
            sb.append(" ").append(timestamp.toEpochMilli() * 1_000_000L); // 나노초 변환
        }
        
        return sb.toString();
    }
    
    /**
     * 필드 값 포맷팅
     */
    private String formatFieldValue(Object value) {
        if (value == null) {
            return "\"\"";
        } else if (value instanceof String) {
            return "\"" + escapeStringValue((String) value) + "\"";
        } else if (value instanceof Boolean) {
            return value.toString();
        } else if (value instanceof Integer || value instanceof Long) {
            return value + "i"; // 정수 타입 명시
        } else {
            return String.valueOf(value); // float/double
        }
    }
    
    /**
     * 키 이스케이프 처리
     */
    private String escapeKey(String key) {
        if (key == null) return "";
        return key.replace(" ", "\\ ")
                 .replace(",", "\\,")
                 .replace("=", "\\=");
    }
    
    /**
     * 값 이스케이프 처리
     */
    private String escapeValue(String value) {
        if (value == null) return "";
        return value.replace(" ", "\\ ")
                   .replace(",", "\\,")
                   .replace("=", "\\=");
    }
    
    /**
     * 문자열 값 이스케이프 처리
     */
    private String escapeStringValue(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\")
                   .replace("\"", "\\\"");
    }
    
    /**
     * 타임스탬프 포맷팅
     */
    private String formatTimestamp(Instant timestamp) {
        return timestamp.toString();
    }
    
    /**
     * JSON 응답 파싱
     */
    private List<Map<String, Object>> parseJsonResponse(String jsonResponse) {
        try {
            if (jsonResponse == null || jsonResponse.trim().isEmpty()) {
                return Collections.emptyList();
            }
            
            JsonNode rootNode = objectMapper.readTree(jsonResponse);
            List<Map<String, Object>> result = new ArrayList<>();
            
            if (rootNode.isArray()) {
                // 배열 형태의 응답
                for (JsonNode node : rootNode) {
                    Map<String, Object> row = objectMapper.convertValue(node, Map.class);
                    result.add(row);
                }
            } else if (rootNode.isObject()) {
                // 단일 객체 응답
                Map<String, Object> row = objectMapper.convertValue(rootNode, Map.class);
                result.add(row);
            }
            
            logger.debug("JSON 파싱 완료: {} rows", result.size());
            return result;
            
        } catch (Exception e) {
            logger.error("JSON 응답 파싱 중 오류 발생: {}", e.getMessage());
            logger.debug("파싱 실패한 JSON: {}", jsonResponse);
            return Collections.emptyList();
        }
    }
}