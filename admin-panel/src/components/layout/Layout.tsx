import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import Sidebar from './Sidebar'
import Header from './Header'
import { useFilterPanel } from '../../hooks/useFilterPanel'

const Layout = () => {
  const { filterPanel } = useFilterPanel()
  const showFilter = true

  // Calculate side margins based on viewport width
  // At 1280px: 0.13 * width (reduced from 0.15 by 0.02)
  // At 600px: 0.0503125 * width (reduced from 0.0703125 by 0.02)
  // Linear interpolation between 600 and 1280
  const getSideMargin = () => {
    return {
      xs: 'calc(0.0503125 * 100vw)', // <= 600px
      sm: 'calc(0.0503125 * 100vw + (0.13 - 0.0503125) * (100vw - 600px) / (1280 - 600))', // 600-1280px
      md: 'calc(0.13 * 100vw)', // >= 1280px
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Header />
      <Box sx={{ flexGrow: 1, display: 'flex', overflow: 'hidden' }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
            px: getSideMargin(),
          }}
        >
          <Box sx={{ display: 'flex', width: '100%', maxWidth: '100%', gap: 2 }}>
            <Sidebar />
            <Box
              sx={{
                flexGrow: 1,
                overflow: 'auto',
                py: 3,
              }}
            >
              <Outlet />
            </Box>
            {showFilter && filterPanel}
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default Layout
