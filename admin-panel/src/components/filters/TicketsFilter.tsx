import { useState, useEffect } from 'react'
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material'
import { FilterSection } from './FilterPanel'

export interface TicketsFilterState {
  search: string
  status: 'all' | 'active' | 'refunded' | 'cancelled' | 'expired' | 'used'
}

const DEFAULT_FILTER_STATE: TicketsFilterState = {
  search: '',
  status: 'all',
}

interface TicketsFilterProps {
  filterState: TicketsFilterState
  onFilterChange: (filter: TicketsFilterState) => void
}

const TicketsFilter = ({ filterState, onFilterChange }: TicketsFilterProps) => {
  const [localFilter, setLocalFilter] = useState<TicketsFilterState>(filterState)

  useEffect(() => {
    setLocalFilter(filterState)
  }, [filterState])

  const handleFilterChange = (updates: Partial<TicketsFilterState>) => {
    const newFilter = { ...localFilter, ...updates }
    setLocalFilter(newFilter)
    onFilterChange(newFilter)
  }

  return (
    <Box>
      <FilterSection title="Status">
        <RadioGroup
          value={localFilter.status}
          onChange={(e) => handleFilterChange({ status: e.target.value as TicketsFilterState['status'] })}
        >
          <FormControlLabel 
            value="all" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>All</Typography>} 
          />
          <FormControlLabel 
            value="active" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Active</Typography>} 
          />
          <FormControlLabel 
            value="refunded" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Refunded</Typography>} 
          />
          <FormControlLabel 
            value="cancelled" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Cancelled</Typography>} 
          />
          <FormControlLabel 
            value="expired" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Expired</Typography>} 
          />
          <FormControlLabel 
            value="used" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Used</Typography>} 
          />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default TicketsFilter
export { DEFAULT_FILTER_STATE }

