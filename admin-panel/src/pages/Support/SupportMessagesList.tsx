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
  ImageList,
  ImageListItem,
  Tabs,
  Tab,
  Modal,
  Backdrop,
  Fade,
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

// Component to load authenticated images
const AuthenticatedImage: React.FC<{
  messageId: number
  photoId: number
  alt: string
  onClick?: () => void
  isAdminMessage?: boolean
}> = ({ messageId, photoId, alt, onClick, isAdminMessage = false }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const loadImage = async () => {
      try {
        const token = localStorage.getItem('token')
        const endpoint = isAdminMessage
          ? `/admin/admin-messages/${messageId}/photos/${photoId}`
          : `/admin/support-messages/${messageId}/photos/${photoId}`
        const response = await api.get(
          endpoint,
          {
            responseType: 'blob',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        const blob = new Blob([response.data])
        const url = URL.createObjectURL(blob)
        setImageUrl(url)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load image:', err)
        setError(true)
        setLoading(false)
      }
    }

    loadImage()

    // Cleanup blob URL on unmount
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [messageId, photoId, isAdminMessage])

  if (loading) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.200',
        }}
      >
        <Typography variant="caption">Loading...</Typography>
      </Box>
    )
  }

  if (error || !imageUrl) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.200',
        }}
      >
        <Typography variant="caption" color="error">
          Failed to load
        </Typography>
      </Box>
    )
  }

  return (
    <img
      src={imageUrl}
      alt={alt}
      loading="lazy"
      style={{ cursor: onClick ? 'pointer' : 'default', width: '100%', height: '100%', objectFit: 'contain' }}
      onClick={onClick}
    />
  )
}

interface SupportMessagePhoto {
  id: number
  support_message_id: number
  file_path: string
  file_name: string
  file_size: number
  mime_type: string
  is_admin_photo: boolean
  created_at: string
}

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
  photos: SupportMessagePhoto[]
}

interface AdminMessagePhoto {
  id: number
  admin_message_id: number
  file_path: string
  file_name: string
  file_size: number
  mime_type: string
  created_at: string
}

interface AdminMessage {
  id: number
  user_id: number
  message: string | null
  sent_by: string
  created_at: string
  updated_at: string
  username: string | null
  first_name: string | null
  last_name: string | null
  photos: AdminMessagePhoto[]
}

type SortOption = 'newest' | 'oldest' | 'status'

