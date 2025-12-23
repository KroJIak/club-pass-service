import api from './api'

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
}

