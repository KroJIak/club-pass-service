import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography } from '@mui/material'
import api from '../../services/api'
import { User } from '../../types'

const UsersList = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await api.get('/admin/users')
        setUsers(response.data.users)
      } catch (error) {
        console.error('Failed to fetch users:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchUsers()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Users</Typography>
      <Grid container spacing={3}>
        {users.map((user) => (
          <Grid item xs={12} sm={6} md={4} key={user.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">
                  {user.first_name} {user.last_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  @{user.username || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Telegram ID: {user.telegram_user_id}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default UsersList

