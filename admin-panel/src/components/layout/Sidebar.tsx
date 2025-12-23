import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Button,
} from '@mui/material'
import {
  Event as EventIcon,
  ConfirmationNumber as TicketTypeIcon,
  People as UsersIcon,
  ConfirmationNumber as TicketIcon,
  Payment as PaymentIcon,
  ShoppingCart as OrderIcon,
  LocalOffer as PromocodeIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const drawerWidth = 240

const menuItems = [
  { text: 'Events', icon: <EventIcon />, path: '/events' },
  { text: 'Ticket Types', icon: <TicketTypeIcon />, path: '/ticket-types' },
  { text: 'Users', icon: <UsersIcon />, path: '/users' },
  { text: 'Tickets', icon: <TicketIcon />, path: '/tickets' },
  { text: 'Payments', icon: <PaymentIcon />, path: '/payments' },
  { text: 'Orders', icon: <OrderIcon />, path: '/orders' },
  { text: 'Promocodes', icon: <PromocodeIcon />, path: '/promocodes' },
]

const Sidebar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout } = useAuth()

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
        <Box sx={{ p: 2, mt: 'auto' }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<LogoutIcon />}
            onClick={logout}
            color="error"
          >
            Logout
          </Button>
        </Box>
      </Box>
    </Drawer>
  )
}

export default Sidebar

