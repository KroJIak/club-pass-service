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

interface CameraDevice {
  id: string
  label: string
}

const QRScanner = () => {
  const [scanning, setScanning] = useState(false)
  const [ticket, setTicket] = useState<TicketDetailResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const [cameras, setCameras] = useState<CameraDevice[]>([])
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null)
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const scannerContainerRef = useRef<HTMLDivElement>(null)

  // Auto-start scanning on mount
  useEffect(() => {
    startScanning()
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {})
      }
    }
  }, [])

  // Load available cameras
  useEffect(() => {
    const loadCameras = async () => {
      try {
        const devices = await Html5Qrcode.getCameras()
        if (devices && devices.length > 0) {
          setCameras(devices)
          // Select first camera by default
          if (!selectedCameraId && devices.length > 0) {
            setSelectedCameraId(devices[0].id)
          }
        }
      } catch (err) {
        console.error('Failed to get cameras:', err)
      }
    }
    loadCameras()
  }, [])

  const startScanning = async (cameraId?: string) => {
    try {
      setError(null)
      setTicket(null)
      
      // Stop existing scanner if any
      if (scannerRef.current) {
        try {
          await scannerRef.current.stop()
          scannerRef.current.clear()
        } catch (e) {
          // Ignore stop errors
        }
      }

      const scanner = new Html5Qrcode('qr-reader')
      scannerRef.current = scanner

      // Use selected camera or default to environment facing camera
      const cameraConfig = cameraId 
        ? { deviceId: { exact: cameraId } }
        : { facingMode: 'environment' }

      await scanner.start(
        cameraConfig,
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
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

  const switchCamera = async (cameraId: string) => {
    if (cameraId === selectedCameraId) return
    
    setSelectedCameraId(cameraId)
    if (scanning) {
      await startScanning(cameraId)
    }
  }


  const handleScan = async (token: string) => {
    if (loading) return

    setLoading(true)
    setError(null)

    try {
      // Stop scanning temporarily
      if (scannerRef.current) {
        try {
          await scannerRef.current.stop()
        } catch (e) {
          // Ignore stop errors
        }
      }

      // Fetch ticket by token
      const response = await api.get(`/admin/tickets/token/${token}`)
      setTicket(response.data)
      setScanning(false)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Ticket not found')
      } else {
        setError(err.response?.data?.detail || 'Error fetching ticket')
      }
      setTicket(null)
      // Restart scanning on error
      setTimeout(() => {
        startScanning(selectedCameraId || undefined)
      }, 500)
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
      setError(err.response?.data?.detail || 'Error accepting ticket')
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
    // Restart scanning
    setTimeout(() => {
      startScanning(selectedCameraId || undefined)
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
        return 'Active'
      case 'used':
        return 'Used'
      case 'refunded':
        return 'Refunded'
      case 'expired':
        return 'Expired'
      case 'cancelled':
        return 'Cancelled'
      default:
        return status
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        QR Scanner
      </Typography>

      {!ticket && (
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
          
          {/* Camera selector - circles in a row */}
          {cameras.length > 1 && (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 2,
                mt: 2,
                mb: 2,
              }}
            >
              {cameras.map((camera, index) => (
                <Box
                  key={camera.id}
                  onClick={() => switchCamera(camera.id)}
                  sx={{
                    width: selectedCameraId === camera.id ? 16 : 10,
                    height: selectedCameraId === camera.id ? 16 : 10,
                    borderRadius: '50%',
                    backgroundColor: selectedCameraId === camera.id ? 'primary.main' : 'grey.400',
                    border: selectedCameraId === camera.id ? '2px solid' : 'none',
                    borderColor: selectedCameraId === camera.id ? 'primary.dark' : 'transparent',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease-in-out',
                    boxShadow: selectedCameraId === camera.id ? '0 0 8px rgba(25, 118, 210, 0.5)' : 'none',
                    '&:hover': {
                      backgroundColor: selectedCameraId === camera.id ? 'primary.dark' : 'grey.500',
                      transform: 'scale(1.3)',
                      boxShadow: selectedCameraId === camera.id ? '0 0 12px rgba(25, 118, 210, 0.7)' : '0 0 4px rgba(0, 0, 0, 0.2)',
                    },
                  }}
                  title={camera.label || `Camera ${index + 1}`}
                />
              ))}
            </Box>
          )}
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
              Ticket Information
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Ticket ID
              </Typography>
              <Typography variant="body1">{ticket.id}</Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Token
              </Typography>
              <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                {ticket.token}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Status
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
                  Event
                </Typography>
                <Typography variant="body1">{ticket.event.name}</Typography>
              </Box>
            )}

            {ticket.ticket_type && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Ticket Type
                </Typography>
                <Typography variant="body1">{ticket.ticket_type.name}</Typography>
              </Box>
            )}

            {ticket.user && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  User
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
                  Used At
                </Typography>
                <Typography variant="body1">
                  {new Date(ticket.used_at).toLocaleString()}
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
                {accepting ? <CircularProgress size={24} /> : 'Accept'}
              </Button>
              <Button variant="outlined" onClick={handleReset} fullWidth>
                Scan Again
              </Button>
            </Box>

            {ticket.status !== 'active' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Ticket cannot be accepted because its status is: {getStatusLabel(ticket.status)}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default QRScanner

