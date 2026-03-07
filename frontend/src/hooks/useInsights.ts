'use client'

import { useState, useCallback } from 'react'
import { insightsApi } from '@/lib/api'
import type { Insight, PaginatedResponse } from '@/types'

export function useInsights() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [total, setTotal] = useState(0)
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchInsights = useCallback(async (page = 1, pageSize = 20) => {
    setIsLoading(true)
    setError(null)
    try {
      const data: PaginatedResponse<Insight> = await insightsApi.getInsights(page, pageSize)
      setInsights(data.items)
      setTotal(data.total)
      setUnreadCount(data.items.filter((i) => !i.is_read).length)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const markAsRead = useCallback(async (id: string) => {
    try {
      const updated = await insightsApi.markInsightRead(id)
      setInsights((prev) => prev.map((i) => (i.id === id ? updated : i)))
      setUnreadCount((prev) => Math.max(0, prev - 1))
      return updated
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark insight as read')
      throw err
    }
  }, [])

  return {
    insights,
    total,
    unreadCount,
    isLoading,
    error,
    fetchInsights,
    markAsRead,
  }
}
