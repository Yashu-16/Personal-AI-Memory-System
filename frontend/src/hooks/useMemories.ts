'use client'

import { useState, useCallback } from 'react'
import { memoriesApi } from '@/lib/api'
import type { Memory, MemoryFilters, PaginatedResponse } from '@/types'

export function useMemories() {
  const [memories, setMemories] = useState<Memory[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<MemoryFilters>({
    page: 1,
    page_size: 20,
  })

  const fetchMemories = useCallback(async (overrideFilters?: MemoryFilters) => {
    setIsLoading(true)
    setError(null)
    try {
      const activeFilters = overrideFilters ?? filters
      const data: PaginatedResponse<Memory> = await memoriesApi.getMemories(activeFilters)
      setMemories(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch memories')
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  const deleteMemory = useCallback(async (id: string) => {
    try {
      await memoriesApi.deleteMemory(id)
      setMemories((prev) => prev.filter((m) => m.id !== id))
      setTotal((prev) => prev - 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete memory')
      throw err
    }
  }, [])

  const updateMemory = useCallback(async (id: string, data: Partial<Memory>) => {
    try {
      const updated = await memoriesApi.updateMemory(id, data)
      setMemories((prev) => prev.map((m) => (m.id === id ? updated : m)))
      return updated
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update memory')
      throw err
    }
  }, [])

  const setFilters = useCallback((newFilters: Partial<MemoryFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...newFilters }))
  }, [])

  return {
    memories,
    total,
    isLoading,
    error,
    filters,
    fetchMemories,
    deleteMemory,
    updateMemory,
    setFilters,
  }
}
