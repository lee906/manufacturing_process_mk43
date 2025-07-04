import React, { useState, useEffect } from 'react';
import axios from 'axios';

const getStatus = (quantity, safetyStock) => {
  if (quantity === 0) return { label: '품절', color: 'status-red' };
  if (quantity <= safetyStock) return { label: '부족', color: 'status-orange' };
  if (quantity <= safetyStock * 1.5) return { label: '주의', color: 'status-yellow' };
  return { label: '정상', color: 'status-green' };
};

const InventoryTable = () => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8080/api/stocks') // 포트 맞게 수정
      .then(response => setItems(response.data))
      .catch(error => console.error('재고 불러오기 실패:', error));
  }, []);

  return (
    <div className="table-responsive">
      <table className="table">
        <thead>
          <tr>
            <th>#</th>
            <th>품목 코드</th>
            <th>품 목 명</th>
            <th>현재 재고 수량</th>
            <th>평균 재고 수량</th>
            <th>창고 위치</th>
            <th>협력 업체</th>
            <th>입고 일자</th>
            <th>재고 상태</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => {
            const status = getStatus(item.currentStock, item.safetyStock);
            return (
              <tr key={item.stockId}>
                <th>{idx + 1}</th>
                <td>{item.stockCode}</td>
                <td>{item.stockName}</td>
                <td>{item.currentStock}</td>
                <td>{item.safetyStock}</td>
                <td>{item.stockLocation}</td>
                <td>{item.partnerCompany}</td>
                <td>{item.inboundDate}</td>
                <td><span className={`status ${status.color}`}>{status.label}</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryTable;
