import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, IconButton } from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Order } from '../../types'
import ConfirmDialog from '../../components/common/ConfirmDialog'

const OrdersList = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; orderId: number | null }>({
    open: false,
    orderId: null,
  })

  useEffect(() => {
    fetchOrders()
  }, [])

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

  const handleDelete = async (orderId: number) => {
    try {
      await api.delete(`/admin/orders/${orderId}`)
      fetchOrders()
    } catch (error) {
      console.error('Failed to delete order:', error)
    }
    setDeleteDialog({ open: false, orderId: null })
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Orders</Typography>
      <Grid container spacing={3}>
        {orders.map((order) => (
          <Grid item xs={12} sm={6} md={4} key={order.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>Order {order.order_id}</Typography>
                    {order.username && (
                      <Typography variant="body2" color="text.secondary">
                        @{order.username}
                      </Typography>
                    )}
                    <Typography variant="body2" color="text.secondary">
                      Quantity: {order.quantity}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Event ID: {order.event_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ticket Type ID: {order.ticket_type_id}
                    </Typography>
                    {order.promocode && (
                      <Typography variant="body2" color="text.secondary">
                        Promocode: {order.promocode}
                      </Typography>
                    )}
                  </Box>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => setDeleteDialog({ open: true, orderId: order.id })}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Order"
        message="Are you sure you want to delete this order? This action cannot be undone."
        onConfirm={() => deleteDialog.orderId && handleDelete(deleteDialog.orderId)}
        onCancel={() => setDeleteDialog({ open: false, orderId: null })}
      />
    </Box>
  )
}

export default OrdersList
