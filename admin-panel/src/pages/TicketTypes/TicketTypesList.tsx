import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Typography,
  IconButton,
  Chip,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { TicketType } from '../../types'

const TicketTypesList = () => {
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTicketTypes = async () => {
      try {
        const response = await api.get('/admin/ticket-types')
        setTicketTypes(response.data.ticket_types)
      } catch (error) {
        console.error('Failed to fetch ticket types:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchTicketTypes()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Ticket Types</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Create New
        </Button>
      </Box>

      <Grid container spacing={3}>
        {ticketTypes.map((tt) => (
          <Grid item xs={12} sm={6} md={4} key={tt.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{tt.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Price: {tt.price} ₽
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available: {tt.available_quantity} / {tt.total_quantity}
                </Typography>
                <Chip
                  label={tt.is_active ? 'Active' : 'Inactive'}
                  color={tt.is_active ? 'success' : 'default'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default TicketTypesList