const SupportMessagesList: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [messages, setMessages] = useState<SupportMessage[]>([])
  const [allMessages, setAllMessages] = useState<SupportMessage[]>([])
  const [adminMessages, setAdminMessages] = useState<AdminMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingAdminMessages, setLoadingAdminMessages] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  
  // Image modal state
  const [selectedImage, setSelectedImage] = useState<{ url: string; alt: string } | null>(null)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [searchText, setSearchText] = useState<string>('')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  
  const [responseText, setResponseText] = useState<{ [key: number]: string }>({})
  const [respondingTo, setRespondingTo] = useState<number | null>(null)
  const [responsePhotos, setResponsePhotos] = useState<{ [key: number]: File[] }>({})
  const [sendingResponse, setSendingResponse] = useState<{ [key: number]: boolean }>({})
  
  // Send message dialog state
  const [sendMessageOpen, setSendMessageOpen] = useState(false)
  const [sendMessageUser, setSendMessageUser] = useState<User | null>(null)
  const [sendMessageText, setSendMessageText] = useState('')
  const [sendMessagePhotos, setSendMessagePhotos] = useState<File[]>([])
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
    if (tabValue === 0) {
    fetchMessages()
    } else {
      fetchAdminMessages()
    }
  }, [statusFilter, selectedUser, dateFrom, dateTo, tabValue])

  const fetchAdminMessages = async () => {
    setLoadingAdminMessages(true)
    try {
      const params: any = {}
      if (selectedUser) {
        params.user_id = selectedUser.id
      }
      if (dateFrom) {
        params.date_from = dateFrom
      }
      if (dateTo) {
        params.date_to = dateTo
      }
      params.limit = 100
      params.offset = 0
      
      const response = await api.get('/admin/admin-messages', { params })
      setAdminMessages(response.data || [])
    } catch (error) {
      console.error('Failed to fetch admin messages:', error)
    } finally {
      setLoadingAdminMessages(false)
    }
  }

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
    // Prevent multiple clicks
    if (sendingResponse[messageId]) {
      return
    }
    
    const response = responseText[messageId]?.trim() || ''
    const photos = responsePhotos[messageId] || []
    
    // Allow sending only photos or only text or both
    if (!response && photos.length === 0) {
      alert('Please enter a response or add photos')
      return
    }

    // Set sending state immediately
    setSendingResponse((prev) => ({ ...prev, [messageId]: true }))

    try {
      let photo_paths: string[] = []
      
      // Upload photos first if any
      if (photos.length > 0) {
        const uploadPromises = photos.map(async (file) => {
          const formData = new FormData()
          formData.append('file', file)
          const uploadResponse = await api.post('/admin/upload-photo', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          return uploadResponse.data.file_path
        })
        photo_paths = await Promise.all(uploadPromises)
      }
      
      await api.put(`/admin/support-messages/${messageId}/respond`, {
        admin_response: response,  // Can be empty if only photos
        photo_paths: photo_paths,
      })
      setResponseText((prev) => ({ ...prev, [messageId]: '' }))
      setResponsePhotos((prev) => ({ ...prev, [messageId]: [] }))
      setRespondingTo(null)
      fetchMessages()
    } catch (error: any) {
      console.error('Failed to send response:', error)
      alert(error.response?.data?.detail || 'Failed to send response')
    } finally {
      // Clear sending state
      setSendingResponse((prev) => ({ ...prev, [messageId]: false }))
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

  const handleCloseSendMessage = () => {
    setSendMessageOpen(false)
    setSendMessageUser(null)
    setSendMessageText('')
    setSendMessagePhotos([])
    setSendMessageError('')
  }

  const [sendMessageError, setSendMessageError] = useState<string>('')

  const handleSendMessage = async () => {
    if (!sendMessageUser || (!sendMessageText.trim() && sendMessagePhotos.length === 0)) {
      setSendMessageError('Please select a user and enter a message or add photos')
      return
    }

    setSendMessageError('')
    setSendingMessage(true)
    try {
      let photo_paths: string[] = []
      
      // Upload photos first if any
      if (sendMessagePhotos.length > 0) {
        const uploadPromises = sendMessagePhotos.map(async (file) => {
          const formData = new FormData()
          formData.append('file', file)
          const uploadResponse = await api.post('/admin/upload-photo', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          return uploadResponse.data.file_path
        })
        photo_paths = await Promise.all(uploadPromises)
      }
      
      await api.post('/admin/send-message', {
        telegram_user_id: sendMessageUser.telegram_user_id,
        message: sendMessageText.trim() || '',
        photo_paths: photo_paths,
      })
      alert('Message sent successfully!')
      handleCloseSendMessage()
      // Refresh admin messages if on that tab
      if (tabValue === 1) {
        fetchAdminMessages()
      }
    } catch (error: any) {
      console.error('Failed to send message:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to send message'
      setSendMessageError(errorMessage)
    } finally {
      setSendingMessage(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Support Messages
        </Typography>
        <Button
          variant="contained"
          startIcon={<SendIcon />}
          onClick={() => {
            setSendMessageOpen(true)
            setSendMessageUser(null)
            setSendMessageText('')
          }}
        >
          Send Message
        </Button>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="User Messages" />
          <Tab label="Admin Messages History" />
        </Tabs>
      </Box>

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
          {tabValue === 0 && (
            <>
          <Grid item xs={12} md={2.5}>
            <TextField
              fullWidth
              select
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              SelectProps={{
                native: false,
              }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="new">New</MenuItem>
              <MenuItem value="responded">Responded</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={2.5}>
            <TextField
              fullWidth
              select
              label="Sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              SelectProps={{
                native: false,
              }}
            >
              <MenuItem value="newest">Newest First</MenuItem>
              <MenuItem value="oldest">Oldest First</MenuItem>
              <MenuItem value="status">By Status</MenuItem>
            </TextField>
          </Grid>
            </>
          )}
        </Grid>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={tabValue === 0 ? fetchMessages : fetchAdminMessages}
          >
            Refresh
          </Button>
          <Button variant="outlined" onClick={clearFilters}>
            Clear Filters
          </Button>
        </Box>
      </Paper>

      {/* Messages List */}
      {tabValue === 0 ? (
        <>
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
                    {msg.message && msg.message.trim() && (
                      <Typography variant="body1">{msg.message}</Typography>
                    )}
                    {/* User photos */}
                    {msg.photos && msg.photos.filter(p => !p.is_admin_photo).length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <ImageList cols={3} rowHeight={100} sx={{ mt: 1 }}>
                          {msg.photos.filter(p => !p.is_admin_photo).map((photo) => (
                            <ImageListItem key={photo.id}>
                              <AuthenticatedImage
                                messageId={msg.id}
                                photoId={photo.id}
                                alt={photo.file_name}
                                onClick={async () => {
                                  try {
                                    const token = localStorage.getItem('token')
                                    const response = await api.get(
                                      `/admin/support-messages/${msg.id}/photos/${photo.id}`,
                                      {
                                        responseType: 'blob',
                                        headers: {
                                          Authorization: `Bearer ${token}`,
                                        },
                                      }
                                    )
                                    const blob = new Blob([response.data])
                                    const url = URL.createObjectURL(blob)
                                    setSelectedImage({ url, alt: photo.file_name })
                                  } catch (err) {
                                    console.error('Failed to open image:', err)
                                  }
                                }}
                              />
                            </ImageListItem>
                          ))}
                        </ImageList>
                      </Box>
                    )}
                  </Box>

                  {msg.admin_response ? (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Admin Response {msg.responded_by && `by ${msg.responded_by}`}
                        {msg.responded_at && ` on ${formatDate(msg.responded_at)}`}
                      </Typography>
                      <Typography variant="body1">{msg.admin_response}</Typography>
                      {/* Admin photos */}
                      {msg.photos && msg.photos.filter(p => p.is_admin_photo).length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <ImageList cols={3} rowHeight={100} sx={{ mt: 1 }}>
                            {msg.photos.filter(p => p.is_admin_photo).map((photo) => (
                              <ImageListItem key={photo.id}>
                                <AuthenticatedImage
                                  messageId={msg.id}
                                  photoId={photo.id}
                                  alt={photo.file_name}
                                  onClick={async () => {
                                    try {
                                      const token = localStorage.getItem('token')
                                      const response = await api.get(
                                        `/admin/support-messages/${msg.id}/photos/${photo.id}`,
                                        {
                                          responseType: 'blob',
                                          headers: {
                                            Authorization: `Bearer ${token}`,
                                          },
                                        }
                                      )
                                      const blob = new Blob([response.data])
                                      const url = URL.createObjectURL(blob)
                                      setSelectedImage({ url, alt: photo.file_name })
                                    } catch (err) {
                                      console.error('Failed to open image:', err)
                                    }
                                  }}
                                />
                              </ImageListItem>
                            ))}
                          </ImageList>
                        </Box>
                      )}
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
                          <Box sx={{ mb: 2 }}>
                            <input
                              accept="image/*"
                              style={{ display: 'none' }}
                              id={`photo-upload-${msg.id}`}
                              type="file"
                              multiple
                              onChange={(e) => {
                                const files = Array.from(e.target.files || [])
                                setResponsePhotos((prev) => ({
                                  ...prev,
                                  [msg.id]: [...(prev[msg.id] || []), ...files],
                                }))
                              }}
                            />
                            <label htmlFor={`photo-upload-${msg.id}`}>
                              <Button variant="outlined" component="span" size="small" sx={{ mr: 1 }}>
                                Add Photos
                              </Button>
                            </label>
                            {responsePhotos[msg.id] && responsePhotos[msg.id].length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  {responsePhotos[msg.id].length} photo(s) selected
                                </Typography>
                                <ImageList cols={3} rowHeight={80} sx={{ mt: 1 }}>
                                  {responsePhotos[msg.id].map((file, index) => (
                                    <ImageListItem key={index}>
                                      <img
                                        src={URL.createObjectURL(file)}
                                        alt={file.name}
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => {
                                          setResponsePhotos((prev) => ({
                                            ...prev,
                                            [msg.id]: prev[msg.id].filter((_, i) => i !== index),
                                          }))
                                        }}
                                      />
                                    </ImageListItem>
                                  ))}
                                </ImageList>
                              </Box>
                            )}
                          </Box>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              startIcon={<SendIcon />}
                              onClick={() => handleRespond(msg.id)}
                              disabled={sendingResponse[msg.id]}
                            >
                              {sendingResponse[msg.id] ? 'Sending...' : 'Send Response'}
                            </Button>
                            <Button 
                              onClick={() => {
                                setRespondingTo(null)
                                setResponsePhotos((prev) => ({ ...prev, [msg.id]: [] }))
                              }}
                              disabled={sendingResponse[msg.id]}
                            >
                              Cancel
                            </Button>
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
        </>
      ) : (
        <>
          {loadingAdminMessages ? (
            <Typography>Loading...</Typography>
          ) : adminMessages.length === 0 ? (
            <Typography>No admin messages found</Typography>
          ) : (
            <Grid container spacing={2}>
              {adminMessages.map((msg) => (
                <Grid item xs={12} key={msg.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            To: {msg.first_name || msg.last_name || msg.username || `User #${msg.user_id}`}
                            {msg.username && ` (@${msg.username})`}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            From: {msg.sent_by} • {dayjs(msg.created_at).format('DD.MM.YYYY HH:mm')}
                          </Typography>
                        </Box>
                      </Box>

                      {msg.message && (
                        <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                          <Typography variant="body1">{msg.message}</Typography>
                        </Box>
                      )}

                      {/* Admin photos */}
                      {msg.photos && msg.photos.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <ImageList cols={3} rowHeight={150} sx={{ mt: 1 }}>
                            {msg.photos.map((photo) => (
                              <ImageListItem key={photo.id}>
                                <AuthenticatedImage
                                  messageId={msg.id}
                                  photoId={photo.id}
                                  alt={photo.file_name}
                                  isAdminMessage={true}
                                  onClick={async () => {
                                    try {
                                      const token = localStorage.getItem('token')
                                      const response = await api.get(
                                        `/admin/admin-messages/${msg.id}/photos/${photo.id}`,
                                        {
                                          responseType: 'blob',
                                          headers: {
                                            Authorization: `Bearer ${token}`,
                                          },
                                        }
                                      )
                                      const blob = new Blob([response.data])
                                      const url = URL.createObjectURL(blob)
                                      setSelectedImage({ url, alt: photo.file_name })
                                    } catch (err) {
                                      console.error('Failed to open image:', err)
                                    }
                                  }}
                                />
                              </ImageListItem>
                            ))}
                          </ImageList>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </>
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
              onChange={(e) => {
                setSendMessageText(e.target.value)
                setSendMessageError('')
              }}
              required
              error={!!sendMessageError}
              helperText={sendMessageError || ""}
            />
            <Box>
              <input
                accept="image/*"
                style={{ display: 'none' }}
                id="send-message-photo-upload"
                type="file"
                multiple
                onChange={(e) => {
                  const files = Array.from(e.target.files || [])
                  setSendMessagePhotos((prev) => [...prev, ...files])
                }}
              />
              <label htmlFor="send-message-photo-upload">
                <Button variant="outlined" component="span" size="small">
                  Add Photos
                </Button>
              </label>
              {sendMessagePhotos.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {sendMessagePhotos.length} photo(s) selected
                  </Typography>
                  <ImageList cols={3} rowHeight={80} sx={{ mt: 1 }}>
                    {sendMessagePhotos.map((file, index) => (
                      <ImageListItem key={index}>
                        <img
                          src={URL.createObjectURL(file)}
                          alt={file.name}
                          style={{ cursor: 'pointer' }}
                          onClick={() => {
                            setSendMessagePhotos((prev) => prev.filter((_, i) => i !== index))
                          }}
                        />
                      </ImageListItem>
                    ))}
                  </ImageList>
                </Box>
              )}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSendMessage}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!sendMessageUser || (!sendMessageText.trim() && sendMessagePhotos.length === 0) || sendingMessage}
            startIcon={<SendIcon />}
          >
            {sendingMessage ? 'Sending...' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Image Modal */}
      <Modal
        open={!!selectedImage}
        onClose={() => {
          if (selectedImage) {
            URL.revokeObjectURL(selectedImage.url)
            setSelectedImage(null)
          }
        }}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Fade in={!!selectedImage}>
          <Box
            sx={{
              position: 'relative',
              maxWidth: '90vw',
              maxHeight: '90vh',
              outline: 'none',
            }}
            onClick={() => {
              if (selectedImage) {
                URL.revokeObjectURL(selectedImage.url)
                setSelectedImage(null)
              }
            }}
          >
            {selectedImage && (
              <img
                src={selectedImage.url}
                alt={selectedImage.alt}
                style={{
                  maxWidth: '100%',
                  maxHeight: '90vh',
                  objectFit: 'contain',
                  display: 'block',
                }}
              />
            )}
          </Box>
        </Fade>
      </Modal>
    </Box>
  )
}

export default SupportMessagesList
