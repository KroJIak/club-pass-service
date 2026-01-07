import { useState, useEffect } from 'react'
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
  Autocomplete,
  TextField as MuiTextField,
} from '@mui/material'
import { useTranslation } from 'react-i18next'
import { FilterSection } from './FilterPanel'
import api from '../../services/api'
import { Event, TicketType } from '../../types'

export interface TicketsFilterState {
  search: string
  status: 'all' | 'active' | 'refunded' | 'cancelled' | 'expired' | 'used'
  event_id: number | null
  ticket_type_id: number | null
}

const DEFAULT_FILTER_STATE: TicketsFilterState = {
  search: '',
  status: 'all',
  event_id: null,
  ticket_type_id: null,
}

interface TicketsFilterProps {
  filterState: TicketsFilterState
  onFilterChange: (filter: TicketsFilterState) => void
}

const TicketsFilter = ({ filterState, onFilterChange }: TicketsFilterProps) => {
  const { t } = useTranslation('tickets')
  const { t: tCommon } = useTranslation('common')
  const [localFilter, setLocalFilter] = useState<TicketsFilterState>(filterState)
  const [events, setEvents] = useState<Event[]>([])
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([])
  const [loadingEvents, setLoadingEvents] = useState(false)
  const [loadingTicketTypes, setLoadingTicketTypes] = useState(false)

  useEffect(() => {
    setLocalFilter(filterState)
  }, [filterState])

  useEffect(() => {
    fetchEvents()
  }, [])

  useEffect(() => {
    if (localFilter.event_id) {
      fetchTicketTypes(localFilter.event_id)
    } else {
      setTicketTypes([])
    }
  }, [localFilter.event_id])

  const fetchEvents = async () => {
    setLoadingEvents(true)
    try {
      const response = await api.get('/admin/events')
      setEvents(response.data.events || [])
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setLoadingEvents(false)
    }
  }

  const fetchTicketTypes = async (eventId: number) => {
    setLoadingTicketTypes(true)
    try {
      const response = await api.get('/admin/ticket-types')
      const allTicketTypes = response.data.ticket_types || []
      const filtered = allTicketTypes.filter((tt: TicketType) => tt.event_id === eventId)
      setTicketTypes(filtered)
    } catch (error) {
      console.error('Failed to fetch ticket types:', error)
    } finally {
      setLoadingTicketTypes(false)
    }
  }

  const handleFilterChange = (updates: Partial<TicketsFilterState>) => {
    const newFilter = { ...localFilter, ...updates }
    // If event changes, reset ticket_type_id
    if (updates.event_id !== undefined && updates.event_id !== localFilter.event_id) {
      newFilter.ticket_type_id = null
    }
    setLocalFilter(newFilter)
    onFilterChange(newFilter)
  }

  const selectedEvent = events.find(e => e.id === localFilter.event_id) || null
  const selectedTicketType = ticketTypes.find(tt => tt.id === localFilter.ticket_type_id) || null

  return (
    <Box>
      <FilterSection title={t('fields.event')}>
        <Autocomplete
          options={events}
          getOptionLabel={(event) => event.name}
          loading={loadingEvents}
          value={selectedEvent}
          onChange={(_, newValue) => {
            handleFilterChange({ event_id: newValue?.id || null })
          }}
          renderInput={(params) => (
            <MuiTextField
              {...params}
              placeholder={t('allEvents')}
              size="small"
              sx={{ '& .MuiInputBase-root': { fontSize: '0.84rem' } }}
            />
          )}
        />
      </FilterSection>

      {localFilter.event_id && (
        <FilterSection title={t('fields.ticketType')}>
          <Autocomplete
            options={ticketTypes}
            getOptionLabel={(tt) => tt.name}
            loading={loadingTicketTypes}
            value={selectedTicketType}
            onChange={(_, newValue) => {
              handleFilterChange({ ticket_type_id: newValue?.id || null })
            }}
            renderInput={(params) => (
              <MuiTextField
                {...params}
                placeholder={t('allTicketTypes')}
                size="small"
                sx={{ '& .MuiInputBase-root': { fontSize: '0.84rem' } }}
              />
            )}
          />
        </FilterSection>
      )}

      <FilterSection title={tCommon('fields.status')}>
        <RadioGroup
          value={localFilter.status}
          onChange={(e) => handleFilterChange({ status: e.target.value as TicketsFilterState['status'] })}
        >
          <FormControlLabel 
            value="all" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{tCommon('status.all')}</Typography>} 
          />
          <FormControlLabel 
            value="active" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{t('status.active')}</Typography>} 
          />
          <FormControlLabel 
            value="refunded" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{t('status.refunded')}</Typography>} 
          />
          <FormControlLabel 
            value="cancelled" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{t('status.cancelled')}</Typography>} 
          />
          <FormControlLabel 
            value="expired" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{t('status.expired')}</Typography>} 
          />
          <FormControlLabel 
            value="used" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>{t('status.used')}</Typography>} 
          />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default TicketsFilter
export { DEFAULT_FILTER_STATE }

