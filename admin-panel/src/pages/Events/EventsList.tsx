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
import { Event } from '../../types'
import EventForm from './EventForm'
import ConfirmDialog from '../../components/common/ConfirmDialog'

const EventsList = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingEvent, setEditingEvent] = useState<Event | null>(null)
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

  const handleEdit = (event: Event) => {
    setEditingEvent(event)
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

  const handleFormClose = () => {
    setFormOpen(false)
    setEditingEvent(null)
    fetchEvents()
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

      <Grid container spacing={3}>
        {events.map((event) => (
          <Grid item xs={12} sm={6} md={4} key={event.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6">{event.name}</Typography>
                  <Chip
                    label={event.is_active ? 'Active' : 'Inactive'}
                    color={event.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {event.date} {event.time}
                </Typography>
                {event.djs && event.djs.length > 0 && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    DJs: {event.djs.join(', ')}
                  </Typography>
                )}
                {event.description && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {event.description}
                  </Typography>
                )}
                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleEdit(event)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => setDeleteDialog({ open: true, eventId: event.id })}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <EventForm
        open={formOpen}
        event={editingEvent}
        onClose={handleFormClose}
      />

      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Event"
        message="Are you sure you want to delete this event?"
        onConfirm={() => deleteDialog.eventId && handleDelete(deleteDialog.eventId)}
        onCancel={() => setDeleteDialog({ open: false, eventId: null })}
      />
    </Box>
  )
}

export default EventsList

