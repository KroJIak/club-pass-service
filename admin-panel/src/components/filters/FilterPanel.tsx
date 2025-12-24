import { useState, ReactNode } from 'react'
import {
  Box,
  TextField,
  Typography,
  Divider,
  Collapse,
  IconButton,
} from '@mui/material'
import { ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material'

export interface FilterPanelProps {
  searchValue: string
  onSearchChange: (value: string) => void
  children: ReactNode
}

const FilterPanel = ({ searchValue, onSearchChange, children }: FilterPanelProps) => {
  return (
    <Box
      sx={{
        width: '300px',
        flexShrink: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        overflow: 'auto',
      }}
    >
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Filters
        </Typography>
        <TextField
          fullWidth
          size="small"
          placeholder="Search..."
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          sx={{ mb: 2 }}
        />
      </Box>
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {children}
      </Box>
    </Box>
  )
}

export interface FilterSectionProps {
  title: string
  children: ReactNode
  defaultExpanded?: boolean
}

export const FilterSection = ({ title, children, defaultExpanded = true }: FilterSectionProps) => {
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <Box sx={{ mb: 2 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 1,
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <IconButton size="small" onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}>
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>
      <Collapse in={expanded}>
        {children}
      </Collapse>
      <Divider sx={{ mt: 2 }} />
    </Box>
  )
}

export default FilterPanel

