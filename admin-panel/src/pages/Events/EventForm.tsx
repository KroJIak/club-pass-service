import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  IconButton,
  Divider,
} from '@mui/material'
import { Close as CloseIcon, Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material'
import { useForm } from 'react-hook-form'
import api from '../../services/api'
import { Event, EventCreate, EventUpdate, TicketType, TicketTypeTemplate } from '../../types'
import TextField from '../../components/forms/TextField'
import DateField from '../../components/forms/DateField'
import TimeField from '../../components/forms/TimeField'
import ArrayField from '../../components/forms/ArrayField'
import BooleanField from '../../components/forms/BooleanField'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import TicketTypeForm from './TicketTypeForm'
import TicketTypeTemplateForm from '../TicketTypes/TicketTypeTemplateForm'
import { usePermissions } from '../../hooks/usePermissions'
import { useTranslation } from 'react-i18next'

interface EventFormProps {
  open?: boolean
  event: Event | null
  onClose: () => void
  embedded?: boolean
}

const EventForm = ({ open = true, event, onClose, embedded = false }: EventFormProps) => {
  const { hasPermission } = usePermissions()
  const { t } = useTranslation('events')
  const { t: tCommon } = useTranslation('common')
  const [loading, setLoading] = useState(false)
  const [djs, setDjs] = useState<string[]>([])
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [templates, setTemplates] = useState<TicketTypeTemplate[]>([])
  const [loadingTicketTypes, setLoadingTicketTypes] = useState(false)
  const [ticketTypeFormOpen, setTicketTypeFormOpen] = useState(false)
  const [templateFormOpen, setTemplateFormOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<TicketTypeTemplate | null>(null)
  const [editingTicketType, setEditingTicketType] = useState<TicketType | null>(null)
  const [deleteTicketTypeDialog, setDeleteTicketTypeDialog] = useState<{ open: boolean; ticketTypeId: number | null }>({
    open: false,
    ticketTypeId: null,
  })
  const [autoDeactivateEvents, setAutoDeactivateEvents] = useState<boolean>(true)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EventCreate | EventUpdate>({
    defaultValues: {
      name: '',
      description: '',
      start_date: '',
      start_time: '',
      end_date: '',
      end_time: '',
      djs: [],
      is_active: true,
    },
    mode: 'onChange',
  })

  const isActive = watch('is_active') ?? true
  const eventId = event?.id

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/admin/ticket-type-templates')
      setTemplates(response.data.templates || [])
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const fetchClubSettings = async () => {
    try {
      const response = await api.get('/admin/club-settings')
      setAutoDeactivateEvents(response.data.auto_deactivate_events ?? true)
    } catch (error) {
      console.error('Failed to fetch club settings:', error)
      // Default to true if fetch fails
      setAutoDeactivateEvents(true)
    }
  }

  useEffect(() => {
    fetchTemplates()
    fetchClubSettings()
  }, [])

  useEffect(() => {
    fetchTemplates()
  }, [])

  useEffect(() => {
    if (event) {
      reset({
        name: event.name,
        description: event.description || '',
        start_date: event.start_date,
        start_time: event.start_time,
        end_date: event.end_date,
        end_time: event.end_time,
        djs: event.djs || [],
        is_active: event.is_active,
      })
      setDjs(event.djs || [])
      if (event.id) {
        fetchTicketTypes(event.id)
      }
    } else {
      reset({
        name: '',
        description: '',
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        djs: [],
        is_active: true,
      })
      setDjs([])
      setTicketTypes([])
    }
  }, [event, reset])

  // Register date and time for validation
  useEffect(() => {
    register('start_date', { required: t('fields.startDate') + ' ' + tCommon('messages.required') })
    register('start_time', { required: t('fields.startTime') + ' ' + tCommon('messages.required') })
    register('end_date', { required: t('fields.endDate') + ' ' + tCommon('messages.required') })
    register('end_time', { required: t('fields.endTime') + ' ' + tCommon('messages.required') })
  }, [register, t, tCommon])

  const fetchTicketTypes = async (eventId: number) => {
    setLoadingTicketTypes(true)
    try {
      const response = await api.get(`/events/${eventId}/ticket-types?active_only=false`)
      setTicketTypes(response.data.ticket_types)
    } catch (error) {
      console.error('Failed to fetch ticket types:', error)
    } finally {
      setLoadingTicketTypes(false)
    }
  }

  const validateDateTime = (startDate: string, startTime: string, endDate: string, endTime: string): string | null => {
    if (!startDate || !startTime || !endDate || !endTime) {
      return null // Let required validation handle empty fields
    }
    
    try {
      const parseDate = (dateStr: string, timeStr: string): Date => {
        const [day, month, year] = dateStr.split('.')
        const [hours, minutes] = timeStr.split(':')
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hours), parseInt(minutes))
      }
      
      const startDt = parseDate(startDate, startTime)
      const endDt = parseDate(endDate, endTime)
      
      if (endDt <= startDt) {
        return t('messages.cannotActivatePastEvent')
      }
    } catch (e) {
      // Invalid format will be caught by other validators
      return null
    }
    
    return null
  }

  const onSubmit = async (data: EventCreate | EventUpdate) => {
    // Validate datetime
    const startDate = data.start_date || (event?.start_date ?? '')
    const startTime = data.start_time || (event?.start_time ?? '')
    const endDate = data.end_date || (event?.end_date ?? '')
    const endTime = data.end_time || (event?.end_time ?? '')
    
    const dateTimeError = validateDateTime(startDate, startTime, endDate, endTime)
    if (dateTimeError) {
      setValue('end_date', endDate, { shouldValidate: true })
      setValue('end_time', endTime, { shouldValidate: true })
      // Show error on end_time field
      return
    }
    
    // Check if trying to activate event with past end date/time
    // Only validate if auto_deactivate_events is enabled
    const willBeActive = data.is_active !== undefined ? data.is_active : (event?.is_active ?? true)
    if (willBeActive && endDate && endTime && autoDeactivateEvents) {
      try {
        const parseDate = (dateStr: string, timeStr: string): Date => {
          const [day, month, year] = dateStr.split('.')
          const [hours, minutes] = timeStr.split(':')
          return new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hours), parseInt(minutes))
        }
        
        const endDt = parseDate(endDate, endTime)
        const now = new Date()
        
        if (endDt <= now) {
          alert(t('messages.cannotActivatePastEvent'))
          setValue('is_active', false, { shouldValidate: true })
          return
        }
      } catch (e) {
        // Invalid format will be caught by other validators
      }
    }
    
    setLoading(true)
    try {
      const payload = { ...data, djs: djs.length > 0 ? djs : null }
      if (event) {
        await api.put(`/admin/events/${event.id}`, payload)
      } else {
        const response = await api.post('/admin/events', payload)
        // After creating event, fetch ticket types if event was created
        if (response.data.id) {
          await fetchTicketTypes(response.data.id)
        }
      }
      onClose()
    } catch (error: any) {
      console.error('Failed to save event:', error)
      if (error.response?.data?.detail) {
        // Show error message
        alert(error.response.data.detail)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleTicketTypeCreated = () => {
    if (eventId) {
      fetchTicketTypes(eventId)
    }
  }

  const handleDeleteTicketType = async (ticketTypeId: number) => {
    try {
      await api.delete(`/admin/ticket-types/${ticketTypeId}`)
      if (eventId) {
        fetchTicketTypes(eventId)
      }
    } catch (error) {
      console.error('Failed to delete ticket type:', error)
    }
    setDeleteTicketTypeDialog({ open: false, ticketTypeId: null })
  }

  const content = (
    <form onSubmit={handleSubmit(onSubmit)}>
      {embedded && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{t('eventDetails')}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {!embedded && <DialogTitle>{event ? t('editEvent') : t('createEvent')}</DialogTitle>}
      <DialogContent>
        <TextField
          label={t('fields.name')}
          {...register('name', { required: t('fields.name') + ' ' + tCommon('messages.required') })}
          error={!!errors.name}
          helperText={errors.name?.message}
          disabled={!hasPermission('events', 'write')}
        />
        <TextField
          label={t('fields.description')}
          multiline
          rows={3}
          {...register('description')}
          disabled={!hasPermission('events', 'write')}
        />
        <DateField
          label={t('fields.startDate')}
          value={watch('start_date') || null}
          onChange={(value) => {
            setValue('start_date', value || '', { shouldValidate: true })
            // Trigger validation on end fields if they exist
            const endDate = watch('end_date')
            const endTime = watch('end_time')
            if (endDate && endTime) {
              const startTime = watch('start_time')
              if (startTime) {
                const error = validateDateTime(value || '', startTime, endDate, endTime)
                if (error) {
                  setValue('end_time', endTime, { shouldValidate: true })
                }
              }
            }
          }}
          error={!!errors.start_date}
          helperText={errors.start_date?.message}
          disabled={!hasPermission('events', 'write')}
        />
        <TimeField
          label={t('fields.startTime')}
          value={watch('start_time') || null}
          onChange={(value) => {
            setValue('start_time', value || '', { shouldValidate: true })
            // Trigger validation on end fields if they exist
            const endDate = watch('end_date')
            const endTime = watch('end_time')
            if (endDate && endTime) {
              const startDate = watch('start_date')
              if (startDate) {
                const error = validateDateTime(startDate, value || '', endDate, endTime)
                if (error) {
                  setValue('end_time', endTime, { shouldValidate: true })
                }
              }
            }
          }}
          error={!!errors.start_time}
          helperText={errors.start_time?.message}
          disabled={!hasPermission('events', 'write')}
        />
        <DateField
          label={t('fields.endDate')}
          value={watch('end_date') || null}
          onChange={(value) => {
            setValue('end_date', value || '', { shouldValidate: true })
          }}
          error={!!errors.end_date}
          helperText={errors.end_date?.message}
          disabled={!hasPermission('events', 'write')}
        />
        <TimeField
          label={t('fields.endTime')}
          value={watch('end_time') || null}
          onChange={(value) => {
            setValue('end_time', value || '', { shouldValidate: true })
          }}
          error={!!errors.end_time}
          helperText={errors.end_time?.message}
          disabled={!hasPermission('events', 'write')}
        />
        <ArrayField
          label={t('fields.djs')}
          value={djs}
          onChange={(value) => {
            setDjs(value)
            setValue('djs', value)
          }}
          disabled={!hasPermission('events', 'write')}
        />
        <BooleanField
          label={t('ticketTypes.isActive')}
          value={isActive}
          onChange={(value) => setValue('is_active', value)}
          disabled={!hasPermission('events', 'write')}
        />

        {eventId && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">{t('ticketTypes.title')}</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {hasPermission('events', 'write') && (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => setTemplateFormOpen(true)}
                  >
                    {t('ticketTypes.saveAsTemplate')}
                  </Button>
                )}
                {hasPermission('events', 'write') && (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => {
                      setEditingTicketType(null)
                      setSelectedTemplate(null)
                      setTicketTypeFormOpen(true)
                    }}
                    disabled={!eventId}
                  >
                    {t('ticketTypes.create')}
                  </Button>
                )}
              </Box>
            </Box>
            {/* Display templates as buttons */}
            {hasPermission('events', 'write') && templates && templates.length > 0 && (
              <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                  {t('ticketTypes.templates')}:
                </Typography>
                {templates.map((template) => (
                  <Button
                    key={template.id}
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      setSelectedTemplate(template)
                      setTicketTypeFormOpen(true)
                    }}
                    sx={{ position: 'relative', pr: hasPermission('events', 'delete') ? 4 : 1.5 }}
                  >
                    {template.name}
                    {hasPermission('events', 'delete') && (
                      <IconButton
                        size="small"
                        color="error"
                        onClick={async (e) => {
                          e.stopPropagation()
                          if (confirm(t('messages.deleteConfirm'))) {
                            try {
                              await api.delete(`/admin/ticket-type-templates/${template.id}`)
                              fetchTemplates()
                            } catch (error: any) {
                              console.error('Failed to delete template:', error)
                              alert(error.response?.data?.detail || tCommon('messages.deleteError'))
                            }
                          }
                        }}
                        title={tCommon('actions.delete')}
                        sx={{
                          position: 'absolute',
                          right: 4,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          padding: 0.5,
                        }}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Button>
                ))}
              </Box>
            )}
            {loadingTicketTypes ? (
              <Typography>{tCommon('status.loading')}</Typography>
            ) : ticketTypes.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                {t('ticketTypes.noTicketTypes', 'No ticket types yet.')}
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {ticketTypes.map((tt) => (
                  <Box
                    key={tt.id}
                    onClick={hasPermission('events', 'write') ? () => {
                      setEditingTicketType(tt)
                      setSelectedTemplate(null)
                      setTicketTypeFormOpen(true)
                    } : undefined}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      cursor: hasPermission('events', 'write') ? 'pointer' : 'default',
                      '&:hover': hasPermission('events', 'write') ? {
                        backgroundColor: 'action.hover',
                      } : {},
                    }}
                  >
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {tt.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {tCommon('fields.price')}: {tt.price % 1 === 0 ? Math.floor(tt.price) : tt.price} ₽ | {t('ticketTypes.available')}: {tt.available_quantity} / {tt.total_quantity}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {hasPermission('events', 'write') && (
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            setEditingTicketType(tt)
                            setSelectedTemplate(null)
                            setTicketTypeFormOpen(true)
                          }}
                          title={tCommon('actions.edit')}
                        >
                          <EditIcon />
                        </IconButton>
                      )}
                      {hasPermission('events', 'delete') && (
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation()
                            setDeleteTicketTypeDialog({ open: true, ticketTypeId: tt.id })
                          }}
                          title={tCommon('actions.delete')}
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{tCommon('actions.cancel')}</Button>
        {hasPermission('events', 'write') && (
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? (event ? tCommon('status.saving') : tCommon('status.loading')) : (event ? tCommon('actions.save') : tCommon('actions.create'))}
          </Button>
        )}
      </DialogActions>
    </form>
  )

  return (
    <>
      {embedded ? (
        <Box>{content}</Box>
      ) : (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
          {content}
        </Dialog>
      )}
      {eventId && (
        <TicketTypeForm
          open={ticketTypeFormOpen}
          eventId={eventId}
          ticketType={editingTicketType}
          template={selectedTemplate}
          onClose={() => {
            setTicketTypeFormOpen(false)
            setEditingTicketType(null)
            setSelectedTemplate(null)
          }}
          onSuccess={() => {
            handleTicketTypeCreated()
            setEditingTicketType(null)
            setSelectedTemplate(null)
          }}
        />
      )}
      <ConfirmDialog
        open={deleteTicketTypeDialog.open}
        title={t('ticketTypes.delete')}
        message={tCommon('messages.confirmDelete')}
        onConfirm={() => deleteTicketTypeDialog.ticketTypeId && handleDeleteTicketType(deleteTicketTypeDialog.ticketTypeId)}
        onCancel={() => setDeleteTicketTypeDialog({ open: false, ticketTypeId: null })}
      />
      <TicketTypeTemplateForm
        open={templateFormOpen}
        onClose={() => setTemplateFormOpen(false)}
        onSuccess={async () => {
          await fetchTemplates()
          setTemplateFormOpen(false)
        }}
      />
    </>
  )
}

export default EventForm
