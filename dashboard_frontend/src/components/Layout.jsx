import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="page">
      {/* Header */}
      <div className="page-wrapper">
        <div className="page-header d-print-none">
          <div className="container-xl">
            <div className="row g-2 align-items-center">
              <div className="col">
                <div className="page-pretitle">디지털 트윈</div>
                <h2 className="page-title">자동차 의장공장 대시보드</h2>
              </div>
              <div className="col-auto ms-auto d-print-none">
                <div className="btn-list">
                  <span className="d-none d-sm-inline">
                    <span className="badge bg-green"></span> 시스템 정상
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="page-header d-print-none">
          <div className="container-xl">
            <div className="row g-2 align-items-center">
              <div className="col">
                <ul className="nav nav-tabs" data-bs-toggle="tabs">
                  <li className="nav-item">
                    <a href="#tabs-dashboard" className="nav-link active" data-bs-toggle="tab">
                      <svg className="icon me-2" width="24" height="24">
                        <use xlinkHref="#tabler-dashboard"></use>
                      </svg>
                      대시보드
                    </a>
                  </li>
                  <li className="nav-item">
                    <a href="#tabs-factory2d" className="nav-link" data-bs-toggle="tab">
                      <svg className="icon me-2" width="24" height="24">
                        <use xlinkHref="#tabler-map"></use>
                      </svg>
                      2D 공정도
                    </a>
                  </li>
                  <li className="nav-item">
                    <a href="#tabs-inventory" className="nav-link" data-bs-toggle="tab">
                      <svg className="icon me-2" width="24" height="24">
                        <use xlinkHref="#tabler-package"></use>
                      </svg>
                      재고관리
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="page-body">
          <div className="container-xl">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Layout;