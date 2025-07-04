import React, { useEffect, useRef, useState } from 'react';
import ApexCharts from 'apexcharts';
import axios from 'axios';

const SummaryCard = () => {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    labels: [],
    series: []
  });

  useEffect(() => {
    axios.get('http://localhost:8080/api/stocks')
      .then((response) => {
        const data = response.data;

        // 차트에 사용할 항목 필터링: 차량 종류 기준 (아반떼, 소나타, 그랜저, 아이오닉, 스포티지)
        const carTypes = ['아반떼', '소나타', '그랜저', '아이오닉', '스포티지'];
        const filtered = data.filter(item => carTypes.includes(item.stockName));

        const labels = filtered.map(item => item.stockName);
        const series = filtered.map(item => item.currentStock);

        setChartData({ labels, series });
      })
      .catch((error) => console.error('Summary 데이터 불러오기 실패:', error));
  }, []);

  useEffect(() => {
    if (!chartRef.current || chartData.series.length === 0) return;

    const chart = new ApexCharts(chartRef.current, {
      chart: {
        type: 'donut',
        fontFamily: 'inherit',
        height: 260,
        sparkline: { enabled: true },
        animations: { enabled: false }
      },
      series: chartData.series,
      labels: chartData.labels,
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
        '#000000', // 아이오닉 (검정)
        '#ef4444'  // 스포티지 (빨강)
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
              show: false
            }
          }
        }
      }
    });

    chart.render();
    return () => chart.destroy();
  }, [chartData]);

  return (
    <div style={{ position: 'relative', paddingTop: '2rem' }}>
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

      <div id="chart-demo-pie" ref={chartRef} />
    </div>
  );
};

export default SummaryCard;
