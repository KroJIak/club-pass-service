import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material'
import { useForm } from 'react-hook-form'
import api from '../../services/api'
import { TicketType, TicketTypeCreate, TicketTypeUpdate, TicketTypeTemplate } from '../../types'
import TextField from '../../components/forms/TextField'

interface TicketTypeFormProps {
  open: boolean
  eventId: number
  ticketType?: TicketType | null
  template?: TicketTypeTemplate | null
  onClose: () => void
  onSuccess: () => void
}

const TicketTypeForm = ({ open, eventId, ticketType, template, onClose, onSuccess }: TicketTypeFormProps) => {
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TicketTypeCreate | TicketTypeUpdate>({
    defaultValues: {
      event_id: eventId,
      name: '',
      price: 0,
      available_quantity: 0,
      total_quantity: 0,
      is_active: true,
    },
  })

  useEffect(() => {
    if (open) {
      if (ticketType) {
        reset({
          name: ticketType.name,
          price: ticketType.price,
          available_quantity: ticketType.available_quantity,
          total_quantity: ticketType.total_quantity,
          is_active: ticketType.is_active,
        })
      } else if (template) {
        reset({
          event_id: eventId,
          name: template.name,
          price: template.price,
          available_quantity: template.available_quantity,
          total_quantity: template.total_quantity,
          is_active: true,
        })
      } else {
        reset({
          event_id: eventId,
          name: '',
          price: 0,
          available_quantity: 0,
          total_quantity: 0,
          is_active: true,
        })
      }
    }
  }, [open, eventId, ticketType, template, reset])

  const onSubmit = async (data: TicketTypeCreate | TicketTypeUpdate) => {
    setLoading(true)
    try {
      if (ticketType) {
        await api.put(`/admin/ticket-types/${ticketType.id}`, data)
      } else {
        // Ensure all required fields are present for creation
        const createData: TicketTypeCreate = {
          event_id: eventId,
          name: data.name || '',
          price: data.price ?? 0,
          available_quantity: data.available_quantity ?? 0,
          total_quantity: data.total_quantity ?? 0,
          is_active: data.is_active ?? true,
        }
        await api.post('/admin/ticket-types', createData)
      }
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Failed to save ticket type:', error)
      alert(error.response?.data?.detail || 'Failed to save ticket type')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{ticketType ? 'Edit Ticket Type' : 'Create Ticket Type'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Name"
            {...register('name', { required: 'Name is required' })}
            error={!!errors.name}
            helperText={errors.name?.message}
          />
          <TextField
            label="Price"
            type="number"
            {...register('price', { 
              required: 'Price is required',
              valueAsNumber: true,
              min: { value: 0, message: 'Price must be positive' }
            })}
            error={!!errors.price}
            helperText={errors.price?.message}
          />
          <TextField
            label="Total Quantity"
            type="number"
            {...register('total_quantity', { 
              required: 'Total quantity is required',
              valueAsNumber: true,
              min: { value: 1, message: 'Quantity must be at least 1' }
            })}
            error={!!errors.total_quantity}
            helperText={errors.total_quantity?.message}
          />
          <TextField
            label="Available Quantity"
            type="number"
            {...register('available_quantity', { 
              required: 'Available quantity is required',
              valueAsNumber: true,
              min: { value: 0, message: 'Available quantity must be non-negative' }
            })}
            error={!!errors.available_quantity}
            helperText={errors.available_quantity?.message}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? (ticketType ? 'Updating...' : 'Creating...') : (ticketType ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default TicketTypeForm

