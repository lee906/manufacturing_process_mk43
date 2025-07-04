import React, { useEffect, useRef, useState } from 'react';
import ApexCharts from 'apexcharts';
import axios from 'axios';

const ChartInventory = () => {
  const chartRef = useRef(null);
  const [series, setSeries] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8080/api/stocks/chart')
      .then(response => {
        const chartData = response.data.map(item => ({
          name: item.carModel,
          data: item.monthlyStock
        }));
        setSeries(chartData);
      })
      .catch(error => {
        console.error("차트 데이터 불러오기 실패:", error);
      });
  }, []);

  useEffect(() => {
    if (!chartRef.current || series.length === 0) return;

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
      series: series,
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
        '#facc15', // 아반떼
        '#10b981', // 소나타
        '#3b82f6', // 그랜저
        '#000000', // 아이오닉
        '#ef4444', // 스포티지
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
  }, [series]);

  return (
    <div className="card">
      <div className="card-body">
        <div ref={chartRef} className="position-relative" id="chart-demo-line"></div>
      </div>
    </div>
  );
};

export default ChartInventory;
