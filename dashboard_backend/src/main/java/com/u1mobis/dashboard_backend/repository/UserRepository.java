package com.u1mobis.dashboard_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.u1mobis.dashboard_backend.entity.User;

public interface UserRepository extends JpaRepository<User, Long> {
    User findByUsername(String username);
}