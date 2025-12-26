import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Typography,
  Chip,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Star as StarIcon, StarBorder as StarBorderIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { TicketType } from '../../types'
import TicketTypeForm from './TicketTypeForm'

const TicketTypesList = () => {
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingTicketType, setEditingTicketType] = useState<TicketType | null>(null)

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

  useEffect(() => {
    fetchTicketTypes()
  }, [])

  const handleSaveAsTemplate = async (ticketTypeId: number) => {
    try {
      await api.post(`/admin/ticket-types/${ticketTypeId}/save-as-template`)
      alert('Ticket type saved as template successfully!')
    } catch (error: any) {
      console.error('Failed to save as template:', error)
      alert(error.response?.data?.detail || 'Failed to save as template')
    }
  }

  const handleDelete = async (ticketTypeId: number) => {
    if (!confirm('Are you sure you want to delete this ticket type?')) {
      return
    }
    try {
      await api.delete(`/admin/ticket-types/${ticketTypeId}`)
      fetchTicketTypes()
    } catch (error: any) {
      console.error('Failed to delete ticket type:', error)
      alert(error.response?.data?.detail || 'Failed to delete ticket type')
    }
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Ticket Types</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => {
            setEditingTicketType(null)
            setFormOpen(true)
          }}
        >
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
                  Price: {tt.price % 1 === 0 ? Math.floor(tt.price) : tt.price} ₽
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
              <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                <IconButton
                  size="small"
                  color="primary"
                  onClick={() => handleSaveAsTemplate(tt.id)}
                  title="Save as template"
                >
                  <StarBorderIcon />
                </IconButton>
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDelete(tt.id)}
                  title="Delete"
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <TicketTypeForm
        open={formOpen}
        ticketType={editingTicketType}
        onClose={() => {
          setFormOpen(false)
          setEditingTicketType(null)
        }}
        onSuccess={() => {
          fetchTicketTypes()
          setFormOpen(false)
          setEditingTicketType(null)
        }}
      />
    </Box>
  )
}

export default TicketTypesList

