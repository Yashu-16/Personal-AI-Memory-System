'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Source } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { RefreshCw, Unplug, Mail, Calendar, FileText, Mic, BookOpen } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const SOURCE_ICONS: Record<string, React.ReactNode> = {
  gmail: <Mail className="h-5 w-5" />,
  calendar: <Calendar className="h-5 w-5" />,
  notion: <BookOpen className="h-5 w-5" />,
  notes: <FileText className="h-5 w-5" />,
  meeting: <Mic className="h-5 w-5" />,
}

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [syncingId, setSyncingId] = useState<string | null>(null)

  const fetchSources = async () => {
    setIsLoading(true)
    try { const data = await api.sources.getSources(); setSources(data.sources || []) }
    catch (err) { console.error(err) }
    finally { setIsLoading(false) }
  }

  useEffect(() => { fetchSources() }, [])

  const handleSync = async (id: string) => {
    setSyncingId(id)
    try { await api.sources.syncSource(id) }
    catch (err) { console.error(err) }
    finally { setSyncingId(null) }
  }

  const handleDisconnect = async (id: string) => {
    if (!confirm('Disconnect this source?')) return
    try { await api.sources.disconnectSource(id); fetchSources() }
    catch (err) { console.error(err) }
  }

  return (
    <div className="space-y-4">
      <div><h1 className="text-2xl font-bold">Data Sources</h1><p className="text-muted-foreground">Manage connected data sources</p></div>
      {isLoading ? <LoadingSpinner /> : sources.length === 0 ? (
        <EmptyState icon={<FileText className="h-8 w-8" />} title="No sources connected" description="Connect Gmail, Google Calendar, Notion, or other sources." />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {sources.map(source => (
            <Card key={source.id}><CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-muted">{SOURCE_ICONS[source.source_type] || <FileText className="h-5 w-5" />}</div>
                  <div>
                    <p className="font-medium capitalize">{source.source_type}</p>
                    <p className="text-xs text-muted-foreground">{source.last_sync_at ? `Synced ${formatDistanceToNow(new Date(source.last_sync_at), { addSuffix: true })}` : 'Never synced'}</p>
                  </div>
                </div>
                <Badge variant={source.is_active ? 'default' : 'secondary'}>{source.is_active ? 'Active' : 'Inactive'}</Badge>
              </div>
              <div className="flex gap-2 mt-3">
                <Button variant="outline" size="sm" onClick={() => handleSync(source.id)} disabled={syncingId === source.id}>
                  <RefreshCw className={`h-3.5 w-3.5 mr-1 ${syncingId === source.id ? 'animate-spin' : ''}`} /> Sync
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleDisconnect(source.id)} className="text-destructive hover:text-destructive">
                  <Unplug className="h-3.5 w-3.5 mr-1" /> Disconnect
                </Button>
              </div>
            </CardContent></Card>
          ))}
        </div>
      )}
    </div>
  )
}
