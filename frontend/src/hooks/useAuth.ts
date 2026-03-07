'use client'

import { create } from 'zustand'
import { authApi } from '@/lib/api'
import { saveTokens, clearTokens } from '@/lib/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

interface AuthActions {
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,
  error: null,

  login: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const tokens = await authApi.login(data)
      saveTokens(tokens.access_token, tokens.refresh_token)
      const user = await authApi.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed'
      set({ isLoading: false, error: message })
      throw err
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const tokens = await authApi.register(data)
      saveTokens(tokens.access_token, tokens.refresh_token)
      const user = await authApi.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed'
      set({ isLoading: false, error: message })
      throw err
    }
  },

  logout: async () => {
    set({ isLoading: true })
    try {
      await authApi.logout()
    } catch {
      // ignore logout errors
    } finally {
      clearTokens()
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  fetchUser: async () => {
    set({ isLoading: true })
    try {
      const user = await authApi.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      clearTokens()
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))

export function useAuth() {
  return useAuthStore()
}
