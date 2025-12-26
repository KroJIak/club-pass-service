export interface User {
  id: number
  telegram_user_id: number
  username: string | null
  first_name: string | null
  last_name: string | null
  created_at: string
  updated_at: string
}

export interface Event {
  id: number
  name: string
  description: string | null
  date: string // DD.MM.YYYY
  time: string // HH:MM
  end_date: string // DD.MM.YYYY
  end_time: string // HH:MM
  djs: string[] | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TicketType {
  id: number
  event_id: number
  name: string
  price: number
  available_quantity: number
  total_quantity: number
  is_active: boolean
}

export interface Ticket {
  id: number
  user_id: number
  event_id: number
  ticket_type_id: number
  token: string
  status: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used'
  used_at: string | null
  refunded_at: string | null
  created_at: string
  updated_at: string
  username: string | null
  first_name: string | null
  last_name: string | null
}

export interface Payment {
  id: number
  user_id: number
  order_id: string | null
  yookassa_payment_id: string | null
  telegram_payment_charge_id: string | null
  amount: number
  status: 'pending' | 'succeeded' | 'cancelled' | 'refunded'
  created_at: string
  updated_at: string
}

export interface Order {
  id: number
  order_id: string
  user_id: number
  event_id: number
  ticket_type_id: number
  quantity: number
  promocode: string | null
  payment_id: number | null
  created_at: string
  updated_at: string
  username: string | null
  first_name: string | null
  last_name: string | null
  event_name: string | null
  ticket_type_name: string | null
}

export interface Promocode {
  id: number
  code: string
  discount_percent: number | null
  discount_amount: number | null
  valid_from: string
  valid_until: string
  usage_limit: number | null
  usage_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// Create/Update types
export interface EventCreate {
  name: string
  description?: string | null
  date: string
  time: string
  end_date: string
  end_time: string
  djs?: string[] | null
  is_active?: boolean
}

export interface EventUpdate {
  name?: string | null
  description?: string | null
  date?: string | null
  time?: string | null
  end_date?: string | null
  end_time?: string | null
  djs?: string[] | null
  is_active?: boolean | null
}

export interface TicketTypeCreate {
  event_id: number
  name: string
  price: number
  available_quantity: number
  total_quantity: number
  is_active?: boolean
}

export interface TicketTypeUpdate {
  name?: string | null
  price?: number | null
  available_quantity?: number | null
  total_quantity?: number | null
  is_active?: boolean | null
}

export interface UserCreate {
  telegram_user_id: number
  username?: string | null
  first_name?: string | null
  last_name?: string | null
}

export interface UserUpdate {
  username?: string | null
  first_name?: string | null
  last_name?: string | null
}

export interface TicketUpdate {
  status?: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used' | null
}

export interface PaymentUpdate {
  status?: 'pending' | 'succeeded' | 'cancelled' | 'refunded' | null
}

export interface PromocodeCreate {
  code: string
  discount_percent?: number | null
  discount_amount?: number | null
  valid_from: string
  valid_until: string
  usage_limit?: number | null
  is_active?: boolean
}

export interface PromocodeUpdate {
  code?: string | null
  discount_percent?: number | null
  discount_amount?: number | null
  valid_from?: string | null
  valid_until?: string | null
  usage_limit?: number | null
  is_active?: boolean | null
}

export interface ExpirationSettings {
  id: number
  ticket_expiration_enabled: boolean
  event_deactivation_enabled: boolean
  check_interval_minutes: number
  updated_at: string
}

export interface ExpirationSettingsUpdate {
  ticket_expiration_enabled?: boolean
  event_deactivation_enabled?: boolean
  check_interval_minutes?: number
}

export interface ClubSettings {
  id: number
  address: string | null
  phone: string | null
  email: string | null
  auto_deactivate_events: boolean
  updated_at: string
}

export interface ClubSettingsUpdate {
  address?: string | null
  phone?: string | null
  email?: string | null
  auto_deactivate_events?: boolean | null
}

export interface TicketDetailResponse {
  id: number
  user_id: number
  event_id: number
  ticket_type_id: number
  token: string
  status: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used'
  used_at: string | null
  refunded_at: string | null
  created_at: string
  updated_at: string
  event: {
    id: number
    name: string
    description: string | null
    date: string
    time: string
    djs: string[] | null
    is_active: boolean
  }
  ticket_type: {
    id: number
    name: string
    price: number
    available_quantity: number
    total_quantity: number
    is_active: boolean
  }
  user?: {
    id: number
    telegram_user_id: number
    username: string | null
    first_name: string | null
    last_name: string | null
  } | null
}

