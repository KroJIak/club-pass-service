import { useState, useEffect } from 'react'
import { Box, CircularProgress, Alert, Typography, Paper, Accordion, AccordionSummary, AccordionDetails } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
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
  const { userId, webApp, user, initData } = useTelegramWebApp()
  const [tabValue, setTabValue] = useState(0)
  const [loading, setLoading] = useState(true)
  const [hasAccess, setHasAccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [apiResponse, setApiResponse] = useState<any>(null)
  
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${timestamp}] ${message}`])
    console.log(message)
  }

  useEffect(() => {
    if (webApp) {
      webApp.ready()
      webApp.expand()
    }
  }, [webApp])

  useEffect(() => {
    const verifyAccess = async () => {
      addLog('=== Starting access verification ===')
      addLog(`userId: ${userId}`)
      addLog(`user object: ${JSON.stringify(user)}`)
      addLog(`webApp exists: ${!!webApp}`)
      addLog(`initData: ${initData ? 'present' : 'missing'}`)
      
      // Wait a bit for user to be loaded from Telegram WebApp
      if (!userId && !user) {
        addLog('Waiting for user data...')
        // Try to get from URL params for testing
        const urlParams = new URLSearchParams(window.location.search)
        const testUserId = urlParams.get('test_user_id')
        if (testUserId) {
          addLog(`Using test_user_id from URL: ${testUserId}`)
          const testUser = { id: parseInt(testUserId) }
          try {
            const result = await checkStaffAccess(parseInt(testUserId))
            addLog(`API Response received: ${JSON.stringify(result)}`)
            setApiResponse(result)
            const accessGranted = result.has_access === true
            setHasAccess(accessGranted)
            if (!accessGranted) {
              setError('У вас нет доступа к этому приложению')
            }
          } catch (err: any) {
            addLog(`ERROR: Exception caught: ${err.message}`)
            setError(err.response?.data?.detail || 'Ошибка при проверке доступа')
          } finally {
            setLoading(false)
          }
          return
        }
        
        // If no test_user_id and no user, wait a bit more
        setTimeout(() => {
          if (!userId && !user) {
            addLog('ERROR: userId is still null after waiting')
            setLoading(false)
            setError('Не удалось получить ID пользователя')
          }
        }, 1000)
        return
      }
      
      const finalUserId = userId || user?.id
      if (!finalUserId) {
        addLog('ERROR: userId is null or undefined')
        setLoading(false)
        setError('Не удалось получить ID пользователя')
        return
      }

      try {
        addLog(`Calling API: /v1/staff/check-access?telegram_user_id=${finalUserId}`)
        const result = await checkStaffAccess(finalUserId)
        addLog(`API Response received: ${JSON.stringify(result)}`)
        setApiResponse(result)
        
        addLog(`has_access value: ${result.has_access}, type: ${typeof result.has_access}`)
        addLog(`staff_user: ${JSON.stringify(result.staff_user)}`)
        
        const accessGranted = result.has_access === true || result.has_access === 'true'
        addLog(`accessGranted calculated: ${accessGranted}`)
        
        setHasAccess(accessGranted)
        if (!accessGranted) {
          addLog('ERROR: Access denied - has_access is false')
          setError('У вас нет доступа к этому приложению')
        } else {
          addLog('SUCCESS: Access granted')
          setError(null) // Clear any previous errors
          setHasAccess(true) // Ensure hasAccess is set
        }
      } catch (err: any) {
        addLog(`ERROR: Exception caught: ${err.message}`)
        addLog(`Error response: ${JSON.stringify(err.response?.data)}`)
        addLog(`Error status: ${err.response?.status}`)
        console.error('Error checking staff access:', err)
        console.error('Error response:', err.response)
        setError(err.response?.data?.detail || 'Ошибка при проверке доступа')
      } finally {
        addLog('=== Access verification completed ===')
        setLoading(false)
      }
    }

    verifyAccess()
  }, [userId, user])

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

  if (error && !hasAccess) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ p: 2 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || 'Доступ запрещен'}
          </Alert>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">Debug Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography variant="subtitle2" gutterBottom>User Info:</Typography>
                  <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto' }}>
                    {JSON.stringify({ userId, user, hasAccess, error }, null, 2)}
                  </Typography>
                </Paper>
                
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography variant="subtitle2" gutterBottom>API Response:</Typography>
                  <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto' }}>
                    {JSON.stringify(apiResponse, null, 2)}
                  </Typography>
                </Paper>
                
                <Paper sx={{ p: 2, bgcolor: 'background.default', maxHeight: '300px', overflow: 'auto' }}>
                  <Typography variant="subtitle2" gutterBottom>Logs:</Typography>
                  <Box component="pre" sx={{ fontSize: '0.7rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {logs.length > 0 ? logs.join('\n') : 'No logs yet'}
                  </Box>
                </Paper>
              </Box>
            </AccordionDetails>
          </Accordion>
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
