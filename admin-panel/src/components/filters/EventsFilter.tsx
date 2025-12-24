import { useState, useEffect } from 'react'
import {
  Box,
  TextField,
  FormControlLabel,
  Radio,
  RadioGroup,
  Checkbox,
  Slider,
  Button,
  Typography,
} from '@mui/material'
import { FilterSection } from './FilterPanel'
import { Event, TicketType } from '../../types'

export interface EventsFilterState {
  search: string
  minPrice: number
  maxPrice: number
  selectedDjs: string[]
  selectedTicketTypes: string[]
  dateFrom: string
  dateTo: string
  isActive: 'all' | 'active' | 'inactive'
}

const DEFAULT_FILTER_STATE: EventsFilterState = {
  search: '',
  minPrice: 0,
  maxPrice: 10000,
  selectedDjs: [],
  selectedTicketTypes: [],
  dateFrom: '',
  dateTo: '',
  isActive: 'all',
}

interface EventsFilterProps {
  events: Event[]
  ticketTypes: TicketType[]
  filterState: EventsFilterState
  onFilterChange: (filter: EventsFilterState) => void
}

const EventsFilter = ({ events, ticketTypes, filterState, onFilterChange }: EventsFilterProps) => {
  const [localFilter, setLocalFilter] = useState<EventsFilterState>(filterState)
  const [djsExpanded, setDjsExpanded] = useState(false)
  const [ticketTypesExpanded, setTicketTypesExpanded] = useState(false)

  useEffect(() => {
    setLocalFilter(filterState)
  }, [filterState])

  const handleFilterChange = (updates: Partial<EventsFilterState>) => {
    const newFilter = { ...localFilter, ...updates }
    setLocalFilter(newFilter)
    onFilterChange(newFilter)
  }

  // Extract unique DJs from events
  const allDjs = Array.from(
    new Set(
      events
        .flatMap((e) => e.djs || [])
        .filter((dj) => dj && dj.trim() !== '')
    )
  ).sort()

  // Extract unique ticket type names
  const allTicketTypeNames = Array.from(
    new Set(ticketTypes.map((tt) => tt.name).filter((name) => name && name.trim() !== ''))
  ).sort()

  const visibleDjs = djsExpanded ? allDjs : allDjs.slice(0, 5)
  const visibleTicketTypes = ticketTypesExpanded ? allTicketTypeNames : allTicketTypeNames.slice(0, 5)

  // Calculate price range from ticket types
  const prices = ticketTypes.map((tt) => tt.price)
  const minPriceValue = prices.length > 0 ? Math.min(...prices) : 0
  const maxPriceValue = prices.length > 0 ? Math.max(...prices) : 10000

  // Initialize price range if not set (only once)
  useEffect(() => {
    if (
      localFilter.minPrice === DEFAULT_FILTER_STATE.minPrice &&
      localFilter.maxPrice === DEFAULT_FILTER_STATE.maxPrice &&
      maxPriceValue > 0 &&
      minPriceValue !== maxPriceValue
    ) {
      handleFilterChange({ minPrice: minPriceValue, maxPrice: maxPriceValue })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleDjToggle = (dj: string) => {
    const newDjs = localFilter.selectedDjs.includes(dj)
      ? localFilter.selectedDjs.filter((d) => d !== dj)
      : [...localFilter.selectedDjs, dj]
    handleFilterChange({ selectedDjs: newDjs })
  }

  const handleTicketTypeToggle = (name: string) => {
    const newTypes = localFilter.selectedTicketTypes.includes(name)
      ? localFilter.selectedTicketTypes.filter((t) => t !== name)
      : [...localFilter.selectedTicketTypes, name]
    handleFilterChange({ selectedTicketTypes: newTypes })
  }

  return (
    <Box>
      <FilterSection title="Price Range">
        <Box sx={{ px: 1 }}>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              size="small"
              label="Min"
              type="number"
              value={localFilter.minPrice}
              onChange={(e) => handleFilterChange({ minPrice: Number(e.target.value) })}
              sx={{ flex: 1, '& .MuiInputBase-input': { fontSize: '0.8rem' }, '& .MuiInputLabel-root': { fontSize: '0.8rem' } }}
            />
            <TextField
              size="small"
              label="Max"
              type="number"
              value={localFilter.maxPrice}
              onChange={(e) => handleFilterChange({ maxPrice: Number(e.target.value) })}
              sx={{ flex: 1, '& .MuiInputBase-input': { fontSize: '0.8rem' }, '& .MuiInputLabel-root': { fontSize: '0.8rem' } }}
            />
          </Box>
          <Slider
            value={[localFilter.minPrice, localFilter.maxPrice]}
            onChange={(_, newValue) => {
              const [min, max] = newValue as number[]
              handleFilterChange({ minPrice: min, maxPrice: max })
            }}
            min={minPriceValue}
            max={maxPriceValue}
            valueLabelDisplay="auto"
            step={100}
          />
        </Box>
      </FilterSection>

      <FilterSection title="DJs">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {visibleDjs.map((dj) => (
              <FormControlLabel
                key={dj}
                control={
                  <Checkbox
                    checked={localFilter.selectedDjs.includes(dj)}
                    onChange={() => handleDjToggle(dj)}
                    size="small"
                    sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }}
                  />
                }
                label={<Typography sx={{ fontSize: '0.8rem' }}>{dj}</Typography>}
              />
          ))}
          {allDjs.length > 5 && (
            <Button
              size="small"
              onClick={() => setDjsExpanded(!djsExpanded)}
              sx={{ mt: 1, alignSelf: 'flex-start', fontSize: '0.75rem' }}
            >
              {djsExpanded ? 'Show Less' : `Show All (${allDjs.length})`}
            </Button>
          )}
        </Box>
      </FilterSection>

      <FilterSection title="Date Range">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            size="small"
            label="From"
            type="date"
            value={localFilter.dateFrom}
            onChange={(e) => handleFilterChange({ dateFrom: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ '& .MuiInputBase-input': { fontSize: '0.8rem' }, '& .MuiInputLabel-root': { fontSize: '0.8rem' } }}
          />
          <TextField
            size="small"
            label="To"
            type="date"
            value={localFilter.dateTo}
            onChange={(e) => handleFilterChange({ dateTo: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ '& .MuiInputBase-input': { fontSize: '0.8rem' }, '& .MuiInputLabel-root': { fontSize: '0.8rem' } }}
          />
        </Box>
      </FilterSection>

      <FilterSection title="Ticket Types">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {visibleTicketTypes.map((name) => (
              <FormControlLabel
                key={name}
                control={
                  <Checkbox
                    checked={localFilter.selectedTicketTypes.includes(name)}
                    onChange={() => handleTicketTypeToggle(name)}
                    size="small"
                    sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }}
                  />
                }
                label={<Typography sx={{ fontSize: '0.8rem' }}>{name}</Typography>}
              />
          ))}
          {allTicketTypeNames.length > 5 && (
            <Button
              size="small"
              onClick={() => setTicketTypesExpanded(!ticketTypesExpanded)}
              sx={{ mt: 1, alignSelf: 'flex-start', fontSize: '0.75rem' }}
            >
              {ticketTypesExpanded ? 'Show Less' : `Show All (${allTicketTypeNames.length})`}
            </Button>
          )}
        </Box>
      </FilterSection>

      <FilterSection title="Status">
        <RadioGroup
          value={localFilter.isActive}
          onChange={(e) => handleFilterChange({ isActive: e.target.value as 'all' | 'active' | 'inactive' })}
        >
          <FormControlLabel 
            value="all" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.8rem' }}>All</Typography>} 
          />
          <FormControlLabel 
            value="active" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.8rem' }}>Active</Typography>} 
          />
          <FormControlLabel 
            value="inactive" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.8rem' }}>Inactive</Typography>} 
          />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default EventsFilter
export { DEFAULT_FILTER_STATE }

