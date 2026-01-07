import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
} from '@mui/material'
import api from '../../services/api'
import { AdminAccount, AdminAccountCreate, AdminAccountUpdate, AdminGroup } from '../../types'

interface AccountFormProps {
  open: boolean
  onClose: () => void
  onSave: () => void
  account: AdminAccount | null
  groupId: number | null
  groups: AdminGroup[]
}

const AccountForm = ({ open, onClose, onSave, account, groupId, groups }: AccountFormProps) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null)
  const [isActive, setIsActive] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (account) {
      setUsername(account.username)
      setPassword('')
      setSelectedGroupId(account.group_id)
      setIsActive(account.is_active)
    } else {
      setUsername('')
      setPassword('')
      setSelectedGroupId(groupId)
      setIsActive(true)
    }
    setError(null)
  }, [account, groupId, open])

  const handleSubmit = async () => {
    if (!username.trim()) {
      setError('Username is required')
      return
    }

    if (!account && !password.trim()) {
      setError('Password is required for new accounts')
      return
    }

    if (!selectedGroupId) {
      setError('Group is required')
      return
    }

    try {
      setLoading(true)
      setError(null)

      if (account) {
        const updateData: AdminAccountUpdate = {
          username: username.trim(),
          group_id: selectedGroupId,
          is_active: isActive,
        }
        if (password.trim()) {
          updateData.password = password.trim()
        }
        await api.put(`/admin/accounts/${account.id}`, updateData)
      } else {
        const createData: AdminAccountCreate = {
          username: username.trim(),
          password: password.trim(),
          group_id: selectedGroupId,
          is_active: isActive,
        }
        await api.post('/admin/accounts', createData)
      }

      onSave()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save account')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{account ? 'Edit Account' : 'Create Account'}</DialogTitle>
      <DialogContent>
        {error && (
          <div style={{ color: 'red', marginBottom: '16px' }}>{error}</div>
        )}
        <TextField
          autoFocus
          margin="dense"
          label="Username"
          fullWidth
          variant="outlined"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          sx={{ mb: 2 }}
        />
        <TextField
          margin="dense"
          label={account ? 'New Password (leave empty to keep current)' : 'Password'}
          type="password"
          fullWidth
          variant="outlined"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required={!account}
          sx={{ mb: 2 }}
        />
        <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
          <InputLabel>Group</InputLabel>
          <Select
            value={selectedGroupId || ''}
            onChange={(e) => setSelectedGroupId(e.target.value as number)}
            label="Group"
            required
          >
            {groups.map((group) => (
              <MenuItem key={group.id} value={group.id}>
                {group.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControlLabel
          control={
            <Switch
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
          }
          label="Active"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {account ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default AccountForm

