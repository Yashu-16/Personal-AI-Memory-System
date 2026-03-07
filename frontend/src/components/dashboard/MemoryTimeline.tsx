'use client'

import { format } from 'date-fns'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { TimelineEntry, MemoryType } from '@/types'

const memoryTypeColor: Record<MemoryType, string> = {
  conversation: 'bg-blue-100 text-blue-800',
  document: 'bg-gray-100 text-gray-800',
  email: 'bg-yellow-100 text-yellow-800',
  meeting: 'bg-purple-100 text-purple-800',
  note: 'bg-green-100 text-green-800',
  task: 'bg-orange-100 text-orange-800',
  commitment: 'bg-red-100 text-red-800',
  insight: 'bg-pink-100 text-pink-800',
  other: 'bg-slate-100 text-slate-800',
}

interface MemoryTimelineProps {
  entries: TimelineEntry[]
}

export function MemoryTimeline({ entries }: MemoryTimelineProps) {
  if (!entries.length) {
    return <p className="text-sm text-muted-foreground">No memories yet.</p>
  }

  return (
    <div className="space-y-6">
      {entries.map((entry) => (
        <div key={entry.date}>
          <div className="mb-3 flex items-center gap-3">
            <p className="text-sm font-semibold">
              {format(new Date(entry.date), 'EEEE, MMM d')}
            </p>
            <Separator className="flex-1" />
          </div>
          <div className="space-y-2 pl-4 border-l-2 border-muted">
            {entry.memories.map((memory) => (
              <div key={memory.id} className="flex items-start gap-2">
                <Badge
                  variant="outline"
                  className={`shrink-0 text-xs capitalize ${memoryTypeColor[memory.memory_type]}`}
                >
                  {memory.memory_type}
                </Badge>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {memory.content.slice(0, 120)}
                  {memory.content.length > 120 && '…'}
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
