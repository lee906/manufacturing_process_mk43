import React from 'react';
import ProductionStatus from './KPI/ProductionStatus';
import OTDStatus from './KPI/OTDStatus';
import FTYStatus from './KPI/FTYStatus';
import ProductionTarget from './KPI/ProductionTarget';
import HourlyProduction from './KPI/HourlyProduction';
import CycleTime from './KPI/CycleTime';
import RobotTable from './Robot/RobotTables';
import InventoryStatus from './Inventory/InventoryTables';
import Danger from './alarm/Danger';

const Dashboard = () => {
  return (
    <div className="row g-3">
      {/* 왼쪽 생산 목표 카드 */}
      <div className="col-sm-12 col-lg-4">
        <div className="card h-100" >
          <div className="card-body">
            <div className="row g-3">
              <div className="col-sm-12">
                <ProductionTarget />
              </div>
              <div className="col-6">
                <HourlyProduction />
              </div>
              <div className="col-6">
                <CycleTime />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 오른쪽 3*1 KPI 차트 카드 */}
      <div className="col-sm-12 col-lg-8">
        <div className="card h-100">
          <div className="card-body">
            <div className="row g-3">
              {/* OEE */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">OEE(설비 종합 효율)</h3>
                    <ProductionStatus />
                  </div>
                </div>
              </div>
              {/* OTD */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">OTD(정기납기율)</h3>
                    <OTDStatus />
                  </div>
                </div>
              </div>
              {/* FTY */}
              <div className="col-sm-12 col-md-4">
                <div className="card">
                  <div className="card-body">
                    <h3 className="card-title">FTY(일발양품률)</h3>
                    <FTYStatus />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h3 className="card-title">실시간 로봇 모니터링</h3>
            <RobotTable />
          </div>
        </div>
      </div>
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h3 className="card-title">재고 현황</h3>
            <InventoryStatus />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;