import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography } from '@mui/material'
import api from '../../services/api'
import { Order } from '../../types'

const OrdersList = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get('/admin/orders')
        setOrders(response.data.orders)
      } catch (error) {
        console.error('Failed to fetch orders:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchOrders()
  }, [])

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Orders</Typography>
      <Grid container spacing={3}>
        {orders.map((order) => (
          <Grid item xs={12} sm={6} md={4} key={order.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">Order {order.order_id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Quantity: {order.quantity}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Event ID: {order.event_id}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default OrdersList

