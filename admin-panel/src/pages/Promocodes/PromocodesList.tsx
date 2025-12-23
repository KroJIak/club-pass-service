import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip, Button } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Promocode } from '../../types'

const PromocodesList = () => {
  const [promocodes, setPromocodes] = useState<Promocode[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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
    fetchPromocodes()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Promocodes</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Create New
        </Button>
      </Box>

      <Grid container spacing={3}>
        {promocodes.map((promo) => (
          <Grid item xs={12} sm={6} md={4} key={promo.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{promo.code}</Typography>
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
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default PromocodesList

