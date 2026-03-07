'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { WeeklyReview } from '@/types'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState } from '@/components/common/EmptyState'
import { BookOpen, CheckCircle, AlertCircle, Target } from 'lucide-react'

export default function WeeklyReviewPage() {
  const [review, setReview] = useState<WeeklyReview | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    api.dashboard.getWeeklyReview().then(setReview).catch(console.error).finally(() => setIsLoading(false))
  }, [])

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-4 max-w-3xl">
      <div><h1 className="text-2xl font-bold">Weekly Review</h1><p className="text-muted-foreground">Your AI-generated weekly summary</p></div>
      {!review ? (
        <EmptyState icon={<BookOpen className="h-8 w-8" />} title="No weekly review yet" description="Weekly reviews are generated automatically after enough data." />
      ) : (
        <div className="space-y-4">
          {review.summary && (
            <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base"><BookOpen className="h-5 w-5 text-primary" /> Week Summary</CardTitle></CardHeader>
              <CardContent><p className="text-sm">{review.summary}</p></CardContent></Card>
          )}
          {review.accomplishments && review.accomplishments.length > 0 && (
            <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base text-green-700"><CheckCircle className="h-5 w-5" /> Accomplishments</CardTitle></CardHeader>
              <CardContent><ul className="space-y-1">{review.accomplishments.map((item, i) => (
                <li key={i} className="text-sm flex items-start gap-2"><CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />{item}</li>
              ))}</ul></CardContent></Card>
          )}
          {review.open_loops && review.open_loops.length > 0 && (
            <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base text-orange-700"><AlertCircle className="h-5 w-5" /> Open Loops</CardTitle></CardHeader>
              <CardContent><ul className="space-y-1">{review.open_loops.map((item, i) => (
                <li key={i} className="text-sm flex items-start gap-2"><AlertCircle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />{item}</li>
              ))}</ul></CardContent></Card>
          )}
          {review.priorities_next_week && review.priorities_next_week.length > 0 && (
            <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base text-blue-700"><Target className="h-5 w-5" /> Priorities for Next Week</CardTitle></CardHeader>
              <CardContent><ul className="space-y-1">{review.priorities_next_week.map((item, i) => (
                <li key={i} className="text-sm flex items-start gap-2">
                  <span className="h-4 w-4 rounded-full bg-blue-100 text-blue-700 text-xs flex items-center justify-center font-medium flex-shrink-0 mt-0.5">{i + 1}</span>{item}
                </li>
              ))}</ul></CardContent></Card>
          )}
        </div>
      )}
    </div>
  )
}
