import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Grid,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Send as SendIcon,
} from '@mui/icons-material'
import api from '../../services/api'
import dayjs from 'dayjs'

interface SupportMessage {
  id: number
  user_id: number
  message: string
  status: 'new' | 'responded' | 'closed'
  admin_response: string | null
  responded_at: string | null
  responded_by: string | null
  created_at: string
  updated_at: string
  username: string | null
  first_name: string | null
  last_name: string | null
}

const SupportMessagesList: React.FC = () => {
  const [messages, setMessages] = useState<SupportMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [responseText, setResponseText] = useState<{ [key: number]: string }>({})
  const [respondingTo, setRespondingTo] = useState<number | null>(null)

  const fetchMessages = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (statusFilter !== 'all') {
        params.status = statusFilter
      }
      const response = await api.get('/admin/support-messages', { params })
      setMessages(response.data.messages || [])
    } catch (error: any) {
      console.error('Failed to fetch support messages:', error)
      alert(error.response?.data?.detail || 'Failed to fetch support messages')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [statusFilter])

  const handleDelete = async (messageId: number) => {
    if (!confirm('Delete this support message?')) return

    try {
      await api.delete(`/admin/support-messages/${messageId}`)
      fetchMessages()
    } catch (error: any) {
      console.error('Failed to delete message:', error)
      alert(error.response?.data?.detail || 'Failed to delete message')
    }
  }

  const handleRespond = async (messageId: number) => {
    const response = responseText[messageId]?.trim()
    if (!response) {
      alert('Please enter a response')
      return
    }

    try {
      await api.put(`/admin/support-messages/${messageId}/respond`, {
        admin_response: response,
      })
      setResponseText((prev) => ({ ...prev, [messageId]: '' }))
      setRespondingTo(null)
      fetchMessages()
    } catch (error: any) {
      console.error('Failed to send response:', error)
      alert(error.response?.data?.detail || 'Failed to send response')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return 'error'
      case 'responded':
        return 'success'
      case 'closed':
        return 'default'
      default:
        return 'default'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return dayjs(dateString).format('DD.MM.YYYY HH:mm')
    } catch {
      return dateString
    }
  }

  const getUserDisplayName = (msg: SupportMessage) => {
    if (msg.first_name || msg.last_name) {
      return [msg.first_name, msg.last_name].filter(Boolean).join(' ') || msg.username || `User #${msg.user_id}`
    }
    return msg.username || `User #${msg.user_id}`
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Support Messages
        </Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Status Filter</InputLabel>
          <Select
            value={statusFilter}
            label="Status Filter"
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="new">New</MenuItem>
            <MenuItem value="responded">Responded</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {loading ? (
        <Typography>Loading...</Typography>
      ) : messages.length === 0 ? (
        <Typography>No support messages found</Typography>
      ) : (
        <Grid container spacing={2}>
          {messages.map((msg) => (
            <Grid item xs={12} key={msg.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {getUserDisplayName(msg)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {formatDate(msg.created_at)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip
                        label={msg.status.toUpperCase()}
                        color={getStatusColor(msg.status) as any}
                        size="small"
                      />
                      <IconButton
                        color="error"
                        onClick={() => handleDelete(msg.id)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>

                  <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="body1">{msg.message}</Typography>
                  </Box>

                  {msg.admin_response ? (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Admin Response {msg.responded_by && `by ${msg.responded_by}`}
                        {msg.responded_at && ` on ${formatDate(msg.responded_at)}`}
                      </Typography>
                      <Typography variant="body1">{msg.admin_response}</Typography>
                    </Box>
                  ) : (
                    <Box sx={{ mt: 2 }}>
                      {respondingTo === msg.id ? (
                        <Box>
                          <TextField
                            fullWidth
                            multiline
                            rows={4}
                            label="Your response"
                            value={responseText[msg.id] || ''}
                            onChange={(e) =>
                              setResponseText((prev) => ({
                                ...prev,
                                [msg.id]: e.target.value,
                              }))
                            }
                            sx={{ mb: 1 }}
                          />
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              startIcon={<SendIcon />}
                              onClick={() => handleRespond(msg.id)}
                            >
                              Send Response
                            </Button>
                            <Button onClick={() => setRespondingTo(null)}>Cancel</Button>
                          </Box>
                        </Box>
                      ) : (
                        <Button
                          variant="outlined"
                          startIcon={<SendIcon />}
                          onClick={() => setRespondingTo(msg.id)}
                        >
                          Respond
                        </Button>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}

export default SupportMessagesList

