import React, { useEffect, useRef } from 'react';
import ApexCharts from 'apexcharts';

const SummaryCard = () => {
  const chartRef = useRef(null);

  useEffect(() => {
    const randomData = Array.from({ length: 5 }, () => Math.floor(Math.random() * 100) + 1);

    const options = {
      chart: {
        type: 'donut',
        fontFamily: 'inherit',
        height: 260,
        sparkline: {
          enabled: true
        },
        animations: {
          enabled: false
        },
      },
      series: randomData,
      labels: ["아반떼", "소나타", "그랜저", "아이오닉", "스포티지"],
      tooltip: {
        theme: 'dark',
        fillSeriesColor: false
      },
      grid: {
        strokeDashArray: 4,
      },
      colors: [
        '#facc15', // 아반떼 (노랑)
        '#10b981', // 소나타 (초록)
        '#3b82f6', // 그랜저 (파랑)
        '#000000', // 아이오닉 (청록)
        '#ef4444', // 스포티지 (빨강)
      ],
      legend: {
        show: true,
        position: 'bottom',
        offsetY: 12,
        markers: {
          width: 10,
          height: 10,
          radius: 100,
        },
        itemMargin: {
          horizontal: 8,
          vertical: 8,
        },
      },
      plotOptions: {
        pie: {
          donut: {
            labels: {
              show: false // 가운데 텍스트는 숨김
            }
          }
        }
      }
    };

    const chart = new ApexCharts(chartRef.current, options);
    chart.render();

    return () => chart.destroy();
  }, []);

  return (
    <div style={{ position: 'relative', paddingTop: '2rem' }}>
      {/* 왼쪽 상단 텍스트 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        fontSize: '1.25rem',
        fontWeight: 'bold',
        color: '#1f2937'
      }}>
        발주
      </div>

      {/* 도넛 차트 */}
      <div id="chart-demo-pie" ref={chartRef} />
    </div>
  );
};

export default SummaryCard;
