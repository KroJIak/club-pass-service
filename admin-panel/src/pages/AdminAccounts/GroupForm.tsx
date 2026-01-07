import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
} from '@mui/material'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import { AdminGroup, AdminGroupCreate, AdminGroupUpdate } from '../../types'

interface GroupFormProps {
  open: boolean
  onClose: () => void
  onSave: () => void
  group: AdminGroup | null
}

const GroupForm = ({ open, onClose, onSave, group }: GroupFormProps) => {
  const { t } = useTranslation('staff')
  const { t: tCommon } = useTranslation('common')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (group) {
      setName(group.name)
      setDescription(group.description || '')
    } else {
      setName('')
      setDescription('')
    }
    setError(null)
  }, [group, open])

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError(t('fields.groupName') + ' ' + tCommon('messages.required'))
      return
    }

    try {
      setLoading(true)
      setError(null)

      if (group) {
        const updateData: AdminGroupUpdate = {
          name: name.trim(),
          description: description.trim() || null,
        }
        await api.put(`/admin/groups/${group.id}`, updateData)
      } else {
        const createData: AdminGroupCreate = {
          name: name.trim(),
          description: description.trim() || null,
        }
        await api.post('/admin/groups', createData)
      }

      onSave()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || tCommon('messages.saveError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{group ? t('editGroup') : t('createGroup')}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        )}
        <TextField
          autoFocus
          margin="dense"
          label={t('fields.groupName')}
          fullWidth
          variant="outlined"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          sx={{ mb: 2 }}
        />
        <TextField
          margin="dense"
          label={t('fields.description')}
          fullWidth
          variant="outlined"
          multiline
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          {tCommon('actions.cancel')}
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {group ? tCommon('actions.save') : tCommon('actions.create')}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default GroupForm

