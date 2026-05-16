import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Building2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showForgot, setShowForgot] = useState(false)
  const [forgotUsername, setForgotUsername] = useState('')
  const [forgotMsg, setForgotMsg] = useState('')
  const [forgotLoading, setForgotLoading] = useState(false)

  if (user) {
    navigate('/', { replace: true })
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  const requestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setForgotLoading(true)
    try {
      const res = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: forgotUsername }),
      })
      const d = await res.json()
      setForgotMsg(d.msg || d.detail || '已发送')
    } catch {
      setForgotMsg('网络错误')
    } finally {
      setForgotLoading(false)
    }
  }

  if (showForgot) {
    return (
      <div className="login-bg flex min-h-screen items-center justify-center px-4">
        <div className="panel w-full max-w-sm p-8">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">重置密码</h2>
          <form onSubmit={requestReset} className="space-y-4">
            <input
              className="input"
              value={forgotUsername}
              onChange={(e) => setForgotUsername(e.target.value)}
              placeholder="用户名"
              required
            />
            <button type="submit" disabled={forgotLoading} className="btn-primary w-full">
              {forgotLoading ? '请求中…' : '获取重置令牌'}
            </button>
            {forgotMsg && <p className="text-sm text-slate-600">{forgotMsg}</p>}
          </form>
          <button type="button" onClick={() => setShowForgot(false)} className="btn-ghost mt-4 w-full">
            返回登录
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="login-bg flex min-h-screen items-center justify-center px-4">
      <div className="panel w-full max-w-md p-10">
        <div className="mb-8 flex gap-4 border-b border-slate-100 pb-8">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white">
            <Building2 className="h-6 w-6" strokeWidth={1.5} aria-hidden />
          </span>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-slate-900">AutoMage Data Console</h1>
            <p className="mt-1 text-sm leading-relaxed text-slate-500">数据中台 · 组织运行与合规控制台</p>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">用户名</label>
            <input
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
              autoComplete="username"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">密码</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? '登录中…' : '登录'}
          </button>
        </form>
        <div className="mt-6 flex justify-between text-xs">
          <button type="button" onClick={() => setShowForgot(true)} className="link font-medium no-underline hover:underline">
            忘记密码？
          </button>
          <Link to="/register" className="link font-medium no-underline hover:underline">
            员工注册
          </Link>
        </div>
      </div>
    </div>
  )
}
