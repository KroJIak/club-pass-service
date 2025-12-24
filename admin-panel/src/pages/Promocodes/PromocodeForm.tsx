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
import { Promocode, PromocodeCreate, PromocodeUpdate } from '../../types'
import TextField from '../../components/forms/TextField'
import BooleanField from '../../components/forms/BooleanField'

interface PromocodeFormProps {
  open: boolean
  promocode: Promocode | null
  onClose: () => void
}

const PromocodeForm = ({ open, promocode, onClose }: PromocodeFormProps) => {
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PromocodeCreate | PromocodeUpdate>({
    defaultValues: {
      code: '',
      discount_percent: null,
      discount_amount: null,
      valid_from: '',
      valid_until: '',
      usage_limit: null,
      is_active: true,
    },
  })

  const isActive = watch('is_active') ?? true

  useEffect(() => {
    if (promocode) {
      reset({
        code: promocode.code,
        discount_percent: promocode.discount_percent || null,
        discount_amount: promocode.discount_amount || null,
        valid_from: promocode.valid_from,
        valid_until: promocode.valid_until,
        usage_limit: promocode.usage_limit || null,
        is_active: promocode.is_active,
      })
    } else {
      reset({
        code: '',
        discount_percent: null,
        discount_amount: null,
        valid_from: '',
        valid_until: '',
        usage_limit: null,
        is_active: true,
      })
    }
  }, [promocode, reset])

  const onSubmit = async (data: PromocodeCreate | PromocodeUpdate) => {
    setLoading(true)
    try {
      if (promocode) {
        await api.put(`/admin/promocodes/${promocode.id}`, data)
      } else {
        await api.post('/admin/promocodes', data)
      }
      onClose()
    } catch (error) {
      console.error('Failed to save promocode:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{promocode ? 'Edit Promocode' : 'Create Promocode'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Code"
            {...register('code', { required: 'Code is required' })}
            error={!!errors.code}
            helperText={errors.code?.message}
          />
          <TextField
            label="Discount Percent"
            type="number"
            {...register('discount_percent', {
              valueAsNumber: true,
              validate: (value) => {
                const discountAmount = watch('discount_amount')
                if (value && discountAmount) {
                  return 'Cannot set both discount_percent and discount_amount'
                }
                if (value && (value < 0 || value > 100)) {
                  return 'Discount percent must be between 0 and 100'
                }
                return true
              },
            })}
            error={!!errors.discount_percent}
            helperText={errors.discount_percent?.message}
          />
          <TextField
            label="Discount Amount"
            type="number"
            {...register('discount_amount', {
              valueAsNumber: true,
              validate: (value) => {
                const discountPercent = watch('discount_percent')
                if (value && discountPercent) {
                  return 'Cannot set both discount_percent and discount_amount'
                }
                if (value && value < 0) {
                  return 'Discount amount must be positive'
                }
                return true
              },
            })}
            error={!!errors.discount_amount}
            helperText={errors.discount_amount?.message}
          />
          <TextField
            label="Valid From (YYYY-MM-DDTHH:mm:ss)"
            {...register('valid_from', { required: 'Valid from is required' })}
            error={!!errors.valid_from}
            helperText={errors.valid_from?.message}
            placeholder="2024-01-01T00:00:00"
          />
          <TextField
            label="Valid Until (YYYY-MM-DDTHH:mm:ss)"
            {...register('valid_until', { required: 'Valid until is required' })}
            error={!!errors.valid_until}
            helperText={errors.valid_until?.message}
            placeholder="2024-12-31T23:59:59"
          />
          <TextField
            label="Usage Limit"
            type="number"
            {...register('usage_limit', {
              valueAsNumber: true,
              min: { value: 1, message: 'Usage limit must be at least 1' },
            })}
            error={!!errors.usage_limit}
            helperText={errors.usage_limit?.message}
          />
          <BooleanField
            label="Active"
            value={isActive}
            onChange={(value) => setValue('is_active', value)}
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

export default PromocodeForm

