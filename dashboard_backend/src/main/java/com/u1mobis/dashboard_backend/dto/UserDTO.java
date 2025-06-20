package com.u1mobis.dashboard_backend.dto;

public class UserDTO {
    private String username;
    private String password;

    // 생성자, getter, setter
    public UserDTO() {}

    public UserDTO(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
