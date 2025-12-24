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
import api from '../../services/api'
import { TicketDetailResponse } from '../../types'

const QRScanner = () => {
  const [scanning, setScanning] = useState(false)
  const [ticket, setTicket] = useState<TicketDetailResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const scannerContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {})
      }
    }
  }, [])

  const startScanning = async () => {
    try {
      setError(null)
      setTicket(null)
      setScanning(true)

      const scanner = new Html5Qrcode('qr-reader')
      scannerRef.current = scanner

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
        },
        (decodedText) => {
          handleScan(decodedText)
        },
        (errorMessage) => {
          // Ignore scanning errors
        }
      )
    } catch (err: any) {
      setError(err.message || 'Не удалось запустить камеру')
      setScanning(false)
    }
  }

  const stopScanning = async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop()
        scannerRef.current.clear()
      } catch (err) {
        // Ignore stop errors
      }
      scannerRef.current = null
    }
    setScanning(false)
  }

  const handleScan = async (token: string) => {
    if (loading) return

    setLoading(true)
    setError(null)

    try {
      // Stop scanning
      await stopScanning()

      // Fetch ticket by token
      const response = await api.get(`/admin/tickets/token/${token}`)
      setTicket(response.data)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Билет не найден')
      } else {
        setError(err.response?.data?.detail || 'Ошибка при получении билета')
      }
      setTicket(null)
    } finally {
      setLoading(false)
    }
  }

  const handleAccept = async () => {
    if (!ticket || accepting) return

    setAccepting(true)
    setError(null)

    try {
      await api.post(`/admin/tickets/${ticket.id}/mark-used`)
      // Refresh ticket data
      const response = await api.get(`/admin/tickets/token/${ticket.token}`)
      setTicket(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при принятии билета')
    } finally {
      setAccepting(false)
    }
  }

  const handleReset = () => {
    setTicket(null)
    setError(null)
    setScanning(false)
    if (scannerRef.current) {
      scannerRef.current.stop().catch(() => {})
      scannerRef.current.clear()
      scannerRef.current = null
    }
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Скан QR
      </Typography>

      {!scanning && !ticket && (
        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            size="large"
            onClick={startScanning}
            fullWidth
            sx={{ mb: 2 }}
          >
            Начать сканирование
          </Button>
        </Box>
      )}

      {scanning && !ticket && (
        <Box sx={{ mt: 3 }}>
          <Box
            id="qr-reader"
            ref={scannerContainerRef}
            sx={{
              width: '100%',
              maxWidth: '500px',
              margin: '0 auto',
              mb: 2,
            }}
          />
          <Button
            variant="outlined"
            onClick={stopScanning}
            fullWidth
            sx={{ maxWidth: '500px', margin: '0 auto', display: 'block' }}
          >
            Остановить сканирование
          </Button>
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
        <Card sx={{ mt: 3, maxWidth: '600px', margin: '0 auto' }}>
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
              <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
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
                  Мероприятие
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

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleAccept}
                disabled={ticket.status !== 'active' || accepting}
                fullWidth
              >
                {accepting ? <CircularProgress size={24} /> : 'Принять'}
              </Button>
              <Button variant="outlined" onClick={handleReset} fullWidth>
                Сканировать еще
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

export default QRScanner

