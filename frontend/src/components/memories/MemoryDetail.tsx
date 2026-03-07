'use client'
import { Memory } from '@/types'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { format } from 'date-fns'

interface MemoryDetailProps {
  memory: Memory | null
  onClose: () => void
}

export function MemoryDetail({ memory, onClose }: MemoryDetailProps) {
  if (!memory) return null

  return (
    <Dialog open={!!memory} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            Memory Detail
            <Badge variant="outline">{memory.memory_type}</Badge>
          </DialogTitle>
        </DialogHeader>
        <Separator />
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">Content</p>
            <p className="text-sm whitespace-pre-wrap">{memory.content}</p>
          </div>
          {memory.summary && (
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Summary</p>
              <p className="text-sm text-muted-foreground">{memory.summary}</p>
            </div>
          )}
          <Separator />
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium text-muted-foreground">Source</p>
              <p>{memory.source_type || '—'}</p>
            </div>
            <div>
              <p className="font-medium text-muted-foreground">Confidence</p>
              <p>{Math.round((memory.confidence || 1) * 100)}%</p>
            </div>
            <div>
              <p className="font-medium text-muted-foreground">Salience</p>
              <p>{Math.round((memory.salience_score || 0.5) * 100)}%</p>
            </div>
            <div>
              <p className="font-medium text-muted-foreground">Created</p>
              <p>{format(new Date(memory.created_at), 'PPpp')}</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
