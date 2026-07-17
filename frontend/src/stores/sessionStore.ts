import { create } from 'zustand'
import { Session, ActionResponse } from '../types'

interface SessionStore {
  sessions: Session[]
  currentSession: Session | null
  actions: ActionResponse[]
  loading: boolean
  error: string | null

  setSessions: (sessions: Session[]) => void
  setCurrentSession: (session: Session | null) => void
  addAction: (action: ActionResponse) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessions: [],
  currentSession: null,
  actions: [],
  loading: false,
  error: null,

  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (currentSession) => set({ currentSession }),
  addAction: (action) =>
    set((state) => ({
      actions: [...state.actions, action],
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}))
