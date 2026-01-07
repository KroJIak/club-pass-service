import { FormControlLabel, Switch } from '@mui/material'

interface BooleanFieldProps {
  label: string
  value: boolean
  onChange: (value: boolean) => void
  disabled?: boolean
}

const BooleanField = ({ label, value, onChange, disabled }: BooleanFieldProps) => {
  return (
    <FormControlLabel
      control={
        <Switch
          checked={value}
          onChange={(e) => onChange(e.target.checked)}
          color="primary"
          disabled={disabled}
        />
      }
      label={label}
      sx={{ mt: 2, mb: 1 }}
    />
  )
}

export default BooleanField

