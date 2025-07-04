package com.u1mobis.dashboard_backend.repository;

import com.u1mobis.dashboard_backend.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface StockRepository extends JpaRepository<Stock, Long> {
    Stock findByStockCode(String stockCode);
}
