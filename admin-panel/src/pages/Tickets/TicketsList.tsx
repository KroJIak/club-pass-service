import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip, IconButton, Button, Drawer, Checkbox } from '@mui/material'
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Ticket } from '../../types'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import TicketForm from './TicketForm'
import FilterPanel from '../../components/filters/FilterPanel'
import TicketsFilter, { TicketsFilterState, DEFAULT_FILTER_STATE } from '../../components/filters/TicketsFilter'
import { useFilterPanel } from '../../hooks/useFilterPanel'
import { useSelection } from '../../hooks/useSelection'

const TicketsList = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [allTickets, setAllTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null)
  const [expandedTicket, setExpandedTicket] = useState<number | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; ticketId: number | null }>({
    open: false,
    ticketId: null,
  })
  const [filterState, setFilterState] = useState<TicketsFilterState>(DEFAULT_FILTER_STATE)
  const { setFilterPanel } = useFilterPanel()
  const selection = useSelection(tickets)

  useEffect(() => {
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      const response = await api.get('/admin/tickets')
      const fetchedTickets = response.data.tickets
      setAllTickets(fetchedTickets)
      setTickets(fetchedTickets)
    } catch (error) {
      console.error('Failed to fetch tickets:', error)
    } finally {
      setLoading(false)
    }
  }

  // Set up filter panel
  useEffect(() => {
    setFilterPanel(
      <FilterPanel
        searchValue={filterState.search}
        onSearchChange={(value) => setFilterState({ ...filterState, search: value })}
      >
        <TicketsFilter
          filterState={filterState}
          onFilterChange={setFilterState}
        />
      </FilterPanel>
    )

    return () => {
      setFilterPanel(null)
    }
  }, [filterState, setFilterPanel])

  // Filter tickets based on filter state
  useEffect(() => {
    let filtered = [...allTickets]

    // Search filter - по номеру тикета (id), токену, имени/username пользователя
    if (filterState.search.trim()) {
      const searchLower = filterState.search.toLowerCase()
      filtered = filtered.filter((ticket) => {
        const ticketIdMatch = ticket.id.toString().includes(searchLower)
        const tokenMatch = ticket.token.toLowerCase().includes(searchLower)
        const usernameMatch = ticket.username?.toLowerCase().includes(searchLower) || false
        const firstNameMatch = ticket.first_name?.toLowerCase().includes(searchLower) || false
        const lastNameMatch = ticket.last_name?.toLowerCase().includes(searchLower) || false
        
        return ticketIdMatch || tokenMatch || usernameMatch || firstNameMatch || lastNameMatch
      })
    }

    // Status filter
    if (filterState.status !== 'all') {
      filtered = filtered.filter((ticket) => {
        return ticket.status === filterState.status
      })
    }

    // Event filter
    if (filterState.event_id !== null) {
      filtered = filtered.filter((ticket) => {
        return ticket.event_id === filterState.event_id
      })
    }

    // Ticket Type filter
    if (filterState.ticket_type_id !== null) {
      filtered = filtered.filter((ticket) => {
        return ticket.ticket_type_id === filterState.ticket_type_id
      })
    }

    setTickets(filtered)
  }, [allTickets, filterState])

  const toggleExpand = (ticketId: number) => {
    if (selection.hasSelection) {
      selection.toggleSelection(ticketId)
      return
    }
    if (expandedTicket === ticketId) {
      setExpandedTicket(null)
    } else {
      setExpandedTicket(ticketId)
      const ticket = tickets.find(t => t.id === ticketId)
      if (ticket) {
        setEditingTicket(ticket)
      }
    }
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

  const handleDeleteSelected = async () => {
    if (!confirm(`Are you sure you want to delete ${selection.selectedCount} ticket(s)? This action cannot be undone.`)) {
      return
    }

    try {
      for (const id of selection.selectedIds) {
        await api.delete(`/admin/tickets/${id}`)
      }
      selection.deselectAll()
      fetchTickets()
    } catch (error) {
      console.error('Failed to delete tickets:', error)
      alert('Failed to delete some tickets')
    }
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Tickets</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {selection.hasSelection && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelected}
            >
              Delete Selected
            </Button>
          )}
          <Checkbox
            checked={selection.getSelectionState() === 'all'}
            indeterminate={selection.getSelectionState() === 'some'}
            onChange={selection.handleSelectAllClick}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              setEditingTicket(null)
              setFormOpen(true)
            }}
          >
            Create New
          </Button>
        </Box>
      </Box>
      <Grid container spacing={3}>
        {tickets.map((ticket) => (
          <Grid item xs={12} sm={6} md={4} key={ticket.id}>
            <Box sx={{ display: 'flex', gap: 2, position: 'relative', height: '100%' }}>
              <Card 
                sx={{ 
                  flex: 1, 
                  height: '100%',
                  display: 'flex', 
                  flexDirection: 'column',
                  cursor: 'pointer',
                  position: 'relative',
                  border: selection.isSelected(ticket.id) ? '2px solid' : 'none',
                  borderColor: selection.isSelected(ticket.id) ? 'primary.main' : 'transparent',
                  bgcolor: selection.isSelected(ticket.id) ? 'action.selected' : 'background.paper',
                }}
                onClick={() => toggleExpand(ticket.id)}
              >
                <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>Ticket #{ticket.id}</Typography>
                      {ticket.event && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          Event: {ticket.event.name}
                        </Typography>
                      )}
                      {ticket.ticket_type && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          Type: {ticket.ticket_type.name}
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        Token: {ticket.token}
                      </Typography>
                      {ticket.username ? (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          @{ticket.username}
                        </Typography>
                      ) : (ticket.first_name || ticket.last_name) ? (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
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
                    {!selection.hasSelection && (
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleExpand(ticket.id)
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation()
                            setDeleteDialog({ open: true, ticketId: ticket.id })
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>

              {expandedTicket === ticket.id && (
                <Drawer
                  anchor="right"
                  open={true}
                  onClose={() => setExpandedTicket(null)}
                  sx={{
                    '& .MuiDrawer-paper': {
                      width: 600,
                      p: 2.98, // уменьшаем отступы на 0.02 (было 3, стало 2.98)
                    },
                  }}
                >
                  <TicketForm
                    ticket={ticket}
                    onClose={() => {
                      setExpandedTicket(null)
                      fetchTickets()
                    }}
                    embedded={true}
                  />
                </Drawer>
              )}
            </Box>
          </Grid>
        ))}
      </Grid>

      <TicketForm
        open={formOpen}
        ticket={editingTicket}
        onClose={handleFormClose}
        embedded={false}
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

