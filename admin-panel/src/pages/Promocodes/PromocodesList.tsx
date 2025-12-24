import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip, Button, IconButton } from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Promocode } from '../../types'
import PromocodeForm from './PromocodeForm'
import ConfirmDialog from '../../components/common/ConfirmDialog'

const PromocodesList = () => {
  const [promocodes, setPromocodes] = useState<Promocode[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editingPromocode, setEditingPromocode] = useState<Promocode | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; promocodeId: number | null }>({
    open: false,
    promocodeId: null,
  })

  useEffect(() => {
    fetchPromocodes()
  }, [])

  const fetchPromocodes = async () => {
    try {
      const response = await api.get('/admin/promocodes')
      setPromocodes(response.data.promocodes)
    } catch (error) {
      console.error('Failed to fetch promocodes:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingPromocode(null)
    setFormOpen(true)
  }

  const handleEdit = (promocode: Promocode) => {
    setEditingPromocode(promocode)
    setFormOpen(true)
  }

  const handleDelete = async (promocodeId: number) => {
    try {
      await api.delete(`/admin/promocodes/${promocodeId}`)
      fetchPromocodes()
    } catch (error) {
      console.error('Failed to delete promocode:', error)
    }
    setDeleteDialog({ open: false, promocodeId: null })
  }

  const handleFormClose = () => {
    setFormOpen(false)
    setEditingPromocode(null)
    fetchPromocodes()
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">Promocodes</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
          Create New
        </Button>
      </Box>

      <Grid container spacing={3}>
        {promocodes.map((promo) => (
          <Grid item xs={12} sm={6} md={4} key={promo.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{promo.code}</Typography>
                    {promo.discount_percent && (
                      <Typography variant="body2" color="text.secondary">
                        Discount: {promo.discount_percent}%
                      </Typography>
                    )}
                    {promo.discount_amount && (
                      <Typography variant="body2" color="text.secondary">
                        Discount: {promo.discount_amount} ₽
                      </Typography>
                    )}
                    <Typography variant="body2" color="text.secondary">
                      Usage: {promo.usage_count} / {promo.usage_limit || '∞'}
                    </Typography>
                    <Chip
                      label={promo.is_active ? 'Active' : 'Inactive'}
                      color={promo.is_active ? 'success' : 'default'}
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleEdit(promo)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => setDeleteDialog({ open: true, promocodeId: promo.id })}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <PromocodeForm
        open={formOpen}
        promocode={editingPromocode}
        onClose={handleFormClose}
      />

      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Promocode"
        message="Are you sure you want to delete this promocode? This action cannot be undone."
        onConfirm={() => deleteDialog.promocodeId && handleDelete(deleteDialog.promocodeId)}
        onCancel={() => setDeleteDialog({ open: false, promocodeId: null })}
      />
    </Box>
  )
}

export default PromocodesList

