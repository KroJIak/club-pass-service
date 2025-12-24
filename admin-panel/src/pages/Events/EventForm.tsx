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
import { Close as CloseIcon, Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { useForm } from 'react-hook-form'
import api from '../../services/api'
import { Event, EventCreate, EventUpdate, TicketType } from '../../types'
import TextField from '../../components/forms/TextField'
import DateField from '../../components/forms/DateField'
import TimeField from '../../components/forms/TimeField'
import ArrayField from '../../components/forms/ArrayField'
import BooleanField from '../../components/forms/BooleanField'
import ConfirmDialog from '../../components/common/ConfirmDialog'

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
  const [loadingTicketTypes, setLoadingTicketTypes] = useState(false)
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
      date: '',
      time: '',
      djs: [],
      is_active: true,
    },
  })

  const isActive = watch('is_active') ?? true
  const eventId = event?.id

  useEffect(() => {
    if (event) {
      reset({
        name: event.name,
        description: event.description || '',
        date: event.date,
        time: event.time,
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
        date: '',
        time: '',
        djs: [],
        is_active: true,
      })
      setDjs([])
      setTicketTypes([])
    }
  }, [event, reset])

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

  const onSubmit = async (data: EventCreate | EventUpdate) => {
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
    } catch (error) {
      console.error('Failed to save event:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTicketType = async () => {
    if (!eventId) return
    
    const name = prompt('Enter ticket type name:')
    if (!name) return
    
    const priceStr = prompt('Enter price:')
    if (!priceStr) return
    const price = parseFloat(priceStr)
    
    const totalQuantityStr = prompt('Enter total quantity:')
    if (!totalQuantityStr) return
    const totalQuantity = parseInt(totalQuantityStr)
    
    try {
      await api.post('/admin/ticket-types', {
        event_id: eventId,
        name,
        price,
        available_quantity: totalQuantity,
        total_quantity: totalQuantity,
        is_active: true,
      })
      if (eventId) {
        fetchTicketTypes(eventId)
      }
    } catch (error) {
      console.error('Failed to create ticket type:', error)
      alert('Failed to create ticket type')
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
          label="Date"
          value={watch('date') || null}
          onChange={(value) => setValue('date', value || '')}
        />
        <TimeField
          label="Time"
          value={watch('time') || null}
          onChange={(value) => setValue('time', value || '')}
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
              <Button
                variant="outlined"
                size="small"
                startIcon={<AddIcon />}
                onClick={handleCreateTicketType}
              >
                Add Ticket Type
              </Button>
            </Box>
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
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                    }}
                  >
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {tt.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Price: {tt.price} ₽ | Available: {tt.available_quantity} / {tt.total_quantity}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => setDeleteTicketTypeDialog({ open: true, ticketTypeId: tt.id })}
                    >
                      <DeleteIcon />
                    </IconButton>
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
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </form>
  )

  if (embedded) {
    return content
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      {content}
      <ConfirmDialog
        open={deleteTicketTypeDialog.open}
        title="Delete Ticket Type"
        message="Are you sure you want to delete this ticket type? This action cannot be undone."
        onConfirm={() => deleteTicketTypeDialog.ticketTypeId && handleDeleteTicketType(deleteTicketTypeDialog.ticketTypeId)}
        onCancel={() => setDeleteTicketTypeDialog({ open: false, ticketTypeId: null })}
      />
    </Dialog>
  )
}

export default EventForm
