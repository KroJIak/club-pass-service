import { useEffect, useState } from 'react'
import { Box, Typography, Tabs, Tab } from '@mui/material'
import StaffUsersList from '../QRScanner/StaffUsersList'
import AdminAccountsList from '../AdminAccounts/AdminAccountsList'
import { usePermissions } from '../../hooks/usePermissions'
import { useTranslation } from 'react-i18next'

const Staff = () => {
  const { t } = useTranslation('staff')
  const { t: tCommon } = useTranslation('common')
  const [tabValue, setTabValue] = useState(0)
  const { isSuperAdmin, isLoading } = usePermissions()

  const showAdminAccountsTab = isSuperAdmin

  useEffect(() => {
    // If the user is not superadmin, ensure we never stay on the Admin Accounts tab.
    if (!showAdminAccountsTab && tabValue !== 0) {
      setTabValue(0)
    }
  }, [showAdminAccountsTab, tabValue])

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>{tCommon('status.loading')}</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('title')}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          {showAdminAccountsTab && <Tab label={t('adminAccounts')} />}
          <Tab label={t('staffBotUsers')} />
        </Tabs>
      </Box>

      {showAdminAccountsTab && tabValue === 0 ? <AdminAccountsList /> : <StaffUsersList />}
    </Box>
  )
}

export default Staff

