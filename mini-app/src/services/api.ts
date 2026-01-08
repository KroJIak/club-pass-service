import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Check staff access
export const checkStaffAccess = async (initData: string) => {
  const response = await api.post('/v1/staff/check-access', {
    init_data: initData,
  })
  return response.data
}

// Get ticket by token
export const getTicketByToken = async (token: string, initData: string) => {
  const response = await api.post(`/v1/staff/tickets/token/${token}`, {
    init_data: initData,
  })
  return response.data
}

// Mark ticket as used
export const markTicketAsUsed = async (ticketId: number, initData: string) => {
  const response = await api.post(`/v1/staff/tickets/${ticketId}/mark-used`, {
    init_data: initData,
  })
  return response.data
}

export default api

