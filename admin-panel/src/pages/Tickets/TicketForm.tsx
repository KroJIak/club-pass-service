import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  MenuItem,
  Autocomplete,
  TextField as MuiTextField,
  Box,
  IconButton,
} from '@mui/material'
import { Refresh as RefreshIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import api from '../../services/api'
import { Ticket, TicketCreate, TicketUpdate, Event, TicketType, User } from '../../types'
import TextField from '../../components/forms/TextField'

interface TicketFormProps {
  open?: boolean
  ticket: Ticket | null
  onClose: () => void
  embedded?: boolean
}

const TicketForm = ({ open = true, ticket, onClose, embedded = false }: TicketFormProps) => {
  const [loading, setLoading] = useState(false)
  const [events, setEvents] = useState<Event[]>([])
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loadingEvents, setLoadingEvents] = useState(false)
  const [loadingTicketTypes, setLoadingTicketTypes] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [selectedTicketType, setSelectedTicketType] = useState<TicketType | null>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  const isEditMode = !!ticket

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<TicketCreate | TicketUpdate>({
    defaultValues: {
      status: 'active',
    },
  })

  // Fetch events
  useEffect(() => {
    if (open) {
      fetchEvents()
      fetchUsers()
    }
  }, [open])

  // Fetch ticket types when event is selected
  useEffect(() => {
    if (selectedEvent && open) {
      fetchTicketTypes(selectedEvent.id)
    } else {
      setTicketTypes([])
      setSelectedTicketType(null)
    }
  }, [selectedEvent, open])

  // Load ticket data when editing
  useEffect(() => {
    if (ticket && open && events.length > 0 && users.length > 0) {
      // Find and set selected event
      const event = events.find(e => e.id === ticket.event_id) || ticket.event
      if (event) {
        setSelectedEvent(event)
        setValue('event_id', event.id)
        // Fetch ticket types for this event, then set the selected one
        fetchTicketTypes(event.id).then(() => {
          // Use ticket.ticket_type if available, otherwise find in loaded ticketTypes
          const ticketType = ticket.ticket_type
          if (ticketType) {
            setSelectedTicketType(ticketType)
            setValue('ticket_type_id', ticketType.id)
          } else {
            // Wait a bit for ticketTypes to be set
            setTimeout(() => {
              const foundType = ticketTypes.find(tt => tt.id === ticket.ticket_type_id)
              if (foundType) {
                setSelectedTicketType(foundType)
                setValue('ticket_type_id', foundType.id)
              }
            }, 200)
          }
        })
      }

      // Find and set selected user
      const user = users.find(u => u.id === ticket.user_id)
      if (user) {
        setSelectedUser(user)
        setValue('user_id', user.id)
      }

      reset({
        token: ticket.token,
        status: ticket.status,
      })
    } else if (!ticket && open) {
      // Reset form for create mode
      reset({
        status: 'active',
        token: '',
      })
      setSelectedEvent(null)
      setSelectedTicketType(null)
      setSelectedUser(null)
    }
  }, [ticket, open, events, users, reset, setValue])

  const fetchEvents = async () => {
    setLoadingEvents(true)
    try {
      const response = await api.get('/admin/events')
      setEvents(response.data.events || [])
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setLoadingEvents(false)
    }
  }

  const fetchTicketTypes = async (eventId: number) => {
    setLoadingTicketTypes(true)
    try {
      const response = await api.get('/admin/ticket-types')
      const allTicketTypes = response.data.ticket_types || []
      // Filter by event_id
      const filtered = allTicketTypes.filter((tt: TicketType) => tt.event_id === eventId)
      setTicketTypes(filtered)
    } catch (error) {
      console.error('Failed to fetch ticket types:', error)
    } finally {
      setLoadingTicketTypes(false)
    }
  }

  const fetchUsers = async () => {
    setLoadingUsers(true)
    try {
      const response = await api.get('/admin/users')
      setUsers(response.data.users || [])
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoadingUsers(false)
    }
  }

  const generateToken = async () => {
    try {
      // Generate token in format TKT-XXXXX-XXXXX
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      const randomPart1 = Array.from({ length: 5 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
      const randomPart2 = Array.from({ length: 5 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
      const newToken = `TKT-${randomPart1}-${randomPart2}`
      setValue('token', newToken)
    } catch (error) {
      console.error('Failed to generate token:', error)
    }
  }

  const onSubmit = async (data: TicketCreate | TicketUpdate) => {
    setLoading(true)
    try {
      if (ticket) {
        // Update mode - only status can be updated
        await api.put(`/admin/tickets/${ticket.id}`, data as TicketUpdate)
      } else {
        // Create mode - validate required fields
        if (!selectedEvent || !selectedTicketType || !selectedUser) {
          alert('Please fill in all required fields: Event, Ticket Type, and User')
          setLoading(false)
          return
        }
        const createData: TicketCreate = {
          user_id: selectedUser.id,
          event_id: selectedEvent.id,
          ticket_type_id: selectedTicketType.id,
          token: (data as TicketCreate).token || undefined,
          status: data.status || 'active',
        }
        await api.post('/admin/tickets', createData)
      }
      onClose()
    } catch (error: any) {
      console.error('Failed to save ticket:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save ticket'
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getEventLabel = (event: Event | null) => {
    if (!event) return ''
    return event.name
  }

  const getUserLabel = (user: User | null) => {
    if (!user) return ''
    if (user.username) return `@${user.username}`
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim()
    if (fullName) return fullName
    return `ID: ${user.telegram_user_id}`
  }

  const content = (
    <form onSubmit={handleSubmit(onSubmit)}>
      {!embedded && <DialogTitle>{isEditMode ? 'Edit Ticket' : 'Create Ticket'}</DialogTitle>}
      <DialogContent sx={{ px: embedded ? 0 : 2.98 }}>
          {!isEditMode && (
            <>
              {/* Event selection */}
              <Autocomplete
                options={events}
                getOptionLabel={getEventLabel}
                loading={loadingEvents}
                value={selectedEvent}
                onChange={(_, newValue) => {
                  setSelectedEvent(newValue)
                  if (newValue) {
                    setValue('event_id' as any, newValue.id, { shouldValidate: true })
                  } else {
                    setValue('event_id' as any, undefined as any)
                  }
                  setSelectedTicketType(null)
                  setValue('ticket_type_id' as any, undefined as any)
                }}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label="Event"
                    error={!!(errors as any).event_id}
                    helperText={(errors as any).event_id?.message}
                    required
                    sx={{ mt: 2 }}
                  />
                )}
              />

              {/* Ticket Type selection (only shown when event is selected) */}
              {selectedEvent && (
                <Autocomplete
                  options={ticketTypes}
                  getOptionLabel={(tt) => tt.name}
                  loading={loadingTicketTypes}
                  value={selectedTicketType}
                  onChange={(_, newValue) => {
                    setSelectedTicketType(newValue)
                    if (newValue) {
                      setValue('ticket_type_id' as any, newValue.id, { shouldValidate: true })
                    } else {
                      setValue('ticket_type_id' as any, undefined as any)
                    }
                  }}
                  renderInput={(params) => (
                    <MuiTextField
                      {...params}
                      label="Ticket Type"
                      error={!!(errors as any).ticket_type_id}
                      helperText={(errors as any).ticket_type_id?.message}
                      required
                      sx={{ mt: 2 }}
                    />
                  )}
                />
              )}

              {/* User selection */}
              <Autocomplete
                options={users}
                getOptionLabel={getUserLabel}
                loading={loadingUsers}
                value={selectedUser}
                onChange={(_, newValue) => {
                  setSelectedUser(newValue)
                  if (newValue) {
                    setValue('user_id' as any, newValue.id, { shouldValidate: true })
                  } else {
                    setValue('user_id' as any, undefined as any)
                  }
                }}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label="User"
                    error={!!(errors as any).user_id}
                    helperText={(errors as any).user_id?.message}
                    required
                    sx={{ mt: 2 }}
                  />
                )}
              />

              {/* Token field with generate button */}
              <Box sx={{ mt: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
                <Controller
                  name={"token" as any}
                  control={control}
                  rules={{ required: !isEditMode ? 'Token is required' : false }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Token"
                      error={!!(errors as any).token}
                      helperText={(errors as any).token?.message}
                      required={!isEditMode}
                      fullWidth
                    />
                  )}
                />
                <IconButton
                  onClick={generateToken}
                  title="Generate Token"
                  sx={{ alignSelf: 'center' }}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>
            </>
          )}

          {/* Status field */}
          <Controller
            name="status"
            control={control}
            rules={{ required: 'Status is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Status"
                error={!!errors.status}
                helperText={errors.status?.message}
                sx={{ mt: 2 }}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="refunded">Refunded</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
                <MenuItem value="expired">Expired</MenuItem>
                <MenuItem value="used">Used</MenuItem>
              </TextField>
            )}
          />
        </DialogContent>
        {!embedded && (
          <DialogActions sx={{ px: 2.98 }}>
            <Button onClick={onClose}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? 'Saving...' : isEditMode ? 'Save' : 'Create'}
            </Button>
          </DialogActions>
        )}
        {embedded && (
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2, px: 0 }}>
            <Button onClick={onClose}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? 'Saving...' : isEditMode ? 'Save' : 'Create'}
            </Button>
          </Box>
        )}
      </form>
    )

  if (embedded) {
    return content
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      {content}
    </Dialog>
  )
}

export default TicketForm
