import { useState, useEffect } from 'react'
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
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
          <FormControlLabel value="all" control={<Radio size="small" />} label="All" />
          <FormControlLabel value="yes" control={<Radio size="small" />} label="Has username" />
          <FormControlLabel value="no" control={<Radio size="small" />} label="No username" />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default UsersFilter
export { DEFAULT_FILTER_STATE }

