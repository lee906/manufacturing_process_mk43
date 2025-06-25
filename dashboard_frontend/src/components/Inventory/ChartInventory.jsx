import React, { useEffect, useRef } from 'react';
import ApexCharts from 'apexcharts';

const ChartInventory = () => {
  const chartRef = useRef(null);

  // 12개의 랜덤 숫자 생성
  const getRandomData = (min, max) => {
    return Array.from({ length: 12 }, () =>
      Math.floor(Math.random() * (max - min + 1)) + min
    );
  };

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = new ApexCharts(chartRef.current, {
      chart: {
        type: "line",
        fontFamily: 'inherit',
        height: 300,
        parentHeightOffset: 0,
        toolbar: { show: false },
        animations: { enabled: false }
      },
      stroke: {
        width: 2,
        lineCap: "round",
        curve: "straight"
      },
      series: [
        {
          name: "아반떼",
          data: getRandomData(0, 100000)
        },
        {
          name: "소나타",
          data: getRandomData(0, 100000)
        },
        {
          name: "그랜저",
          data: getRandomData(0, 100000)
        },
        {
          name: "아이오닉",
          data: getRandomData(0, 100000)
        },
        {
          name: "스포티지",
          data: getRandomData(0, 100000)
        }
      ],
      tooltip: {
        theme: 'dark'
      },
      grid: {
        padding: {
          top: -20,
          right: 0,
          left: -4,
          bottom: -4
        },
        strokeDashArray: 4
      },
      xaxis: {
        categories: [
          '1월', '2월', '3월', '4월', '5월', '6월',
          '7월', '8월', '9월', '10월', '11월', '12월'
        ],
        labels: {
          padding: 0
        },
        tooltip: { enabled: false }
      },
      yaxis: {
        tickAmount: 8,
        min: 0,
        max: 100000,
        labels: {
          formatter: (val) => val.toLocaleString(),
          padding: 4
        }
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
          radius: 100
        },
        itemMargin: {
          horizontal: 8,
          vertical: 8
        }
      }
    });

    chart.render();

    return () => chart.destroy();
  }, []);

  return (
    <div className="card">
      <div className="card-body">
        <div ref={chartRef} className="position-relative" id="chart-demo-line"></div>
      </div>
    </div>
  );
};

export default ChartInventory;
