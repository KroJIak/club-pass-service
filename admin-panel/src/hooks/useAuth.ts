import { useState, useEffect, useCallback } from 'react'
import { authService } from '../services/auth'

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        // Verify token by fetching user info
        await authService.getMe()
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('token')
        setIsAuthenticated(false)
      }
    } else {
      setIsAuthenticated(false)
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (username: string, password: string) => {
    try {
      const response = await authService.login({ username, password })
      localStorage.setItem('token', response.access_token)
      setIsAuthenticated(true)
      setIsLoading(false)
      // Load permissions after login
      try {
        const perms = await authService.getPermissions()
        localStorage.setItem('permissions', JSON.stringify(perms))
      } catch (e) {
        console.error('Failed to load permissions after login:', e)
      }
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('permissions')
    setIsAuthenticated(false)
    // Use window.location to ensure full page reload
    window.location.href = '/login'
  }

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
  }
}

