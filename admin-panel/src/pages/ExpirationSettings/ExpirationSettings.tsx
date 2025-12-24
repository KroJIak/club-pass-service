import { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  CircularProgress,
  TextField,
} from '@mui/material'
import api from '../../services/api'
import type { ExpirationSettings, ExpirationSettingsUpdate } from '../../types'

const ExpirationSettings = () => {
  const [settings, setSettings] = useState<ExpirationSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get<ExpirationSettings>('/admin/expiration-settings')
      setSettings(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = (field: 'ticket_expiration_enabled' | 'event_deactivation_enabled') => {
    if (!settings) return
    
    setSettings({
      ...settings,
      [field]: !settings[field],
    })
  }

  const handleIntervalChange = (value: string) => {
    if (!settings) return
    
    const numValue = parseInt(value, 10)
    if (!isNaN(numValue) && numValue >= 1) {
      setSettings({
        ...settings,
        check_interval_minutes: numValue,
      })
    }
  }

  const handleSave = async () => {
    if (!settings) return

    try {
      setSaving(true)
      setError(null)
      setSuccess(false)

      const update: ExpirationSettingsUpdate = {
        ticket_expiration_enabled: settings.ticket_expiration_enabled,
        event_deactivation_enabled: settings.event_deactivation_enabled,
        check_interval_minutes: settings.check_interval_minutes,
      }

      const response = await api.put<ExpirationSettings>('/admin/expiration-settings', update)
      setSettings(response.data)
      setSuccess(true)
      
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (!settings) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">Failed to load settings</Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
              <Typography variant="h6" component="h1" gutterBottom>
                Expiration Service Settings
              </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Manage expiration service functionality
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
            Settings saved successfully!
          </Alert>
        )}

        <Box sx={{ mb: 4 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.ticket_expiration_enabled}
                onChange={() => handleToggle('ticket_expiration_enabled')}
                color="primary"
              />
            }
            label="Ticket Expiration"
          />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 1 }}>
            Automatically mark tickets as expired if they are not used or refunded by 12:00 PM the day after the event
          </Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.event_deactivation_enabled}
                onChange={() => handleToggle('event_deactivation_enabled')}
                color="primary"
              />
            }
            label="Event Deactivation"
          />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 1 }}>
            Automatically deactivate events after they end (at 12:00 PM the day after the event)
          </Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          <TextField
            label="Check Interval (minutes)"
            type="number"
            value={settings.check_interval_minutes}
            onChange={(e) => handleIntervalChange(e.target.value)}
            inputProps={{ min: 1 }}
            helperText="How often the expiration service checks for expired tickets and events (minimum 1 minute)"
            sx={{ width: '100%', maxWidth: 400 }}
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
            size="large"
          >
            {saving ? <CircularProgress size={24} /> : 'Save Settings'}
          </Button>
          <Button
            variant="outlined"
            onClick={async () => {
              try {
                setSaving(true)
                setError(null)
                setSuccess(false)
                
                // Reset to default values (both enabled, 30 minutes interval)
                const update: ExpirationSettingsUpdate = {
                  ticket_expiration_enabled: true,
                  event_deactivation_enabled: true,
                  check_interval_minutes: 30,
                }
                
                const response = await api.put<ExpirationSettings>('/admin/expiration-settings', update)
                setSettings(response.data)
                setSuccess(true)
                setTimeout(() => setSuccess(false), 3000)
              } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to reset settings')
              } finally {
                setSaving(false)
              }
            }}
            disabled={saving || loading}
            size="large"
          >
            Reset
          </Button>
        </Box>

        {settings.updated_at && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Last updated: {new Date(settings.updated_at).toLocaleString()}
          </Typography>
        )}
      </Paper>
    </Container>
  )
}

export default ExpirationSettings

