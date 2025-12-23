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
      console.log('Attempting login with username:', username)
      const response = await authService.login({ username, password })
      console.log('Login successful, received token')
      localStorage.setItem('token', response.access_token)
      setIsAuthenticated(true)
      console.log('Token saved, redirecting...')
      // Use window.location for navigation to ensure state update
      setTimeout(() => {
        window.location.href = '/'
      }, 100)
      return { success: true }
    } catch (error: any) {
      console.error('Login error:', error)
      console.error('Error response:', error.response)
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login failed',
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

