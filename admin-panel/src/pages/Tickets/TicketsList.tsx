import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip, IconButton } from '@mui/material'
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Ticket } from '../../types'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import TicketForm from './TicketForm'

const TicketsList = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; ticketId: number | null }>({
    open: false,
    ticketId: null,
  })

  useEffect(() => {
    fetchTickets()
  }, [])

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

  const handleEdit = (ticket: Ticket) => {
    setEditingTicket(ticket)
    setFormOpen(true)
  }

  const handleDelete = async (ticketId: number) => {
    try {
      await api.delete(`/admin/tickets/${ticketId}`)
      fetchTickets()
    } catch (error) {
      console.error('Failed to delete ticket:', error)
    }
    setDeleteDialog({ open: false, ticketId: null })
  }

  const handleFormClose = () => {
    setFormOpen(false)
    setEditingTicket(null)
    fetchTickets()
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Tickets</Typography>
      <Grid container spacing={3}>
        {tickets.map((ticket) => (
          <Grid item xs={12} sm={6} md={4} key={ticket.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>Ticket #{ticket.id}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Token: {ticket.token}
                    </Typography>
                    {ticket.username ? (
                      <Typography variant="body2" color="text.secondary">
                        @{ticket.username}
                      </Typography>
                    ) : (ticket.first_name || ticket.last_name) ? (
                      <Typography variant="body2" color="text.secondary">
                        {`${ticket.first_name || ''} ${ticket.last_name || ''}`.trim()}
                      </Typography>
                    ) : null}
                    <Chip
                      label={ticket.status}
                      color={
                        ticket.status === 'active' 
                          ? 'success' 
                          : ticket.status === 'used'
                          ? 'warning'
                          : ticket.status === 'refunded'
                          ? 'info'
                          : ticket.status === 'expired'
                          ? 'error'
                          : ticket.status === 'cancelled'
                          ? 'default'
                          : 'default'
                      }
                      size="small"
                      sx={{ mt: 1, mr: 1 }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleEdit(ticket)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => setDeleteDialog({ open: true, ticketId: ticket.id })}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <TicketForm
        open={formOpen}
        ticket={editingTicket}
        onClose={handleFormClose}
      />

      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Ticket"
        message="Are you sure you want to delete this ticket? This action cannot be undone."
        onConfirm={() => deleteDialog.ticketId && handleDelete(deleteDialog.ticketId)}
        onCancel={() => setDeleteDialog({ open: false, ticketId: null })}
      />
    </Box>
  )
}

export default TicketsList

