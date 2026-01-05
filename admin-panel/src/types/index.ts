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
  start_date: string // DD.MM.YYYY
  start_time: string // HH:MM
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

export interface TicketTypeTemplate {
  id: number
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
  event: Event | null
  ticket_type: TicketType | null
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
  payment_id: number | null
  created_at: string
  updated_at: string
  username: string | null
  first_name: string | null
  last_name: string | null
  event_name: string | null
  ticket_type_name: string | null
  amount: number | null
  payment_status: string | null
}


// Create/Update types
export interface EventCreate {
  name: string
  description?: string | null
  start_date: string
  start_time: string
  end_date: string
  end_time: string
  djs?: string[] | null
  is_active?: boolean
}

export interface EventUpdate {
  name?: string | null
  description?: string | null
  start_date?: string | null
  start_time?: string | null
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

export interface TicketTypeTemplateCreate {
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

export interface TicketCreate {
  user_id: number
  event_id: number
  ticket_type_id: number
  token?: string | null
  status?: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used' | null
}

export interface TicketUpdate {
  user_id?: number | null
  event_id?: number | null
  ticket_type_id?: number | null
  token?: string | null
  status?: 'active' | 'refunded' | 'cancelled' | 'expired' | 'used' | null
}

export interface PaymentUpdate {
  status?: 'pending' | 'succeeded' | 'cancelled' | 'refunded' | null
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
  additional_info: string | null
  auto_deactivate_events: boolean
  timezone: string
  updated_at: string
}

export interface ClubSettingsUpdate {
  address?: string | null
  phone?: string | null
  email?: string | null
  additional_info?: string | null
  auto_deactivate_events?: boolean | null
  timezone?: string | null
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

export interface MenuPhoto {
  id: number
  file_path: string
  file_name: string
  file_size: number
  mime_type: string
  display_order: number
  created_at: string
  updated_at: string
}

export interface MenuPhotoReorderItem {
  id: number
  display_order: number
}

export interface MenuPhotoReorderRequest {
  photos: MenuPhotoReorderItem[]
}

export interface MusicRequest {
  id: number
  user_id: number
  event_id: number
  track_title: string
  track_artist: string
  yandex_music_url: string | null
  other_source_url: string | null
  request_count: number
  created_at: string
  updated_at: string
}

export interface MusicQueue {
  id: number
  track_title: string
  track_artist: string
  yandex_music_url: string | null
  other_source_url: string | null
  queue_order: number
  created_at: string
  updated_at: string
}

export interface MusicQueueReorderItem {
  id: number
  queue_order: number
}

export interface MusicQueueReorderRequest {
  items: MusicQueueReorderItem[]
}

