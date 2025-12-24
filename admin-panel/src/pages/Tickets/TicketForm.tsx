import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  MenuItem,
} from '@mui/material'
import { useForm, Controller } from 'react-hook-form'
import api from '../../services/api'
import { Ticket, TicketUpdate } from '../../types'
import TextField from '../../components/forms/TextField'

interface TicketFormProps {
  open: boolean
  ticket: Ticket | null
  onClose: () => void
}

const TicketForm = ({ open, ticket, onClose }: TicketFormProps) => {
  const [loading, setLoading] = useState(false)

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TicketUpdate>({
    defaultValues: {
      status: 'active',
    },
  })

  useEffect(() => {
    if (ticket) {
      reset({
        status: ticket.status,
      })
    } else {
      reset({
        status: 'active',
      })
    }
  }, [ticket, reset])

  const onSubmit = async (data: TicketUpdate) => {
    setLoading(true)
    try {
      if (ticket) {
        await api.put(`/admin/tickets/${ticket.id}`, data)
      }
      onClose()
    } catch (error) {
      console.error('Failed to save ticket:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>Edit Ticket</DialogTitle>
        <DialogContent>
          <Controller
            name="status"
            control={control}
            rules={{ required: 'Status is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Status"
                error={!!errors.status}
                helperText={errors.status?.message}
                sx={{ mt: 2 }}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="refunded">Refunded</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
                <MenuItem value="expired">Expired</MenuItem>
                <MenuItem value="used">Used</MenuItem>
              </TextField>
            )}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default TicketForm

