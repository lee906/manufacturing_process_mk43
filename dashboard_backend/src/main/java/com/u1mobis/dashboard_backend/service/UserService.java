package com.u1mobis.dashboard_backend.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.u1mobis.dashboard_backend.dto.UserDTO;
import com.u1mobis.dashboard_backend.entity.User;
import com.u1mobis.dashboard_backend.repository.UserRepository;

@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private PasswordEncoder passwordEncoder;

    public boolean register(UserDTO userDTO) {
        if (userRepository.findByUserName(userDTO.getUsername()) != null) {
            return false; // 이미 존재
        }
        User user = new User(null, userDTO.getUsername(), passwordEncoder.encode(userDTO.getPassword()));
        userRepository.save(user);
        return true;
    }

    public boolean login(UserDTO userDTO) {
        User user = userRepository.findByUserName(userDTO.getUsername());
        if (user == null) return false;
        return passwordEncoder.matches(userDTO.getPassword(), user.getPassword());
    }
}