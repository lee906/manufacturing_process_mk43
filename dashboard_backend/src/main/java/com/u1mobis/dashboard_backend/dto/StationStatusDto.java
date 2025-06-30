package com.u1mobis.dashboard_backend.dto;

public class StationStatusDto {
    private String stationId;
    private String status;

    public StationStatusDto() {
    }

    public StationStatusDto(String stationId, String status) {
        this.stationId = stationId;
        this.status = status;
    }

    public String getStationId() {
        return stationId;
    }

    public void setStationId(String stationId) {
        this.stationId = stationId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
