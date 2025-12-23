import { useState, useEffect } from 'react'
import { authService } from '../services/auth'

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token by fetching user info
      authService
        .getMe()
        .then(() => {
          setIsAuthenticated(true)
        })
        .catch(() => {
          localStorage.removeItem('token')
          setIsAuthenticated(false)
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsAuthenticated(false)
      setIsLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await authService.login({ username, password })
      localStorage.setItem('token', response.access_token)
      setIsAuthenticated(true)
      // Use window.location for navigation to ensure state update
      window.location.href = '/'
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    window.location.href = '/login'
  }

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
  }
}

