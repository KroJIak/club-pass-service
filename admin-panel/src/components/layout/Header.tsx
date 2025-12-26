import { Box, Typography, IconButton } from '@mui/material'
import { Logout as LogoutIcon } from '@mui/icons-material'
import { useAuth } from '../../hooks/useAuth'
import { useState, useEffect } from 'react'
import { authService } from '../../services/auth'

const Header = () => {
  const { logout } = useAuth()
  const [username, setUsername] = useState<string>('Admin')

  useEffect(() => {
    const fetchAdminInfo = async () => {
      try {
        const info = await authService.getMe()
        setUsername(info.username)
      } catch (error) {
        console.error('Failed to fetch admin info:', error)
      }
    }
    fetchAdminInfo()
  }, [])

  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        py: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: {
            xs: 'calc(0.064375 * 100vw)', // <= 600px (reduced from 0.084375 by 0.02)
            sm: 'calc(0.064375 * 100vw + (0.16 - 0.064375) * (100vw - 600px) / (1280 - 600))', // 600-1280px (reduced from 0.18 by 0.02)
            md: 'calc(0.16 * 100vw)', // >= 1280px (reduced from 0.18 by 0.02)
          },
        }}
      >
        <Typography variant="h6" component="div">
          Admin Panel
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body1">{username}</Typography>
          <IconButton
            color="error"
            onClick={logout}
            size="small"
          >
            <LogoutIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  )
}

export default Header
