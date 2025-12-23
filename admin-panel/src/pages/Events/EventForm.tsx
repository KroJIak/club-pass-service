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
import { Event, EventCreate, EventUpdate } from '../../types'
import TextField from '../../components/forms/TextField'
import DateField from '../../components/forms/DateField'
import TimeField from '../../components/forms/TimeField'
import ArrayField from '../../components/forms/ArrayField'
import BooleanField from '../../components/forms/BooleanField'

interface EventFormProps {
  open: boolean
  event: Event | null
  onClose: () => void
}

const EventForm = ({ open, event, onClose }: EventFormProps) => {
  const [loading, setLoading] = useState(false)
  const [djs, setDjs] = useState<string[]>([])

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
    }
  }, [event, reset])

  const onSubmit = async (data: EventCreate | EventUpdate) => {
    setLoading(true)
    try {
      const payload = { ...data, djs: djs.length > 0 ? djs : null }
      if (event) {
        await api.put(`/admin/events/${event.id}`, payload)
      } else {
        await api.post('/admin/events', payload)
      }
      onClose()
    } catch (error) {
      console.error('Failed to save event:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{event ? 'Edit Event' : 'Create Event'}</DialogTitle>
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

export default EventForm

