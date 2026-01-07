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
  Link,
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
import { Checkbox } from '@mui/material'
import api from '../../services/api'
import { User } from '../../types'
import dayjs from 'dayjs'
import { useSelection } from '../../hooks/useSelection'
import { usePermissions } from '../../hooks/usePermissions'
import { useTranslation } from 'react-i18next'

// Component to load authenticated images
const AuthenticatedImage: React.FC<{
  messageId: number
  photoId: number
  alt: string
  onClick?: () => void
  isAdminMessage?: boolean
}> = ({ messageId, photoId, alt, onClick, isAdminMessage = false }) => {
  const { t } = useTranslation('common')
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
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.200',
        }}
      >
        <Typography variant="caption">{t('status.loading')}</Typography>
      </Box>
    )
  }

  if (error || !imageUrl) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.200',
        }}
      >
        <Typography variant="caption" color="error">
          {t('status.error')}
        </Typography>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      <img
        src={imageUrl}
        alt={alt}
        loading="lazy"
        style={{
          cursor: onClick ? 'pointer' : 'default',
          maxWidth: '100%',
          maxHeight: '100%',
          width: 'auto',
          height: 'auto',
          objectFit: 'contain',
        }}
        onClick={onClick}
      />
    </Box>
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
  const { hasPermission } = usePermissions()
  const { t } = useTranslation('support')
  const { t: tCommon } = useTranslation('common')
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
  
  const selection = useSelection(messages)
  const adminSelection = useSelection(adminMessages)

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
      alert(error.response?.data?.detail || t('messages.fetchFailed'))
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
        sorted.sort((a, b) => statusOrder[a.status as 'new' | 'responded' | 'closed'] - statusOrder[b.status as 'new' | 'responded' | 'closed'])
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
    return user.username || `${t('fields.user')} #${user.id}`
  }

  const handleDelete = async (messageId: number) => {
    if (!confirm(t('messages.deleteConfirm'))) return

    try {
      await api.delete(`/admin/support-messages/${messageId}`)
      fetchMessages()
    } catch (error: any) {
      console.error('Failed to delete message:', error)
      alert(error.response?.data?.detail || t('messages.deleteError'))
    }
  }

  const handleDeleteAdminMessage = async (messageId: number) => {
    if (!confirm(t('messages.deleteConfirm'))) return

    try {
      await api.delete(`/admin/admin-messages/${messageId}`)
      fetchAdminMessages()
    } catch (error: any) {
      console.error('Failed to delete admin message:', error)
      alert(error.response?.data?.detail || t('messages.deleteError'))
    }
  }

  const handleDeleteSelected = async () => {
    if (!confirm(t('messages.deleteSelectedConfirm', { count: selection.selectedCount }))) {
      return
    }

    try {
      for (const id of selection.selectedIds) {
        await api.delete(`/admin/support-messages/${id}`)
      }
      selection.deselectAll()
      fetchMessages()
    } catch (error: any) {
      console.error('Failed to delete messages:', error)
      alert(t('messages.deleteFailed'))
    }
  }

  const handleDeleteSelectedAdmin = async () => {
    if (!confirm(t('messages.deleteSelectedConfirm', { count: adminSelection.selectedCount }))) {
      return
    }

    try {
      for (const id of adminSelection.selectedIds) {
        await api.delete(`/admin/admin-messages/${id}`)
      }
      adminSelection.deselectAll()
      fetchAdminMessages()
    } catch (error: any) {
      console.error('Failed to delete admin messages:', error)
      alert(t('messages.deleteFailed'))
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
      alert(t('messages.sendFailed'))
      return
    }

    // Set sending state immediately
    setSendingResponse((prev) => ({ ...prev, [messageId]: true }))

    try {
      let photo_paths: string[] = []
      
      // Upload photos first if any (with compression)
      if (photos.length > 0) {
        const uploadPromises = photos.map(async (file) => {
          // Compress image before upload
          const compressedFile = await compressImage(file)
          const formData = new FormData()
          formData.append('file', compressedFile)
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
      alert(error.response?.data?.detail || t('messages.sendFailed'))
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

  // Compress image before upload
  const compressImage = async (file: File, maxWidth: number = 1920, quality: number = 0.85): Promise<File> => {
    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const img = new Image()
        img.onload = () => {
          const canvas = document.createElement('canvas')
          let width = img.width
          let height = img.height

          // Resize if too large
          if (width > maxWidth) {
            height = (height * maxWidth) / width
            width = maxWidth
          }

          canvas.width = width
          canvas.height = height

          const ctx = canvas.getContext('2d')
          if (ctx) {
            ctx.drawImage(img, 0, 0, width, height)
            canvas.toBlob(
              (blob) => {
                if (blob) {
                  const compressedFile = new File([blob], file.name, { type: 'image/jpeg' })
                  resolve(compressedFile)
                } else {
                  resolve(file)
                }
              },
              'image/jpeg',
              quality
            )
          } else {
            resolve(file)
          }
        }
        img.onerror = () => resolve(file)
        img.src = e.target?.result as string
      }
      reader.onerror = () => resolve(file)
      reader.readAsDataURL(file)
    })
  }

  const handleSendMessage = async () => {
    if (!sendMessageUser || (!sendMessageText.trim() && sendMessagePhotos.length === 0)) {
      setSendMessageError(t('messages.sendFailed'))
      return
    }

    setSendMessageError('')
    setSendingMessage(true)
    try {
      let photo_paths: string[] = []
      
      // Upload photos first if any (with compression)
      if (sendMessagePhotos.length > 0) {
        const uploadPromises = sendMessagePhotos.map(async (file) => {
          // Compress image before upload
          const compressedFile = await compressImage(file)
          const formData = new FormData()
          formData.append('file', compressedFile)
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
      alert(t('messages.sendSuccess'))
      handleCloseSendMessage()
      // Refresh admin messages if on that tab
      if (tabValue === 1) {
        fetchAdminMessages()
      }
    } catch (error: any) {
      console.error('Failed to send message:', error)
      const errorMessage = error.response?.data?.detail || t('messages.sendFailed')
      setSendMessageError(errorMessage)
    } finally {
      setSendingMessage(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('title')}
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
          {t('sendMessage')}
        </Button>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label={t('userMessages')} />
          <Tab label={t('adminMessages')} />
        </Tabs>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'error.dark', color: 'white' }}>
            <CardContent sx={{ py: 1.5, px: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <MailIcon fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{t('status.new')}</Typography>
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
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{t('status.responded')}</Typography>
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
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{tCommon('fields.total')}</Typography>
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
              label={tCommon('actions.search')}
              placeholder={tCommon('actions.search') + '...'}
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
              openOnFocus
              disablePortal={false}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('fields.user')}
                  placeholder={t('fields.user') + '...'}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label={tCommon('fields.date') + ' (' + tCommon('actions.back') + ')'}
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label={tCommon('fields.date') + ' (' + tCommon('actions.next') + ')'}
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              InputLabelProps={{ shrink: true }}
              error={!!(dateFrom && dateTo && dateFrom > dateTo)}
              helperText={dateFrom && dateTo && dateFrom > dateTo ? tCommon('messages.invalidFormat') : ''}
            />
          </Grid>
          {tabValue === 0 && (
            <>
          <Grid item xs={12} md={2.5}>
            <FormControl fullWidth>
              <InputLabel id="status-filter-label">{tCommon('fields.status')}</InputLabel>
              <Select
                labelId="status-filter-label"
                id="status-filter-select"
                value={statusFilter}
                label={tCommon('fields.status')}
                onChange={(e) => setStatusFilter(e.target.value)}
                MenuProps={{
                  disablePortal: false,
                  PaperProps: {
                    style: {
                      maxHeight: 300,
                    },
                  },
                }}
              >
                <MenuItem value="all">{tCommon('status.all')}</MenuItem>
                <MenuItem value="new">{t('status.new')}</MenuItem>
                <MenuItem value="responded">{t('status.responded')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2.5}>
            <FormControl fullWidth>
              <InputLabel id="sort-filter-label">{tCommon('actions.sort')}</InputLabel>
              <Select
                labelId="sort-filter-label"
                id="sort-filter-select"
                value={sortBy}
                label={tCommon('actions.sort')}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                MenuProps={{
                  disablePortal: false,
                  PaperProps: {
                    style: {
                      maxHeight: 300,
                    },
                  },
                }}
              >
                <MenuItem value="newest">{tCommon('status.newest')}</MenuItem>
                <MenuItem value="oldest">{tCommon('status.oldest')}</MenuItem>
                <MenuItem value="status">{tCommon('status.byStatus')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
            </>
          )}
        </Grid>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          {hasPermission('support', 'delete') && tabValue === 0 && selection.hasSelection && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelected}
            >
              {t('deleteSelected')}
            </Button>
          )}
          {hasPermission('support', 'delete') && tabValue === 1 && adminSelection.hasSelection && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelectedAdmin}
            >
              {t('deleteSelected')}
            </Button>
          )}
          {hasPermission('support', 'delete') && tabValue === 0 && (
            <Checkbox
              checked={selection.getSelectionState() === 'all'}
              indeterminate={selection.getSelectionState() === 'some'}
              onChange={selection.handleSelectAllClick}
            />
          )}
          {hasPermission('support', 'delete') && tabValue === 1 && (
            <Checkbox
              checked={adminSelection.getSelectionState() === 'all'}
              indeterminate={adminSelection.getSelectionState() === 'some'}
              onChange={adminSelection.handleSelectAllClick}
            />
          )}
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={tabValue === 0 ? fetchMessages : fetchAdminMessages}
          >
            {tCommon('actions.refresh')}
          </Button>
          <Button variant="outlined" onClick={clearFilters}>
            {tCommon('actions.reset')}
          </Button>
        </Box>
      </Paper>

      {/* Messages List */}
      {tabValue === 0 ? (
        <>
      {loading ? (
        <Typography>{t('common:status.loading')}</Typography>
      ) : messages.length === 0 ? (
        <Typography>{t('messages.noResults')}</Typography>
      ) : (
        <Grid container spacing={2}>
          {messages.map((msg) => (
            <Grid item xs={12} key={msg.id}>
              <Card
                sx={{
                  cursor: hasPermission('support', 'delete') && selection.hasSelection ? 'pointer' : 'default',
                  border: hasPermission('support', 'delete') && selection.isSelected(msg.id) ? '2px solid' : 'none',
                  borderColor: hasPermission('support', 'delete') && selection.isSelected(msg.id) ? 'primary.main' : 'transparent',
                  bgcolor: hasPermission('support', 'delete') && selection.isSelected(msg.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
                }}
                onClick={() => {
                  if (hasPermission('support', 'delete') && selection.hasSelection) {
                    selection.toggleSelection(msg.id)
                  }
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {msg.username ? (
                          <Link
                            href={`https://t.me/${msg.username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{ textDecoration: 'none', color: 'inherit', '&:hover': { textDecoration: 'underline' } }}
                          >
                        {getUserDisplayName(msg)}
                          </Link>
                        ) : (
                          getUserDisplayName(msg)
                        )}
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
                      {!selection.hasSelection && hasPermission('support', 'delete') && (
                        <IconButton
                          color="error"
                          onClick={() => handleDelete(msg.id)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Box>

                  <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                    {msg.message && msg.message.trim() && (
                    <Typography variant="body1">{msg.message}</Typography>
                    )}
                    {/* User photos */}
                    {msg.photos && msg.photos.filter(p => !p.is_admin_photo).length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <ImageList cols={3} rowHeight={200} gap={8} sx={{ mt: 1 }}>
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

                  {(msg.admin_response || (msg.photos && msg.photos.filter(p => p.is_admin_photo).length > 0)) ? (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        {t('adminResponse')} {msg.responded_by && t('byAdmin', { admin: msg.responded_by })}
                        {msg.responded_at && t('onDate', { date: formatDate(msg.responded_at) })}
                      </Typography>
                      {msg.admin_response && (
                      <Typography variant="body1">{msg.admin_response}</Typography>
                      )}
                      {/* Admin photos */}
                      {msg.photos && msg.photos.filter(p => p.is_admin_photo).length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <ImageList cols={3} rowHeight={200} gap={8} sx={{ mt: 1 }}>
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
                            label={t('yourResponse')}
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
                                {t('addPhotos')}
                              </Button>
                            </label>
                            {responsePhotos[msg.id] && responsePhotos[msg.id].length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  {t('photosSelected', { count: responsePhotos[msg.id].length })}
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
                              {sendingResponse[msg.id] ? tCommon('status.loading') : t('respondButton')}
                            </Button>
                            <Button 
                              onClick={() => {
                              setRespondingTo(null)
                              setResponsePhotos((prev) => ({ ...prev, [msg.id]: [] }))
                              }}
                              disabled={sendingResponse[msg.id]}
                            >
                              {tCommon('actions.cancel')}
                            </Button>
                          </Box>
                        </Box>
                      ) : msg.status !== 'responded' && msg.status !== 'closed' && !selection.hasSelection ? (
                        <Button
                          variant="outlined"
                          startIcon={<SendIcon />}
                          onClick={() => setRespondingTo(msg.id)}
                        >
                          {t('respondButton')}
                        </Button>
                      ) : null}
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
            <Typography>{t('common:status.loading')}</Typography>
          ) : adminMessages.length === 0 ? (
            <Typography>{t('messages.noResults')}</Typography>
          ) : (
            <Grid container spacing={2}>
              {adminMessages.map((msg) => (
                <Grid item xs={12} key={msg.id}>
                  <Card
                    sx={{
                      cursor: hasPermission('support', 'delete') && adminSelection.hasSelection ? 'pointer' : 'default',
                      border: hasPermission('support', 'delete') && adminSelection.isSelected(msg.id) ? '2px solid' : 'none',
                      borderColor: hasPermission('support', 'delete') && adminSelection.isSelected(msg.id) ? 'primary.main' : 'transparent',
                      bgcolor: hasPermission('support', 'delete') && adminSelection.isSelected(msg.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
                    }}
                    onClick={() => {
                      if (hasPermission('support', 'delete') && adminSelection.hasSelection) {
                        adminSelection.toggleSelection(msg.id)
                      }
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {t('toUser')}: {msg.first_name || msg.last_name || msg.username || `${t('fields.user')} #${msg.user_id}`}
                            {msg.username && ` (@${msg.username})`}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {t('fromAdmin')}: {msg.sent_by} • {dayjs(msg.created_at).format('DD.MM.YYYY HH:mm')}
                          </Typography>
                        </Box>
                        {!adminSelection.hasSelection && hasPermission('support', 'delete') && (
                          <IconButton
                            color="error"
                            onClick={() => handleDeleteAdminMessage(msg.id)}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        )}
                      </Box>

                      {msg.message && (
                        <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                          <Typography variant="body1">{msg.message}</Typography>
                        </Box>
                      )}

                      {/* Admin photos */}
                      {msg.photos && msg.photos.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <ImageList cols={3} rowHeight={200} gap={8} sx={{ mt: 1 }}>
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
        <DialogTitle>{t('sendMessageToUser')}</DialogTitle>
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
                  label={t('fields.user')}
                  placeholder={t('chooseUserPlaceholder')}
                  required
                />
              )}
            />
            <TextField
              fullWidth
              multiline
              rows={6}
              label={t('fields.message')}
              placeholder={t('enterYourMessagePlaceholder')}
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
                  {t('addPhotos')}
                </Button>
              </label>
              {sendMessagePhotos.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {t('photosSelected', { count: sendMessagePhotos.length })}
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
          <Button onClick={handleCloseSendMessage}>{tCommon('actions.cancel')}</Button>
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!sendMessageUser || (!sendMessageText.trim() && sendMessagePhotos.length === 0) || sendingMessage}
            startIcon={<SendIcon />}
          >
            {sendingMessage ? tCommon('status.loading') : tCommon('actions.send')}
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
