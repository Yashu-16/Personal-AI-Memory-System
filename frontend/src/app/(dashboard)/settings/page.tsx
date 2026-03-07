'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { clearTokens } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { AlertCircle, Download, Trash2, Shield } from 'lucide-react'

export default function SettingsPage() {
  const router = useRouter()
  const [isDeleting, setIsDeleting] = useState(false)
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const data = await api.privacy.exportData()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `memora-export-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) { console.error(err) }
    finally { setIsExporting(false) }
  }

  const handleDelete = async () => {
    if (!confirm('Delete ALL your data? This cannot be undone.')) return
    setIsDeleting(true)
    try { await api.privacy.deleteAllData(); clearTokens(); router.push('/login') }
    catch (err) { console.error(err) }
    finally { setIsDeleting(false) }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div><h1 className="text-2xl font-bold">Settings</h1><p className="text-muted-foreground">Manage your account and privacy settings</p></div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5" /> Privacy &amp; Data</CardTitle>
          <CardDescription>Control your personal data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Export Your Data</p>
              <p className="text-xs text-muted-foreground">Download all your memories and data as JSON</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleExport} disabled={isExporting}>
              <Download className="h-4 w-4 mr-1" />{isExporting ? 'Exporting...' : 'Export'}
            </Button>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-destructive flex items-center gap-1"><AlertCircle className="h-4 w-4" /> Delete All Data</p>
              <p className="text-xs text-muted-foreground">Permanently delete all your memories and account data</p>
            </div>
            <Button variant="destructive" size="sm" onClick={handleDelete} disabled={isDeleting}>
              <Trash2 className="h-4 w-4 mr-1" />{isDeleting ? 'Deleting...' : 'Delete All'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
