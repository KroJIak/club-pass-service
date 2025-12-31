import React, { useState, useEffect, useMemo } from 'react'
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
  Autocomplete,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Send as SendIcon,
  Search as SearchIcon,
  Mail as MailIcon,
  CheckCircle as CheckCircleIcon,
  Inbox as InboxIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import api from '../../services/api'
import { User } from '../../types'
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

type SortOption = 'newest' | 'oldest' | 'status'

const SupportMessagesList: React.FC = () => {
  const [messages, setMessages] = useState<SupportMessage[]>([])
  const [allMessages, setAllMessages] = useState<SupportMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [users, setUsers] = useState<User[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [searchText, setSearchText] = useState<string>('')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  
  const [responseText, setResponseText] = useState<{ [key: number]: string }>({})
  const [respondingTo, setRespondingTo] = useState<number | null>(null)
  
  // Send message dialog state
  const [sendMessageOpen, setSendMessageOpen] = useState(false)
  const [sendMessageUser, setSendMessageUser] = useState<User | null>(null)
  const [sendMessageText, setSendMessageText] = useState('')
  const [sendingMessage, setSendingMessage] = useState(false)

  // Fetch users for autocomplete
  useEffect(() => {
    fetchUsers()
  }, [])

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

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchMessages()
    }, 400)
    return () => clearTimeout(timer)
  }, [searchText])

  // Fetch messages when filters change
  useEffect(() => {
    fetchMessages()
  }, [statusFilter, selectedUser, dateFrom, dateTo])

  const fetchMessages = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (statusFilter !== 'all') {
        params.status = statusFilter
      }
      if (selectedUser) {
        params.user_id = selectedUser.id
      }
      if (dateFrom) {
        params.date_from = dateFrom
      }
      if (dateTo) {
        params.date_to = dateTo
      }
      if (searchText.trim().length >= 2) {
        params.search = searchText.trim()
      }
      
      const response = await api.get('/admin/support-messages', { params })
      const fetchedMessages = response.data.messages || []
      setAllMessages(fetchedMessages)
      setMessages(fetchedMessages)
    } catch (error: any) {
      console.error('Failed to fetch support messages:', error)
      alert(error.response?.data?.detail || 'Failed to fetch support messages')
    } finally {
      setLoading(false)
    }
  }

  // Apply sorting
  useEffect(() => {
    let sorted = [...allMessages]
    
    switch (sortBy) {
      case 'newest':
        sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
      case 'oldest':
        sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'status':
        const statusOrder = { 'new': 0, 'responded': 1, 'closed': 2 }
        sorted.sort((a, b) => statusOrder[a.status] - statusOrder[b.status])
        break
    }
    
    setMessages(sorted)
  }, [sortBy, allMessages])

  // Calculate statistics
  const statistics = useMemo(() => {
    const newCount = allMessages.filter(m => m.status === 'new').length
    const respondedCount = allMessages.filter(m => m.status === 'responded').length
    const totalCount = allMessages.length
    return { newCount, respondedCount, totalCount }
  }, [allMessages])

  const getUserLabel = (user: User) => {
    if (user.first_name || user.last_name) {
      const name = [user.first_name, user.last_name].filter(Boolean).join(' ')
      return user.username ? `${name} (@${user.username})` : name
    }
    return user.username || `User #${user.id}`
  }

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

  const clearFilters = () => {
    setStatusFilter('all')
    setSelectedUser(null)
    setDateFrom('')
    setDateTo('')
    setSearchText('')
    setSortBy('newest')
  }

  const handleOpenSendMessage = () => {
    setSendMessageOpen(true)
    setSendMessageUser(null)
    setSendMessageText('')
  }

  const handleCloseSendMessage = () => {
    setSendMessageOpen(false)
    setSendMessageUser(null)
    setSendMessageText('')
  }

  const handleSendMessage = async () => {
    if (!sendMessageUser || !sendMessageText.trim()) {
      alert('Please select a user and enter a message')
      return
    }

    setSendingMessage(true)
    try {
      await api.post('/admin/send-message', {
        telegram_user_id: sendMessageUser.telegram_user_id,
        message: sendMessageText.trim(),
      })
      alert('Message sent successfully!')
      handleCloseSendMessage()
    } catch (error: any) {
      console.error('Failed to send message:', error)
      alert(error.response?.data?.detail || 'Failed to send message')
    } finally {
      setSendingMessage(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Support Messages
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'error.dark', color: 'white' }}>
            <CardContent sx={{ py: 1.5, px: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <MailIcon fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>New Messages</Typography>
              </Box>
              <Typography variant="h5" sx={{ mt: 0.5, fontWeight: 'bold' }}>
                {statistics.newCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'success.dark', color: 'white' }}>
            <CardContent sx={{ py: 1.5, px: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircleIcon fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Responded</Typography>
              </Box>
              <Typography variant="h5" sx={{ mt: 0.5, fontWeight: 'bold' }}>
                {statistics.respondedCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'grey.700', color: 'white' }}>
            <CardContent sx={{ py: 1.5, px: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <InboxIcon fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Total</Typography>
              </Box>
              <Typography variant="h5" sx={{ mt: 0.5, fontWeight: 'bold' }}>
                {statistics.totalCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters Panel */}
      <Paper sx={{ p: 2, mb: 3 }}>
        {/* Search on separate row */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Search"
              placeholder="Search in messages..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
        </Grid>
        
        {/* Other filters */}
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={users}
              getOptionLabel={getUserLabel}
              loading={loadingUsers}
              value={selectedUser}
              onChange={(_, newValue) => {
                setSelectedUser(newValue)
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Filter by User"
                  placeholder="Select user..."
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label="Date From"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label="Date To"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              InputLabelProps={{ shrink: true }}
              error={!!(dateFrom && dateTo && dateFrom > dateTo)}
              helperText={dateFrom && dateTo && dateFrom > dateTo ? 'Date To must be after Date From' : ''}
            />
          </Grid>
          <Grid item xs={12} md={2.5}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="new">New</MenuItem>
                <MenuItem value="responded">Responded</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2.5}>
            <FormControl fullWidth>
              <InputLabel>Sort</InputLabel>
              <Select
                value={sortBy}
                label="Sort"
                onChange={(e) => setSortBy(e.target.value as SortOption)}
              >
                <MenuItem value="newest">Newest First</MenuItem>
                <MenuItem value="oldest">Oldest First</MenuItem>
                <MenuItem value="status">By Status</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchMessages}
          >
            Refresh
          </Button>
          <Button variant="outlined" onClick={clearFilters}>
            Clear Filters
          </Button>
        </Box>
      </Paper>

      {/* Messages List */}
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

      {/* Send Message Dialog */}
      <Dialog open={sendMessageOpen} onClose={handleCloseSendMessage} maxWidth="sm" fullWidth>
        <DialogTitle>Send Message to User</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Autocomplete
              options={users}
              getOptionLabel={getUserLabel}
              loading={loadingUsers}
              value={sendMessageUser}
              onChange={(_, newValue) => {
                setSendMessageUser(newValue)
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select User"
                  placeholder="Choose user..."
                  required
                />
              )}
            />
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Message"
              placeholder="Enter your message..."
              value={sendMessageText}
              onChange={(e) => setSendMessageText(e.target.value)}
              required
              helperText="You can use HTML formatting (e.g., &lt;b&gt;bold&lt;/b&gt;, &lt;i&gt;italic&lt;/i&gt;)"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSendMessage}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!sendMessageUser || !sendMessageText.trim() || sendingMessage}
            startIcon={<SendIcon />}
          >
            {sendingMessage ? 'Sending...' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SupportMessagesList
