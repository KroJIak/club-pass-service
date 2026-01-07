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
  Autocomplete,
  TextField as MuiTextField,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import api from '../../services/api'
import { TicketType, TicketTypeTemplate, TicketTypeCreate, TicketTypeUpdate, Event } from '../../types'
import TextField from '../../components/forms/TextField'
import BooleanField from '../../components/forms/BooleanField'
import { usePermissions } from '../../hooks/usePermissions'
import { useTranslation } from 'react-i18next'

interface TicketTypeFormProps {
  open?: boolean
  ticketType: TicketType | null
  template?: TicketTypeTemplate | null
  eventId?: number | null
  onClose: () => void
  onSuccess?: () => void
  embedded?: boolean
}

const TicketTypeForm = ({ 
  open = true, 
  ticketType,
  template,
  eventId,
  onClose, 
  onSuccess,
  embedded = false 
}: TicketTypeFormProps) => {
  const { t } = useTranslation('settings')
  const { t: tCommon } = useTranslation('common')
  const { hasPermission } = usePermissions()
  const [loading, setLoading] = useState(false)
  const [events, setEvents] = useState<Event[]>([])

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
    },
  })

  useEffect(() => {
    fetchEvents()
  }, [])

  useEffect(() => {
    if (ticketType) {
      reset({
        name: ticketType.name,
        price: ticketType.price,
        available_quantity: ticketType.available_quantity,
        total_quantity: ticketType.total_quantity,
        is_active: ticketType.is_active,
      })
      if (ticketType.event_id) {
        setValue('event_id', ticketType.event_id)
      }
    } else if (template) {
      // Fill form with template data
      reset({
        name: template.name,
        price: template.price,
        available_quantity: template.available_quantity,
        total_quantity: template.total_quantity,
        is_active: template.is_active,
      })
      if (eventId) {
        setValue('event_id', eventId)
      }
    } else {
      reset({
        name: '',
        price: 0,
        available_quantity: 0,
        total_quantity: 0,
        is_active: true,
      })
      if (eventId) {
        setValue('event_id', eventId)
      }
    }
  }, [ticketType, template, eventId, reset, setValue])

  const fetchEvents = async () => {
    try {
      const response = await api.get('/admin/events')
      setEvents(response.data.events || [])
    } catch (error) {
      console.error('Failed to fetch events:', error)
    }
  }

  const onSubmit = async (data: TicketTypeCreate | TicketTypeUpdate) => {
    setLoading(true)
    try {
      if (ticketType) {
        await api.put(`/admin/ticket-types/${ticketType.id}`, data)
      } else {
        // Ensure all required fields are present for creation
        const createData: TicketTypeCreate = {
          name: data.name || '',
          price: data.price || 0,
          available_quantity: data.available_quantity || 0,
          total_quantity: data.total_quantity || 0,
          is_active: data.is_active ?? true,
          event_id: eventId || (data as TicketTypeCreate).event_id!,
        }
        await api.post('/admin/ticket-types', createData)
      }
      onSuccess?.()
      onClose()
    } catch (error: any) {
      console.error('Failed to save ticket type:', error)
      alert(error.response?.data?.detail || t('ticketTypes.messages.saveError'))
    } finally {
      setLoading(false)
    }
  }

  const content = (
    <form onSubmit={handleSubmit(onSubmit)}>
      {embedded && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{ticketType ? t('ticketTypes.actions.edit') : t('ticketTypes.actions.create')}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {!embedded && <DialogTitle>{ticketType ? t('ticketTypes.actions.edit') : t('ticketTypes.actions.create')}</DialogTitle>}
      <DialogContent>
        {!eventId && (
          <Controller
            name="event_id"
            control={control}
            rules={{ required: !ticketType ? t('ticketTypes.validation.eventRequired') : false }}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={events}
                getOptionLabel={(option) => option.name}
                value={events.find(e => e.id === field.value) || null}
                onChange={(_, value) => field.onChange(value?.id || null)}
                disabled={!!ticketType || !hasPermission('tickets', 'write')}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label={t('ticketTypes.fields.event')}
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
          label={tCommon('fields.name')}
          {...register('name', { required: t('ticketTypes.validation.nameRequired') })}
          error={!!errors.name}
          helperText={errors.name?.message}
          disabled={!hasPermission('tickets', 'write')}
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
              disabled={!hasPermission('tickets', 'write')}
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
              disabled={!hasPermission('tickets', 'write')}
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
              disabled={!hasPermission('tickets', 'write')}
            />
          )}
        />
        <Controller
          name="is_active"
          control={control}
          render={({ field }) => (
            <BooleanField
              label={tCommon('status.active')}
              {...field}
              value={field.value ?? true}
              disabled={!hasPermission('tickets', 'write')}
            />
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          {tCommon('actions.cancel')}
        </Button>
        {hasPermission('tickets', 'write') && (
          <Button type="submit" variant="contained" disabled={loading}>
            {ticketType ? tCommon('actions.update') : tCommon('actions.create')}
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
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
          {content}
        </Dialog>
      )}
    </>
  )
}

export default TicketTypeForm

