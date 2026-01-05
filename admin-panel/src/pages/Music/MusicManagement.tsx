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
  DragStartEvent,
  useDroppable,
  DragOverlay,
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
  onDelete: (id: number) => void
  disableDrag?: boolean
}

const SortableQueueItem = ({ item, isSelected, onDelete, disableDrag = false }: SortableQueueItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: `queue-${item.id}`, disabled: disableDrag })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Paper
      ref={setNodeRef}
      style={style}
      {...(disableDrag ? {} : { ...attributes, ...listeners })}
      sx={{
        p: 2,
        mb: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        cursor: isDragging ? 'grabbing' : 'grab',
        border: isSelected ? '2px solid' : 'none',
        borderColor: isSelected ? 'primary.main' : 'transparent',
        bgcolor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
        position: 'relative',
      }}
    >
      <DragIndicatorIcon sx={{ color: 'text.secondary', cursor: 'grab' }} />
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body1" fontWeight="bold">
          {item.track_title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {item.track_artist}
        </Typography>
        {item.request_count !== undefined && item.request_count > 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, display: 'block', fontSize: '0.95rem' }}>
            Requests: {item.request_count}
          </Typography>
        )}
        <Box sx={{ mt: 1, display: 'flex', gap: 1, pointerEvents: 'auto' }}>
          {item.yandex_music_url && (
            <Link href={item.yandex_music_url} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
              Yandex Music
            </Link>
          )}
          {item.other_source_url && (
            <Link href={item.other_source_url} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
              Other Source
            </Link>
          )}
        </Box>
      </Box>
      <IconButton onClick={(e) => { e.stopPropagation(); onDelete(item.id); }} color="error">
        <DeleteIcon />
      </IconButton>
    </Paper>
  )
}

// Sortable Wishlist Item Component
interface SortableWishlistItemProps {
  item: MusicRequest
  isSelected: boolean
  onDelete: (id: number) => void
  onMoveToQueue: (id: number) => void
  disableDrag?: boolean
}

const SortableWishlistItem = ({ item, isSelected, onDelete, onMoveToQueue, disableDrag = false }: SortableWishlistItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: `wishlist-${item.id}`, disabled: disableDrag })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Paper
      ref={setNodeRef}
      style={style}
      {...(disableDrag ? {} : { ...attributes, ...listeners })}
      sx={{
        p: 2,
        mb: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        cursor: isDragging ? 'grabbing' : 'grab',
        border: isSelected ? '2px solid' : 'none',
        borderColor: isSelected ? 'primary.main' : 'transparent',
        bgcolor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
        position: 'relative',
      }}
    >
      <DragIndicatorIcon sx={{ color: 'text.secondary', cursor: 'grab' }} />
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body1" fontWeight="bold">
          {item.track_title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {item.track_artist}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, display: 'block', fontSize: '0.95rem' }}>
          Requests: {item.request_count}
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
          {item.yandex_music_url && (
            <Link href={item.yandex_music_url} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
              Yandex Music
            </Link>
          )}
          {item.other_source_url && (
            <Link href={item.other_source_url} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
              Other Source
            </Link>
          )}
        </Box>
      </Box>
      <IconButton 
        onClick={(e) => { 
          e.stopPropagation(); 
          onMoveToQueue(item.id); 
        }} 
        color="primary"
        sx={{ pointerEvents: 'auto' }}
      >
        <PlayArrowIcon />
      </IconButton>
      <IconButton 
        onClick={(e) => { 
          e.stopPropagation(); 
          onDelete(item.id); 
        }} 
        color="error"
        sx={{ pointerEvents: 'auto' }}
      >
        <DeleteIcon />
      </IconButton>
    </Paper>
  )
}

// Droppable zone for Queue
const QueueDroppable = ({ children }: { children: React.ReactNode }) => {
  const { setNodeRef, isOver } = useDroppable({ id: 'queue-droppable' })
  return (
    <Box
      ref={setNodeRef}
      sx={{
        minHeight: '200px',
        border: isOver ? '2px dashed' : 'none',
        borderColor: isOver ? 'primary.main' : 'transparent',
        borderRadius: 1,
        p: isOver ? 1 : 0,
      }}
    >
      {children}
    </Box>
  )
}

