import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Grid, Typography, IconButton, Button, Checkbox } from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import api from '../../services/api'
import { Order } from '../../types'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import FilterPanel from '../../components/filters/FilterPanel'
import OrdersFilter, { OrdersFilterState, DEFAULT_FILTER_STATE } from '../../components/filters/OrdersFilter'
import { useFilterPanel } from '../../hooks/useFilterPanel'
import { useSelection } from '../../hooks/useSelection'
import { usePermissions } from '../../hooks/usePermissions'

const OrdersList = () => {
  const { hasPermission } = usePermissions()
  const [orders, setOrders] = useState<Order[]>([])
  const [allOrders, setAllOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; orderId: number | null }>({
    open: false,
    orderId: null,
  })
  const [filterState, setFilterState] = useState<OrdersFilterState>(DEFAULT_FILTER_STATE)
  const { setFilterPanel } = useFilterPanel()
  const selection = useSelection(orders)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const response = await api.get('/admin/orders')
      const fetchedOrders = response.data.orders
      setAllOrders(fetchedOrders)
      setOrders(fetchedOrders)
    } catch (error) {
      console.error('Failed to fetch orders:', error)
    } finally {
      setLoading(false)
    }
  }

  // Set up filter panel
  useEffect(() => {
    setFilterPanel(
      <FilterPanel
        searchValue={filterState.search}
        onSearchChange={(value) => setFilterState({ ...filterState, search: value })}
      >
        <OrdersFilter
          filterState={filterState}
          onFilterChange={setFilterState}
        />
      </FilterPanel>
    )

    return () => {
      setFilterPanel(null)
    }
  }, [filterState, setFilterPanel])

  // Filter orders based on filter state
  useEffect(() => {
    let filtered = [...allOrders]

    // Search filter - по order_id, username, имени/фамилии пользователя, event_name, ticket_type_name
    if (filterState.search.trim()) {
      const searchLower = filterState.search.toLowerCase()
      filtered = filtered.filter((order) => {
        const orderIdMatch = order.order_id.toLowerCase().includes(searchLower)
        const usernameMatch = order.username?.toLowerCase().includes(searchLower) || false
        const firstNameMatch = order.first_name?.toLowerCase().includes(searchLower) || false
        const lastNameMatch = order.last_name?.toLowerCase().includes(searchLower) || false
        const eventNameMatch = order.event_name?.toLowerCase().includes(searchLower) || false
        const ticketTypeNameMatch = order.ticket_type_name?.toLowerCase().includes(searchLower) || false
        return orderIdMatch || usernameMatch || firstNameMatch || lastNameMatch || eventNameMatch || ticketTypeNameMatch
      })
    }


    setOrders(filtered)
  }, [allOrders, filterState])

  const handleDelete = async (orderId: number) => {
    try {
      await api.delete(`/admin/orders/${orderId}`)
      fetchOrders()
    } catch (error) {
      console.error('Failed to delete order:', error)
    }
    setDeleteDialog({ open: false, orderId: null })
  }

  const handleDeleteSelected = async () => {
    if (!confirm(`Are you sure you want to delete ${selection.selectedCount} order(s)? This action cannot be undone.`)) {
      return
    }

    try {
      for (const id of selection.selectedIds) {
        await api.delete(`/admin/orders/${id}`)
      }
      selection.deselectAll()
      fetchOrders()
    } catch (error) {
      console.error('Failed to delete orders:', error)
      alert('Failed to delete some orders')
    }
  }

  if (loading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Orders</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {hasPermission('orders', 'delete') && selection.hasSelection && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelected}
            >
              Delete Selected
            </Button>
          )}
          {hasPermission('orders', 'delete') && (
            <Checkbox
              checked={selection.getSelectionState() === 'all'}
              indeterminate={selection.getSelectionState() === 'some'}
              onChange={selection.handleSelectAllClick}
            />
          )}
        </Box>
      </Box>
      <Grid container spacing={3}>
        {orders.map((order) => (
          <Grid item xs={12} sm={6} md={4} key={order.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                cursor: 'pointer',
                border: selection.isSelected(order.id) ? '2px solid' : 'none',
                borderColor: selection.isSelected(order.id) ? 'primary.main' : 'transparent',
                bgcolor: selection.isSelected(order.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
              }}
              onClick={() => selection.toggleSelection(order.id)}
            >
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1 }}>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 500,
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word'
                      }}
                    >
                      {order.order_id}
                    </Typography>
                    {order.username ? (
                      <Typography variant="body2" color="text.secondary">
                        @{order.username}
                      </Typography>
                    ) : (order.first_name || order.last_name) ? (
                      <Typography variant="body2" color="text.secondary">
                        {`${order.first_name || ''} ${order.last_name || ''}`.trim()}
                      </Typography>
                    ) : null}
                    <Typography variant="body2" color="text.secondary">
                      Quantity: {order.quantity}
                    </Typography>
                    {order.amount !== null && (
                      <Typography variant="body2" color="text.secondary">
                        Amount: {order.amount} ₽
                      </Typography>
                    )}
                    {order.payment_status && (
                      <Typography variant="body2" color="text.secondary">
                        Payment: {order.payment_status}
                      </Typography>
                    )}
                    <Typography variant="body2" color="text.secondary">
                      {order.event_name 
                        ? `Event: ${order.event_name} (ID: ${order.event_id})`
                        : `Event ID: ${order.event_id}`
                      }
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {order.ticket_type_name 
                        ? `Type: ${order.ticket_type_name} (ID: ${order.ticket_type_id})`
                        : `Ticket Type ID: ${order.ticket_type_id}`
                      }
                    </Typography>
                  </Box>
                  {!selection.hasSelection && (
                    <IconButton
                      size="small"
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation()
                        setDeleteDialog({ open: true, orderId: order.id })
                      }}
                      sx={{ flexShrink: 0 }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
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
