import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
} from '@mui/material'
import {
  Event as EventIcon,
  People as UsersIcon,
  ConfirmationNumber as TicketIcon,
  Payment as PaymentIcon,
  ShoppingCart as OrderIcon,
  QrCodeScanner as QrCodeIcon,
  Business as BusinessIcon,
  Support as SupportIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'

const menuItems = [
  { text: 'QR Scanner', icon: <QrCodeIcon />, path: '/qr-scanner' },
  { text: 'Events', icon: <EventIcon />, path: '/events' },
  { text: 'Users', icon: <UsersIcon />, path: '/users' },
  { text: 'Tickets', icon: <TicketIcon />, path: '/tickets' },
  { text: 'Support', icon: <SupportIcon />, path: '/support' },
  { text: 'Payments', icon: <PaymentIcon />, path: '/payments' },
  { text: 'Orders', icon: <OrderIcon />, path: '/orders' },
  { text: 'Club Settings', icon: <BusinessIcon />, path: '/club-settings' },
]

const Sidebar = () => {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Box
      sx={{
        width: '120px', // В 2 раза меньше стандартного
        flexShrink: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid',
        borderColor: 'divider',
      }}
    >
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                flexDirection: 'column',
                py: 1.5,
                '& .MuiListItemIcon-root': {
                  minWidth: 'auto',
                  mb: 0.5,
                },
              }}
            >
              <ListItemIcon sx={{ justifyContent: 'center' }}>{item.icon}</ListItemIcon>
              <ListItemText 
                primary={item.text} 
                primaryTypographyProps={{ 
                  variant: 'caption',
                  sx: { textAlign: 'center', fontSize: '0.7rem' }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  )
}

export default Sidebar

