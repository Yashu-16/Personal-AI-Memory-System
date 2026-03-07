import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import { getAccessToken, getRefreshToken, saveTokens, clearTokens } from './auth'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  Memory,
  MemoryFilters,
  Commitment,
  CommitmentFilters,
  CommitmentStatus,
  Task,
  TaskFilters,
  TaskStatus,
  TaskPriority,
  Insight,
  Source,
  SourceType,
  QueryRequest,
  QueryResponse,
  DashboardSummary,
  WeeklyReview,
  TimelineEntry,
  AuditLog,
  PaginatedResponse,
} from '@/types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

// ─── Request interceptor – attach JWT ─────────────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor – handle 401 ────────────────────────────────────────
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: string) => void
  reject: (reason: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token as string)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearTokens()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post<TokenResponse>(`${BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        })
        saveTokens(data.access_token, data.refresh_token)
        processQueue(null, data.access_token)
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        }
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        clearTokens()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/api/auth/login', data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    api.post<TokenResponse>('/api/auth/register', data).then((r) => r.data),

  refreshToken: (refreshToken: string) =>
    api
      .post<TokenResponse>('/api/auth/refresh', { refresh_token: refreshToken })
      .then((r) => r.data),

  getMe: () => api.get<User>('/api/auth/me').then((r) => r.data),

  logout: () => api.post('/api/auth/logout').then((r) => r.data),
}

// ─── Memories ─────────────────────────────────────────────────────────────────
export const memoriesApi = {
  getMemories: (filters: MemoryFilters = {}) =>
    api
      .get<PaginatedResponse<Memory>>('/api/memories', { params: filters })
      .then((r) => r.data),

  getMemory: (id: string) =>
    api.get<Memory>(`/api/memories/${id}`).then((r) => r.data),

  updateMemory: (id: string, data: Partial<Memory>) =>
    api.put<Memory>(`/api/memories/${id}`, data).then((r) => r.data),

  deleteMemory: (id: string) =>
    api.delete(`/api/memories/${id}`).then((r) => r.data),

  searchMemories: (query: string, limit = 20) =>
    api
      .get<Memory[]>('/api/memories/search', { params: { q: query, limit } })
      .then((r) => r.data),
}

// ─── Query ────────────────────────────────────────────────────────────────────
export const queryApi = {
  sendQuery: (data: QueryRequest) =>
    api.post<QueryResponse>('/api/query', data).then((r) => r.data),
}

// ─── Sources ──────────────────────────────────────────────────────────────────
export const sourcesApi = {
  getSources: () =>
    api.get<Source[]>('/api/sources').then((r) => r.data),

  connectSource: (sourceType: SourceType, config: Record<string, unknown>) =>
    api.post<Source>('/api/sources', { source_type: sourceType, config }).then((r) => r.data),

  disconnectSource: (id: string) =>
    api.delete(`/api/sources/${id}`).then((r) => r.data),

  syncSource: (id: string) =>
    api.post<Source>(`/api/sources/${id}/sync`).then((r) => r.data),
}

// ─── Commitments ──────────────────────────────────────────────────────────────
export const commitmentsApi = {
  getCommitments: (filters: CommitmentFilters = {}) =>
    api
      .get<PaginatedResponse<Commitment>>('/api/commitments', { params: filters })
      .then((r) => r.data),

  updateCommitment: (id: string, status: CommitmentStatus) =>
    api.put<Commitment>(`/api/commitments/${id}`, { status }).then((r) => r.data),
}

// ─── Tasks ────────────────────────────────────────────────────────────────────
export const tasksApi = {
  getTasks: (filters: TaskFilters = {}) =>
    api.get<PaginatedResponse<Task>>('/api/tasks', { params: filters }).then((r) => r.data),

  createTask: (data: {
    title: string
    description?: string
    priority?: TaskPriority
    due_date?: string
    tags?: string[]
  }) => api.post<Task>('/api/tasks', data).then((r) => r.data),

  updateTask: (id: string, data: { status?: TaskStatus; priority?: TaskPriority; title?: string; description?: string; due_date?: string }) =>
    api.put<Task>(`/api/tasks/${id}`, data).then((r) => r.data),
}

// ─── Insights ─────────────────────────────────────────────────────────────────
export const insightsApi = {
  getInsights: (page = 1, pageSize = 20) =>
    api
      .get<PaginatedResponse<Insight>>('/api/insights', { params: { page, page_size: pageSize } })
      .then((r) => r.data),

  markInsightRead: (id: string) =>
    api.put<Insight>(`/api/insights/${id}/read`).then((r) => r.data),
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
export const dashboardApi = {
  getDashboardSummary: () =>
    api.get<DashboardSummary>('/api/dashboard/summary').then((r) => r.data),

  getWeeklyReview: () =>
    api.get<WeeklyReview>('/api/dashboard/weekly-review').then((r) => r.data),

  getTimeline: (days = 7) =>
    api
      .get<TimelineEntry[]>('/api/dashboard/timeline', { params: { days } })
      .then((r) => r.data),
}

// ─── Privacy ──────────────────────────────────────────────────────────────────
export const privacyApi = {
  deleteAllData: () =>
    api.delete('/api/privacy/data').then((r) => r.data),

  exportData: () =>
    api.get<Blob>('/api/privacy/export', { responseType: 'blob' }).then((r) => r.data),

  getAuditLog: (page = 1, pageSize = 50) =>
    api
      .get<PaginatedResponse<AuditLog>>('/api/privacy/audit-log', {
        params: { page, page_size: pageSize },
      })
      .then((r) => r.data),
}

export default api
