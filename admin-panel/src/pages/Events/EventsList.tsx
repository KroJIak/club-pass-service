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
import { Event } from '../../types'
import EventForm from './EventForm'
import ConfirmDialog from '../../components/common/ConfirmDialog'

const EventsList = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingEvent, setEditingEvent] = useState<Event | null>(null)
  const [expandedEvent, setExpandedEvent] = useState<number | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; eventId: number | null }>({
    open: false,
    eventId: null,
  })

  const fetchEvents = async () => {
    try {
      const response = await api.get('/admin/events')
      setEvents(response.data.events)
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [])

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
        <Typography variant="h4">Events</Typography>
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
              }}
              onClick={() => toggleExpand(event.id)}
            >
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ display: 'inline', mr: 1 }}>{event.name}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'inline' }}>
                      {event.date} {event.time}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Switch
                      checked={event.is_active}
                      onChange={(e) => handleToggleActive(event, e)}
                      size="small"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <Chip
                      label={event.is_active ? 'Active' : 'Inactive'}
                      color={event.is_active ? 'success' : 'default'}
                      size="small"
                    />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
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
