import React, { useState, useEffect } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { api } from '../services/api';

interface Accident {
  id: number;
  timestamp: string;
  latitude: number;
  longitude: number;
  confidence_score: number | null;
  is_confirmed: boolean;
}

const LiveAccidentAlerts: React.FC = () => {
  const [accidents, setAccidents] = useState<Accident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAccidents = async () => {
      try {
        const response = await api.get('/accidents');
        setAccidents(response.data);
      } catch (err) {
        setError('Failed to fetch accident alerts');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccidents();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchAccidents, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (accidents.length === 0) {
    return (
      <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
        No recent accident alerts
      </Typography>
    );
  }

  return (
    <List>
      {accidents.slice(0, 5).map((accident) => (
        <ListItem
          key={accident.id}
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            mb: 1,
          }}
        >
          <ListItemIcon>
            {accident.is_confirmed ? (
              <CheckCircleIcon color="success" />
            ) : accident.confidence_score && accident.confidence_score > 0.7 ? (
              <WarningIcon color="warning" />
            ) : (
              <ErrorIcon color="error" />
            )}
          </ListItemIcon>
          <ListItemText
            primary={`Accident #${accident.id}`}
            secondary={new Date(accident.timestamp).toLocaleString()}
          />
          <Chip
            label={
              accident.is_confirmed
                ? 'Confirmed'
                : accident.confidence_score
                ? `${Math.round(accident.confidence_score * 100)}%`
                : 'Pending'
            }
            color={
              accident.is_confirmed
                ? 'success'
                : accident.confidence_score && accident.confidence_score > 0.7
                ? 'warning'
                : 'default'
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default LiveAccidentAlerts;