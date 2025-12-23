import { useState } from 'react'
import { TextField, Box, Chip } from '@mui/material'
import AddIcon from '@mui/icons-material/Add'

interface ArrayFieldProps {
  label: string
  value: string[]
  onChange: (value: string[]) => void
}

const ArrayField = ({ label, value, onChange }: ArrayFieldProps) => {
  const [inputValue, setInputValue] = useState('')

  const handleAdd = () => {
    if (inputValue.trim()) {
      onChange([...value, inputValue.trim()])
      setInputValue('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }

  const handleDelete = (index: number) => {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <Box sx={{ mt: 2, mb: 2 }}>
      <TextField
        fullWidth
        label={label}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        margin="normal"
        InputProps={{
          endAdornment: (
            <AddIcon
              sx={{ cursor: 'pointer', color: 'primary.main' }}
              onClick={handleAdd}
            />
          ),
        }}
      />
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
        {value.map((item, index) => (
          <Chip
            key={index}
            label={item}
            onDelete={() => handleDelete(index)}
            color="primary"
            variant="outlined"
          />
        ))}
      </Box>
    </Box>
  )
}

export default ArrayField

