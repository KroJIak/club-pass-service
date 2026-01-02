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
} from '@mui/material'
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material'
import api from '../../services/api'

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
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    telegram_user_id: '',
    first_name: '',
    last_name: '',
  })

  useEffect(() => {
    loadStaffUsers()
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

  const handleAdd = () => {
    setFormData({ telegram_user_id: '', first_name: '', last_name: '' })
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setFormData({ telegram_user_id: '', first_name: '', last_name: '' })
  }

  const handleSubmit = async () => {
    if (!formData.telegram_user_id) {
      setError('Telegram User ID is required')
      return
    }

    try {
      await api.post('/admin/staff-users', {
        telegram_user_id: parseInt(formData.telegram_user_id),
        first_name: formData.first_name || null,
        last_name: formData.last_name || null,
      })
      handleCloseDialog()
      loadStaffUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create staff user')
    }
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
            <TextField
              label="Telegram User ID"
              type="number"
              value={formData.telegram_user_id}
              onChange={(e) => setFormData({ ...formData, telegram_user_id: e.target.value })}
              required
              fullWidth
            />
            <TextField
              label="First Name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Last Name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StaffUsersList

