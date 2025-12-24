import { useState, useEffect } from 'react'
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material'
import { FilterSection } from './FilterPanel'

export interface UsersFilterState {
  search: string
  hasUsername: 'all' | 'yes' | 'no'
}

const DEFAULT_FILTER_STATE: UsersFilterState = {
  search: '',
  hasUsername: 'all',
}

interface UsersFilterProps {
  filterState: UsersFilterState
  onFilterChange: (filter: UsersFilterState) => void
}

const UsersFilter = ({ filterState, onFilterChange }: UsersFilterProps) => {
  const [localFilter, setLocalFilter] = useState<UsersFilterState>(filterState)

  useEffect(() => {
    setLocalFilter(filterState)
  }, [filterState])

  const handleFilterChange = (updates: Partial<UsersFilterState>) => {
    const newFilter = { ...localFilter, ...updates }
    setLocalFilter(newFilter)
    onFilterChange(newFilter)
  }

  return (
    <Box>
      <FilterSection title="Username">
        <RadioGroup
          value={localFilter.hasUsername}
          onChange={(e) => handleFilterChange({ hasUsername: e.target.value as 'all' | 'yes' | 'no' })}
        >
          <FormControlLabel 
            value="all" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>All</Typography>} 
          />
          <FormControlLabel 
            value="yes" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Has username</Typography>} 
          />
          <FormControlLabel 
            value="no" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>No username</Typography>} 
          />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default UsersFilter
export { DEFAULT_FILTER_STATE }

