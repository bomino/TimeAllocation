import { create } from 'zustand'
import type { User } from '@/types/user'
import apiClient, { setTokens, clearTokens, loadRefreshToken } from '@/lib/api-client'
import type { LoginCredentials, LoginResponse } from '@/types/user'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  fetchUser: () => Promise<void>
  initAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login/', credentials)
      const { access, refresh, user } = response.data
      setTokens(access, refresh)
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  logout: async () => {
    try {
      const refreshToken = loadRefreshToken()
      if (refreshToken) {
        await apiClient.post('/auth/logout/', { refresh: refreshToken })
      }
    } catch {
      // Ignore logout errors
    } finally {
      clearTokens()
      set({ user: null, isAuthenticated: false })
    }
  },

  refreshToken: async () => {
    const refreshToken = loadRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token')
    }
    const response = await apiClient.post('/auth/refresh/', { refresh: refreshToken })
    const { access, refresh } = response.data
    setTokens(access, refresh)
  },

  fetchUser: async () => {
    try {
      const response = await apiClient.get<User>('/users/me/')
      set({ user: response.data, isAuthenticated: true })
    } catch {
      clearTokens()
      set({ user: null, isAuthenticated: false })
    }
  },

  initAuth: async () => {
    set({ isLoading: true })
    const refreshToken = loadRefreshToken()
    if (!refreshToken) {
      set({ isLoading: false })
      return
    }
    try {
      await get().refreshToken()
      await get().fetchUser()
    } catch {
      clearTokens()
      set({ user: null, isAuthenticated: false })
    } finally {
      set({ isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
