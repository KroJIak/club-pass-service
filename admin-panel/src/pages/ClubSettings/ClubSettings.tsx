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
  IconButton,
  Card,
  CardMedia,
} from '@mui/material'
import { Delete as DeleteIcon, Add as AddIcon, DragIndicator } from '@mui/icons-material'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import type { ClubSettings, ClubSettingsUpdate, MenuPhoto, MenuPhotoReorderRequest } from '../../types'
import { usePermissions } from '../../hooks/usePermissions'

// Sortable Menu Photo Item Component
interface SortableMenuPhotoProps {
  photo: MenuPhoto
  onDelete: (id: number) => void
}

const SortableMenuPhoto = ({ photo, onDelete }: SortableMenuPhotoProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: photo.id })

  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const loadImage = async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await api.get(
          `/admin/menu-photos/${photo.id}/file`,
          {
            responseType: 'blob',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        const blob = new Blob([response.data])
        const url = URL.createObjectURL(blob)
        setImageUrl(url)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load menu photo:', err)
        setError(true)
        setLoading(false)
      }
    }

    loadImage()

    // Cleanup blob URL on unmount
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [photo.id])

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Card
      ref={setNodeRef}
      style={style}
      sx={{
        width: 200,
        height: 200,
        position: 'relative',
        cursor: 'grab',
        '&:active': {
          cursor: 'grabbing',
        },
      }}
    >
      <Box
        {...attributes}
        {...listeners}
        sx={{
          position: 'absolute',
          top: 8,
          left: 8,
          zIndex: 2,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          borderRadius: 1,
          padding: 0.5,
          display: 'flex',
          alignItems: 'center',
          cursor: 'grab',
        }}
      >
        <DragIndicator sx={{ color: 'white', fontSize: 20 }} />
      </Box>
      {loading ? (
        <Box
          sx={{
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'grey.200',
          }}
        >
          <CircularProgress size={24} />
        </Box>
      ) : error || !imageUrl ? (
        <Box
          sx={{
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'grey.200',
          }}
        >
          <Typography variant="caption" color="error">
            Failed to load
          </Typography>
        </Box>
      ) : (
        <CardMedia
          component="img"
          image={imageUrl}
          alt={photo.file_name}
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      )}
      <IconButton
        onClick={() => onDelete(photo.id)}
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          backgroundColor: 'rgba(255, 0, 0, 0.7)',
          color: 'white',
          '&:hover': {
            backgroundColor: 'rgba(255, 0, 0, 0.9)',
          },
        }}
        size="small"
      >
        <DeleteIcon fontSize="small" />
      </IconButton>
    </Card>
  )
}

