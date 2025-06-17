import { useEffect, useRef } from 'react'
import ApexCharts from 'apexcharts'

const ProductionStatus = () => {
  const chartRef = useRef(null)

  useEffect(() => {
    // DOM 요소가 준비될 때까지 기다림
    const timer = setTimeout(() => {
      const chartElement = document.getElementById('chart-production-status')
      
      if (!chartElement) {
        console.error("Chart element not found")
        return
      }

      const options = {
        chart: {
          type: "donut",
          fontFamily: 'inherit',
          height: 200,
          animations: {
            enabled: true
          },
        },
        series: [61.2, 38.8],
        labels: ["OEE", "미달성"],
        colors: ['#206bc4', '#e9ecef'],
        legend: {
          show: false
        },
        plotOptions: {
          pie: {
            donut: {
              size: '65%',
              labels: {
                show: true,
                total: {
                  show: true,
                  color: '#206bc4',
                  fontSize: '18px',
                  fontWeight: 600,
                  label: 'OEE',
                  formatter: function (w) {
                    return '61.2%';
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: true,
          y: {
            formatter: function (val, opts) {
              if (opts.seriesIndex === 0) {
                return '가동률: 85%<br/>성능률: 78%<br/>품질률: 92%<br/>OEE: ' + val + '%';
              }
              return val + '%';
            }
          }
        },
        dataLabels: {
          enabled: false
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              height: 180
            },
            legend: {
              fontSize: '10px'
            }
          }
        }]
      };

      try {
        if (chartRef.current) {
          chartRef.current.destroy();
        }
        
        chartRef.current = new ApexCharts(chartElement, options);
        chartRef.current.render();
      } catch (error) {
        console.error("Chart rendering error:", error);
      }
    }, 100);

    return () => {
      clearTimeout(timer);
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, []);

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="card-title">생산 현황</h3>
        <div id="chart-production-status" className="position-relative"></div>
        <div className="mt-3">
          <div className="row text-center">
            <div className="col-4">
              <div className="text-muted small">가동률</div>
              <div className="h4 text-primary">85%</div>
            </div>
            <div className="col-4">
              <div className="text-muted small">성능률</div>
              <div className="h4 text-primary">78%</div>
            </div>
            <div className="col-4">
              <div className="text-muted small">품질률</div>
              <div className="h4 text-primary">92%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductionStatus;