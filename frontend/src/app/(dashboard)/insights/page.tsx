'use client'
import { useInsights } from '@/hooks/useInsights'
import { InsightCard } from '@/components/dashboard/InsightCard'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Lightbulb } from 'lucide-react'

export default function InsightsPage() {
  const { insights, isLoading, markAsRead } = useInsights()

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Insights</h1>
        <p className="text-muted-foreground">Proactive intelligence from your memory system</p>
      </div>
      {isLoading ? <LoadingSpinner /> : insights.length === 0 ? (
        <EmptyState icon={<Lightbulb className="h-8 w-8" />} title="No insights yet" description="Insights are generated automatically as you add more data." />
      ) : (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {insights.map(insight => <InsightCard key={insight.id} insight={insight} onMarkRead={markAsRead} />)}
        </div>
      )}
    </div>
  )
}
