'use client'

import { format } from 'date-fns'
import { AlertTriangle, CheckSquare, Lightbulb, BookOpen } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { DashboardSummary } from '@/types'

interface DailySummaryProps {
  summary: DashboardSummary
}

export function DailySummary({ summary }: DailySummaryProps) {
  const formattedDate = format(new Date(summary.date), 'EEEE, MMMM d, yyyy')

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium text-muted-foreground">{formattedDate}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {summary.overdue_commitments > 0 && (
          <div className="flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>
              <strong>{summary.overdue_commitments}</strong> overdue commitment
              {summary.overdue_commitments !== 1 ? 's' : ''}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm">
          <CheckSquare className="h-4 w-4 text-muted-foreground shrink-0" />
          <span>
            <strong>{summary.pending_tasks}</strong> pending task
            {summary.pending_tasks !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <Lightbulb className="h-4 w-4 text-muted-foreground shrink-0" />
          <span>
            <strong>{summary.unread_insights}</strong> unread insight
            {summary.unread_insights !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <BookOpen className="h-4 w-4 text-muted-foreground shrink-0" />
          <span>
            <strong>{summary.recent_memories_count}</strong> recent memor
            {summary.recent_memories_count !== 1 ? 'ies' : 'y'}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
