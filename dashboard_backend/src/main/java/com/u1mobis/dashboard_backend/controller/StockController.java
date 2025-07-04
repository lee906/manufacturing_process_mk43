package com.u1mobis.dashboard_backend.controller;

import com.u1mobis.dashboard_backend.entity.Stock;
import com.u1mobis.dashboard_backend.service.StockService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/stocks")
@CrossOrigin(origins = "*") // 프론트엔드 접근 허용
public class StockController {

    private final StockService stockService;

    public StockController(StockService stockService) {
        this.stockService = stockService;
    }

    // 🔍 전체 재고 조회
    @GetMapping
    public List<Stock> getAllStocks() {
        return stockService.getAllStocks();
    }

    // 🔍 ID로 단일 재고 조회
    @GetMapping("/{id}")
    public ResponseEntity<Stock> getStockById(@PathVariable Long id) {
        return stockService.getStockById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // ➕ 재고 등록
    @PostMapping
    public ResponseEntity<Stock> createStock(@RequestBody Stock stock) {
        Stock created = stockService.createStock(stock);
        return ResponseEntity.ok(created);
    }

    // ✏️ 재고 수정
    @PutMapping("/{id}")
    public ResponseEntity<Stock> updateStock(@PathVariable Long id, @RequestBody Stock updatedStock) {
        try {
            Stock updated = stockService.updateStock(id, updatedStock);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // ❌ 재고 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteStock(@PathVariable Long id) {
        try {
            stockService.deleteStock(id);
            return ResponseEntity.noContent().build(); // 204 No Content
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build(); // 404 Not Found
        }
    }
}
