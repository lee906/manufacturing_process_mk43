import React from 'react';

const ClickRobot = ({ isOpen, onClose, processName, onSelectRobot, position }) => {
  // 각 공정별 로봇 데이터 (예제)
  const robotData = {
    '도어탈거': [
      { id: 1, name: '로봇1', status: '운영중', type: 'KUKA' },
      { id: 2, name: '로봇2', status: '정지', type: 'ABB' },
      { id: 3, name: '로봇3', status: '점검중', type: 'Fanuc' }
    ],
    '와이어링': [
      { id: 4, name: '로봇1', status: '운영중', type: 'KUKA' },
      { id: 5, name: '로봇2', status: '운영중', type: 'Universal' },
      { id: 6, name: '로봇3', status: '정지', type: 'ABB' },
      { id: 7, name: '로봇4', status: '운영중', type: 'Fanuc' }
    ],
    '헤드라이너': [
      { id: 8, name: '로봇1', status: '운영중', type: 'ABB' },
      { id: 9, name: '로봇2', status: '점검중', type: 'KUKA' }
    ],
    '크래쉬패드': [
      { id: 10, name: '로봇1', status: '운영중', type: 'Fanuc' },
      { id: 11, name: '로봇2', status: '운영중', type: 'Universal' },
      { id: 12, name: '로봇3', status: '정지', type: 'KUKA' },
      { id: 13, name: '로봇4', status: '운영중', type: 'ABB' },
      { id: 14, name: '로봇5', status: '점검중', type: 'Fanuc' }
    ],
    '연료탱크': [
      { id: 15, name: '로봇1', status: '운영중', type: 'ABB' },
      { id: 16, name: '로봇2', status: '정지', type: 'KUKA' }
    ],
    '샤시메리지': [
      { id: 17, name: '로봇1', status: '운영중', type: 'Fanuc' },
      { id: 18, name: '로봇2', status: '운영중', type: 'Universal' },
      { id: 19, name: '로봇3', status: '점검중', type: 'ABB' },
      { id: 20, name: '로봇4', status: '운영중', type: 'KUKA' }
    ],
    '머플러': [
      { id: 21, name: '로봇1', status: '운영중', type: 'Universal' },
      { id: 22, name: '로봇2', status: '정지', type: 'Fanuc' }
    ],
    'FEM': [
      { id: 23, name: '로봇1', status: '운영중', type: 'KUKA' },
      { id: 24, name: '로봇2', status: '운영중', type: 'ABB' },
      { id: 25, name: '로봇3', status: '점검중', type: 'Fanuc' }
    ],
    '범퍼': [
      { id: 26, name: '로봇1', status: '운영중', type: 'Universal' },
      { id: 27, name: '로봇2', status: '정지', type: 'KUKA' }
    ],
    '글라스': [
      { id: 28, name: '로봇1', status: '운영중', type: 'ABB' },
      { id: 29, name: '로봇2', status: '운영중', type: 'Fanuc' },
      { id: 30, name: '로봇3', status: '점검중', type: 'Universal' }
    ],
    '시트': [
      { id: 31, name: '로봇1', status: '운영중', type: 'KUKA' },
      { id: 32, name: '로봇2', status: '정지', type: 'ABB' },
      { id: 33, name: '로봇3', status: '운영중', type: 'Fanuc' }
    ],
    '타이어': [
      { id: 34, name: '로봇1', status: '운영중', type: 'Universal' },
      { id: 35, name: '로봇2', status: '점검중', type: 'KUKA' }
    ],
    '수밀검사': [
      { id: 36, name: '로봇1', status: '운영중', type: 'ABB' },
      { id: 37, name: '로봇2', status: '운영중', type: 'Fanuc' },
      { id: 38, name: '로봇3', status: '정지', type: 'Universal' },
      { id: 39, name: '로봇4', status: '운영중', type: 'KUKA' }
    ],
    '헤드램프': [
      { id: 40, name: '로봇1', status: '운영중', type: 'Fanuc' },
      { id: 41, name: '로봇2', status: '점검중', type: 'ABB' }
    ],
    '휠 얼라이언트': [
      { id: 42, name: '로봇1', status: '운영중', type: 'KUKA' },
      { id: 43, name: '로봇2', status: '정지', type: 'Universal' },
      { id: 44, name: '로봇3', status: '운영중', type: 'Fanuc' }
    ]
  };

  // 현재 공정의 로봇 목록
  const robots = robotData[processName] || [];

  // 상태별 색상 정의
  const getStatusColor = (status) => {
    switch (status) {
      case '운영중': return '#4CAF50'; // 초록색
      case '정지': return '#f44336';   // 빨간색
      case '점검중': return '#ff9800';  // 오렌지색
      default: return '#9e9e9e';       // 회색
    }
  };

  // 로봇 선택 핸들러
  const handleRobotSelect = (robot) => {
    onSelectRobot(robot);
    onClose(); // 모달 닫기
  };

  if (!isOpen) return null;

  // 팝오버 위치 계산
  const popoverStyle = {
    position: 'fixed', // absolute에서 fixed로 변경
    left: position.x,
    top: position.y - 10, // 클릭 위치보다 10px 위에 표시 (20px에서 줄임)
    transform: 'translateX(-50%)', // 중앙 정렬
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '12px',
    minWidth: '280px',
    maxWidth: '400px',
    maxHeight: '300px',
    overflow: 'auto',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.1)',
    zIndex: 1000,
    fontSize: '14px'
  };

  return (
    <div style={popoverStyle}>
      {/* 팝오버 화살표 (아래쪽 꼬리) */}
      <div style={{
        position: 'absolute',
        bottom: '-8px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '8px solid transparent',
        borderRight: '8px solid transparent',
        borderTop: '8px solid white'
      }} />
      
      {/* 헤더 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px',
        paddingBottom: '8px',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <h3 style={{
          margin: 0,
          color: '#333',
          fontSize: '16px',
          fontWeight: 'bold'
        }}>
          {processName}
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#666',
            padding: '2px',
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#f0f0f0'}
          onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
        >
          ×
        </button>
      </div>

      {/* 로봇 목록 */}
      <div>
        <p style={{ 
          margin: '0 0 8px 0', 
          color: '#666', 
          fontSize: '12px' 
        }}>
          {robots.length}개 로봇
        </p>
        
        {robots.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '20px',
            color: '#999',
            fontSize: '14px'
          }}>
            등록된 로봇이 없습니다.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {robots.map((robot) => (
              <div
                key={robot.id}
                onClick={() => handleRobotSelect(robot)}
                style={{
                  padding: '10px',
                  border: '1px solid #e0e0e0',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  backgroundColor: '#fafafa'
                }}
                onMouseOver={(e) => {
                  e.target.style.borderColor = '#1976d2';
                  e.target.style.backgroundColor = '#f3f7fd';
                }}
                onMouseOut={(e) => {
                  e.target.style.borderColor = '#e0e0e0';
                  e.target.style.backgroundColor = '#fafafa';
                }}
              >
                <div>
                  <div style={{
                    fontWeight: 'bold',
                    fontSize: '14px',
                    color: '#333',
                    marginBottom: '2px'
                  }}>
                    {robot.name}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#666'
                  }}>
                    {robot.type}
                  </div>
                </div>
                
                <span style={{
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  color: 'white',
                  backgroundColor: getStatusColor(robot.status)
                }}>
                  {robot.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ClickRobot;