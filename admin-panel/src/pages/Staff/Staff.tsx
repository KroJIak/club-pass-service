import { useEffect, useState } from 'react'
import { Box, Typography, Tabs, Tab } from '@mui/material'
import StaffUsersList from '../QRScanner/StaffUsersList'
import AdminAccountsList from '../AdminAccounts/AdminAccountsList'
import { usePermissions } from '../../hooks/usePermissions'

const Staff = () => {
  const [tabValue, setTabValue] = useState(0)
  const { isSuperAdmin, isLoading } = usePermissions()

  const showAdminAccountsTab = isSuperAdmin
  const staffTabIndex = showAdminAccountsTab ? 1 : 0

  useEffect(() => {
    // If the user is not superadmin, ensure we never stay on the Admin Accounts tab.
    if (!showAdminAccountsTab && tabValue !== 0) {
      setTabValue(0)
    }
  }, [showAdminAccountsTab, tabValue])

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading...</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Staff
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          {showAdminAccountsTab && <Tab label="Admin Panel Accounts" />}
          <Tab label="Staff Bot Users" />
        </Tabs>
      </Box>

      {showAdminAccountsTab && tabValue === 0 ? <AdminAccountsList /> : <StaffUsersList />}
    </Box>
  )
}

export default Staff

