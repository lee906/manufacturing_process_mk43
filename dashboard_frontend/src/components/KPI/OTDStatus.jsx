import { useEffect, useRef } from 'react'
import ApexCharts from 'apexcharts'

const OTDStatus = () => {
  const chartRef = useRef(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      const chartElement = document.getElementById('chart-otd-status')
      
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
        series: [92.5, 7.5], // OTD 92.5% 가정
        labels: ["OTD", "지연"],
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
                  label: 'OTD',
                  formatter: function (w) {
                    return '92.5%';
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
                return '납기 준수: ' + val + '%';
              }
              return '납기 지연: ' + val + '%';
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
    <div id="chart-otd-status" className="position-relative"></div>
  );
};

export default OTDStatus;