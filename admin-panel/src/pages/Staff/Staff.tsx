import { useState } from 'react'
import { Box, Typography, Tabs, Tab } from '@mui/material'
import StaffUsersList from '../QRScanner/StaffUsersList'
import AdminAccountsList from '../AdminAccounts/AdminAccountsList'

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
        <AdminAccountsList />
      ) : (
        <StaffUsersList />
      )}
    </Box>
  )
}

export default Staff

