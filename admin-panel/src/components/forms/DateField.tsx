import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import dayjs, { Dayjs } from 'dayjs'
import 'dayjs/locale/ru'

interface DateFieldProps {
  label: string
  value: string | null // DD.MM.YYYY format
  onChange: (value: string | null) => void
  error?: boolean
  helperText?: string
  disabled?: boolean
}

const DateField = ({ label, value, onChange, error, helperText, disabled }: DateFieldProps) => {
  const dayjsValue = value ? dayjs(value, 'DD.MM.YYYY') : null

  const handleChange = (newValue: Dayjs | null) => {
    if (newValue) {
      onChange(newValue.format('DD.MM.YYYY'))
    } else {
      onChange(null)
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ru">
      <DatePicker
        label={label}
        value={dayjsValue}
        onChange={handleChange}
        format="DD.MM.YYYY"
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

export default DateField

