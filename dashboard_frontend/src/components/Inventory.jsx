import React from 'react';
import InventoryTable from './Inventory/InventoryTable';
import ChartInventory from './Inventory/ChartInventory';
import SummaryCard from './Inventory/SummaryCard'; // 새 컴포넌트 추가

const Inventory = () => {
  return (
    <div className="row row-deck row-cards">
      <div className="col-6">
        <div className="card-body">
          <ChartInventory />
        </div>
      </div>

      <div className="col-6">
        <div className="card">
          <div className="card-body" style={{ height: "10rem" }}>
            <SummaryCard />
          </div>
        </div>
      </div>

      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <InventoryTable />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Inventory;
