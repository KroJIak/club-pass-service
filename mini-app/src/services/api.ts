import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Check staff access
export const checkStaffAccess = async (telegramUserId: number) => {
  const response = await api.get('/v1/staff/check-access', {
    params: { telegram_user_id: telegramUserId },
  })
  return response.data
}

// Get ticket by token
export const getTicketByToken = async (token: string, telegramUserId: number) => {
  const response = await api.get(`/v1/staff/tickets/token/${token}`, {
    params: { telegram_user_id: telegramUserId },
  })
  return response.data
}

// Mark ticket as used
export const markTicketAsUsed = async (ticketId: number, telegramUserId: number) => {
  const response = await api.post(`/v1/staff/tickets/${ticketId}/mark-used`, null, {
    params: { telegram_user_id: telegramUserId },
  })
  return response.data
}

export default api

