import { Spinner } from '@/components/ui/spinner'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
  label?: string
}

export function LoadingSpinner({ className, size = 'md', label = 'Loading…' }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2', className)}>
      <Spinner size={size} className="text-primary" />
      {label && <span className="text-sm text-muted-foreground">{label}</span>}
    </div>
  )
}
