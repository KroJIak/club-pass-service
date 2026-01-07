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
import { User, UserCreate, UserUpdate } from '../../types'
import TextField from '../../components/forms/TextField'
import { useTranslation } from 'react-i18next'

interface UserFormProps {
  open: boolean
  user: User | null
  onClose: () => void
}

const UserForm = ({ open, user, onClose }: UserFormProps) => {
  const { t } = useTranslation('users')
  const { t: tCommon } = useTranslation('common')
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UserCreate | UserUpdate>({
    defaultValues: user ? {
      username: '',
      first_name: '',
      last_name: '',
    } : {
      telegram_user_id: 0,
      username: '',
      first_name: '',
      last_name: '',
    },
  })

  useEffect(() => {
    if (user) {
      reset({
        username: user.username || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      })
    } else {
      reset({
        telegram_user_id: 0,
        username: '',
        first_name: '',
        last_name: '',
      })
    }
  }, [user, reset])

  const onSubmit = async (data: UserCreate | UserUpdate) => {
    setLoading(true)
    try {
      if (user) {
        await api.put(`/admin/users/${user.id}`, data)
      } else {
        await api.post('/admin/users', data)
      }
      onClose()
    } catch (error: any) {
      console.error('Failed to save user:', error)
      alert(error.response?.data?.detail || t('messages.saveError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{user ? t('actions.edit') : t('actions.create')}</DialogTitle>
        <DialogContent>
          {!user && (
            <TextField
              label={t('fields.telegramId')}
              type="number"
              {...register('telegram_user_id' as keyof UserCreate, {
                required: t('validation.telegramIdRequired'),
                valueAsNumber: true,
                min: { value: 1, message: t('validation.telegramIdPositive') },
              })}
              error={!!(errors as any).telegram_user_id}
              helperText={(errors as any).telegram_user_id?.message}
            />
          )}
          <TextField
            label={t('fields.username')}
            {...register('username')}
            error={!!errors.username}
            helperText={errors.username?.message}
          />
          <TextField
            label={t('fields.firstName')}
            {...register('first_name')}
            error={!!errors.first_name}
            helperText={errors.first_name?.message}
          />
          <TextField
            label={t('fields.lastName')}
            {...register('last_name')}
            error={!!errors.last_name}
            helperText={errors.last_name?.message}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>{tCommon('actions.cancel')}</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? tCommon('actions.saving') : tCommon('actions.save')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default UserForm

