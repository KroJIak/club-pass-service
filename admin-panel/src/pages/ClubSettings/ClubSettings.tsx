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
  FormControlLabel,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
    auto_deactivate_events: true,
    timezone: 'Europe/Moscow',
  })

  // Common timezones for Russia and nearby regions
  const timezones = [
    { value: 'Europe/Kaliningrad', label: 'Калининград (UTC+2)' },
    { value: 'Europe/Moscow', label: 'Москва (UTC+3)' },
    { value: 'Europe/Samara', label: 'Самара (UTC+4)' },
    { value: 'Europe/Yekaterinburg', label: 'Екатеринбург (UTC+5)' },
    { value: 'Asia/Omsk', label: 'Омск (UTC+6)' },
    { value: 'Asia/Krasnoyarsk', label: 'Красноярск (UTC+7)' },
    { value: 'Asia/Irkutsk', label: 'Иркутск (UTC+8)' },
    { value: 'Asia/Yakutsk', label: 'Якутск (UTC+9)' },
    { value: 'Asia/Vladivostok', label: 'Владивосток (UTC+10)' },
    { value: 'Asia/Magadan', label: 'Магадан (UTC+11)' },
    { value: 'Asia/Kamchatka', label: 'Камчатка (UTC+12)' },
    { value: 'Europe/Astrakhan', label: 'Астрахань (UTC+4)' },
    { value: 'Europe/Volgograd', label: 'Волгоград (UTC+3)' },
    { value: 'Europe/Saratov', label: 'Саратов (UTC+4)' },
    { value: 'Europe/Ulyanovsk', label: 'Ульяновск (UTC+4)' },
  ]

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
        auto_deactivate_events: response.data.auto_deactivate_events ?? true,
        timezone: response.data.timezone || 'Europe/Moscow',
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

  const handleTimezoneChange = (e: any) => {
    setFormData({
      ...formData,
      timezone: e.target.value,
    })
  }

  const handleToggleAutoDeactivate = (checked: boolean) => {
    setFormData({
      ...formData,
      auto_deactivate_events: checked,
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
        auto_deactivate_events: formData.auto_deactivate_events,
        timezone: formData.timezone || null,
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

        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="timezone-label">Часовой пояс</InputLabel>
            <Select
              labelId="timezone-label"
              id="timezone-select"
              value={formData.timezone}
              label="Часовой пояс"
              onChange={handleTimezoneChange}
            >
              {timezones.map((tz) => (
                <MenuItem key={tz.value} value={tz.value}>
                  {tz.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Часовой пояс для отображения времени в системе
          </Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={formData.auto_deactivate_events}
                onChange={(e) => handleToggleAutoDeactivate(e.target.checked)}
                color="primary"
              />
            }
            label="Auto Deactivate Events"
          />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 1 }}>
            Automatically deactivate events and expire tickets when event end time is reached
          </Typography>
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

