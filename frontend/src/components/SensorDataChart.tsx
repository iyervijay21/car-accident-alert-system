import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { CircularProgress, Box, Typography } from '@mui/material';

// Generate mock sensor data for demonstration
const generateMockData = () => {
  const data = [];
  const now = new Date();
  
  for (let i = 9; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 1000);
    data.push({
      time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      acceleration: Math.random() * 10 - 5,
      gyroscope: Math.random() * 6 - 3,
    });
  }
  
  return data;
};

const SensorDataChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial data load
    setData(generateMockData());
    setLoading(false);
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData.slice(1), ...generateMockData().slice(-1)];
        return newData;
      });
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="acceleration"
            stroke="#1976d2"
            activeDot={{ r: 8 }}
            name="Acceleration (m/s²)"
          />
          <Line
            type="monotone"
            dataKey="gyroscope"
            stroke="#dc004e"
            name="Gyroscope (rad/s)"
          />
        </LineChart>
      </ResponsiveContainer>
      <Typography variant="caption" color="text.secondary" align="center" display="block" mt={1}>
        Real-time sensor data visualization
      </Typography>
    </Box>
  );
};

export default SensorDataChart;