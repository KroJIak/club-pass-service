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
  const [scanning, setScanning] = useState(false)
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const scannerContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (userId) {
      startScanning()
    }
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {})
      }
    }
  }, [userId])

  const startScanning = async () => {
    if (!userId) return

    try {
      setError(null)
      setTicket(null)
      
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

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 300, height: 300 },
        },
        (decodedText) => {
          handleScan(decodedText)
        },
        () => {
          // Ignore scanning errors
        }
      )
      
      setScanning(true)
    } catch (err: any) {
      setError(err.message || 'Failed to start camera')
      setScanning(false)
    }
  }

  const handleScan = async (token: string) => {
    if (loading || !userId) return

    setLoading(true)
    setError(null)

    try {
      if (scannerRef.current) {
        try {
          await scannerRef.current.stop()
        } catch (e) {
          // Ignore stop errors
        }
      }

      const ticketData = await getTicketByToken(token, userId)
      setTicket(ticketData)
      setScanning(false)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Билет не найден')
      } else if (err.response?.status === 403) {
        setError('Доступ запрещен')
      } else {
        setError(err.response?.data?.detail || 'Ошибка при получении билета')
      }
      setTicket(null)
      setTimeout(() => {
        startScanning()
      }, 500)
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
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop()
        scannerRef.current.clear()
      } catch (e) {
        // Ignore stop errors
      }
      scannerRef.current = null
    }
    setScanning(false)
    setTimeout(() => {
      startScanning()
    }, 100)
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
    <Box sx={{ p: 2, pb: 10 }}>
      {!ticket && (
        <Box sx={{ mt: 2 }}>
          <Box
            id="qr-reader-mobile"
            ref={scannerContainerRef}
            sx={{
              width: '100%',
              maxWidth: '100%',
              margin: '0 auto',
              mb: 2,
            }}
          />
        </Box>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
          {error}
        </Alert>
      )}

      {ticket && (
        <Card sx={{ mt: 2 }}>
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
      )}
    </Box>
  )
}

export default ScannerPage

