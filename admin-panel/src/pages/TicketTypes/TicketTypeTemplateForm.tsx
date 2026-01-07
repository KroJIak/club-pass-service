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
import { useTranslation } from 'react-i18next'

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
  const { t } = useTranslation('settings')
  const { t: tCommon } = useTranslation('common')
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
    },
  })

  useEffect(() => {
    if (open) {
      reset({
        name: '',
        price: 0,
        available_quantity: 0,
        total_quantity: 0,
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
      alert(error.response?.data?.detail || t('ticketTypes.messages.saveError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">{t('ticketTypes.actions.createTemplate')}</Typography>
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            label={tCommon('fields.name')}
            {...register('name', { required: t('ticketTypes.validation.nameRequired') })}
            error={!!errors.name}
            helperText={errors.name?.message}
          />
          <Controller
            name="price"
            control={control}
            rules={{ required: t('ticketTypes.validation.priceRequired'), min: { value: 0, message: t('ticketTypes.validation.pricePositive') } }}
            render={({ field }) => (
              <TextField
                label={tCommon('fields.price')}
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
            rules={{ required: t('ticketTypes.validation.availableQuantityRequired'), min: { value: 0, message: t('ticketTypes.validation.availableQuantityNonNegative') } }}
            render={({ field }) => (
              <TextField
                label={t('ticketTypes.fields.availableQuantity')}
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
            rules={{ required: t('ticketTypes.validation.totalQuantityRequired'), min: { value: 0, message: t('ticketTypes.validation.availableQuantityNonNegative') } }}
            render={({ field }) => (
              <TextField
                label={t('ticketTypes.fields.totalQuantity')}
                type="number"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                error={!!errors.total_quantity}
                helperText={errors.total_quantity?.message}
              />
            )}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            {tCommon('actions.cancel')}
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {tCommon('actions.create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
  )
}

export default TicketTypeTemplateForm

