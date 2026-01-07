import { TimePicker } from '@mui/x-date-pickers/TimePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import dayjs, { Dayjs } from 'dayjs'

interface TimeFieldProps {
  label: string
  value: string | null // HH:MM format
  onChange: (value: string | null) => void
  error?: boolean
  helperText?: string
  disabled?: boolean
}

const TimeField = ({ label, value, onChange, error, helperText, disabled }: TimeFieldProps) => {
  const dayjsValue = value ? dayjs(value, 'HH:mm') : null

  const handleChange = (newValue: Dayjs | null) => {
    if (newValue) {
      onChange(newValue.format('HH:mm'))
    } else {
      onChange(null)
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <TimePicker
        label={label}
        value={dayjsValue}
        onChange={handleChange}
        format="HH:mm"
        disabled={disabled}
        slotProps={{
          textField: {
            fullWidth: true,
            margin: 'normal',
            error,
            helperText,
          },
        }}
      />
    </LocalizationProvider>
  )
}

export default TimeField

