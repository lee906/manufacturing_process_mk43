package com.u1mobis.dashboard_backend.service;

import com.u1mobis.dashboard_backend.entity.Stock;
import com.u1mobis.dashboard_backend.repository.StockRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class StockService {

    private final StockRepository stockRepository;

    public StockService(StockRepository stockRepository) {
        this.stockRepository = stockRepository;
    }

    // 🔍 전체 재고 조회
    public List<Stock> getAllStocks() {
        return stockRepository.findAll();
    }

    // 🔍 단일 재고 조회
    public Optional<Stock> getStockById(Long id) {
        return stockRepository.findById(id);
    }

    // ➕ 재고 추가
    public Stock createStock(Stock stock) {
        return stockRepository.save(stock);
    }

    // ✏️ 재고 수정
    public Stock updateStock(Long id, Stock updatedStock) {
        return stockRepository.findById(id)
                .map(stock -> {
                    stock.setStockCode(updatedStock.getStockCode());
                    stock.setStockName(updatedStock.getStockName());
                    stock.setCurrentStock(updatedStock.getCurrentStock());
                    stock.setSafetyStock(updatedStock.getSafetyStock());
                    stock.setStockLocation(updatedStock.getStockLocation());
                    stock.setPartnerCompany(updatedStock.getPartnerCompany());
                    stock.setInboundDate(updatedStock.getInboundDate());
                    stock.setStockState(updatedStock.getStockState());
                    return stockRepository.save(stock);
                })
                .orElseThrow(() -> new IllegalArgumentException("재고 ID 없음: " + id));
    }

    // ❌ 재고 삭제
    public void deleteStock(Long id) {
        if (!stockRepository.existsById(id)) {
            throw new IllegalArgumentException("삭제 실패: ID " + id + " 존재하지 않음");
        }
        stockRepository.deleteById(id);
    }
}
