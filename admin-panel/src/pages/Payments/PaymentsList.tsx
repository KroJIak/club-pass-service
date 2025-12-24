import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip } from '@mui/material'
import api from '../../services/api'
import { Payment } from '../../types'

const PaymentsList = () => {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        const response = await api.get('/admin/payments')
        setPayments(response.data.payments)
      } catch (error) {
        console.error('Failed to fetch payments:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchPayments()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Payments</Typography>
      <Grid container spacing={3}>
        {payments.map((payment) => (
          <Grid item xs={12} sm={6} md={4} key={payment.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Payment #{payment.id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Amount: {payment.amount} ₽
                </Typography>
                <Chip
                  label={payment.status}
                  color={payment.status === 'succeeded' ? 'success' : 'default'}
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

export default PaymentsList

