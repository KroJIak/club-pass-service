import { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Checkbox,
  Paper,
  Link,
  CircularProgress,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  DragIndicator as DragIndicatorIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import api from '../../services/api'
import { MusicRequest, MusicQueue, MusicQueueReorderRequest } from '../../types'
import { useSelection } from '../../hooks/useSelection'

// Sortable Queue Item Component
interface SortableQueueItemProps {
  item: MusicQueue
  isSelected: boolean
  onSelect: (id: number) => void
  onDelete: (id: number) => void
}

const SortableQueueItem = ({ item, isSelected, onSelect, onDelete }: SortableQueueItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Paper
      ref={setNodeRef}
      style={style}
      sx={{
        p: 2,
        mb: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
    >
      <Checkbox
        checked={isSelected}
        onChange={() => onSelect(item.id)}
        onClick={(e) => e.stopPropagation()}
      />
      <DragIndicatorIcon {...attributes} {...listeners} sx={{ cursor: 'grab' }} />
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body1" fontWeight="bold">
          {item.track_title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {item.track_artist}
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
          {item.yandex_music_url && (
            <Link href={item.yandex_music_url} target="_blank" rel="noopener">
              Яндекс.Музыка
            </Link>
          )}
          {item.other_source_url && (
            <Link href={item.other_source_url} target="_blank" rel="noopener">
              Другой источник
            </Link>
          )}
        </Box>
      </Box>
      <IconButton onClick={() => onDelete(item.id)} color="error">
        <DeleteIcon />
      </IconButton>
    </Paper>
  )
}

// Wishlist Item Component
interface WishlistItemProps {
  item: MusicRequest
  isSelected: boolean
  onSelect: (id: number) => void
  onDelete: (id: number) => void
  onMoveToQueue: (id: number) => void
}

const WishlistItem = ({ item, isSelected, onSelect, onDelete, onMoveToQueue }: WishlistItemProps) => {
  return (
    <Paper
      sx={{
        p: 2,
        mb: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
      }}
    >
      <Checkbox
        checked={isSelected}
        onChange={() => onSelect(item.id)}
        onClick={(e) => e.stopPropagation()}
      />
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body1" fontWeight="bold">
          {item.track_title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {item.track_artist}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
          Запросов: {item.request_count}
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
          {item.yandex_music_url && (
            <Link href={item.yandex_music_url} target="_blank" rel="noopener">
              Яндекс.Музыка
            </Link>
          )}
          {item.other_source_url && (
            <Link href={item.other_source_url} target="_blank" rel="noopener">
              Другой источник
            </Link>
          )}
        </Box>
      </Box>
      <IconButton onClick={() => onMoveToQueue(item.id)} color="primary">
        <PlayArrowIcon />
      </IconButton>
      <IconButton onClick={() => onDelete(item.id)} color="error">
        <DeleteIcon />
      </IconButton>
    </Paper>
  )
}

const MusicManagement = () => {
  const [queue, setQueue] = useState<MusicQueue[]>([])
  const [wishlist, setWishlist] = useState<MusicRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [queueLoading, setQueueLoading] = useState(false)
  const [wishlistLoading, setWishlistLoading] = useState(false)

  const queueSelection = useSelection(queue)
  const wishlistSelection = useSelection(wishlist)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const fetchQueue = useCallback(async () => {
    try {
      const response = await api.get('/admin/music-queue')
      setQueue(response.data.queue || [])
    } catch (error) {
      console.error('Failed to fetch music queue:', error)
    } finally {
      setQueueLoading(false)
    }
  }, [])

  const fetchWishlist = useCallback(async () => {
    try {
      const response = await api.get('/admin/music-wishlist')
      setWishlist(response.data.requests || [])
    } catch (error) {
      console.error('Failed to fetch music wishlist:', error)
    } finally {
      setWishlistLoading(false)
    }
  }, [])

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([fetchQueue(), fetchWishlist()])
      setLoading(false)
    }
    loadData()
  }, [fetchQueue, fetchWishlist])

  // Auto-refresh every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchQueue()
      fetchWishlist()
    }, 2000)

    return () => clearInterval(interval)
  }, [fetchQueue, fetchWishlist])

  const handleQueueDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event

    if (!over || active.id === over.id) {
      return
    }

    const oldIndex = queue.findIndex((item) => item.id === active.id)
    const newIndex = queue.findIndex((item) => item.id === over.id)

    const newQueue = arrayMove(queue, oldIndex, newIndex)
    setQueue(newQueue)

    // Update queue_order in backend
    try {
      const reorderRequest: MusicQueueReorderRequest = {
        items: newQueue.map((item, index) => ({
          id: item.id,
          queue_order: index,
        })),
      }
      await api.put('/admin/music-queue/reorder', reorderRequest)
    } catch (error) {
      console.error('Failed to reorder queue:', error)
      // Revert on error
      fetchQueue()
    }
  }

  const handleDeleteQueueItem = async (id: number) => {
    if (!confirm('Удалить трек из очереди?')) return

    try {
      await api.delete(`/admin/music-queue/${id}`)
      fetchQueue()
    } catch (error) {
      console.error('Failed to delete queue item:', error)
      alert('Ошибка при удалении')
    }
  }

  const handleDeleteWishlistItem = async (id: number) => {
    if (!confirm('Удалить трек из списка желаемого?')) return

    try {
      await api.delete(`/admin/music-wishlist/${id}`)
      fetchWishlist()
    } catch (error) {
      console.error('Failed to delete wishlist item:', error)
      alert('Ошибка при удалении')
    }
  }

  const handleMoveToQueue = async (id: number) => {
    try {
      await api.post(`/admin/music-wishlist/${id}/move-to-queue`)
      fetchQueue()
      fetchWishlist()
    } catch (error) {
      console.error('Failed to move to queue:', error)
      alert('Ошибка при переносе в очередь')
    }
  }

  const handleDeleteSelectedQueue = async () => {
    if (!confirm(`Удалить ${queueSelection.selectedCount} треков из очереди?`)) return

    try {
      await api.delete('/admin/music-queue/batch', {
        data: queueSelection.selectedIds,
      })
      queueSelection.deselectAll()
      fetchQueue()
    } catch (error) {
      console.error('Failed to delete selected queue items:', error)
      alert('Ошибка при удалении')
    }
  }

  const handleDeleteSelectedWishlist = async () => {
    if (!confirm(`Удалить ${wishlistSelection.selectedCount} треков из списка желаемого?`)) return

    try {
      await api.delete('/admin/music-wishlist/batch', {
        data: wishlistSelection.selectedIds,
      })
      wishlistSelection.deselectAll()
      fetchWishlist()
    } catch (error) {
      console.error('Failed to delete selected wishlist items:', error)
      alert('Ошибка при удалении')
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Управление музыкой
      </Typography>

      <Box sx={{ display: 'flex', gap: 3, mt: 3 }}>
        {/* Queue Block */}
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Очередь</Typography>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Checkbox
                  checked={queueSelection.getSelectionState() === 'all'}
                  indeterminate={queueSelection.getSelectionState() === 'some'}
                  onChange={(e) => {
                    if (e.target.checked) {
                      queueSelection.selectAll()
                    } else {
                      queueSelection.deselectAll()
                    }
                  }}
                />
                {queueSelection.hasSelection && (
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={handleDeleteSelectedQueue}
                  >
                    Удалить выбранные
                  </Button>
                )}
              </Box>
            </Box>

            {queueLoading ? (
              <CircularProgress />
            ) : (
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleQueueDragEnd}
              >
                <SortableContext items={queue.map((item) => item.id)} strategy={verticalListSortingStrategy}>
                  {queue.length === 0 ? (
                    <Typography color="text.secondary">Очередь пуста</Typography>
                  ) : (
                    queue.map((item) => (
                      <SortableQueueItem
                        key={item.id}
                        item={item}
                        isSelected={queueSelection.isSelected(item.id)}
                        onSelect={queueSelection.toggleSelection}
                        onDelete={handleDeleteQueueItem}
                      />
                    ))
                  )}
                </SortableContext>
              </DndContext>
            )}
          </CardContent>
        </Card>

        {/* Wishlist Block */}
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Список желаемого</Typography>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Checkbox
                  checked={wishlistSelection.getSelectionState() === 'all'}
                  indeterminate={wishlistSelection.getSelectionState() === 'some'}
                  onChange={(e) => {
                    if (e.target.checked) {
                      wishlistSelection.selectAll()
                    } else {
                      wishlistSelection.deselectAll()
                    }
                  }}
                />
                {wishlistSelection.hasSelection && (
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={handleDeleteSelectedWishlist}
                  >
                    Удалить выбранные
                  </Button>
                )}
              </Box>
            </Box>

            {wishlistLoading ? (
              <CircularProgress />
            ) : wishlist.length === 0 ? (
              <Typography color="text.secondary">Список желаемого пуст</Typography>
            ) : (
              wishlist.map((item) => (
                <WishlistItem
                  key={item.id}
                  item={item}
                  isSelected={wishlistSelection.isSelected(item.id)}
                  onSelect={wishlistSelection.toggleSelection}
                  onDelete={handleDeleteWishlistItem}
                  onMoveToQueue={handleMoveToQueue}
                />
              ))
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}

export default MusicManagement

