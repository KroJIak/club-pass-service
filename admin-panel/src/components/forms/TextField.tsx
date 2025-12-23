import { TextField as MuiTextField, TextFieldProps } from '@mui/material'

const TextField = (props: TextFieldProps) => {
  return <MuiTextField {...props} fullWidth margin="normal" />
}

export default TextField

