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
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import api from '../../services/api'
import { TicketTypeTemplateCreate } from '../../types'
import TextField from '../../components/forms/TextField'
import BooleanField from '../../components/forms/BooleanField'

interface TicketTypeTemplateFormProps {
  open?: boolean
  onClose: () => void
  onSuccess?: () => void
}

const TicketTypeTemplateForm = ({ 
  open = true, 
  onClose, 
  onSuccess,
}: TicketTypeTemplateFormProps) => {
  const [loading, setLoading] = useState(false)

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TicketTypeTemplateCreate>({
    defaultValues: {
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
        name: '',
        price: 0,
        available_quantity: 0,
        total_quantity: 0,
        is_active: true,
      })
    }
  }, [open, reset])

  const onSubmit = async (data: TicketTypeTemplateCreate) => {
    setLoading(true)
    try {
      await api.post('/admin/ticket-type-templates', data)
      onSuccess?.()
      onClose()
    } catch (error: any) {
      console.error('Failed to save template:', error)
      alert(error.response?.data?.detail || 'Failed to save template')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Create Template</Typography>
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
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
                value={field.value ?? true}
              />
            )}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            Create
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default TicketTypeTemplateForm

