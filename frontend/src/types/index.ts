// ─── User ─────────────────────────────────────────────────────────────────────
export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ─── Memory ───────────────────────────────────────────────────────────────────
export type MemoryType =
  | 'conversation'
  | 'document'
  | 'email'
  | 'meeting'
  | 'note'
  | 'task'
  | 'commitment'
  | 'insight'
  | 'other'

export type SourceType =
  | 'gmail'
  | 'slack'
  | 'notion'
  | 'calendar'
  | 'manual'
  | 'api'
  | 'other'

export interface Entity {
  name: string
  type: string
  value?: string
}

export interface Memory {
  id: string
  user_id: string
  content: string
  memory_type: MemoryType
  source_type: SourceType
  source_id?: string
  source_metadata?: Record<string, unknown>
  entities: Entity[]
  embedding_id?: string
  occurred_at?: string
  created_at: string
  updated_at: string
}

// ─── Commitment ────────────────────────────────────────────────────────────────
export type CommitmentStatus = 'pending' | 'completed' | 'overdue' | 'cancelled'

export interface Commitment {
  id: string
  user_id: string
  memory_id?: string
  subject: string
  action: string
  person_name?: string
  person_email?: string
  deadline?: string
  status: CommitmentStatus
  notes?: string
  created_at: string
  updated_at: string
}

// ─── Task ─────────────────────────────────────────────────────────────────────
export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Task {
  id: string
  user_id: string
  memory_id?: string
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  due_date?: string
  tags: string[]
  created_at: string
  updated_at: string
}

// ─── Insight ──────────────────────────────────────────────────────────────────
export type InsightType =
  | 'pattern'
  | 'reminder'
  | 'anomaly'
  | 'recommendation'
  | 'summary'
  | 'connection'

export type InsightUrgency = 'low' | 'medium' | 'high'

export interface Insight {
  id: string
  user_id: string
  insight_type: InsightType
  title: string
  content: string
  related_memory_ids: string[]
  urgency: InsightUrgency
  is_read: boolean
  metadata?: Record<string, unknown>
  created_at: string
  updated_at: string
}

// ─── Source ───────────────────────────────────────────────────────────────────
export type SyncStatus = 'idle' | 'syncing' | 'success' | 'error' | 'never'

export interface Source {
  id: string
  user_id: string
  source_type: SourceType
  display_name: string
  is_active: boolean
  last_sync_at?: string
  sync_status: SyncStatus
  sync_error?: string
  config?: Record<string, unknown>
  created_at: string
  updated_at: string
}

// ─── Query / Chat ─────────────────────────────────────────────────────────────
export interface MemoryReference {
  memory_id: string
  content_excerpt: string
  relevance_score: number
  memory_type: MemoryType
  occurred_at?: string
  source_type: SourceType
}

export interface QueryMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  supporting_memories?: MemoryReference[]
  confidence?: number
  suggested_actions?: string[]
  created_at: string
}

export interface QueryRequest {
  query: string
  conversation_id?: string
  include_sources?: boolean
  max_memories?: number
}

export interface QueryResponse {
  answer: string
  conversation_id: string
  supporting_memories: MemoryReference[]
  confidence: number
  suggested_actions: string[]
  query_time_ms?: number
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
export interface DashboardSummary {
  date: string
  overdue_commitments: number
  pending_commitments: number
  pending_tasks: number
  unread_insights: number
  recent_memories_count: number
  high_urgency_insights: Insight[]
  upcoming_deadlines: Commitment[]
}

export interface TimelineEntry {
  date: string
  memories: Memory[]
}

export interface WeeklyReview {
  week_start: string
  week_end: string
  summary: string
  accomplishments: string[]
  open_loops: string[]
  key_people: string[]
  memory_count: number
  new_commitments: number
  completed_commitments: number
}

// ─── Privacy ──────────────────────────────────────────────────────────────────
export type AuditAction =
  | 'login'
  | 'logout'
  | 'memory_created'
  | 'memory_deleted'
  | 'memory_updated'
  | 'query'
  | 'export'
  | 'delete_all'
  | 'source_connected'
  | 'source_disconnected'

export interface AuditLog {
  id: string
  user_id: string
  action: AuditAction
  resource_type?: string
  resource_id?: string
  metadata?: Record<string, unknown>
  ip_address?: string
  created_at: string
}

// ─── Auth ─────────────────────────────────────────────────────────────────────
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// ─── Pagination ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// ─── Filters ──────────────────────────────────────────────────────────────────
export interface MemoryFilters {
  memory_type?: MemoryType | ''
  source_type?: SourceType | ''
  start_date?: string
  end_date?: string
  search?: string
  page?: number
  page_size?: number
}

export interface CommitmentFilters {
  status?: CommitmentStatus | ''
  page?: number
  page_size?: number
}

export interface TaskFilters {
  status?: TaskStatus | ''
  priority?: TaskPriority | ''
  page?: number
  page_size?: number
}
