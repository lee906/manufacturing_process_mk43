package com.u1mobis.dashboard_backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.HttpHeaders;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Primary;

import java.time.Duration;

@Configuration
@ConfigurationProperties(prefix = "influxdb")
public class InfluxDB3Config {
    
    // 기본 연결 설정
    @Value("${influxdb.url}")
    private String url;
    
    @Value("${influxdb.token}")
    private String token;
    
    @Value("${influxdb.database}")
    private String database;
    
    // API 엔드포인트 설정
    @Value("${influxdb.api.sql.endpoint:/api/v3/query/sql}")
    private String sqlEndpoint;
    
    @Value("${influxdb.api.write.endpoint:/api/v2/write}")
    private String writeEndpoint;
    
    @Value("${influxdb.api.health.endpoint:/health}")
    private String healthEndpoint;
    
    // 타임아웃 설정
    @Value("${influxdb.connection-timeout:30000}")
    private int connectionTimeout;
    
    @Value("${influxdb.read-timeout:60000}")
    private int readTimeout;
    
    @Value("${influxdb.write-timeout:30000}")
    private int writeTimeout;
    
    // 배치 처리 설정
    @Value("${influxdb.batch.enabled:true}")
    private boolean batchEnabled;
    
    @Value("${influxdb.batch.size:1000}")
    private int batchSize;
    
    @Value("${influxdb.batch.flush-interval:5000}")
    private int batchFlushInterval;
    
    @Value("${influxdb.batch.max-retries:3}")
    private int batchMaxRetries;
    
    // 압축 설정
    @Value("${influxdb.compression.enabled:true}")
    private boolean compressionEnabled;
    
    @Value("${influxdb.compression.type:gzip}")
    private String compressionType;
    
    // 쿼리 설정
    @Value("${influxdb.query.max-rows:10000}")
    private int queryMaxRows;
    
    @Value("${influxdb.query.timeout:30000}")
    private int queryTimeout;
    
    @Value("${influxdb.query.cache.enabled:true}")
    private boolean queryCacheEnabled;
    
    /**
     * InfluxDB 3.x SQL 쿼리용 WebClient
     */
    @Bean
    @Primary
    public WebClient influxDb3SqlClient() {
        return WebClient.builder()
            .baseUrl(url)
            .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
            .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
            .defaultHeader(HttpHeaders.ACCEPT, "application/json")
            .defaultHeader("User-Agent", "dashboard-backend-v3/1.0")
            .codecs(configurer -> {
                configurer.defaultCodecs().maxInMemorySize(32 * 1024 * 1024); // 32MB
            })
            .build();
    }
    
    /**
     * InfluxDB 3.x 데이터 쓰기용 WebClient (v2 API 호환)
     */
    @Bean
    public WebClient influxDb3WriteClient() {
        return WebClient.builder()
            .baseUrl(url)
            .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
            .defaultHeader(HttpHeaders.CONTENT_TYPE, "text/plain; charset=utf-8")
            .defaultHeader("User-Agent", "dashboard-backend-v3/1.0")
            .codecs(configurer -> {
                configurer.defaultCodecs().maxInMemorySize(64 * 1024 * 1024); // 64MB for batch
            })
            .build();
    }
    
    /**
     * Write API 전체 URL 생성
     */
    public String getWriteApiUrl() {
        return writeEndpoint + "?bucket=" + database;
    }
    
    /**
     * SQL API 전체 URL 생성
     */
    public String getSqlApiUrl() {
        return sqlEndpoint;
    }
    
    /**
     * Health check URL 생성
     */
    public String getHealthApiUrl() {
        return healthEndpoint;
    }
    
    // Getter 메소드들
    public String getUrl() { return url; }
    public String getToken() { return token; }
    public String getDatabase() { return database; }
    public String getSqlEndpoint() { return sqlEndpoint; }
    public String getWriteEndpoint() { return writeEndpoint; }
    public String getHealthEndpoint() { return healthEndpoint; }
    public int getConnectionTimeout() { return connectionTimeout; }
    public int getReadTimeout() { return readTimeout; }
    public int getWriteTimeout() { return writeTimeout; }
    public boolean isBatchEnabled() { return batchEnabled; }
    public int getBatchSize() { return batchSize; }
    public int getBatchFlushInterval() { return batchFlushInterval; }
    public int getBatchMaxRetries() { return batchMaxRetries; }
    public boolean isCompressionEnabled() { return compressionEnabled; }
    public String getCompressionType() { return compressionType; }
    public int getQueryMaxRows() { return queryMaxRows; }
    public int getQueryTimeout() { return queryTimeout; }
    public boolean isQueryCacheEnabled() { return queryCacheEnabled; }
    
    // Setter 메소드들 (ConfigurationProperties용)
    public void setUrl(String url) { this.url = url; }
    public void setToken(String token) { this.token = token; }
    public void setDatabase(String database) { this.database = database; }
    public void setConnectionTimeout(int connectionTimeout) { this.connectionTimeout = connectionTimeout; }
    public void setReadTimeout(int readTimeout) { this.readTimeout = readTimeout; }
    public void setWriteTimeout(int writeTimeout) { this.writeTimeout = writeTimeout; }
    public void setBatchEnabled(boolean batchEnabled) { this.batchEnabled = batchEnabled; }
    public void setBatchSize(int batchSize) { this.batchSize = batchSize; }
    public void setBatchFlushInterval(int batchFlushInterval) { this.batchFlushInterval = batchFlushInterval; }
    public void setBatchMaxRetries(int batchMaxRetries) { this.batchMaxRetries = batchMaxRetries; }
    public void setCompressionEnabled(boolean compressionEnabled) { this.compressionEnabled = compressionEnabled; }
    public void setCompressionType(String compressionType) { this.compressionType = compressionType; }
    public void setQueryMaxRows(int queryMaxRows) { this.queryMaxRows = queryMaxRows; }
    public void setQueryTimeout(int queryTimeout) { this.queryTimeout = queryTimeout; }
    public void setQueryCacheEnabled(boolean queryCacheEnabled) { this.queryCacheEnabled = queryCacheEnabled; }
}