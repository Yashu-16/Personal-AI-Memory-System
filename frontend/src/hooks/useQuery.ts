'use client'

import { useState, useCallback } from 'react'
import { queryApi } from '@/lib/api'
import type { QueryMessage, QueryResponse } from '@/types'

function makeId() {
  return Math.random().toString(36).slice(2)
}

export function useQuery() {
  const [messages, setMessages] = useState<QueryMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | undefined>()

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: QueryMessage = {
      id: makeId(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response: QueryResponse = await queryApi.sendQuery({
        query: content,
        conversation_id: conversationId,
        include_sources: true,
      })

      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: QueryMessage = {
        id: makeId(),
        role: 'assistant',
        content: response.answer,
        supporting_memories: response.supporting_memories,
        confidence: response.confidence,
        suggested_actions: response.suggested_actions,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      return response
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [conversationId])

  const clearMessages = useCallback(() => {
    setMessages([])
    setConversationId(undefined)
  }, [])

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearMessages,
  }
}
