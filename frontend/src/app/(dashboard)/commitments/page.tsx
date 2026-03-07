'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Commitment, CommitmentStatus } from '@/types'
import { CommitmentCard } from '@/components/dashboard/CommitmentCard'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CheckSquare } from 'lucide-react'

export default function CommitmentsPage() {
  const [commitments, setCommitments] = useState<Commitment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('all')

  const fetchCommitments = async () => {
    setIsLoading(true)
    try {
      const params: Record<string, string> = {}
      if (statusFilter !== 'all') params.status = statusFilter
      const data = await api.commitments.getCommitments(params)
      setCommitments(data.commitments || [])
    } catch (err) { console.error(err) }
    finally { setIsLoading(false) }
  }

  useEffect(() => { fetchCommitments() }, [statusFilter])

  const handleUpdateStatus = async (id: string, status: CommitmentStatus) => {
    try { await api.commitments.updateCommitment(id, { status }); fetchCommitments() }
    catch (err) { console.error(err) }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold">Commitments</h1><p className="text-muted-foreground">Track promises and obligations</p></div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="overdue">Overdue</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {isLoading ? <LoadingSpinner /> : commitments.length === 0 ? (
        <EmptyState icon={<CheckSquare className="h-8 w-8" />} title="No commitments found" description="Commitments are extracted automatically from your data." />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {commitments.map(c => <CommitmentCard key={c.id} commitment={c} onUpdateStatus={handleUpdateStatus} />)}
        </div>
      )}
    </div>
  )
}
