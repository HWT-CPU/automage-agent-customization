import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'

interface User {
  id: string
  username: string
  display_name: string
  role: 'staff' | 'manager' | 'executive'
  level: string
  department_id: string
  org_id: string
  meta?: Record<string, unknown>
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  getToken: () => string | null
}

const AuthContext = createContext<AuthContextType | null>(null)

const TOKEN_KEY = 'automage_access_token'
const REFRESH_KEY = 'automage_refresh_token'
const USER_KEY = 'automage_user'

function getStoredAuth(): AuthState {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const refreshToken = localStorage.getItem(REFRESH_KEY)
    const userJson = localStorage.getItem(USER_KEY)
    const user = userJson ? (JSON.parse(userJson) as User) : null
    return {
      user,
      token,
      refreshToken,
      isAuthenticated: !!token && !!user,
      isLoading: false,
    }
  } catch {
    return { user: null, token: null, refreshToken: null, isAuthenticated: false, isLoading: false }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => ({ ...getStoredAuth(), isLoading: true }))

  useEffect(() => {
    const stored = getStoredAuth()
    if (stored.isAuthenticated) {
      // Validate token on mount
      fetch(`${import.meta.env.VITE_AUTOMAGE_API_BASE || ''}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${stored.token}` },
      })
        .then((r) => {
          if (!r.ok) throw new Error('Token invalid')
          return r.json()
        })
        .then((d) => {
          if (d.code === 200) setState({ ...stored, isLoading: false })
          else throw new Error('Token invalid')
        })
        .catch(() => {
          localStorage.removeItem(TOKEN_KEY)
          localStorage.removeItem(REFRESH_KEY)
          localStorage.removeItem(USER_KEY)
          setState({ user: null, token: null, refreshToken: null, isAuthenticated: false, isLoading: false })
        })
    } else {
      setState((s) => ({ ...s, isLoading: false }))
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const apiBase = import.meta.env.VITE_AUTOMAGE_API_BASE || ''
    const res = await fetch(`${apiBase}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '登录失败' }))
      throw new Error(err.detail || '登录失败')
    }

    const json = await res.json()
    const data = json.data
    const user: User = data.user
    const token = data.access_token
    const refreshToken = data.refresh_token

    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(REFRESH_KEY, refreshToken)
    localStorage.setItem(USER_KEY, JSON.stringify(user))

    setState({ user, token, refreshToken, isAuthenticated: true, isLoading: false })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USER_KEY)
    setState({ user: null, token: null, refreshToken: null, isAuthenticated: false, isLoading: false })
  }, [])

  const getToken = useCallback(() => state.token, [state.token])

  return (
    <AuthContext.Provider value={{ ...state, login, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
