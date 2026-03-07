import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface ConfidenceBadgeProps {
  score: number
  className?: string
}

export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  const label = `${Math.round(score * 100)}%`

  const colorClass =
    score > 0.8
      ? 'bg-green-100 text-green-800 border-green-200'
      : score > 0.5
      ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
      : 'bg-red-100 text-red-800 border-red-200'

  return (
    <Badge variant="outline" className={cn(colorClass, className)}>
      {label} confidence
    </Badge>
  )
}
