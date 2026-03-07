'use client'
import { Memory } from '@/types'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Trash2, Edit, Brain, Calendar, FileText } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { cn } from '@/lib/utils'

const MEMORY_TYPE_COLORS: Record<string, string> = {
  fact: 'bg-blue-100 text-blue-800',
  commitment: 'bg-orange-100 text-orange-800',
  task: 'bg-green-100 text-green-800',
  event: 'bg-purple-100 text-purple-800',
  preference: 'bg-yellow-100 text-yellow-800',
  goal: 'bg-red-100 text-red-800',
  insight: 'bg-indigo-100 text-indigo-800',
}

interface MemoryCardProps {
  memory: Memory
  onDelete?: (id: string) => void
  onEdit?: (memory: Memory) => void
  onClick?: (memory: Memory) => void
}

export function MemoryCard({ memory, onDelete, onEdit, onClick }: MemoryCardProps) {
  return (
    <Card
      className={cn('cursor-pointer hover:shadow-md transition-shadow', onClick && 'hover:border-primary')}
      onClick={() => onClick?.(memory)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', MEMORY_TYPE_COLORS[memory.memory_type] || 'bg-gray-100 text-gray-800')}>
              {memory.memory_type}
            </span>
            {memory.source_type && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <FileText className="h-3 w-3" />
                {memory.source_type}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
            {onEdit && (
              <Button variant="ghost" size="sm" onClick={() => onEdit(memory)} className="h-7 w-7 p-0">
                <Edit className="h-3.5 w-3.5" />
              </Button>
            )}
            {onDelete && (
              <Button variant="ghost" size="sm" onClick={() => onDelete(memory.id)} className="h-7 w-7 p-0 text-destructive hover:text-destructive">
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm line-clamp-3 mb-2">{memory.content}</p>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDistanceToNow(new Date(memory.created_at), { addSuffix: true })}
          </span>
          <span className="flex items-center gap-1">
            <Brain className="h-3 w-3" />
            {Math.round((memory.confidence || 1) * 100)}% confidence
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
