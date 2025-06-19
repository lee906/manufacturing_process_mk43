import { useEffect, useRef } from 'react'
import ApexCharts from 'apexcharts'

const FPYStatus = () => {
  const chartRef = useRef(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      const chartElement = document.getElementById('chart-fpy-status')
      
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
        series: [95.3, 4.7], // FPY 95.3% 가정
        labels: ["FPY", "불량"],
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
                  label: 'FPY',
                  formatter: function (w) {
                    return '95.3%';
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
                return '일발 양품: ' + val + '%';
              }
              return '불량: ' + val + '%';
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
    <div id="chart-fpy-status" className="position-relative"></div>
  );
};

export default FPYStatus;