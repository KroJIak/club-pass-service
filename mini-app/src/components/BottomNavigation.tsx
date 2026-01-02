import { Box, BottomNavigation, BottomNavigationAction } from '@mui/material'
import { QrCodeScanner, List as ListIcon } from '@mui/icons-material'

interface BottomNavigationProps {
  value: number
  onChange: (event: React.SyntheticEvent, newValue: number) => void
}

const BottomNav = ({ value, onChange }: BottomNavigationProps) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        borderTop: '1px solid',
        borderColor: 'divider',
      }}
    >
      <BottomNavigation value={value} onChange={onChange} showLabels>
        <BottomNavigationAction label="Сканер QR" icon={<QrCodeScanner />} />
        <BottomNavigationAction label="Списки" icon={<ListIcon />} />
      </BottomNavigation>
    </Box>
  )
}

export default BottomNav

