import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert,
  CircularProgress,
  Autocomplete,
} from '@mui/material'
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material'
import api from '../../services/api'
import { User } from '../../types'

interface StaffUser {
  id: number
  telegram_user_id: number
  first_name: string | null
  last_name: string | null
  created_at: string
  updated_at: string
}

const StaffUsersList = () => {
  const [staffUsers, setStaffUsers] = useState<StaffUser[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  useEffect(() => {
    loadStaffUsers()
    loadUsers()
  }, [])

  const loadStaffUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get('/admin/staff-users')
      setStaffUsers(response.data.staff_users)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load staff users')
    } finally {
      setLoading(false)
    }
  }

  const loadUsers = async () => {
    setLoadingUsers(true)
    try {
      const response = await api.get('/admin/users')
      setUsers(response.data.users)
    } catch (err: any) {
      console.error('Failed to load users:', err)
    } finally {
      setLoadingUsers(false)
    }
  }

  const handleAdd = () => {
    setSelectedUser(null)
    setError(null)
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedUser(null)
    setError(null)
  }

  const handleSubmit = async () => {
    if (!selectedUser) {
      setError('Please select a user')
      return
    }

    try {
      setError(null)
      await api.post('/admin/staff-users', {
        telegram_user_id: selectedUser.telegram_user_id,
        first_name: selectedUser.first_name || null,
        last_name: selectedUser.last_name || null,
      })
      handleCloseDialog()
      loadStaffUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create staff user')
    }
  }

  const getUserDisplayName = (user: User) => {
    const name = [user.first_name, user.last_name].filter(Boolean).join(' ')
    if (name) {
      return `${name} (@${user.username || 'N/A'}) - ID: ${user.telegram_user_id}`
    }
    return `@${user.username || 'N/A'} - ID: ${user.telegram_user_id}`
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this staff user?')) {
      return
    }

    setDeletingId(id)
    try {
      await api.delete(`/admin/staff-users/${id}`)
      loadStaffUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete staff user')
    } finally {
      setDeletingId(null)
    }
  }

  const getFullName = (user: StaffUser) => {
    const parts = [user.first_name, user.last_name].filter(Boolean)
    return parts.length > 0 ? parts.join(' ') : 'N/A'
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Staff Users</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          Add User
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Telegram User ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {staffUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No staff users found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                staffUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{user.telegram_user_id}</TableCell>
                    <TableCell>{getFullName(user)}</TableCell>
                    <TableCell>{new Date(user.created_at).toLocaleString()}</TableCell>
                    <TableCell>
                      <IconButton
                        color="error"
                        onClick={() => handleDelete(user.id)}
                        disabled={deletingId === user.id}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Add Staff User</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Autocomplete
              options={users}
              getOptionLabel={(option) => getUserDisplayName(option)}
              value={selectedUser}
              onChange={(_, newValue) => setSelectedUser(newValue)}
              loading={loadingUsers}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select User"
                  placeholder="Search by name, username, or Telegram ID"
                  required
                />
              )}
              filterOptions={(options, { inputValue }) => {
                const searchLower = inputValue.toLowerCase()
                return options.filter((user) => {
                  const name = [user.first_name, user.last_name].filter(Boolean).join(' ').toLowerCase()
                  const username = (user.username || '').toLowerCase()
                  const telegramId = user.telegram_user_id.toString()
                  return (
                    name.includes(searchLower) ||
                    username.includes(searchLower) ||
                    telegramId.includes(searchLower)
                  )
                })
              }}
            />
            {selectedUser && (
              <Box sx={{ mt: 1, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Selected User:
                </Typography>
                <Typography variant="body1">
                  {[selectedUser.first_name, selectedUser.last_name].filter(Boolean).join(' ') || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Username: @{selectedUser.username || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Telegram ID: {selectedUser.telegram_user_id}
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!selectedUser}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StaffUsersList

