import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material'
import { useForm } from 'react-hook-form'
import api from '../../services/api'
import { TicketTypeCreate } from '../../types'
import TextField from '../../components/forms/TextField'

interface TicketTypeFormProps {
  open: boolean
  eventId: number
  onClose: () => void
  onSuccess: () => void
}

const TicketTypeForm = ({ open, eventId, onClose, onSuccess }: TicketTypeFormProps) => {
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TicketTypeCreate>({
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
      reset({
        event_id: eventId,
        name: '',
        price: 0,
        available_quantity: 0,
        total_quantity: 0,
        is_active: true,
      })
    }
  }, [open, eventId, reset])

  const onSubmit = async (data: TicketTypeCreate) => {
    setLoading(true)
    try {
      await api.post('/admin/ticket-types', data)
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Failed to create ticket type:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>Create Ticket Type</DialogTitle>
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
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default TicketTypeForm

