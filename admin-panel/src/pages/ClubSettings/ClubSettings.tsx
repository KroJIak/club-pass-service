import { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  TextField,
} from '@mui/material'
import api from '../../services/api'
import type { ClubSettings, ClubSettingsUpdate } from '../../types'

const ClubSettings = () => {
  const [settings, setSettings] = useState<ClubSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [formData, setFormData] = useState({
    address: '',
    phone: '',
    email: '',
  })

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get<ClubSettings>('/admin/club-settings')
      setSettings(response.data)
      setFormData({
        address: response.data.address || '',
        phone: response.data.phone || '',
        email: response.data.email || '',
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: 'address' | 'phone' | 'email') => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData({
      ...formData,
      [field]: e.target.value,
    })
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(false)

      const update: ClubSettingsUpdate = {
        address: formData.address.trim() || null,
        phone: formData.phone.trim() || null,
        email: formData.email.trim() || null,
      }

      const response = await api.put<ClubSettings>('/admin/club-settings', update)
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

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h6" component="h1" gutterBottom>
          Club Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Manage club information displayed in the bot
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

        <Box sx={{ mb: 3 }}>
          <TextField
            label="Address"
            value={formData.address}
            onChange={handleChange('address')}
            fullWidth
            multiline
            rows={2}
            helperText="Club address displayed in the bot"
            sx={{ mb: 2 }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label="Phone"
            value={formData.phone}
            onChange={handleChange('phone')}
            fullWidth
            helperText="Club phone number displayed in the bot"
            sx={{ mb: 2 }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label="Email"
            value={formData.email}
            onChange={handleChange('email')}
            fullWidth
            type="email"
            helperText="Club email address displayed in the bot"
            sx={{ mb: 2 }}
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
            onClick={fetchSettings}
            disabled={saving || loading}
            size="large"
          >
            Reset
          </Button>
        </Box>

        {settings?.updated_at && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Last updated: {new Date(settings.updated_at).toLocaleString()}
          </Typography>
        )}
      </Paper>
    </Container>
  )
}

export default ClubSettings

