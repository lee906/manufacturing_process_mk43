import React from 'react';

const InventoryTable = () => {
  const inventory = [
    {
      id: 'MAT_001',
      name: '시트 어셈블리',
      location: '창고A-01',
      currentStock: 45,
      safetyStock: 30,
      consumptionRate: '8개/시간',
      estimatedRunOut: '5.6시간',
      status: '정상',
      lastSupply: '14:30 예정'
    },
    {
      id: 'MAT_002',
      name: '백 프레임',
      location: '창고A-02',
      currentStock: 28,
      safetyStock: 35,
      consumptionRate: '10개/시간',
      estimatedRunOut: '2.8시간',
      status: '부족',
      lastSupply: '15:00 예정'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case '정상': return 'status-green';
      case '주의': return 'status-yellow';
      case '부족': return 'status-orange';
      case '긴급': return 'status-red';
      default: return 'status-gray';
    }
  };

  const getSupplyColor = (supply) => {
    if (supply.includes('완료')) return 'status-green';
    if (supply.includes('지연')) return 'status-red';
    return 'status-blue';
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
          {inventory.map((item) => (
            <tr key={item.id}>
              <th>{item.id}</th>
              <td>{item.name}</td>
              <td>{item.location}</td>
              <td>{item.currentStock}개</td>
              <td>{item.safetyStock}개</td>
              <td>{item.consumptionRate}</td>
              <td>{item.estimatedRunOut}</td>
              <td>
                <span className={`status ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </td>
              <td>
                <span className={`status ${getSupplyColor(item.lastSupply)}`}>
                  {item.lastSupply}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 범례 */}
      <div className="mt-3">
        <small className="text-muted">
          <strong>상태 기준:</strong> 
          <span className="status status-green ms-1">정상</span> 안전재고 이상 | 
          <span className="status status-yellow ms-1">주의</span> 안전재고 근접 | 
          <span className="status status-orange ms-1">부족</span> 안전재고 미만 | 
          <span className="status status-red ms-1">긴급</span> 2시간 내 소진
        </small>
      </div>
    </div>
  );
};

export default InventoryTable;