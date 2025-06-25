import React, { useState, useEffect } from 'react';

const getStatus = (quantity, safetyStock) => {
  if (quantity === 0) return { label: '품절', color: 'status-red' };
  if (quantity <= safetyStock) return { label: '부족', color: 'status-orange' };
  if (quantity <= safetyStock * 1.5) return { label: '주의', color: 'status-yellow' };
  return { label: '정상', color: 'status-green' };
};

const InventoryTable = () => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    setItems([
      {
        id: 1,
        itemCode: 'A1001',
        itemName: '엔진 블록',
        quantity: 10,
        safetyStock: 20,
        location: '창고1',
        supplier: '현대제철',
        receivedDate: '2025-06-10'
      },
      {
        id: 2,
        itemCode: 'B2002',
        itemName: '변속기',
        quantity: 30,
        safetyStock: 10,
        location: '창고2',
        supplier: '만도',
        receivedDate: '2025-06-15'
      },
      {
        id: 3,
        itemCode: 'C3003',
        itemName: '도어 패널',
        quantity: 120,
        safetyStock: 50,
        location: '창고3',
        supplier: '한온시스템',
        receivedDate: '2025-06-12'
      },
      {
        id: 4,
        itemCode: 'D4004',
        itemName: '시트 프레임',
        quantity: 0,
        safetyStock: 15,
        location: '창고4',
        supplier: '세종공업',
        receivedDate: '2025-06-18'
      }
    ]);
  }, []);

  return (
    <div className="table-responsive">
      <table className="table">
        <thead>
          <tr>
            <th><span class="flag flag-xs flag-country-us"></span></th>
            <th className="text-nowrap">품목 코드</th>
            <th className="text-nowrap">품 목 명</th>
            <th className="text-nowrap">현재 재고 수량</th>
            <th className="text-nowrap">평균 재고 수량</th>
            <th className="text-nowrap">창고 위치</th>
            <th className="text-nowrap">협력 업체</th>
            <th className="text-nowrap">입고 일자</th>
            <th className="text-nowrap">실시간 재고 상태</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => {
            const status = getStatus(item.quantity, item.safetyStock);
            return (
              <tr key={item.id}>
                <th>{idx + 1}</th>
                <td>{item.itemCode}</td>
                <td>{item.itemName}</td>
                <td>{item.quantity}</td>
                <td>{item.safetyStock}</td>
                <td>{item.location}</td>
                <td>{item.supplier}</td>
                <td>{item.receivedDate}</td>
                <td>
                  <span className={`status ${status.color}`}>{status.label}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryTable;