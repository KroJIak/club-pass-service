import { useState, useEffect, useRef } from 'react'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material'
import { Html5Qrcode } from 'html5-qrcode'
import { useTelegramWebApp } from '../hooks/useTelegramWebApp'
import { getTicketByToken, markTicketAsUsed } from '../services/api'

interface Ticket {
  id: number
  token: string
  status: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used'
  used_at: string | null
  event: {
    id: number
    name: string
  } | null
  ticket_type: {
    id: number
    name: string
  } | null
  user: {
    id: number
    telegram_user_id: number
    username: string | null
    first_name: string | null
    last_name: string | null
  } | null
}

const ScannerPage = () => {
  const { userId } = useTelegramWebApp()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const [debugLogs, setDebugLogs] = useState<string[]>([])
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const scannerContainerRef = useRef<HTMLDivElement>(null)
  const cameraActiveRef = useRef<boolean>(false)
  const initRef = useRef<boolean>(false)

  // Initialize camera only once
  useEffect(() => {
    if (userId && !initRef.current) {
      initRef.current = true
      startScanning()
    }
    return () => {
      // Don't stop camera on unmount - keep it running
    }
  }, [userId])

  const addDebugLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    const logMessage = `[${timestamp}] ${message}`
    setDebugLogs(prev => [...prev, logMessage])
    console.log(logMessage)
  }

  const startScanning = async () => {
    if (!userId || cameraActiveRef.current) {
      addDebugLog(`startScanning: Skipped - userId: ${!!userId}, cameraActive: ${cameraActiveRef.current}`)
      return
    }

    try {
      setError(null)
      addDebugLog('startScanning: Starting...')
      
      if (scannerRef.current) {
        try {
          addDebugLog('startScanning: Stopping existing scanner...')
          await scannerRef.current.stop()
          scannerRef.current.clear()
          addDebugLog('startScanning: Existing scanner stopped')
        } catch (e: any) {
          addDebugLog(`startScanning: Error stopping existing scanner: ${e.message}`)
          // Ignore stop errors
        }
      }

      addDebugLog('startScanning: Creating new Html5Qrcode instance...')
      const scanner = new Html5Qrcode('qr-reader-mobile')
      scannerRef.current = scanner
      addDebugLog('startScanning: Html5Qrcode instance created')

      addDebugLog('startScanning: Starting camera with constraints...')
      try {
        await scanner.start(
          { 
            facingMode: 'environment',
          },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0,
            disableFlip: false,
          },
          (decodedText) => {
            addDebugLog(`QR Code detected: ${decodedText}`)
            handleScan(decodedText)
          },
          (errorMessage) => {
            // Ignore scanning errors, but log them
            // addDebugLog(`Scanning error: ${errorMessage}`)
          }
        )
        addDebugLog('startScanning: Camera started successfully')
        cameraActiveRef.current = true
      } catch (startErr: any) {
        addDebugLog(`startScanning: Error starting camera: ${startErr.message}`)
        addDebugLog(`startScanning: Error stack: ${startErr.stack}`)
        throw startErr
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to start camera'
      addDebugLog(`startScanning: Fatal error: ${errorMessage}`)
      addDebugLog(`startScanning: Error details: ${JSON.stringify(err)}`)
      setError(errorMessage)
      cameraActiveRef.current = false
    }
  }

  const handleScan = async (token: string) => {
    if (loading || !userId) return

    setLoading(true)
    setError(null)

    // Don't stop camera - keep it running
    try {
      const ticketData = await getTicketByToken(token, userId)
      setTicket(ticketData)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Билет не найден')
      } else if (err.response?.status === 403) {
        setError('Доступ запрещен')
      } else {
        setError(err.response?.data?.detail || 'Ошибка при получении билета')
      }
      setTicket(null)
    } finally {
      setLoading(false)
    }
  }

  const handleAccept = async () => {
    if (!ticket || accepting || !userId) return

    setAccepting(true)
    setError(null)

    try {
      await markTicketAsUsed(ticket.id, userId)
      const ticketData = await getTicketByToken(ticket.token, userId)
      setTicket(ticketData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при принятии билета')
    } finally {
      setAccepting(false)
    }
  }

  const handleReset = async () => {
    setTicket(null)
    setError(null)
    // Camera should already be running, no need to restart
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'used':
        return 'warning'
      case 'refunded':
        return 'error'
      case 'expired':
        return 'error'
      case 'cancelled':
        return 'default'
      default:
        return 'default'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Активен'
      case 'used':
        return 'Использован'
      case 'refunded':
        return 'Возвращен'
      case 'expired':
        return 'Истек'
      case 'cancelled':
        return 'Отменен'
      default:
        return status
    }
  }

  if (!userId) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Alert severity="error">Ошибка авторизации</Alert>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        p: 0,
        zIndex: 1,
      }}
    >
      {!ticket && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 1,
          }}
        >
          <Box
            id="qr-reader-mobile"
            ref={scannerContainerRef}
            sx={{
              width: '100%',
              height: '100%',
              position: 'relative',
              overflow: 'hidden',
              '& video': {
                width: '100% !important',
                height: '100% !important',
                objectFit: 'cover',
              },
              '& canvas': {
                display: 'none', // Hide canvas overlay
              },
              // Corner indicators (semi-transparent 30%)
              '&::before': {
                content: '""',
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '80%',
                maxWidth: '300px',
                height: '60%',
                maxHeight: '300px',
                zIndex: 10,
                pointerEvents: 'none',
                // Top-left corner
                borderTop: '3px solid rgba(255, 255, 255, 0.3)',
                borderLeft: '3px solid rgba(255, 255, 255, 0.3)',
                borderTopLeftRadius: '12px',
                // Top-right corner
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: '40px',
                  height: '40px',
                  borderTop: '3px solid rgba(255, 255, 255, 0.3)',
                  borderRight: '3px solid rgba(255, 255, 255, 0.3)',
                  borderTopRightRadius: '12px',
                },
              },
              // Corner indicators using pseudo-elements
              '&::after': {
                content: '""',
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '80%',
                maxWidth: '300px',
                height: '60%',
                maxHeight: '300px',
                zIndex: 10,
                pointerEvents: 'none',
                // Bottom corners
                borderBottom: '3px solid rgba(255, 255, 255, 0.3)',
                borderRight: '3px solid rgba(255, 255, 255, 0.3)',
                borderBottomRightRadius: '12px',
              },
            }}
          />
          {/* Corner indicators overlay */}
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '80%',
              maxWidth: '300px',
              height: '60%',
              maxHeight: '300px',
              zIndex: 10,
              pointerEvents: 'none',
            }}
          >
            {/* Top-left corner */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '40px',
                height: '40px',
                borderTop: '3px solid rgba(255, 255, 255, 0.3)',
                borderLeft: '3px solid rgba(255, 255, 255, 0.3)',
                borderTopLeftRadius: '12px',
              }}
            />
            {/* Top-right corner */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '40px',
                height: '40px',
                borderTop: '3px solid rgba(255, 255, 255, 0.3)',
                borderRight: '3px solid rgba(255, 255, 255, 0.3)',
                borderTopRightRadius: '12px',
              }}
            />
            {/* Bottom-left corner */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                width: '40px',
                height: '40px',
                borderBottom: '3px solid rgba(255, 255, 255, 0.3)',
                borderLeft: '3px solid rgba(255, 255, 255, 0.3)',
                borderBottomLeftRadius: '12px',
              }}
            />
            {/* Bottom-right corner */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                right: 0,
                width: '40px',
                height: '40px',
                borderBottom: '3px solid rgba(255, 255, 255, 0.3)',
                borderRight: '3px solid rgba(255, 255, 255, 0.3)',
                borderBottomRightRadius: '12px',
              }}
            />
          </Box>
        </Box>
      )}

      {loading && (
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 100,
            bgcolor: 'rgba(0, 0, 0, 0.7)',
            borderRadius: 2,
            p: 3,
          }}
        >
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert
          severity="error"
          sx={{
            position: 'absolute',
            top: 16,
            left: 16,
            right: 16,
            zIndex: 100,
            maxWidth: 'calc(100% - 32px)',
          }}
        >
          {error}
        </Alert>
      )}

      {/* Debug logs */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 80,
          left: 16,
          right: 16,
          zIndex: 100,
          bgcolor: 'rgba(0, 0, 0, 0.8)',
          borderRadius: 2,
          p: 2,
          maxHeight: '200px',
          overflowY: 'auto',
        }}
      >
        <Typography variant="caption" sx={{ color: 'white', fontFamily: 'monospace', fontSize: '0.7rem', mb: 1, display: 'block' }}>
          <strong>Debug Logs:</strong>
        </Typography>
        <Box
          component="pre"
          sx={{
            color: 'white',
            fontFamily: 'monospace',
            fontSize: '0.7rem',
            margin: 0,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {debugLogs.length > 0 ? debugLogs.slice(-20).join('\n') : 'No logs yet...'}
        </Box>
      </Box>

      {ticket && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            overflowY: 'auto',
            zIndex: 50,
            bgcolor: 'background.default',
            p: 2,
          }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Информация о билете
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  ID билета
                </Typography>
                <Typography variant="body1">{ticket.id}</Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Токен
                </Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  {ticket.token}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Статус
                </Typography>
                <Chip
                  label={getStatusLabel(ticket.status)}
                  color={getStatusColor(ticket.status) as any}
                  sx={{ mt: 0.5 }}
                />
              </Box>

              {ticket.event && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Событие
                  </Typography>
                  <Typography variant="body1">{ticket.event.name}</Typography>
                </Box>
              )}

              {ticket.ticket_type && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Тип билета
                  </Typography>
                  <Typography variant="body1">{ticket.ticket_type.name}</Typography>
                </Box>
              )}

              {ticket.user && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Пользователь
                  </Typography>
                  <Typography variant="body1">
                    {ticket.user.username ||
                      `${ticket.user.first_name || ''} ${ticket.user.last_name || ''}`.trim() ||
                      `ID: ${ticket.user.telegram_user_id}`}
                  </Typography>
                </Box>
              )}

              {ticket.used_at && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Использован
                  </Typography>
                  <Typography variant="body1">
                    {new Date(ticket.used_at).toLocaleString('ru-RU')}
                  </Typography>
                </Box>
              )}

              <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleAccept}
                  disabled={ticket.status !== 'active' || accepting}
                  fullWidth
                  size="large"
                >
                  {accepting ? <CircularProgress size={24} /> : 'Принять'}
                </Button>
                <Button variant="outlined" onClick={handleReset} fullWidth size="large">
                  Сканировать снова
                </Button>
              </Box>

              {ticket.status !== 'active' && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Билет не может быть принят, так как его статус: {getStatusLabel(ticket.status)}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  )
}

export default ScannerPage
