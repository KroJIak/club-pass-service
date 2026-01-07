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
import { useTranslation } from 'react-i18next'

interface MenuItem {
  textKey: string
  icon: JSX.Element
  path: string
  resource: ResourceName
}

const allMenuItems: MenuItem[] = [
  { textKey: 'menu.qrScanner', icon: <QrCodeIcon />, path: '/qr-scanner', resource: 'qr_scanner' },
  { textKey: 'menu.events', icon: <EventIcon />, path: '/events', resource: 'events' },
  { textKey: 'menu.users', icon: <UsersIcon />, path: '/users', resource: 'users' },
  { textKey: 'menu.tickets', icon: <TicketIcon />, path: '/tickets', resource: 'tickets' },
  { textKey: 'menu.music', icon: <MusicIcon />, path: '/music', resource: 'music' },
  { textKey: 'menu.support', icon: <SupportIcon />, path: '/support', resource: 'support' },
  { textKey: 'menu.orders', icon: <OrderIcon />, path: '/orders', resource: 'orders' },
  { textKey: 'menu.staff', icon: <StaffIcon />, path: '/staff', resource: 'staff' },
  { textKey: 'menu.clubSettings', icon: <BusinessIcon />, path: '/club-settings', resource: 'club_settings' },
]

const Sidebar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { canAccessResource } = usePermissions()
  const { t } = useTranslation('navigation')
  
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
                primary={t(item.textKey)} 
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

