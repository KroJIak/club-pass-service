import { AppBar, Toolbar, Typography } from '@mui/material'

interface HeaderProps {
  title: string
}

const Header = ({ title }: HeaderProps) => {
  return (
    <AppBar position="static" elevation={0}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
      </Toolbar>
    </AppBar>
  )
}

export default Header

