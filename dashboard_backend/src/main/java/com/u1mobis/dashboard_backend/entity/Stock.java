package com.u1mobis.dashboard_backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;

@Entity
@Table(name = "stock")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Stock {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long stockId;

    private String stockCode;
    private String stockName;
    private int currentStock;
    private int safetyStock;
    private String stockLocation;
    private String partnerCompany;
    private LocalDate inboundDate;
    private String stockState;

    // 네트워크 기본 지식 배워오기 - get, post

// 엔티티를 생성을 하고 백엔드를 실행을 시키면 데이터베이스에 자동으로 테이블이 생성
// 테이블이 생성되었는지 확인 - 원격 접속해서 확인 못하겠으면 준태몬
// 테이블에 재고 값을 임의로 넣기 - 못하겠으면 준태몬, 현대 차 5종이 필요한 부품들 모두 뽑아서 + (컬럼)을 gpt에 넣고 100개씩 넣는 쿼리문 알려줘.

// 그 다음 백엔드 레포지토리 추가 (스프링 부트 레포지토리 알아보기)
// 백엔드 컨트롤러(라우터) 및 서비스(로직) 추가


// 프론트엔드에 더미데이터가 아닌 데이터베이스에 있는 재고 값이 뜨게 수정 

// 레포지토리 -> 서비스-> 컨트롤러 
}
