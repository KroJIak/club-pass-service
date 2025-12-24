import { useState, useEffect } from 'react'
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material'
import { FilterSection } from './FilterPanel'
import { Order } from '../../types'

export interface OrdersFilterState {
  search: string
  hasPromocode: 'all' | 'yes' | 'no'
}

const DEFAULT_FILTER_STATE: OrdersFilterState = {
  search: '',
  hasPromocode: 'all',
}

interface OrdersFilterProps {
  orders: Order[]
  filterState: OrdersFilterState
  onFilterChange: (filter: OrdersFilterState) => void
}

const OrdersFilter = ({ orders, filterState, onFilterChange }: OrdersFilterProps) => {
  const [localFilter, setLocalFilter] = useState<OrdersFilterState>(filterState)

  useEffect(() => {
    setLocalFilter(filterState)
  }, [filterState])

  const handleFilterChange = (updates: Partial<OrdersFilterState>) => {
    const newFilter = { ...localFilter, ...updates }
    setLocalFilter(newFilter)
    onFilterChange(newFilter)
  }

  return (
    <Box>
      <FilterSection title="Promocode">
        <RadioGroup
          value={localFilter.hasPromocode}
          onChange={(e) => handleFilterChange({ hasPromocode: e.target.value as 'all' | 'yes' | 'no' })}
        >
          <FormControlLabel 
            value="all" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>All</Typography>} 
          />
          <FormControlLabel 
            value="yes" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>Has promocode</Typography>} 
          />
          <FormControlLabel 
            value="no" 
            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: '1rem' } }} />} 
            label={<Typography sx={{ fontSize: '0.84rem' }}>No promocode</Typography>} 
          />
        </RadioGroup>
      </FilterSection>
    </Box>
  )
}

export default OrdersFilter
export { DEFAULT_FILTER_STATE }

