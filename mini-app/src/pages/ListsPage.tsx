import { Box, Typography, List, ListItem, ListItemText, Paper } from '@mui/material'

const ListsPage = () => {
  // Заглушка с тремя ФИО
  const mockLists = [
    { id: 1, name: 'Иванов Иван Иванович' },
    { id: 2, name: 'Петров Петр Петрович' },
    { id: 3, name: 'Сидоров Сидор Сидорович' },
  ]

  return (
    <Box sx={{ p: 2, pb: 10 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Списки
      </Typography>
      <Paper>
        <List>
          {mockLists.map((item) => (
            <ListItem key={item.id}>
              <ListItemText primary={item.name} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  )
}

export default ListsPage

