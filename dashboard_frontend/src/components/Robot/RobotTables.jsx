import React from 'react';

const RobotTable = () => {
    const robots = [
        {
            id: 'ROB_001',
            name: '시트조립로봇#1',
            location: 'Line-A St-3',
            status: '가동중',
            utilization: '95.2%',
            cycleTime: '18초',
            alarm: '정상',
            health: '87점',
            workCount: '847건',
            connection: '온라인'
        },
        {
            id: 'ROB_002',
            name: '시트조립로봇#2',
            location: 'Line-A St-4',
            status: '대기중',
            utilization: '88.5%',
            cycleTime: '20초',
            alarm: '경고',
            health: '92점',
            workCount: '823건',
            connection: '오프라인'
        }
    ];

    const getStatusColor = (status) => {
        switch (status) {
            case '가동중': return 'status-blue';
            case '대기중': return 'status-yellow';
            case '정지': return 'status-red';
            default: return 'status-gray';
        }
    };

    const getAlarmColor = (alarm) => {
        switch (alarm) {
            case '정상': return 'status-green';
            case '경고': return 'status-orange';
            case '심각': return 'status-red';
            default: return 'status-gray';
        }
    };

    const getConnectionColor = (connection) => {
        switch (connection) {
            case '온라인': return 'status-green';
            case '오프라인': return 'status-red';
            default: return 'status-gray';
        }
    };

    return (
        <div className="table-responsive">
            <table className="table table-vcenter">
                <thead>
                    <tr>
                        <th>로봇ID</th>
                        <th className="text-nowrap">로봇명</th>
                        <th className="text-nowrap">위치</th>
                        <th className="text-nowrap">상태</th>
                        <th className="text-nowrap">가동률</th>
                        <th className="text-nowrap">사이클타임</th>
                        <th className="text-nowrap">알람</th>
                        <th className="text-nowrap">건강도</th>
                        <th className="text-nowrap">작업량</th>
                        <th className="text-nowrap">통신상태</th>
                    </tr>
                </thead>
                <tbody>
                    {robots.map((robot) => (
                        <tr key={robot.id}>
                            <th>{robot.id}</th>
                            <td>{robot.name}</td>
                            <td>{robot.location}</td>
                            <td>
                                <span className={`status ${getStatusColor(robot.status)}`}>
                                    {robot.status}
                                </span>
                            </td>
                            <td>{robot.utilization}</td>
                            <td>{robot.cycleTime}</td>
                            <td>
                                <span className={`status ${getAlarmColor(robot.alarm)}`}>
                                    {robot.alarm}
                                </span>
                            </td>
                            <td>{robot.health}</td>
                            <td>{robot.workCount}</td>
                            <td>
                                <span className={`status ${getConnectionColor(robot.connection)}`}>
                                    {robot.connection}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default RobotTable;