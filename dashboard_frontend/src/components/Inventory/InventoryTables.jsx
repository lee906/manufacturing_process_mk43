import React, { useEffect, useState } from 'react';
import axios from 'axios';

const InventoryTables = () => {
  const [inventory, setInventory] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8080/api/stocks')
      .then(response => setInventory(response.data))
      .catch(error => console.error("재고 데이터 불러오기 실패:", error));
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case '정상': return 'status-green';
      case '주의': return 'status-yellow';
      case '부족': return 'status-orange';
      case '긴급': return 'status-red';
      default: return 'status-gray';
    }
  };

  const getSupplyColor = (date) => {
    // 날짜가 오늘 이후면 "예정", 오늘이면 "완료", 과거면 "지연"
    const today = new Date();
    const inbound = new Date(date);
    if (inbound > today) return 'status-blue';
    if (inbound.toDateString() === today.toDateString()) return 'status-green';
    return 'status-red';
  };

  return (
    <div className="table-responsive">
      <table className="table table-vcenter">
        <thead>
          <tr>
            <th>자재ID</th>
            <th className="text-nowrap">자재명</th>
            <th className="text-nowrap">위치</th>
            <th className="text-nowrap">현재재고</th>
            <th className="text-nowrap">안전재고</th>
            <th className="text-nowrap">소모율</th>
            <th className="text-nowrap">예상소진</th>
            <th className="text-nowrap">상태</th>
            <th className="text-nowrap">공급현황</th>
          </tr>
        </thead>
        <tbody>
          {inventory.map((item) => {
            const consumptionRate = '8개/시간'; // 추후 DB에서 가져오게 수정 가능
            const estimatedRunOut = `${(item.currentStock / 8).toFixed(1)}시간`; // 가정
            return (
              <tr key={item.stockCode}>
                <th>{item.stockCode}</th>
                <td>{item.stockName}</td>
                <td>{item.stockLocation}</td>
                <td>{item.currentStock}개</td>
                <td>{item.safetyStock}개</td>
                <td>{consumptionRate}</td>
                <td>{estimatedRunOut}</td>
                <td>
                  <span className={`status ${getStatusColor(item.stockState)}`}>
                    {item.stockState}
                  </span>
                </td>
                <td>
                  <span className={`status ${getSupplyColor(item.inboundDate)}`}>
                    {new Date(item.inboundDate).toLocaleDateString()} 예정
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* 범례 */}
      <div className="mt-3">
        <small className="text-muted">
          <strong>상태 기준:</strong> 
          <span className="status status-green ms-1">정상</span> 안전재고 이상 | 
          <span className="status status-yellow ms-1">주의</span> 근접 | 
          <span className="status status-orange ms-1">부족</span> 미만 | 
          <span className="status status-red ms-1">긴급</span> 2시간 내 소진
        </small>
      </div>
    </div>
  );
};

export default InventoryTables;
