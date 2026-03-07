'use client'

import { ConfidenceBadge } from '@/components/common/ConfidenceBadge'
import { SourceCitation } from '@/components/chat/SourceCitation'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { QueryMessage } from '@/types'

interface ChatMessageProps {
  message: QueryMessage
  onSuggestedAction?: (action: string) => void
}

export function ChatMessage({ message, onSuggestedAction }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex w-full', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-3 space-y-2',
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-sm'
            : 'bg-muted text-foreground rounded-bl-sm'
        )}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>

        {!isUser && message.confidence !== undefined && (
          <ConfidenceBadge score={message.confidence} />
        )}

        {!isUser && message.supporting_memories && message.supporting_memories.length > 0 && (
          <div className="space-y-1 pt-1">
            <p className="text-xs font-semibold text-muted-foreground">Sources</p>
            {message.supporting_memories.map((mem) => (
              <SourceCitation key={mem.memory_id} memory={mem} />
            ))}
          </div>
        )}

        {!isUser && message.suggested_actions && message.suggested_actions.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {message.suggested_actions.map((action) => (
              <Badge
                key={action}
                variant="outline"
                className="cursor-pointer hover:bg-accent text-xs"
                onClick={() => onSuggestedAction?.(action)}
              >
                {action}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
