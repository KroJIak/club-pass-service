import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Box,
  Typography,
  Divider,
} from '@mui/material'
import api from '../../services/api'
import { AdminGroup, AdminPermission, AdminPermissionItem, AdminPermissionUpdateRequest } from '../../types'

interface PermissionsEditorProps {
  open: boolean
  onClose: () => void
  group: AdminGroup
  onSave: () => void
}

const RESOURCES: Array<{ key: string; label: string }> = [
  { key: 'qr_scanner', label: 'QR Scanner' },
  { key: 'events', label: 'Events' },
  { key: 'users', label: 'Users' },
  { key: 'tickets', label: 'Tickets' },
  { key: 'support', label: 'Support' },
  { key: 'orders', label: 'Orders' },
  { key: 'staff', label: 'Staff' },
  { key: 'music', label: 'Music' },
  { key: 'club_settings', label: 'Club Settings' },
]

const PermissionsEditor = ({ open, onClose, group, onSave }: PermissionsEditorProps) => {
  const [permissions, setPermissions] = useState<Record<string, AdminPermissionItem>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      loadPermissions()
    }
  }, [open, group.id])

  const loadPermissions = async () => {
    try {
      const response = await api.get<{ permissions: AdminPermission[] }>(`/admin/groups/${group.id}/permissions`)
      const permsMap: Record<string, AdminPermissionItem> = {}
      
      // Initialize all resources
      RESOURCES.forEach((resource) => {
        permsMap[resource.key] = {
          resource: resource.key,
          can_read: false,
          can_write: false,
          can_delete: false,
        }
      })
      
      // Load existing permissions
      response.data.permissions.forEach((perm) => {
        // Only allow editing known resources from RESOURCES list.
        // Admin accounts are superadmin-only and intentionally excluded from the UI.
        if (permsMap[perm.resource]) {
        permsMap[perm.resource] = {
          resource: perm.resource,
          can_read: perm.can_read,
          can_write: perm.can_write,
          can_delete: perm.can_delete,
          }
        }
      })
      
      setPermissions(permsMap)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load permissions')
    }
  }

  const handlePermissionChange = (resource: string, field: 'can_read' | 'can_write' | 'can_delete', value: boolean) => {
    setPermissions((prev) => {
      const updated = { ...prev }
      updated[resource] = { ...updated[resource], [field]: value }
      
      // If can_read is unchecked, uncheck can_write and can_delete
      if (field === 'can_read' && !value) {
        updated[resource].can_write = false
        updated[resource].can_delete = false
      }
      
      // If can_write or can_delete is checked, ensure can_read is checked
      if ((field === 'can_write' || field === 'can_delete') && value) {
        updated[resource].can_read = true
      }
      
      return updated
    })
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      const permissionsList: AdminPermissionItem[] = RESOURCES.map((r) => permissions[r.key]).filter(
        (p): p is AdminPermissionItem => !!p
      )
      const updateRequest: AdminPermissionUpdateRequest = {
        permissions: permissionsList,
      }

      await api.put(`/admin/groups/${group.id}/permissions`, updateRequest)
      onSave()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save permissions')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Edit Permissions: {group.name}</DialogTitle>
      <DialogContent>
        {error && (
          <Box sx={{ color: 'error.main', mb: 2, p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
            {error}
          </Box>
        )}
        
        <Box sx={{ mt: 2 }}>
          {RESOURCES.map((resource) => {
            const perm = permissions[resource.key]
            if (!perm) return null
            
            return (
              <Box key={resource.key} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {resource.label}
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={perm.can_read}
                        onChange={(e) => handlePermissionChange(resource.key, 'can_read', e.target.checked)}
                      />
                    }
                    label="Read"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={perm.can_write}
                        onChange={(e) => handlePermissionChange(resource.key, 'can_write', e.target.checked)}
                        disabled={!perm.can_read}
                      />
                    }
                    label="Write"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={perm.can_delete}
                        onChange={(e) => handlePermissionChange(resource.key, 'can_delete', e.target.checked)}
                        disabled={!perm.can_read}
                      />
                    }
                    label="Delete"
                  />
                </FormGroup>
                <Divider sx={{ mt: 2 }} />
              </Box>
            )
          })}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          Save Permissions
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default PermissionsEditor

