import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import { AdminGroup, AdminAccount } from '../../types'
import GroupForm from './GroupForm'
import AccountForm from './AccountForm'
import PermissionsEditor from './PermissionsEditor'

const AdminAccountsList = () => {
  const { t } = useTranslation('staff')
  const { t: tCommon } = useTranslation('common')
  const [groups, setGroups] = useState<AdminGroup[]>([])
  const [accounts, setAccounts] = useState<Record<number, AdminAccount[]>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedGroup, setSelectedGroup] = useState<AdminGroup | null>(null)
  const [groupFormOpen, setGroupFormOpen] = useState(false)
  const [accountFormOpen, setAccountFormOpen] = useState(false)
  const [permissionsDialogOpen, setPermissionsDialogOpen] = useState(false)
  const [editingGroup, setEditingGroup] = useState<AdminGroup | null>(null)
  const [editingAccount, setEditingAccount] = useState<AdminAccount | null>(null)
  const [accountGroupId, setAccountGroupId] = useState<number | null>(null)

  const loadGroups = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get<{ groups: AdminGroup[] }>('/admin/groups')
      setGroups(response.data.groups)
      
      // Load accounts for each group
      const accountsMap: Record<number, AdminAccount[]> = {}
      for (const group of response.data.groups) {
        try {
          const accountsResponse = await api.get<{ accounts: AdminAccount[] }>(`/admin/groups/${group.id}/accounts`)
          accountsMap[group.id] = accountsResponse.data.accounts
        } catch (e) {
          accountsMap[group.id] = []
        }
      }
      setAccounts(accountsMap)
    } catch (err: any) {
      setError(err.response?.data?.detail || t('messages.fetchFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGroups()
  }, [])

  const handleCreateGroup = () => {
    setEditingGroup(null)
    setGroupFormOpen(true)
  }

  const handleEditGroup = (group: AdminGroup) => {
    setEditingGroup(group)
    setGroupFormOpen(true)
  }

  const handleDeleteGroup = async (groupId: number) => {
    if (!window.confirm(t('messages.deleteConfirm'))) {
      return
    }
    
    try {
      await api.delete(`/admin/groups/${groupId}`)
      await loadGroups()
    } catch (err: any) {
      setError(err.response?.data?.detail || tCommon('messages.deleteError'))
    }
  }

  const handleCreateAccount = (groupId: number) => {
    setAccountGroupId(groupId)
    setEditingAccount(null)
    setAccountFormOpen(true)
  }

  const handleEditAccount = (account: AdminAccount) => {
    setEditingAccount(account)
    setAccountGroupId(null)
    setAccountFormOpen(true)
  }

  const handleDeleteAccount = async (accountId: number) => {
    if (!window.confirm(t('messages.deleteConfirm'))) {
      return
    }
    
    try {
      await api.delete(`/admin/accounts/${accountId}`)
      await loadGroups()
    } catch (err: any) {
      setError(err.response?.data?.detail || tCommon('messages.deleteError'))
    }
  }

  const handleEditPermissions = (group: AdminGroup) => {
    setSelectedGroup(group)
    setPermissionsDialogOpen(true)
  }

  const handleGroupFormClose = () => {
    setGroupFormOpen(false)
    setEditingGroup(null)
  }

  const handleAccountFormClose = () => {
    setAccountFormOpen(false)
    setEditingAccount(null)
    setAccountGroupId(null)
  }

  const handlePermissionsDialogClose = () => {
    setPermissionsDialogOpen(false)
    setSelectedGroup(null)
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">{t('adminAccounts')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateGroup}
        >
          {t('createGroup')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {groups.map((group) => (
        <Paper key={group.id} sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h6">{group.name}</Typography>
              {group.description && (
                <Typography variant="body2" color="text.secondary">
                  {group.description}
                </Typography>
              )}
            </Box>
            <Box>
              <Button
                size="small"
                startIcon={<PeopleIcon />}
                onClick={() => handleEditPermissions(group)}
                sx={{ mr: 1 }}
              >
                {t('fields.permissions')}
              </Button>
              <IconButton
                size="small"
                onClick={() => handleEditGroup(group)}
                sx={{ mr: 1 }}
                title={tCommon('actions.edit')}
              >
                <EditIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleDeleteGroup(group.id)}
                color="error"
                title={tCommon('actions.delete')}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => handleCreateAccount(group.id)}
            >
              {t('createAccount')}
            </Button>
          </Box>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t('fields.username')}</TableCell>
                  <TableCell>{tCommon('fields.status')}</TableCell>
                  <TableCell>{tCommon('fields.date')}</TableCell>
                  <TableCell align="right">{tCommon('actions.actions')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {accounts[group.id]?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      {tCommon('messages.noData')}
                    </TableCell>
                  </TableRow>
                ) : (
                  accounts[group.id]?.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.username}</TableCell>
                      <TableCell>
                        <Chip
                          label={account.is_active ? tCommon('status.active') : tCommon('status.inactive')}
                          color={account.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(account.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => handleEditAccount(account)}
                          title={tCommon('actions.edit')}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteAccount(account.id)}
                          color="error"
                          title={tCommon('actions.delete')}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      ))}

      {groups.length === 0 && !loading && (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            {tCommon('messages.noData')}
          </Typography>
        </Paper>
      )}

      <GroupForm
        open={groupFormOpen}
        onClose={handleGroupFormClose}
        onSave={loadGroups}
        group={editingGroup}
      />

      <AccountForm
        open={accountFormOpen}
        onClose={handleAccountFormClose}
        onSave={loadGroups}
        account={editingAccount}
        groupId={accountGroupId}
        groups={groups}
      />

      {selectedGroup && (
        <PermissionsEditor
          open={permissionsDialogOpen}
          onClose={handlePermissionsDialogClose}
          group={selectedGroup}
          onSave={loadGroups}
        />
      )}
    </Box>
  )
}

export default AdminAccountsList

