import { useState } from 'react'
import { Box, Typography, Tabs, Tab, Paper, Alert } from '@mui/material'
import StaffUsersList from '../QRScanner/StaffUsersList'

const Staff = () => {
  const [tabValue, setTabValue] = useState(0)

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Сотрудники
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Аккаунты админ-панели" />
          <Tab label="Пользователи staff-бота" />
        </Tabs>
      </Box>

      {tabValue === 0 ? (
        <Paper sx={{ p: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Функционал создания аккаунтов админ-панели с разными правами доступа будет реализован в будущем.
          </Alert>
          <Typography variant="body1" color="text.secondary">
            Здесь будет возможность создавать и управлять аккаунтами администраторов с различными уровнями доступа.
          </Typography>
        </Paper>
      ) : (
        <StaffUsersList />
      )}
    </Box>
  )
}

export default Staff

