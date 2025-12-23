import { Outlet, useLocation } from 'react-router-dom'
import { Box } from '@mui/material'
import Sidebar from './Sidebar'
import Header from './Header'

const getPageTitle = (pathname: string): string => {
  const titles: Record<string, string> = {
    '/events': 'Events',
    '/ticket-types': 'Ticket Types',
    '/users': 'Users',
    '/tickets': 'Tickets',
    '/payments': 'Payments',
    '/orders': 'Orders',
    '/promocodes': 'Promocodes',
  }
  return titles[pathname] || 'Admin Panel'
}

const Layout = () => {
  const location = useLocation()
  const title = getPageTitle(location.pathname)

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header title={title} />
        <Box sx={{ flexGrow: 1, p: 3, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}

export default Layout

