'use client'

import { format, isPast } from 'date-fns'
import { CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { Commitment, CommitmentStatus } from '@/types'
import { cn } from '@/lib/utils'

const statusVariant: Record<CommitmentStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  pending: 'secondary',
  completed: 'default',
  overdue: 'destructive',
  cancelled: 'outline',
}

interface CommitmentCardProps {
  commitment: Commitment
  onUpdate: (id: string, status: CommitmentStatus) => void
}

export function CommitmentCard({ commitment, onUpdate }: CommitmentCardProps) {
  const isOverdue =
    commitment.status === 'overdue' ||
    (commitment.deadline &&
      isPast(new Date(commitment.deadline)) &&
      commitment.status === 'pending')

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="font-semibold">{commitment.subject}</p>
            <p className="text-sm text-muted-foreground">{commitment.action}</p>
          </div>
          <Badge variant={statusVariant[commitment.status]} className="shrink-0 capitalize">
            {commitment.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {commitment.person_name && (
          <p className="text-sm text-muted-foreground">
            Person: <span className="font-medium text-foreground">{commitment.person_name}</span>
          </p>
        )}
        {commitment.deadline && (
          <p
            className={cn(
              'text-sm',
              isOverdue ? 'font-semibold text-red-600' : 'text-muted-foreground'
            )}
          >
            Due: {format(new Date(commitment.deadline), 'MMM d, yyyy')}
            {isOverdue && ' (overdue)'}
          </p>
        )}
        {commitment.status === 'pending' && (
          <Button
            size="sm"
            variant="outline"
            className="mt-1"
            onClick={() => onUpdate(commitment.id, 'completed')}
          >
            <CheckCircle className="mr-1 h-4 w-4" />
            Mark Complete
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
