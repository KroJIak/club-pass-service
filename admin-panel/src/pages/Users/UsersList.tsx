import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Button, Checkbox } from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { User } from '../../types'
import FilterPanel from '../../components/filters/FilterPanel'
import UsersFilter, { UsersFilterState, DEFAULT_FILTER_STATE } from '../../components/filters/UsersFilter'
import { useFilterPanel } from '../../hooks/useFilterPanel'
import { useSelection } from '../../hooks/useSelection'
import { usePermissions } from '../../hooks/usePermissions'
import { useTranslation } from 'react-i18next'

const UsersList = () => {
  const { hasPermission } = usePermissions()
  const { t } = useTranslation('users')
  const { t: tCommon } = useTranslation('common')
  const [users, setUsers] = useState<User[]>([])
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [filterState, setFilterState] = useState<UsersFilterState>(DEFAULT_FILTER_STATE)
  const { setFilterPanel } = useFilterPanel()
  const selection = useSelection(users)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users')
      const fetchedUsers = response.data.users
      setAllUsers(fetchedUsers)
      setUsers(fetchedUsers)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  // Set up filter panel
  useEffect(() => {
    setFilterPanel(
      <FilterPanel
        searchValue={filterState.search}
        onSearchChange={(value) => setFilterState({ ...filterState, search: value })}
      >
        <UsersFilter
          filterState={filterState}
          onFilterChange={setFilterState}
        />
      </FilterPanel>
    )

    return () => {
      setFilterPanel(null)
    }
  }, [allUsers, filterState, setFilterPanel])

  // Filter users based on filter state
  useEffect(() => {
    let filtered = [...allUsers]

    // Search filter - по имени, фамилии, username и user_id
    if (filterState.search.trim()) {
      const searchLower = filterState.search.toLowerCase()
      filtered = filtered.filter((user) => {
        const firstNameMatch = user.first_name?.toLowerCase().includes(searchLower) || false
        const lastNameMatch = user.last_name?.toLowerCase().includes(searchLower) || false
        const usernameMatch = user.username?.toLowerCase().includes(searchLower) || false
        const userIdMatch = user.telegram_user_id.toString().includes(searchLower) || false
        
        return firstNameMatch || lastNameMatch || usernameMatch || userIdMatch
      })
    }

    // Username filter
    if (filterState.hasUsername !== 'all') {
      filtered = filtered.filter((user) => {
        if (filterState.hasUsername === 'yes') {
          return user.username !== null && user.username.trim() !== ''
        } else {
          return user.username === null || user.username.trim() === ''
        }
      })
    }

    setUsers(filtered)
  }, [allUsers, filterState])

  const handleDeleteSelected = async () => {
    if (!confirm(t('messages.deleteSelectedConfirm', { count: selection.selectedCount }))) {
      return
    }

    try {
      for (const id of selection.selectedIds) {
        await api.delete(`/admin/users/${id}`)
      }
      selection.deselectAll()
      fetchUsers()
    } catch (error) {
      console.error('Failed to delete users:', error)
      alert(tCommon('messages.deleteError'))
    }
  }

  if (loading) {
    return <Typography>{tCommon('status.loading')}</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">{t('title')}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {hasPermission('users', 'delete') && selection.hasSelection && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelected}
            >
              {t('deleteSelected')}
            </Button>
          )}
          {hasPermission('users', 'delete') && (
            <Checkbox
              checked={selection.getSelectionState() === 'all'}
              indeterminate={selection.getSelectionState() === 'some'}
              onChange={selection.handleSelectAllClick}
            />
          )}
        </Box>
      </Box>
      <Grid container spacing={3}>
        {users.map((user) => (
          <Grid item xs={12} sm={6} md={4} key={user.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                cursor: hasPermission('users', 'delete') ? 'pointer' : 'default',
                border: hasPermission('users', 'delete') && selection.isSelected(user.id) ? '2px solid' : 'none',
                borderColor: hasPermission('users', 'delete') && selection.isSelected(user.id) ? 'primary.main' : 'transparent',
                bgcolor: hasPermission('users', 'delete') && selection.isSelected(user.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
              }}
              onClick={() => hasPermission('users', 'delete') && selection.toggleSelection(user.id)}
            >
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {user.first_name || user.last_name 
                      ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                      : t('fields.noName')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    @{user.username || tCommon('fields.notApplicable')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('fields.telegramId')}: {user.telegram_user_id}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default UsersList
