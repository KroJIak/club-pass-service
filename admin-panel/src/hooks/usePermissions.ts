import { useState, useEffect, useCallback } from 'react'
import { authService } from '../services/auth'
import { UserPermissions, ResourceName, Action } from '../types'

export const usePermissions = () => {
  const [permissions, setPermissions] = useState<UserPermissions | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadPermissions = useCallback(async () => {
    try {
      const perms = await authService.getPermissions()
      setPermissions(perms)
      // Also store in localStorage for quick access
      localStorage.setItem('permissions', JSON.stringify(perms))
    } catch (error) {
      console.error('Failed to load permissions:', error)
      setPermissions(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    // Try to load from localStorage first
    const stored = localStorage.getItem('permissions')
    if (stored) {
      try {
        setPermissions(JSON.parse(stored))
        setIsLoading(false)
      } catch (e) {
        // Invalid JSON, load from API
        loadPermissions()
      }
    } else {
      loadPermissions()
    }
  }, [loadPermissions])

  const hasPermission = useCallback((resource: ResourceName, action: Action): boolean => {
    if (!permissions) return false
    
    // Superadmin has all permissions
    if (permissions.is_superadmin) return true
    
    const resourcePerms = permissions.permissions[resource]
    if (!resourcePerms) return false
    
    if (action === 'read') return resourcePerms.can_read
    if (action === 'write') return resourcePerms.can_write
    if (action === 'delete') return resourcePerms.can_delete
    
    return false
  }, [permissions])

  const canAccessResource = useCallback((resource: ResourceName): boolean => {
    return hasPermission(resource, 'read')
  }, [hasPermission])

  const refreshPermissions = useCallback(() => {
    loadPermissions()
  }, [loadPermissions])

  return {
    permissions,
    isLoading,
    hasPermission,
    canAccessResource,
    isSuperAdmin: permissions?.is_superadmin ?? false,
    refreshPermissions,
  }
}