// Droppable zone for Wishlist
const WishlistDroppable = ({ children }: { children: React.ReactNode }) => {
  const { setNodeRef, isOver } = useDroppable({ id: 'wishlist-droppable' })
  return (
    <Box
      ref={setNodeRef}
      sx={{
        minHeight: '200px',
        border: isOver ? '2px dashed' : 'none',
        borderColor: isOver ? 'primary.main' : 'transparent',
        borderRadius: 1,
        p: isOver ? 1 : 0,
      }}
    >
      {children}
    </Box>
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
  const [activeId, setActiveId] = useState<string | null>(null)

  // Disable drag if any items are selected
  const disableDrag = queueSelection.hasSelection || wishlistSelection.hasSelection

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
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

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(String(event.active.id))
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event
    setActiveId(null)

    if (!over) {
      return
    }

    const activeId = String(active.id)
    const overId = String(over.id)

    // Check if dragging from wishlist to queue (droppable zone or queue item)
    if (activeId.startsWith('wishlist-') && (overId === 'queue-droppable' || overId.startsWith('queue-'))) {
      const wishlistId = parseInt(activeId.replace('wishlist-', ''))
      await handleMoveToQueue(wishlistId)
      return
    }

    // Check if dragging from queue to wishlist (droppable zone or wishlist item)
    if (activeId.startsWith('queue-') && (overId === 'wishlist-droppable' || overId.startsWith('wishlist-'))) {
      const queueId = parseInt(activeId.replace('queue-', ''))
      await handleMoveToWishlist(queueId)
      return
    }

    // Check if dragging within queue
    if (activeId.startsWith('queue-') && overId.startsWith('queue-')) {
      const activeQueueId = parseInt(activeId.replace('queue-', ''))
      const overQueueId = parseInt(overId.replace('queue-', ''))

      const oldIndex = queue.findIndex((item) => item.id === activeQueueId)
      const newIndex = queue.findIndex((item) => item.id === overQueueId)

      if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) {
        return
      }

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
  }

  const handleDeleteQueueItem = async (id: number) => {
    if (!confirm('Delete track from queue?')) return

    try {
      await api.delete(`/admin/music-queue/${id}`)
      fetchQueue()
    } catch (error) {
      console.error('Failed to delete queue item:', error)
      alert('Error deleting')
    }
  }

  const handleDeleteWishlistItem = async (id: number) => {
    if (!confirm('Delete track from wishlist?')) return

    try {
      await api.delete(`/admin/music-wishlist/${id}`)
      fetchWishlist()
    } catch (error) {
      console.error('Failed to delete wishlist item:', error)
      alert('Error deleting')
    }
  }

  const handleMoveToQueue = async (id: number) => {
    try {
      await api.post(`/admin/music-wishlist/${id}/move-to-queue`)
      fetchQueue()
      fetchWishlist()
    } catch (error) {
      console.error('Failed to move to queue:', error)
      alert('Error moving to queue')
    }
  }

  const handleMoveToWishlist = async (id: number) => {
    try {
      await api.post(`/admin/music-queue/${id}/move-to-wishlist`)
      fetchQueue()
      fetchWishlist()
    } catch (error) {
      console.error('Failed to move to wishlist:', error)
      alert('Error moving to wishlist')
    }
  }

  const handleDeleteSelectedQueue = async () => {
    if (!confirm(`Delete ${queueSelection.selectedCount} tracks from queue?`)) return

    try {
      await api.delete('/admin/music-queue/batch', {
        data: queueSelection.selectedIds,
      })
      queueSelection.deselectAll()
      fetchQueue()
    } catch (error) {
      console.error('Failed to delete selected queue items:', error)
      alert('Error deleting')
    }
  }

  const handleDeleteSelectedWishlist = async () => {
    if (!confirm(`Delete ${wishlistSelection.selectedCount} tracks from wishlist?`)) return

    try {
      await api.delete('/admin/music-wishlist/batch', {
        data: wishlistSelection.selectedIds,
      })
      wishlistSelection.deselectAll()
      fetchWishlist()
    } catch (error) {
      console.error('Failed to delete selected wishlist items:', error)
      alert('Error deleting')
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    )
  }

  // Find active item for DragOverlay
  const activeQueueItem = activeId?.startsWith('queue-') 
    ? queue.find((item) => `queue-${item.id}` === activeId)
    : null
  const activeWishlistItem = activeId?.startsWith('wishlist-')
    ? wishlist.find((item) => `wishlist-${item.id}` === activeId)
    : null

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Music Management
        </Typography>

        <Box sx={{ display: 'flex', gap: 3, mt: 3 }}>
          {/* Queue Block */}
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Queue</Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexDirection: 'row-reverse' }}>
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
                      Delete Selected
                    </Button>
                  )}
                </Box>
              </Box>

              {queueLoading ? (
                <CircularProgress />
              ) : (
                <QueueDroppable>
                  <SortableContext items={queue.map((item) => `queue-${item.id}`)} strategy={verticalListSortingStrategy}>
                    {queue.length === 0 ? (
                      <Typography color="text.secondary">Queue is empty</Typography>
                    ) : (
                      queue.map((item) => (
                        <SortableQueueItem
                          key={item.id}
                          item={item}
                          isSelected={queueSelection.isSelected(item.id)}
                          onDelete={handleDeleteQueueItem}
                          disableDrag={disableDrag}
                        />
                      ))
                    )}
                  </SortableContext>
                </QueueDroppable>
              )}
            </CardContent>
          </Card>

          {/* Wishlist Block */}
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Wishlist</Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexDirection: 'row-reverse' }}>
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
                      Delete Selected
                    </Button>
                  )}
                </Box>
              </Box>

              {wishlistLoading ? (
                <CircularProgress />
              ) : wishlist.length === 0 ? (
                <Typography color="text.secondary">Wishlist is empty</Typography>
              ) : (
                <WishlistDroppable>
                  <SortableContext items={wishlist.map((item) => `wishlist-${item.id}`)} strategy={verticalListSortingStrategy}>
                    {wishlist.map((item) => (
                      <SortableWishlistItem
                        key={item.id}
                        item={item}
                        isSelected={wishlistSelection.isSelected(item.id)}
                        onDelete={handleDeleteWishlistItem}
                        onMoveToQueue={handleMoveToQueue}
                        disableDrag={disableDrag}
                      />
                    ))}
                  </SortableContext>
                </WishlistDroppable>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
      <DragOverlay style={{ zIndex: 9999 }}>
        {activeQueueItem ? (
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              cursor: 'grabbing',
              border: queueSelection.isSelected(activeQueueItem.id) ? '2px solid' : 'none',
              borderColor: queueSelection.isSelected(activeQueueItem.id) ? 'primary.main' : 'transparent',
              bgcolor: queueSelection.isSelected(activeQueueItem.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
              boxShadow: 6,
              width: '400px',
            }}
          >
            <DragIndicatorIcon sx={{ color: 'text.secondary' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                {activeQueueItem.track_title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {activeQueueItem.track_artist}
              </Typography>
              {activeQueueItem.request_count !== undefined && activeQueueItem.request_count > 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, display: 'block', fontSize: '0.95rem' }}>
                  Requests: {activeQueueItem.request_count}
                </Typography>
              )}
            </Box>
          </Paper>
        ) : activeWishlistItem ? (
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              cursor: 'grabbing',
              border: wishlistSelection.isSelected(activeWishlistItem.id) ? '2px solid' : 'none',
              borderColor: wishlistSelection.isSelected(activeWishlistItem.id) ? 'primary.main' : 'transparent',
              bgcolor: wishlistSelection.isSelected(activeWishlistItem.id) ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
              boxShadow: 6,
              width: '400px',
            }}
          >
            <DragIndicatorIcon sx={{ color: 'text.secondary' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                {activeWishlistItem.track_title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {activeWishlistItem.track_artist}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, display: 'block', fontSize: '0.95rem' }}>
                Requests: {activeWishlistItem.request_count}
              </Typography>
            </Box>
          </Paper>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

export default MusicManagement

