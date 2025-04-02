import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Box, Typography, Button, List, ListItem, ListItemText, Divider, Paper } from '@mui/material';

function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const response = await api.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDiscount = async () => {
    try {
      await api.generateDiscount();
      await fetchStats(); // Refresh stats
    } catch (error) {
      console.error('Error generating discount:', error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) return <Typography>Loading admin data...</Typography>;

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>Admin Panel</Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Statistics</Typography>
        <Typography>Total Orders: {stats.total_orders}</Typography>
        <Typography>Total Sales: ${stats.total_sales}</Typography>
        <Typography>Total Discounts Given: {stats.total_discounts}</Typography>
        <Typography>Total Discount Amount: ${stats.total_discount_amount}</Typography>
      </Paper>
      
      <Button 
        variant="contained" 
        color="primary" 
        onClick={handleGenerateDiscount}
        sx={{ mb: 3 }}
      >
        Generate Discount Code
      </Button>
      
      <Typography variant="h6" gutterBottom>Active Discount Codes</Typography>
      <List>
        {stats.active_discounts.map(discount => (
          <React.Fragment key={discount.code}>
            <ListItem>
              <ListItemText
                primary={discount.code}
                secondary={`Created: ${new Date(discount.created_at).toLocaleString()}`}
              />
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
}

export default AdminPanel;