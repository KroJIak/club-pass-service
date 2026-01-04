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
import { Html5Qrcode, Html5QrcodeScanType } from 'html5-qrcode'
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
  const [scanning, setScanning] = useState(false)
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const scannerContainerRef = useRef<HTMLDivElement>(null)
  const cameraActiveRef = useRef<boolean>(false)

  // Keep camera active at all times
  useEffect(() => {
    if (userId && !cameraActiveRef.current) {
      startScanning()
    }
    return () => {
      // Don't stop camera on unmount - keep it running
    }
  }, [userId])

  // Restart camera when ticket is cleared
  useEffect(() => {
    if (!ticket && userId && !scanning && !cameraActiveRef.current) {
      startScanning()
    }
  }, [ticket, userId, scanning])

  const startScanning = async () => {
    if (!userId || cameraActiveRef.current) return

    try {
      setError(null)
      
      if (scannerRef.current) {
        try {
          await scannerRef.current.stop()
          scannerRef.current.clear()
        } catch (e) {
          // Ignore stop errors
        }
      }

      const scanner = new Html5Qrcode('qr-reader-mobile')
      scannerRef.current = scanner

      // Get container dimensions for full-screen scanning
      const container = scannerContainerRef.current
      const width = container?.clientWidth || window.innerWidth
      const height = container?.clientHeight || window.innerHeight

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          // Disable qrbox to scan entire area, but keep it for visual guide
          qrbox: { width: Math.min(300, width * 0.8), height: Math.min(300, height * 0.6) },
          aspectRatio: 1.0,
          // Enable scanning from entire viewport
          disableFlip: false,
        },
        (decodedText) => {
          handleScan(decodedText)
        },
        () => {
          // Ignore scanning errors
        }
      )
      
      cameraActiveRef.current = true
      setScanning(true)
    } catch (err: any) {
      setError(err.message || 'Failed to start camera')
      setScanning(false)
      cameraActiveRef.current = false
    }
  }

  const handleScan = async (token: string) => {
    if (loading || !userId) return

    setLoading(true)
    setError(null)

    // Don't stop camera - keep it running
    // Only pause scanning temporarily
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
        position: 'relative',
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        p: 0,
        pb: 10,
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
              '& video': {
                width: '100% !important',
                height: '100% !important',
                objectFit: 'cover',
              },
              '& canvas': {
                display: 'none', // Hide canvas overlay
              },
              // Overlay for scanning area indicator
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
                border: '3px solid rgba(255, 255, 255, 0.6)',
                borderRadius: '12px',
                zIndex: 10,
                pointerEvents: 'none',
                boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.4)',
              },
            }}
          />
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
