import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Typography,
  Chip,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Delete as DeleteIcon, Close as CloseIcon, Edit as EditIcon } from '@mui/icons-material'
import api from '../../services/api'
import { TicketType, TicketTypeTemplate } from '../../types'
import TicketTypeForm from './TicketTypeForm'
import TicketTypeTemplateForm from './TicketTypeTemplateForm'
import { usePermissions } from '../../hooks/usePermissions'

const TicketTypesList = () => {
  const { hasPermission } = usePermissions()
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [templates, setTemplates] = useState<TicketTypeTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [templateFormOpen, setTemplateFormOpen] = useState(false)
  const [editingTicketType, setEditingTicketType] = useState<TicketType | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<TicketTypeTemplate | null>(null)

  const fetchTicketTypes = async () => {
    try {
      const response = await api.get('/admin/ticket-types')
      setTicketTypes(response.data.ticket_types)
    } catch (error) {
      console.error('Failed to fetch ticket types:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/admin/ticket-type-templates')
      console.log('Templates response:', response.data)
      setTemplates(response.data.templates || [])
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  useEffect(() => {
    fetchTicketTypes()
    fetchTemplates()
  }, [])

  const handleDelete = async (ticketTypeId: number) => {
    if (!confirm('Are you sure you want to delete this ticket type?')) {
      return
    }
    try {
      await api.delete(`/admin/ticket-types/${ticketTypeId}`)
      fetchTicketTypes()
    } catch (error: any) {
      console.error('Failed to delete ticket type:', error)
      alert(error.response?.data?.detail || 'Failed to delete ticket type')
    }
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Ticket Types</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {hasPermission('tickets', 'write') && (
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />}
              onClick={() => {
                setTemplateFormOpen(true)
              }}
            >
              Create Template
            </Button>
          )}
          {hasPermission('tickets', 'write') && (
            <Button 
              variant="contained" 
              startIcon={<AddIcon />}
              onClick={() => {
                setEditingTicketType(null)
                setFormOpen(true)
              }}
            >
              Create New
            </Button>
          )}
        </Box>
      </Box>

      {/* Display templates as buttons */}
      {templates.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
            Templates:
          </Typography>
          {templates.map((template) => (
            <Button
              key={template.id}
              variant="outlined"
              size="small"
              onClick={() => {
                // Open form with template data
                setSelectedTemplate(template)
                setEditingTicketType(null)
                setFormOpen(true)
              }}
              sx={{ position: 'relative', pr: 4 }}
            >
              {template.name}
              <IconButton
                size="small"
                color="error"
                onClick={async (e) => {
                  e.stopPropagation()
                  if (confirm(`Delete template "${template.name}"?`)) {
                    try {
                      await api.delete(`/admin/ticket-type-templates/${template.id}`)
                      fetchTemplates()
                    } catch (error: any) {
                      console.error('Failed to delete template:', error)
                      alert(error.response?.data?.detail || 'Failed to delete template')
                    }
                  }
                }}
                title="Delete template"
                sx={{
                  position: 'absolute',
                  right: 4,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  padding: 0.5,
                }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Button>
          ))}
        </Box>
      )}

      <Grid container spacing={3}>
        {ticketTypes.map((tt) => (
          <Grid item xs={12} sm={6} md={4} key={tt.id}>
            <Card
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 4,
                },
              }}
              onClick={() => {
                setEditingTicketType(tt)
                setSelectedTemplate(null)
                setFormOpen(true)
              }}
            >
              <CardContent>
                <Typography variant="h6">{tt.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Price: {tt.price % 1 === 0 ? Math.floor(tt.price) : tt.price} ₽
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available: {tt.available_quantity} / {tt.total_quantity}
                </Typography>
                <Chip
                  label={tt.is_active ? 'Active' : 'Inactive'}
                  color={tt.is_active ? 'success' : 'default'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                <IconButton
                  size="small"
                  color="primary"
                  onClick={(e) => {
                    e.stopPropagation()
                    setEditingTicketType(tt)
                    setSelectedTemplate(null)
                    setFormOpen(true)
                  }}
                  title="Edit"
                  disabled={!hasPermission('tickets', 'write')}
                >
                  <EditIcon />
                </IconButton>
                {hasPermission('tickets', 'delete') && (
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(tt.id)
                    }}
                    title="Delete"
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <TicketTypeForm
        open={formOpen}
        ticketType={editingTicketType}
        template={selectedTemplate}
        onClose={() => {
          setFormOpen(false)
          setEditingTicketType(null)
          setSelectedTemplate(null)
        }}
        onSuccess={() => {
          fetchTicketTypes()
          setFormOpen(false)
          setEditingTicketType(null)
          setSelectedTemplate(null)
        }}
      />

      <TicketTypeTemplateForm
        open={templateFormOpen}
        onClose={() => {
          setTemplateFormOpen(false)
        }}
        onSuccess={() => {
          fetchTemplates()
          setTemplateFormOpen(false)
        }}
      />
    </Box>
  )
}

export default TicketTypesList

