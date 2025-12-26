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
  Grid,
  Card,
  CardContent,
  Autocomplete,
  TextField as MuiTextField,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import api from '../../services/api'
import { TicketType, TicketTypeCreate, TicketTypeUpdate, Event } from '../../types'
import TextField from '../../components/forms/TextField'
import BooleanField from '../../components/forms/BooleanField'

interface TicketTypeFormProps {
  open?: boolean
  ticketType: TicketType | null
  eventId?: number | null
  onClose: () => void
  onSuccess?: () => void
  embedded?: boolean
}

const TicketTypeForm = ({ 
  open = true, 
  ticketType, 
  eventId,
  onClose, 
  onSuccess,
  embedded = false 
}: TicketTypeFormProps) => {
  const [loading, setLoading] = useState(false)
  const [events, setEvents] = useState<Event[]>([])
  const [templates, setTemplates] = useState<TicketType[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<TicketType | null>(null)

  const {
    control,
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<TicketTypeCreate | TicketTypeUpdate>({
    defaultValues: {
      name: '',
      price: 0,
      available_quantity: 0,
      total_quantity: 0,
      is_active: true,
      is_template: false,
    },
  })

  useEffect(() => {
    fetchEvents()
    fetchTemplates()
  }, [])

  useEffect(() => {
    if (ticketType) {
      reset({
        name: ticketType.name,
        price: ticketType.price,
        available_quantity: ticketType.available_quantity,
        total_quantity: ticketType.total_quantity,
        is_active: ticketType.is_active,
        is_template: ticketType.is_template,
      })
      if (ticketType.event_id) {
        setValue('event_id', ticketType.event_id)
      }
    } else {
      reset({
        name: '',
        price: 0,
        available_quantity: 0,
        total_quantity: 0,
        is_active: true,
        is_template: false,
      })
      if (eventId) {
        setValue('event_id', eventId)
      }
    }
  }, [ticketType, eventId, reset, setValue])

  // Apply template when selected
  useEffect(() => {
    if (selectedTemplate && !ticketType) {
      setValue('name', selectedTemplate.name)
      setValue('price', selectedTemplate.price)
      setValue('available_quantity', selectedTemplate.available_quantity)
      setValue('total_quantity', selectedTemplate.total_quantity)
      setValue('is_active', selectedTemplate.is_active)
    }
  }, [selectedTemplate, ticketType, setValue])

  const fetchEvents = async () => {
    try {
      const response = await api.get('/admin/events')
      setEvents(response.data.events || [])
    } catch (error) {
      console.error('Failed to fetch events:', error)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/admin/ticket-types/templates')
      setTemplates(response.data.ticket_types || [])
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const onSubmit = async (data: TicketTypeCreate | TicketTypeUpdate) => {
    setLoading(true)
    try {
      if (ticketType) {
        await api.put(`/admin/ticket-types/${ticketType.id}`, data)
      } else {
        const createData: TicketTypeCreate = {
          ...data,
          event_id: eventId || (data as TicketTypeCreate).event_id || null,
          is_template: false, // New ticket types are never templates
        }
        await api.post('/admin/ticket-types', createData)
      }
      onSuccess?.()
      onClose()
    } catch (error: any) {
      console.error('Failed to save ticket type:', error)
      alert(error.response?.data?.detail || 'Failed to save ticket type')
    } finally {
      setLoading(false)
    }
  }

  const content = (
    <form onSubmit={handleSubmit(onSubmit)}>
      {embedded && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{ticketType ? 'Edit Ticket Type' : 'Create Ticket Type'}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {!embedded && <DialogTitle>{ticketType ? 'Edit Ticket Type' : 'Create Ticket Type'}</DialogTitle>}
      <DialogContent>
        {!ticketType && templates.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Templates:</Typography>
            <Grid container spacing={2}>
              {templates.map((template) => (
                <Grid item xs={12} sm={6} key={template.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      border: selectedTemplate?.id === template.id ? 2 : 1,
                      borderColor: selectedTemplate?.id === template.id ? 'primary.main' : 'divider',
                    }}
                    onClick={() => setSelectedTemplate(template)}
                  >
                    <CardContent>
                      <Typography variant="subtitle1">{template.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {template.price} ₽
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {!eventId && (
          <Controller
            name="event_id"
            control={control}
            rules={{ required: !ticketType ? 'Event is required' : false }}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={events}
                getOptionLabel={(option) => option.name}
                value={events.find(e => e.id === field.value) || null}
                onChange={(_, value) => field.onChange(value?.id || null)}
                disabled={!!ticketType}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label="Event"
                    error={!!(errors as any).event_id}
                    helperText={(errors as any).event_id?.message}
                    required={!ticketType}
                    sx={{ mb: 2 }}
                  />
                )}
              />
            )}
          />
        )}

        <TextField
          label="Name"
          {...register('name', { required: 'Name is required' })}
          error={!!errors.name}
          helperText={errors.name?.message}
        />
        <Controller
          name="price"
          control={control}
          rules={{ required: 'Price is required', min: { value: 0, message: 'Price must be positive' } }}
          render={({ field }) => (
            <TextField
              label="Price"
              type="number"
              {...field}
              onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
              error={!!errors.price}
              helperText={errors.price?.message}
            />
          )}
        />
        <Controller
          name="available_quantity"
          control={control}
          rules={{ required: 'Available quantity is required', min: { value: 0, message: 'Quantity must be non-negative' } }}
          render={({ field }) => (
            <TextField
              label="Available Quantity"
              type="number"
              {...field}
              onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
              error={!!errors.available_quantity}
              helperText={errors.available_quantity?.message}
            />
          )}
        />
        <Controller
          name="total_quantity"
          control={control}
          rules={{ required: 'Total quantity is required', min: { value: 0, message: 'Quantity must be non-negative' } }}
          render={({ field }) => (
            <TextField
              label="Total Quantity"
              type="number"
              {...field}
              onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
              error={!!errors.total_quantity}
              helperText={errors.total_quantity?.message}
            />
          )}
        />
        <Controller
          name="is_active"
          control={control}
          render={({ field }) => (
            <BooleanField
              label="Active"
              {...field}
            />
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {ticketType ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </form>
  )

  return (
    <>
      {embedded ? (
        <Box>{content}</Box>
      ) : (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
          {content}
        </Dialog>
      )}
    </>
  )
}

export default TicketTypeForm

