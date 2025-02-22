// orbital-agent/web/src/components/ClusterStatus.tsx
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

interface MetricsData {
    timestamp: string;
    cpuUsage: number;
    memoryUsage: number;
}

const ClusterStatus: React.FC = () => {
    const [metrics, setMetrics] = useState<MetricsData[]>([]);

    useEffect(() => {
        const fetchMetrics = async () => {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            setMetrics(data.slice(-10));
        };
        
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    const chartData = {
        labels: metrics.map(m => m.timestamp),
        datasets: [
            {
                label: 'CPU Usage',
                data: metrics.map(m => m.cpuUsage),
                borderColor: 'rgb(75, 192, 192)',
            },
            {
                label: 'Memory Usage',
                data: metrics.map(m => m.memoryUsage),
                borderColor: 'rgb(255, 99, 132)',
            }
        ]
    };

    return <Line data={chartData} />;
};

export default ClusterStatus;
