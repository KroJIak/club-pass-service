import { useState } from 'react'
import { Box, Typography, Tabs, Tab, Paper, Alert } from '@mui/material'
import StaffUsersList from '../QRScanner/StaffUsersList'

const Staff = () => {
  const [tabValue, setTabValue] = useState(0)

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Staff
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Admin Panel Accounts" />
          <Tab label="Staff Bot Users" />
        </Tabs>
      </Box>

      {tabValue === 0 ? (
        <Paper sx={{ p: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            The functionality for creating admin panel accounts with different access levels will be implemented in the future.
          </Alert>
          <Typography variant="body1" color="text.secondary">
            Here you will be able to create and manage administrator accounts with various access levels.
          </Typography>
        </Paper>
      ) : (
        <StaffUsersList />
      )}
    </Box>
  )
}

export default Staff

