import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, Chip } from '@mui/material'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import { Payment } from '../../types'

const PaymentsList = () => {
  const { t } = useTranslation('orders')
  const { t: tCommon } = useTranslation('common')
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
    return <Typography>{tCommon('status.loading')}</Typography>
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>{t('payments.title')}</Typography>
      <Grid container spacing={3}>
        {payments.map((payment) => (
          <Grid item xs={12} sm={6} md={4} key={payment.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{t('payments.paymentNumber', { id: payment.id })}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('payments.amount')}: {payment.amount} ₽
                </Typography>
                <Chip
                  label={tCommon(`status.${payment.status}`)}
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

