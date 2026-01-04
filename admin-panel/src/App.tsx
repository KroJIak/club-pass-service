import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Login from './pages/Login'
import Layout from './components/layout/Layout'
import EventsList from './pages/Events/EventsList'
import UsersList from './pages/Users/UsersList'
import TicketsList from './pages/Tickets/TicketsList'
import OrdersList from './pages/Orders/OrdersList'
import QRScanner from './pages/QRScanner/QRScanner'
import ClubSettings from './pages/ClubSettings/ClubSettings'
import SupportMessagesList from './pages/Support/SupportMessagesList'
import Staff from './pages/Staff/Staff'
import { useAuth } from './hooks/useAuth'
import { FilterPanelProvider } from './hooks/useFilterPanel'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FilterPanelProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/events" replace />} />
              <Route path="events" element={<EventsList />} />
              <Route path="users" element={<UsersList />} />
              <Route path="tickets" element={<TicketsList />} />
              <Route path="orders" element={<OrdersList />} />
              <Route path="qr-scanner" element={<QRScanner />} />
              <Route path="support" element={<SupportMessagesList />} />
              <Route path="staff" element={<Staff />} />
              <Route path="club-settings" element={<ClubSettings />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </FilterPanelProvider>
    </ThemeProvider>
  )
}

export default App

