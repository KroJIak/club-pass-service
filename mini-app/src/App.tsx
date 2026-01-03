import { useState, useEffect } from 'react'
import { Box, CircularProgress, Alert } from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { useTelegramWebApp } from './hooks/useTelegramWebApp'
import { checkStaffAccess } from './services/api'
import ScannerPage from './pages/ScannerPage'
import ListsPage from './pages/ListsPage'
import BottomNav from './components/BottomNavigation'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  const { userId, webApp } = useTelegramWebApp()
  const [tabValue, setTabValue] = useState(0)
  const [loading, setLoading] = useState(true)
  const [hasAccess, setHasAccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (webApp) {
      webApp.ready()
      webApp.expand()
    }
  }, [webApp])

  useEffect(() => {
    const verifyAccess = async () => {
      console.log('Verifying access, userId:', userId)
      if (!userId) {
        setLoading(false)
        setError('Не удалось получить ID пользователя')
        return
      }

      try {
        console.log('Calling checkStaffAccess with userId:', userId)
        const result = await checkStaffAccess(userId)
        console.log('Staff access check result:', result)
        console.log('has_access value:', result.has_access, 'type:', typeof result.has_access)
        const accessGranted = result.has_access === true || result.has_access === 'true'
        setHasAccess(accessGranted)
        if (!accessGranted) {
          setError('У вас нет доступа к этому приложению')
        }
      } catch (err: any) {
        console.error('Error checking staff access:', err)
        console.error('Error response:', err.response)
        setError(err.response?.data?.detail || 'Ошибка при проверке доступа')
      } finally {
        setLoading(false)
      }
    }

    verifyAccess()
  }, [userId])

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
          }}
        >
          <CircularProgress />
        </Box>
      </ThemeProvider>
    )
  }

  if (error || !hasAccess) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ p: 2 }}>
          <Alert severity="error">{error || 'Доступ запрещен'}</Alert>
        </Box>
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ pb: 8 }}>
        {tabValue === 0 ? <ScannerPage /> : <ListsPage />}
      </Box>
      <BottomNav value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} />
    </ThemeProvider>
  )
}

export default App
