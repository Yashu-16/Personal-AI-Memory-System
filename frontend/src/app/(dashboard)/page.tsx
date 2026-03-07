'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { DailySummary } from '@/components/dashboard/DailySummary'
import { StatsOverview } from '@/components/dashboard/StatsOverview'
import { InsightCard } from '@/components/dashboard/InsightCard'
import { MemoryTimeline } from '@/components/dashboard/MemoryTimeline'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { DashboardSummary, Insight } from '@/types'
import { Lightbulb } from 'lucide-react'

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryData, insightsData] = await Promise.all([
          api.dashboard.getSummary(),
          api.insights.getInsights({ limit: 3 }),
        ])
        setSummary(summaryData)
        setInsights(insightsData.insights || [])
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Your memory intelligence overview</p>
      </div>
      {summary && <DailySummary summary={summary} />}
      {summary && <StatsOverview summary={summary} />}
      <div>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Recent Insights
        </h2>
        {insights.length === 0 ? (
          <EmptyState icon={<Lightbulb className="h-8 w-8" />} title="No insights yet" description="Connect data sources to start generating insights." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {insights.map(insight => (
              <InsightCard key={insight.id} insight={insight} onMarkRead={() => {}} />
            ))}
          </div>
        )}
      </div>
      {summary?.recent_memories && summary.recent_memories.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Recent Memories</h2>
          <MemoryTimeline memories={summary.recent_memories} />
        </div>
      )}
    </div>
  )
}
