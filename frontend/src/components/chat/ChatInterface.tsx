'use client'

import { useEffect, useRef } from 'react'
import { MessageSquare } from 'lucide-react'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { QueryInput } from '@/components/chat/QueryInput'
import { EmptyState } from '@/components/common/EmptyState'
import { Spinner } from '@/components/ui/spinner'
import { useQuery } from '@/hooks/useQuery'

export function ChatInterface() {
  const { messages, isLoading, sendMessage } = useQuery()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSuggestedAction = (action: string) => {
    sendMessage(action)
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && !isLoading ? (
          <EmptyState
            icon={MessageSquare}
            title="Ask Memora anything"
            description="Query your personal memory — past conversations, notes, emails, and more."
            className="h-full"
          />
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onSuggestedAction={handleSuggestedAction}
            />
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-muted px-4 py-3">
              <Spinner size="sm" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="border-t bg-background px-4 py-3">
        <QueryInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}
