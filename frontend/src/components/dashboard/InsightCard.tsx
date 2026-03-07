'use client'

import { Eye, Zap, BookOpen, Bell, TrendingUp, Link2, BarChart2 } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { Insight, InsightType, InsightUrgency } from '@/types'

const typeIcon: Record<InsightType, React.ElementType> = {
  pattern: TrendingUp,
  reminder: Bell,
  anomaly: Zap,
  recommendation: BookOpen,
  summary: BarChart2,
  connection: Link2,
}

const urgencyVariant: Record<InsightUrgency, 'default' | 'secondary' | 'destructive'> = {
  low: 'secondary',
  medium: 'default',
  high: 'destructive',
}

interface InsightCardProps {
  insight: Insight
  onMarkRead: (id: string) => void
}

export function InsightCard({ insight, onMarkRead }: InsightCardProps) {
  const Icon = typeIcon[insight.insight_type]

  return (
    <Card className={insight.is_read ? 'opacity-70' : ''}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
            <p className="font-semibold">{insight.title}</p>
          </div>
          <Badge variant={urgencyVariant[insight.urgency]} className="shrink-0 capitalize">
            {insight.urgency}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm text-muted-foreground line-clamp-3">{insight.content}</p>
        {!insight.is_read && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onMarkRead(insight.id)}
          >
            <Eye className="mr-1 h-4 w-4" />
            Mark Read
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
