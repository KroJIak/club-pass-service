import { forwardRef } from 'react'
import { TextField as MuiTextField, TextFieldProps } from '@mui/material'

const TextField = forwardRef<HTMLDivElement, TextFieldProps>((props, ref) => {
  return <MuiTextField {...props} ref={ref} fullWidth margin="normal" />
})

TextField.displayName = 'TextField'

export default TextField

