import Factory2DTwin from "./Twin/Factory2DTwin";
import Navbar from "./Twin/Navabr";



const Factory2D = () => {

  return (
    <div className="row g-3">
      <div className="col-sm-6 col-lg-4">
        <div className="card">
          <div className="card-body" style={{ height: "50rem" }}>
            <Navbar />
            {/* 왼쪽 생산 목표 카드 */}
            
          </div>
        </div>
      </div>

      <div className="col-sm-6 col-lg-8">
        <div className="card">
          <div className="card-body" style={{ height: "50rem" }}>
            <Factory2DTwin />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Factory2D;
