'use client'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, X } from 'lucide-react'

export interface MemoryFilterValues {
  search: string
  memory_type: string
  source_type: string
  start_date: string
  end_date: string
}

interface MemoryFiltersProps {
  filters: MemoryFilterValues
  onChange: (filters: MemoryFilterValues) => void
}

export function MemoryFilters({ filters, onChange }: MemoryFiltersProps) {
  const update = (key: keyof MemoryFilterValues, value: string) =>
    onChange({ ...filters, [key]: value })

  const reset = () =>
    onChange({ search: '', memory_type: '', source_type: '', start_date: '', end_date: '' })

  const hasFilters = Object.values(filters).some(Boolean)

  return (
    <div className="flex flex-wrap gap-2 items-end">
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search memories..."
          value={filters.search}
          onChange={e => update('search', e.target.value)}
          className="pl-8"
        />
      </div>
      <Select value={filters.memory_type || 'all'} onValueChange={v => update('memory_type', v === 'all' ? '' : v)}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          <SelectItem value="fact">Fact</SelectItem>
          <SelectItem value="commitment">Commitment</SelectItem>
          <SelectItem value="task">Task</SelectItem>
          <SelectItem value="event">Event</SelectItem>
          <SelectItem value="preference">Preference</SelectItem>
          <SelectItem value="goal">Goal</SelectItem>
          <SelectItem value="insight">Insight</SelectItem>
        </SelectContent>
      </Select>
      <Select value={filters.source_type || 'all'} onValueChange={v => update('source_type', v === 'all' ? '' : v)}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Source" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Sources</SelectItem>
          <SelectItem value="gmail">Gmail</SelectItem>
          <SelectItem value="calendar">Calendar</SelectItem>
          <SelectItem value="notion">Notion</SelectItem>
          <SelectItem value="notes">Notes</SelectItem>
          <SelectItem value="meeting">Meeting</SelectItem>
          <SelectItem value="manual">Manual</SelectItem>
        </SelectContent>
      </Select>
      <div className="flex gap-2 items-center">
        <Input type="date" value={filters.start_date} onChange={e => update('start_date', e.target.value)} className="w-[140px]" />
        <span className="text-muted-foreground text-sm">to</span>
        <Input type="date" value={filters.end_date} onChange={e => update('end_date', e.target.value)} className="w-[140px]" />
      </div>
      {hasFilters && (
        <Button variant="outline" size="sm" onClick={reset}>
          <X className="h-3.5 w-3.5 mr-1" /> Clear
        </Button>
      )}
    </div>
  )
}
