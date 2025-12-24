import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography } from '@mui/material'
import api from '../../services/api'
import { User } from '../../types'
import FilterPanel from '../../components/filters/FilterPanel'
import UsersFilter, { UsersFilterState, DEFAULT_FILTER_STATE } from '../../components/filters/UsersFilter'
import { useFilterPanel } from '../../hooks/useFilterPanel'

const UsersList = () => {
  const [users, setUsers] = useState<User[]>([])
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [filterState, setFilterState] = useState<UsersFilterState>(DEFAULT_FILTER_STATE)
  const { setFilterPanel } = useFilterPanel()

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

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Users</Typography>
      <Grid container spacing={3}>
        {users.map((user) => (
          <Grid item xs={12} sm={6} md={4} key={user.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {user.first_name || user.last_name 
                      ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                      : 'No name'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    @{user.username || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Telegram ID: {user.telegram_user_id}
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
