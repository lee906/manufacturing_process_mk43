package com.u1mobis.dashboard_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED) // JPA 요구사항
@ToString(exclude = {"password"}) // 보안상 password 제외
@EqualsAndHashCode(onlyExplicitlyIncluded = true) // ID만으로 비교
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    @EqualsAndHashCode.Include // equals/hashCode에 ID만 포함
    private Long userId;

    @Column(name = "company_id", nullable = false)
    private Long companyId;

    @Column(name = "user_name", unique = true, nullable = false)
    private String userName;

    @Column(name = "password", nullable = false)
    private String password;

    // 비즈니스 로직에 필요한 생성자만 명시적으로 생성
    public User(Long companyId, String userName, String password) {
        this.companyId = companyId;
        this.userName = userName;
        this.password = password;
    }
}