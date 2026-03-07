import { Badge } from '@/components/ui/badge'
import type { MemoryReference, MemoryType } from '@/types'

const typeColor: Record<MemoryType, string> = {
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

interface SourceCitationProps {
  memory: MemoryReference
}

export function SourceCitation({ memory }: SourceCitationProps) {
  return (
    <div className="rounded border bg-background px-2 py-1.5 text-xs space-y-0.5">
      <div className="flex items-center justify-between gap-2">
        <Badge
          variant="outline"
          className={`text-xs capitalize px-1.5 py-0 ${typeColor[memory.memory_type]}`}
        >
          {memory.memory_type}
        </Badge>
        <span className="text-muted-foreground">
          {Math.round(memory.relevance_score * 100)}% relevant
        </span>
      </div>
      <p className="line-clamp-2 text-muted-foreground">{memory.content_excerpt}</p>
    </div>
  )
}
