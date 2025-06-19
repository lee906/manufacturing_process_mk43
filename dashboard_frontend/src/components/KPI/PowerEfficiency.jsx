import { useEffect, useRef } from 'react'
import ApexCharts from 'apexcharts'

const PowerEfficiency = () => {
  const chartRef = useRef(null)

  useEffect(() => {
    // DOM 요소가 준비될 때까지 기다림
    const timer = setTimeout(() => {
      const chartElement = document.getElementById('chart-power-efficiency')
      
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
        series: [73.5, 26.5],
        labels: ["전력효율", "손실"],
        colors: ['#28a745', '#e9ecef'],
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
                  color: '#28a745',
                  fontSize: '18px',
                  fontWeight: 600,
                  label: '전력효율',
                  formatter: function (w) {
                    return '73.5%';
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
                return '입력전력: 1,360kW<br/>출력전력: 1,000kW<br/>손실전력: 360kW<br/>전력효율: ' + val + '%';
              }
              return '손실률: ' + val + '%';
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
        <h3 className="card-title">전력 효율</h3>
        <div id="chart-power-efficiency" className="position-relative"></div>
        <div className="mt-3">
          <div className="row text-center">
            <div className="col-4">
              <div className="text-muted small">입력전력</div>
              <div className="h4 text-success">1,360kW</div>
            </div>
            <div className="col-4">
              <div className="text-muted small">출력전력</div>
              <div className="h4 text-success">1,000kW</div>
            </div>
            <div className="col-4">
              <div className="text-muted small">손실전력</div>
              <div className="h4 text-danger">360kW</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PowerEfficiency;