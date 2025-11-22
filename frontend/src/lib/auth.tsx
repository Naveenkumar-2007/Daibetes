import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { authAPI } from './api'

interface User {
  user_id: string
  username: string
  full_name: string
  email?: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const response = await authAPI.getSession()
      if (response.data.authenticated) {
        setUser(response.data.user)
      } else {
        setUser(null)
      }
    } catch (error) {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await authAPI.login(username, password)
    if (response.data.success) {
      await checkAuth()
    } else {
      throw new Error(response.data.message || 'Login failed')
    }
  }

  const logout = async () => {
    await authAPI.logout()
    setUser(null)
  }

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
