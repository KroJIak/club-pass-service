import { useState, useCallback } from 'react'

type SelectionState = 'none' | 'some' | 'all'

export const useSelection = <T extends { id: number }>(items: T[]) => {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  const isSelected = useCallback((id: number) => {
    return selectedIds.has(id)
  }, [selectedIds])

  const toggleSelection = useCallback((id: number) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const selectAll = useCallback(() => {
    setSelectedIds(new Set(items.map(item => item.id)))
  }, [items])

  const deselectAll = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  const getSelectionState = useCallback((): SelectionState => {
    if (selectedIds.size === 0) return 'none'
    if (selectedIds.size === items.length) return 'all'
    return 'some'
  }, [selectedIds, items])

  const handleSelectAllClick = useCallback(() => {
    const state = getSelectionState()
    if (state === 'none' || state === 'some') {
      selectAll()
    } else {
      deselectAll()
    }
  }, [getSelectionState, selectAll, deselectAll])

  const selectedCount = selectedIds.size
  const hasSelection = selectedCount > 0

  return {
    selectedIds: Array.from(selectedIds),
    isSelected,
    toggleSelection,
    selectAll,
    deselectAll,
    handleSelectAllClick,
    getSelectionState,
    selectedCount,
    hasSelection,
  }
}

