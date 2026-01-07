import api from './api'
import { UserPermissions } from '../types'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface AdminInfo {
  username: string
  is_superadmin: boolean
  group_id: number | null
  language: string
  permissions: Record<string, { can_read: boolean; can_write: boolean; can_delete: boolean }> | null
}

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/admin/login', credentials)
    return response.data
  },

  getMe: async (): Promise<AdminInfo> => {
    const response = await api.get<AdminInfo>('/admin/me')
    return response.data
  },

  getPermissions: async (): Promise<UserPermissions> => {
    const response = await api.get<UserPermissions>('/admin/permissions')
    return response.data
  },
}

