import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { api } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface Accident {
  id: number;
  timestamp: string;
  latitude: number;
  longitude: number;
  confidence_score: number | null;
  is_confirmed: boolean;
}

const Reports: React.FC = () => {
  const [accidents, setAccidents] = useState<Accident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAccidents = async () => {
      try {
        const response = await api.get('/accidents');
        setAccidents(response.data);
      } catch (err) {
        setError('Failed to fetch accident reports');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccidents();
  }, []);

  // Prepare data for charts
  const accidentStats = accidents.reduce(
    (acc, accident) => {
      if (accident.is_confirmed) {
        acc.confirmed++;
      } else if (accident.confidence_score && accident.confidence_score > 0.7) {
        acc.potential++;
      } else {
        acc.lowConfidence++;
      }
      return acc;
    },
    { confirmed: 0, potential: 0, lowConfidence: 0 }
  );

  const chartData = [
    { name: 'Confirmed', value: accidentStats.confirmed },
    { name: 'Potential', value: accidentStats.potential },
    { name: 'Low Confidence', value: accidentStats.lowConfidence },
  ];

  const COLORS = ['#4caf50', '#ff9800', '#f44336'];

  const barChartData = accidents.slice(0, 10).map(accident => ({
    name: `#${accident.id}`,
    confidence: accident.confidence_score ? accident.confidence_score * 100 : 0,
  }));

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Accident Reports & Analytics
        </Typography>
        
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Confirmed Accidents" />
              <CardContent>
                <Typography variant="h3" color="success.main">
                  {accidentStats.confirmed}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Potential Accidents" />
              <CardContent>
                <Typography variant="h3" color="warning.main">
                  {accidentStats.potential}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Low Confidence" />
              <CardContent>
                <Typography variant="h3" color="error.main">
                  {accidentStats.lowConfidence}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Accident Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Accidents Confidence
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={barChartData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value) => [`${value}%`, 'Confidence']} />
                  <Legend />
                  <Bar dataKey="confidence" name="Confidence Score" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
        
        <Paper elevation={3}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Accident ID</TableCell>
                  <TableCell>Date & Time</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {accidents.map((accident) => (
                  <TableRow key={accident.id}>
                    <TableCell>#{accident.id}</TableCell>
                    <TableCell>{new Date(accident.timestamp).toLocaleString()}</TableCell>
                    <TableCell>
                      {accident.latitude.toFixed(6)}, {accident.longitude.toFixed(6)}
                    </TableCell>
                    <TableCell>
                      {accident.confidence_score !== null
                        ? `${(accident.confidence_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={
                          accident.is_confirmed ? (
                            <CheckCircleIcon />
                          ) : accident.confidence_score && accident.confidence_score > 0.7 ? (
                            <WarningIcon />
                          ) : (
                            <ErrorIcon />
                          )
                        }
                        label={
                          accident.is_confirmed
                            ? 'Confirmed'
                            : accident.confidence_score && accident.confidence_score > 0.7
                            ? 'Potential'
                            : 'Low Confidence'
                        }
                        color={
                          accident.is_confirmed
                            ? 'success'
                            : accident.confidence_score && accident.confidence_score > 0.7
                            ? 'warning'
                            : 'error'
                        }
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>
    </Container>
  );
};

export default Reports;