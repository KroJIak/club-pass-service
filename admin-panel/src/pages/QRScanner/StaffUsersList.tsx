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
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import { User } from '../../types/index'
import { usePermissions } from '../../hooks/usePermissions'

interface StaffUser {
  id: number
  telegram_user_id: number
  first_name: string | null
  last_name: string | null
  created_at: string
  updated_at: string
}

const StaffUsersList = () => {
  const { hasPermission } = usePermissions()
  const { t } = useTranslation('staff')
  const { t: tCommon } = useTranslation('common')
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
      setError(err.response?.data?.detail || t('messages.fetchFailed'))
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
      setError(tCommon('fields.user') + ' ' + tCommon('messages.required'))
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
      setError(err.response?.data?.detail || tCommon('messages.saveError'))
    }
  }

  const getUserDisplayName = (user: User) => {
    const name = [user.first_name, user.last_name].filter(Boolean).join(' ')
    if (name) {
      return `${name} (@${user.username || tCommon('fields.notApplicable')}) - ${tCommon('fields.id')}: ${user.telegram_user_id}`
    }
    return `@${user.username || tCommon('fields.notApplicable')} - ${tCommon('fields.id')}: ${user.telegram_user_id}`
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm(t('messages.deleteConfirm'))) {
      return
    }

    setDeletingId(id)
    try {
      await api.delete(`/admin/staff-users/${id}`)
      loadStaffUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || tCommon('messages.deleteError'))
    } finally {
      setDeletingId(null)
    }
  }

  const getFullName = (user: StaffUser) => {
    const parts = [user.first_name, user.last_name].filter(Boolean)
    return parts.length > 0 ? parts.join(' ') : tCommon('fields.notApplicable')
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">{t('staffBotUsers')}</Typography>
        {hasPermission('staff', 'write') && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
            {tCommon('actions.add')}
          </Button>
        )}
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
                <TableCell>{tCommon('fields.id')}</TableCell>
                <TableCell>{t('fields.telegramId')}</TableCell>
                <TableCell>{tCommon('fields.name')}</TableCell>
                <TableCell>{tCommon('fields.date')}</TableCell>
                <TableCell>{tCommon('actions.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {staffUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary">
                      {tCommon('messages.noData')}
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
                        disabled={!hasPermission('staff', 'delete') || deletingId === user.id}
                        title={tCommon('actions.delete')}
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
        <DialogTitle>{tCommon('actions.add')}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Autocomplete
              options={users.filter((user) => {
                // Filter out users who are already staff
                return !staffUsers.some((staffUser) => staffUser.telegram_user_id === user.telegram_user_id)
              })}
              getOptionLabel={(option) => getUserDisplayName(option)}
              value={selectedUser}
              onChange={(_, newValue) => setSelectedUser(newValue)}
              loading={loadingUsers}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={tCommon('fields.user')}
                  placeholder={tCommon('fields.user') + '...'}
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
                  {tCommon('fields.user')}:
                </Typography>
                <Typography variant="body1">
                  {[selectedUser.first_name, selectedUser.last_name].filter(Boolean).join(' ') || tCommon('fields.notApplicable')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('fields.username')}: @{selectedUser.username || tCommon('fields.notApplicable')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('fields.telegramId')}: {selectedUser.telegram_user_id}
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{tCommon('actions.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!selectedUser}>
            {tCommon('actions.add')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StaffUsersList

