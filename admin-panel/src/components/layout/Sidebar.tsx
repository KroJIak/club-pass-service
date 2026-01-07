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
  ShoppingCart as OrderIcon,
  QrCodeScanner as QrCodeIcon,
  Business as BusinessIcon,
  Support as SupportIcon,
  Badge as StaffIcon,
  MusicNote as MusicIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'
import { usePermissions } from '../../hooks/usePermissions'
import { ResourceName } from '../../types'

interface MenuItem {
  text: string
  icon: JSX.Element
  path: string
  resource: ResourceName
}

const allMenuItems: MenuItem[] = [
  { text: 'QR Scanner', icon: <QrCodeIcon />, path: '/qr-scanner', resource: 'qr_scanner' },
  { text: 'Events', icon: <EventIcon />, path: '/events', resource: 'events' },
  { text: 'Users', icon: <UsersIcon />, path: '/users', resource: 'users' },
  { text: 'Tickets', icon: <TicketIcon />, path: '/tickets', resource: 'tickets' },
  { text: 'Support', icon: <SupportIcon />, path: '/support', resource: 'support' },
  { text: 'Orders', icon: <OrderIcon />, path: '/orders', resource: 'orders' },
  { text: 'Staff', icon: <StaffIcon />, path: '/staff', resource: 'staff' },
  { text: 'Music', icon: <MusicIcon />, path: '/music', resource: 'music' },
  { text: 'Club Settings', icon: <BusinessIcon />, path: '/club-settings', resource: 'club_settings' },
]

const Sidebar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { canAccessResource } = usePermissions()
  
  // Filter menu items based on permissions
  const menuItems = allMenuItems.filter(item => canAccessResource(item.resource))

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

