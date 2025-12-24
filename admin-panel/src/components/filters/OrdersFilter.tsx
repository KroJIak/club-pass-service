import { Box } from '@mui/material'

export interface OrdersFilterState {
  search: string
}

const DEFAULT_FILTER_STATE: OrdersFilterState = {
  search: '',
}

interface OrdersFilterProps {
  filterState: OrdersFilterState
  onFilterChange: (filter: OrdersFilterState) => void
}

const OrdersFilter = ({ filterState, onFilterChange }: OrdersFilterProps) => {
  return <Box />
}

export default OrdersFilter
export { DEFAULT_FILTER_STATE }