const ClubSettings = () => {
  const { hasPermission } = usePermissions()
  const { t } = useTranslation('settings')
  const { t: tCommon } = useTranslation('common')
  const [settings, setSettings] = useState<ClubSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [menuPhotos, setMenuPhotos] = useState<MenuPhoto[]>([])
  const [loadingPhotos, setLoadingPhotos] = useState(false)
  const [uploadingPhoto, setUploadingPhoto] = useState(false)
  const [menuPhotosError, setMenuPhotosError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    address: '',
    phone: '',
    email: '',
    additional_info: '',
    auto_deactivate_events: true,
    timezone: 'Europe/Moscow',
  })

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

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
    fetchMenuPhotos()
  }, [])

  const fetchMenuPhotos = async () => {
    try {
      setLoadingPhotos(true)
      setMenuPhotosError(null)
      const response = await api.get<{ photos: MenuPhoto[] }>('/admin/menu-photos')
      setMenuPhotos(response.data.photos)
    } catch (err: any) {
      setMenuPhotosError(err.response?.data?.detail || t('clubSettings.messages.fetchFailed'))
      console.error('Failed to load menu photos:', err)
    } finally {
      setLoadingPhotos(false)
    }
  }

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (menuPhotos.length >= 10) {
      setError(t('clubSettings.messages.maxPhotosReached', { defaultValue: 'Maximum 10 menu photos allowed' }))
      return
    }

    try {
      setUploadingPhoto(true)
      setMenuPhotosError(null)
      const formData = new FormData()
      formData.append('file', file)

      await api.post<MenuPhoto>('/admin/menu-photos', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      await fetchMenuPhotos()
      // Reset file input
      event.target.value = ''
    } catch (err: any) {
      setMenuPhotosError(err.response?.data?.detail || t('clubSettings.messages.photoUploadSuccess'))
    } finally {
      setUploadingPhoto(false)
    }
  }

  const handlePhotoDelete = async (photoId: number) => {
    if (!window.confirm(tCommon('messages.deleteConfirm'))) return

    try {
      setMenuPhotosError(null)
      await api.delete(`/admin/menu-photos/${photoId}`)
      await fetchMenuPhotos()
    } catch (err: any) {
      setMenuPhotosError(err.response?.data?.detail || t('clubSettings.messages.photoDeleteSuccess'))
    }
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event

    if (!over || active.id === over.id) {
      return
    }

    const oldIndex = menuPhotos.findIndex((photo) => photo.id === active.id)
    const newIndex = menuPhotos.findIndex((photo) => photo.id === over.id)

    const newPhotos = arrayMove(menuPhotos, oldIndex, newIndex)
    setMenuPhotos(newPhotos)

    // Update display_order on server
    try {
      const reorderRequest: MenuPhotoReorderRequest = {
        photos: newPhotos.map((photo, index) => ({
          id: photo.id,
          display_order: index,
        })),
      }
      await api.put('/admin/menu-photos/reorder', reorderRequest)
    } catch (err: any) {
      setMenuPhotosError(err.response?.data?.detail || t('clubSettings.messages.reorderError', { defaultValue: 'Failed to reorder photos' }))
      // Revert on error
      await fetchMenuPhotos()
    }
  }

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
        additional_info: response.data.additional_info || '',
        auto_deactivate_events: response.data.auto_deactivate_events ?? true,
        timezone: response.data.timezone || 'Europe/Moscow',
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || t('clubSettings.messages.fetchFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: 'address' | 'phone' | 'email' | 'additional_info') => (
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
        additional_info: formData.additional_info.trim() || null,
        auto_deactivate_events: formData.auto_deactivate_events,
        timezone: formData.timezone || null,
      }

      const response = await api.put<ClubSettings>('/admin/club-settings', update)
      setSettings(response.data)
      setSuccess(true)
      
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || t('clubSettings.messages.saveError'))
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
          {t('clubSettings.title')}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          {t('clubSettings.description')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
            {t('clubSettings.messages.updateSuccess')}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          <TextField
            label={t('clubSettings.fields.address')}
            value={formData.address}
            onChange={handleChange('address')}
            fullWidth
            multiline
            rows={2}
            helperText={t('clubSettings.fields.addressHelper')}
            sx={{ mb: 2 }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label={t('clubSettings.fields.phone')}
            value={formData.phone}
            onChange={handleChange('phone')}
            fullWidth
            helperText={t('clubSettings.fields.phoneHelper')}
            sx={{ mb: 2 }}
            disabled={!hasPermission('club_settings', 'write')}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label={tCommon('fields.email')}
            value={formData.email}
            onChange={handleChange('email')}
            fullWidth
            type="email"
            helperText={t('clubSettings.fields.emailHelper')}
            sx={{ mb: 2 }}
            disabled={!hasPermission('club_settings', 'write')}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label={t('clubSettings.fields.additionalInfo')}
            value={formData.additional_info}
            onChange={handleChange('additional_info')}
            fullWidth
            multiline
            rows={3}
            helperText={t('clubSettings.fields.additionalInfoHelper')}
            sx={{ mb: 2 }}
            disabled={!hasPermission('club_settings', 'write')}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="timezone-label">{t('clubSettings.fields.timezone')}</InputLabel>
            <Select
              labelId="timezone-label"
              id="timezone-select"
              value={formData.timezone}
              label={t('clubSettings.fields.timezone')}
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
            {t('clubSettings.fields.timezoneHelper')}
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
            label={t('clubSettings.fields.autoDeactivateEvents')}
          />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 1 }}>
            {t('clubSettings.fields.autoDeactivateEventsHelper')}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving || !hasPermission('club_settings', 'write')}
            size="large"
          >
            {saving ? <CircularProgress size={24} /> : tCommon('actions.save')}
          </Button>
          <Button
            variant="outlined"
            onClick={fetchSettings}
            disabled={saving || loading}
            size="large"
          >
            {tCommon('actions.reset')}
          </Button>
        </Box>

        {settings?.updated_at && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            {tCommon('fields.date')}: {new Date(settings.updated_at).toLocaleString()}
          </Typography>
        )}
      </Paper>

      {/* Menu Photos Section */}
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {t('clubSettings.fields.menuPhotos')}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {t('clubSettings.fields.menuPhotosHelper')}
        </Typography>

        {menuPhotosError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setMenuPhotosError(null)}>
            {menuPhotosError}
          </Alert>
        )}

        {loadingPhotos ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={menuPhotos.map((p) => p.id)}
              strategy={horizontalListSortingStrategy}
            >
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  overflowX: 'auto',
                  pb: 2,
                  minHeight: 220,
                }}
              >
                {menuPhotos.map((photo) => (
                  <SortableMenuPhoto
                    key={photo.id}
                    photo={photo}
                    onDelete={handlePhotoDelete}
                  />
                ))}
                {menuPhotos.length < 10 && (
                  <Card
                    sx={{
                      width: 200,
                      height: 200,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      border: '2px dashed',
                      borderColor: 'divider',
                      cursor: uploadingPhoto ? 'wait' : 'pointer',
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'action.hover',
                      },
                    }}
                    component="label"
                  >
                    <input
                      type="file"
                      accept="image/*"
                      hidden
                      onChange={handlePhotoUpload}
                      disabled={uploadingPhoto}
                    />
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 1,
                      }}
                    >
                      {uploadingPhoto ? (
                        <CircularProgress size={24} />
                      ) : (
                        <>
                          <AddIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {tCommon('actions.add')}
                          </Typography>
                        </>
                      )}
                    </Box>
                  </Card>
                )}
              </Box>
            </SortableContext>
          </DndContext>
        )}

        {menuPhotos.length >= 10 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            {t('clubSettings.messages.maxPhotosReached')}
          </Alert>
        )}
      </Paper>
    </Container>
  )
}

export default ClubSettings

