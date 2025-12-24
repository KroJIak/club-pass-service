import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  IconButton,
  Chip,
  Drawer,
  Switch,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Event, TicketType } from '../../types'
import EventForm from './EventForm'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import FilterPanel from '../../components/filters/FilterPanel'
import EventsFilter, { EventsFilterState, DEFAULT_FILTER_STATE } from '../../components/filters/EventsFilter'
import { useFilterPanel } from '../../hooks/useFilterPanel'

const EventsList = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [allEvents, setAllEvents] = useState<Event[]>([])
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingEvent, setEditingEvent] = useState<Event | null>(null)
  const [expandedEvent, setExpandedEvent] = useState<number | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; eventId: number | null }>({
    open: false,
    eventId: null,
  })
  const [filterState, setFilterState] = useState<EventsFilterState>(DEFAULT_FILTER_STATE)
  const { setFilterPanel } = useFilterPanel()

  const fetchEvents = async () => {
    try {
      const response = await api.get('/admin/events')
      const fetchedEvents = response.data.events
      setAllEvents(fetchedEvents)
      setEvents(fetchedEvents)
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTicketTypes = async () => {
    try {
      const response = await api.get('/admin/ticket-types')
      setTicketTypes(response.data.ticket_types)
    } catch (error) {
      console.error('Failed to fetch ticket types:', error)
    }
  }

  useEffect(() => {
    fetchEvents()
    fetchTicketTypes()
  }, [])

  // Set up filter panel
  useEffect(() => {
    setFilterPanel(
      <FilterPanel
        searchValue={filterState.search}
        onSearchChange={(value) => setFilterState({ ...filterState, search: value })}
      >
        <EventsFilter
          events={allEvents}
          ticketTypes={ticketTypes}
          filterState={filterState}
          onFilterChange={setFilterState}
        />
      </FilterPanel>
    )

    return () => {
      setFilterPanel(null)
    }
  }, [allEvents, ticketTypes, filterState, setFilterPanel])

  // Filter events based on filter state
  useEffect(() => {
    let filtered = [...allEvents]

    // Search filter
    if (filterState.search.trim()) {
      const searchLower = filterState.search.toLowerCase()
      filtered = filtered.filter((event) => {
        const nameMatch = event.name?.toLowerCase().includes(searchLower)
        const dateMatch = event.date?.toLowerCase().includes(searchLower)
        const djsMatch = event.djs?.some((dj) => dj.toLowerCase().includes(searchLower))
        const descMatch = event.description?.toLowerCase().includes(searchLower)
        
        // Check ticket type names for this event
        const eventTicketTypes = ticketTypes.filter((tt) => tt.event_id === event.id)
        const ticketTypeMatch = eventTicketTypes.some((tt) => tt.name.toLowerCase().includes(searchLower))

        return nameMatch || dateMatch || djsMatch || descMatch || ticketTypeMatch
      })
    }

    // Price filter
    if (filterState.minPrice > 0 || filterState.maxPrice < 10000) {
      filtered = filtered.filter((event) => {
        const eventTicketTypes = ticketTypes.filter((tt) => tt.event_id === event.id)
        return eventTicketTypes.some((tt) => {
          return tt.price >= filterState.minPrice && tt.price <= filterState.maxPrice
        })
      })
    }

    // DJs filter
    if (filterState.selectedDjs.length > 0) {
      filtered = filtered.filter((event) => {
        return event.djs?.some((dj) => filterState.selectedDjs.includes(dj))
      })
    }

    // Date range filter
    if (filterState.dateFrom) {
      const fromDate = new Date(filterState.dateFrom)
      filtered = filtered.filter((event) => {
        const eventDate = parseDate(event.date)
        return eventDate >= fromDate
      })
    }
    if (filterState.dateTo) {
      const toDate = new Date(filterState.dateTo)
      toDate.setHours(23, 59, 59, 999) // End of day
      filtered = filtered.filter((event) => {
        const eventDate = parseDate(event.date)
        return eventDate <= toDate
      })
    }

    // Ticket types filter
    if (filterState.selectedTicketTypes.length > 0) {
      filtered = filtered.filter((event) => {
        const eventTicketTypes = ticketTypes.filter((tt) => tt.event_id === event.id)
        return eventTicketTypes.some((tt) => filterState.selectedTicketTypes.includes(tt.name))
      })
    }

    // Active/Inactive filter
    if (filterState.isActive !== 'all') {
      filtered = filtered.filter((event) => {
        return filterState.isActive === 'active' ? event.is_active : !event.is_active
      })
    }

    setEvents(filtered)
  }, [allEvents, ticketTypes, filterState])

  // Helper function to parse DD.MM.YYYY date
  const parseDate = (dateStr: string): Date => {
    if (!dateStr) return new Date(0)
    const [day, month, year] = dateStr.split('.')
    if (!day || !month || !year) return new Date(0)
    return new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  }

  const handleCreate = () => {
    setEditingEvent(null)
    setFormOpen(true)
  }

  const handleDelete = async (eventId: number) => {
    try {
      await api.delete(`/admin/events/${eventId}`)
      fetchEvents()
    } catch (error) {
      console.error('Failed to delete event:', error)
    }
    setDeleteDialog({ open: false, eventId: null })
  }

  const handleToggleActive = async (event: Event, e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation()
    try {
      await api.put(`/admin/events/${event.id}`, {
        ...event,
        is_active: e.target.checked,
      })
      fetchEvents()
    } catch (error) {
      console.error('Failed to toggle event active status:', error)
    }
  }

  const handleFormClose = () => {
    setFormOpen(false)
    setEditingEvent(null)
    setExpandedEvent(null)
    fetchEvents()
  }

  const toggleExpand = (eventId: number) => {
    setExpandedEvent(expandedEvent === eventId ? null : eventId)
    if (expandedEvent !== eventId) {
      const event = events.find(e => e.id === eventId)
      if (event) {
        setEditingEvent(event)
      }
    }
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">Events</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
          Create New
        </Button>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {events.map((event) => (
          <Box key={event.id} sx={{ display: 'flex', gap: 2, position: 'relative' }}>
            <Card 
              sx={{ 
                flex: 1, 
                minHeight: 80, 
                display: 'flex', 
                flexDirection: 'column',
                cursor: 'pointer',
                position: 'relative',
              }}
              onClick={() => toggleExpand(event.id)}
            >
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body1" sx={{ display: 'inline', mr: 1, fontWeight: 500 }}>{event.name}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'inline' }}>
                      {event.date} {event.time}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Switch
                      checked={event.is_active}
                      onChange={(e) => handleToggleActive(event, e)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <Chip
                      label={event.is_active ? 'Active' : 'Inactive'}
                      color={event.is_active ? 'success' : 'default'}
                      size="small"
                    />
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleExpand(event.id)
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                </Box>
                {event.djs && event.djs.length > 0 && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    DJs: {event.djs.join(', ')}
                  </Typography>
                )}
                {event.description && (
                  <Typography variant="body2" sx={{ mt: 1, flex: 1 }}>
                    {event.description}
                  </Typography>
                )}
                <Box sx={{ position: 'absolute', bottom: 16, right: 16 }}>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation()
                      setDeleteDialog({ open: true, eventId: event.id })
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>

            {expandedEvent === event.id && (
              <Drawer
                anchor="right"
                open={true}
                onClose={() => setExpandedEvent(null)}
                sx={{
                  '& .MuiDrawer-paper': {
                    width: 600,
                    p: 3,
                  },
                }}
              >
                <EventForm
                  event={event}
                  onClose={handleFormClose}
                  embedded={true}
                />
              </Drawer>
            )}
          </Box>
        ))}
      </Box>

      <EventForm
        open={formOpen}
        event={editingEvent}
        onClose={handleFormClose}
      />

      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Event"
        message="Are you sure you want to delete this event? This action cannot be undone."
        onConfirm={() => deleteDialog.eventId && handleDelete(deleteDialog.eventId)}
        onCancel={() => setDeleteDialog({ open: false, eventId: null })}
      />
    </Box>
  )
}

export default EventsList
