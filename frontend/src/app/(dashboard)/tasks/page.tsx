'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Task, TaskStatus, TaskPriority } from '@/types'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CheckSquare2, Plus, Calendar } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { cn } from '@/lib/utils'

const PRIORITY_COLORS: Record<string, string> = { low: 'bg-slate-100 text-slate-700', medium: 'bg-blue-100 text-blue-700', high: 'bg-orange-100 text-orange-700', urgent: 'bg-red-100 text-red-700' }
const STATUS_COLORS: Record<string, string> = { todo: 'bg-gray-100 text-gray-700', in_progress: 'bg-blue-100 text-blue-700', done: 'bg-green-100 text-green-700', cancelled: 'bg-red-100 text-red-700' }

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [newTitle, setNewTitle] = useState('')

  const fetchTasks = async () => {
    setIsLoading(true)
    try { const data = await api.tasks.getTasks(); setTasks(data.tasks || []) }
    catch (err) { console.error(err) }
    finally { setIsLoading(false) }
  }

  useEffect(() => { fetchTasks() }, [])

  const handleCreate = async () => {
    if (!newTitle.trim()) return
    try { await api.tasks.createTask({ title: newTitle.trim(), priority: 'medium' as TaskPriority }); setNewTitle(''); fetchTasks() }
    catch (err) { console.error(err) }
  }

  const handleUpdate = async (id: string, status: TaskStatus) => {
    try { await api.tasks.updateTask(id, { status }); fetchTasks() }
    catch (err) { console.error(err) }
  }

  return (
    <div className="space-y-4">
      <div><h1 className="text-2xl font-bold">Tasks</h1><p className="text-muted-foreground">Manage extracted and manual tasks</p></div>
      <div className="flex gap-2">
        <Input placeholder="Add a new task..." value={newTitle} onChange={e => setNewTitle(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleCreate()} className="flex-1" />
        <Button onClick={handleCreate} disabled={!newTitle.trim()}><Plus className="h-4 w-4 mr-1" /> Add Task</Button>
      </div>
      {isLoading ? <LoadingSpinner /> : tasks.length === 0 ? (
        <EmptyState icon={<CheckSquare2 className="h-8 w-8" />} title="No tasks yet" description="Tasks are extracted automatically or add them manually." />
      ) : (
        <div className="space-y-2">
          {tasks.map(task => (
            <Card key={task.id}><CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className={cn('text-sm font-medium', task.status === 'done' && 'line-through text-muted-foreground')}>{task.title}</p>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', PRIORITY_COLORS[task.priority || 'medium'])}>{task.priority}</span>
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', STATUS_COLORS[task.status])}>{task.status.replace('_', ' ')}</span>
                    {task.deadline && <span className="text-xs text-muted-foreground flex items-center gap-1"><Calendar className="h-3 w-3" />{formatDistanceToNow(new Date(task.deadline), { addSuffix: true })}</span>}
                  </div>
                </div>
                <Select value={task.status} onValueChange={v => handleUpdate(task.id, v as TaskStatus)}>
                  <SelectTrigger className="w-[110px] h-8 text-xs"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todo">To Do</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="done">Done</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent></Card>
          ))}
        </div>
      )}
    </div>
  )
}
