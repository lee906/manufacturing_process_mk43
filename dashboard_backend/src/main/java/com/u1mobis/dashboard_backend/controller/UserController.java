package com.u1mobis.dashboard_backend.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.u1mobis.dashboard_backend.dto.UserDTO;
import com.u1mobis.dashboard_backend.service.UserService;

@RestController
@RequestMapping("/api/user")
@CrossOrigin // 프론트엔드 연동시 필요
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public boolean register(@RequestBody UserDTO userDTO) {
        return userService.register(userDTO);
    }
    @PostMapping("/login")
    public boolean login(@RequestBody UserDTO userDTO) {
        return userService.login(userDTO);
    }
    // 추가적인 사용자 관련 API를 여기에 정의할 수 있습니다.    
}