'use client'

import { BookOpen, CheckSquare, Lightbulb, ListTodo } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { DashboardSummary } from '@/types'

interface StatsOverviewProps {
  summary: DashboardSummary
}

const stats = (summary: DashboardSummary) => [
  {
    label: 'Recent Memories',
    value: summary.recent_memories_count,
    icon: BookOpen,
    color: 'text-blue-500',
  },
  {
    label: 'Commitments',
    value: summary.pending_commitments,
    icon: CheckSquare,
    color: 'text-orange-500',
  },
  {
    label: 'Pending Tasks',
    value: summary.pending_tasks,
    icon: ListTodo,
    color: 'text-purple-500',
  },
  {
    label: 'Insights',
    value: summary.unread_insights,
    icon: Lightbulb,
    color: 'text-yellow-500',
  },
]

export function StatsOverview({ summary }: StatsOverviewProps) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {stats(summary).map(({ label, value, icon: Icon, color }) => (
        <Card key={label}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
            <Icon className={`h-5 w-5 ${color}`} />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
