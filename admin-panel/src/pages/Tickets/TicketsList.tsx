import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip } from '@mui/material'
import api from '../../services/api'
import { Ticket } from '../../types'

const TicketsList = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const response = await api.get('/admin/tickets')
        setTickets(response.data.tickets)
      } catch (error) {
        console.error('Failed to fetch tickets:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchTickets()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Tickets</Typography>
      <Grid container spacing={3}>
        {tickets.map((ticket) => (
          <Grid item xs={12} sm={6} md={4} key={ticket.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">Ticket #{ticket.id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Token: {ticket.token}
                </Typography>
                <Chip
                  label={ticket.status}
                  color={ticket.status === 'active' ? 'success' : 'default'}
                  size="small"
                  sx={{ mt: 1, mr: 1 }}
                />
                {ticket.is_used && (
                  <Chip label="Used" color="warning" size="small" sx={{ mt: 1 }} />
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default TicketsList

