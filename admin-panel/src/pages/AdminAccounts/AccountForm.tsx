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
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Refresh as RefreshIcon, Visibility, VisibilityOff } from '@mui/icons-material'
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
  const [showPassword, setShowPassword] = useState(false)
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

  const generateRandomPassword = () => {
    // Generate a random password with 16 characters
    // Using uppercase, lowercase, numbers, and special characters
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    const lowercase = 'abcdefghijklmnopqrstuvwxyz'
    const numbers = '0123456789'
    const special = '!@#$%^&*'
    const allChars = uppercase + lowercase + numbers + special
    
    let password = ''
    // Ensure at least one character from each category
    password += uppercase[Math.floor(Math.random() * uppercase.length)]
    password += lowercase[Math.floor(Math.random() * lowercase.length)]
    password += numbers[Math.floor(Math.random() * numbers.length)]
    password += special[Math.floor(Math.random() * special.length)]
    
    // Fill the rest randomly
    for (let i = password.length; i < 16; i++) {
      password += allChars[Math.floor(Math.random() * allChars.length)]
    }
    
    // Shuffle the password
    password = password.split('').sort(() => Math.random() - 0.5).join('')
    
    setPassword(password)
  }

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
          type={showPassword ? 'text' : 'password'}
          fullWidth
          variant="outlined"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required={!account}
          sx={{ mb: 2 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={generateRandomPassword}
                  edge="end"
                  title="Generate random password"
                  sx={{ mr: 0.5 }}
                >
                  <RefreshIcon />
                </IconButton>
                <IconButton
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
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

