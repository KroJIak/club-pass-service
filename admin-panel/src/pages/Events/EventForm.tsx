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

interface EventFormProps {
  open?: boolean
  event: Event | null
  onClose: () => void
  embedded?: boolean
}

const EventForm = ({ open = true, event, onClose, embedded = false }: EventFormProps) => {
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

  useEffect(() => {
    fetchTemplates()
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
    register('start_date', { required: 'Start date is required' })
    register('start_time', { required: 'Start time is required' })
    register('end_date', { required: 'End date is required' })
    register('end_time', { required: 'End time is required' })
  }, [register])

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
        return 'End date and time must be later than start date and time'
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
    const willBeActive = data.is_active !== undefined ? data.is_active : (event?.is_active ?? true)
    if (willBeActive && endDate && endTime) {
      try {
        const parseDate = (dateStr: string, timeStr: string): Date => {
          const [day, month, year] = dateStr.split('.')
          const [hours, minutes] = timeStr.split(':')
          return new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hours), parseInt(minutes))
        }
        
        const endDt = parseDate(endDate, endTime)
        const now = new Date()
        
        if (endDt <= now) {
          alert('Cannot activate event with end date and time in the past')
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

  const handleCreateTicketType = () => {
    if (!eventId) return
    setTicketTypeFormOpen(true)
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
          <Typography variant="h6">Event Settings</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {!embedded && <DialogTitle>{event ? 'Edit Event' : 'Create Event'}</DialogTitle>}
      <DialogContent>
        <TextField
          label="Name"
          {...register('name', { required: 'Name is required' })}
          error={!!errors.name}
          helperText={errors.name?.message}
        />
        <TextField
          label="Description"
          multiline
          rows={3}
          {...register('description')}
        />
        <DateField
          label="Start Date"
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
        />
        <TimeField
          label="Start Time"
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
        />
        <DateField
          label="End Date"
          value={watch('end_date') || null}
          onChange={(value) => {
            setValue('end_date', value || '', { shouldValidate: true })
          }}
          error={!!errors.end_date}
          helperText={errors.end_date?.message || 'Date when the event ends'}
        />
        <TimeField
          label="End Time"
          value={watch('end_time') || null}
          onChange={(value) => {
            setValue('end_time', value || '', { shouldValidate: true })
          }}
          error={!!errors.end_time}
          helperText={errors.end_time?.message || 'Time when the event ends'}
        />
        <ArrayField
          label="DJs"
          value={djs}
          onChange={(value) => {
            setDjs(value)
            setValue('djs', value)
          }}
        />
        <BooleanField
          label="Active"
          value={isActive}
          onChange={(value) => setValue('is_active', value)}
        />

        {eventId && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Ticket Types</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => setTemplateFormOpen(true)}
                >
                  Create Template
                </Button>
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
                  Add Ticket Type
                </Button>
              </Box>
            </Box>
            {/* Display templates as buttons */}
            {templates && templates.length > 0 && (
              <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                  Templates:
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
                    sx={{ position: 'relative', pr: 4 }}
                  >
                    {template.name}
                    <IconButton
                      size="small"
                      color="error"
                      onClick={async (e) => {
                        e.stopPropagation()
                        if (confirm(`Delete template "${template.name}"?`)) {
                          try {
                            await api.delete(`/admin/ticket-type-templates/${template.id}`)
                            fetchTemplates()
                          } catch (error: any) {
                            console.error('Failed to delete template:', error)
                            alert(error.response?.data?.detail || 'Failed to delete template')
                          }
                        }
                      }}
                      title="Delete template"
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
                  </Button>
                ))}
              </Box>
            )}
            {loadingTicketTypes ? (
              <Typography>Loading ticket types...</Typography>
            ) : ticketTypes.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No ticket types yet. Click "Add Ticket Type" to create one.
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {ticketTypes.map((tt) => (
                  <Box
                    key={tt.id}
                    onClick={() => {
                      setEditingTicketType(tt)
                      setSelectedTemplate(null)
                      setTicketTypeFormOpen(true)
                    }}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {tt.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Price: {tt.price % 1 === 0 ? Math.floor(tt.price) : tt.price} ₽ | Available: {tt.available_quantity} / {tt.total_quantity}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingTicketType(tt)
                          setSelectedTemplate(null)
                          setTicketTypeFormOpen(true)
                        }}
                        title="Edit"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDeleteTicketTypeDialog({ open: true, ticketTypeId: tt.id })
                        }}
                        title="Delete"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {loading ? (event ? 'Saving...' : 'Creating...') : (event ? 'Save' : 'Create')}
        </Button>
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
        title="Delete Ticket Type"
        message="Are you sure you want to delete this ticket type? This action cannot be undone."
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
