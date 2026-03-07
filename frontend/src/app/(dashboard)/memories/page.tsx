'use client'
import { useEffect, useState } from 'react'
import { useMemories } from '@/hooks/useMemories'
import { MemoryCard } from '@/components/memories/MemoryCard'
import { MemoryFilters, MemoryFilterValues } from '@/components/memories/MemoryFilters'
import { MemoryDetail } from '@/components/memories/MemoryDetail'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Memory } from '@/types'
import { Button } from '@/components/ui/button'
import { Brain, ChevronLeft, ChevronRight } from 'lucide-react'

export default function MemoriesPage() {
  const { memories, total, isLoading, fetchMemories, deleteMemory } = useMemories()
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<MemoryFilterValues>({ search: '', memory_type: '', source_type: '', start_date: '', end_date: '' })
  const pageSize = 20

  useEffect(() => {
    fetchMemories({ page, page_size: pageSize, memory_type: filters.memory_type || undefined, source_type: filters.source_type || undefined, start_date: filters.start_date || undefined, end_date: filters.end_date || undefined, search: filters.search || undefined })
  }, [page, filters])

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Memories</h1>
        <p className="text-muted-foreground">{total} total memories</p>
      </div>
      <MemoryFilters filters={filters} onChange={f => { setFilters(f); setPage(1) }} />
      {isLoading ? <LoadingSpinner /> : memories.length === 0 ? (
        <EmptyState icon={<Brain className="h-8 w-8" />} title="No memories found" description="Connect data sources or adjust your filters." />
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {memories.map(m => <MemoryCard key={m.id} memory={m} onClick={setSelectedMemory} onDelete={deleteMemory} />)}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}><ChevronLeft className="h-4 w-4" /></Button>
              <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
              <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}><ChevronRight className="h-4 w-4" /></Button>
            </div>
          )}
        </>
      )}
      <MemoryDetail memory={selectedMemory} onClose={() => setSelectedMemory(null)} />
    </div>
  )
}
