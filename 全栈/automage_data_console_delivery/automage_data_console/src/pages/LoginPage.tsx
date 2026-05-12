import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
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
    const role = user.role
    navigate(role === 'executive' ? '/executive' : role === 'manager' ? '/manager' : '/staff', { replace: true })
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      const stored = localStorage.getItem('automage_user')
      const u = stored ? JSON.parse(stored) : null
      navigate(u?.role === 'executive' ? '/executive' : u?.role === 'manager' ? '/manager' : '/staff', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally { setLoading(false) }
  }

  const requestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setForgotLoading(true)
    try {
      const res = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: forgotUsername }),
      })
      const d = await res.json()
      setForgotMsg(d.msg || d.detail || '已发送')
    } catch { setForgotMsg('网络错误') }
    finally { setForgotLoading(false) }
  }

  if (showForgot) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="w-full max-w-sm panel p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">重置密码</h2>
          <form onSubmit={requestReset} className="space-y-4">
            <input className="input" value={forgotUsername} onChange={e => setForgotUsername(e.target.value)} placeholder="用户名" required />
            <button type="submit" disabled={forgotLoading} className="btn-primary w-full">{forgotLoading ? '请求中...' : '获取重置令牌'}</button>
            {forgotMsg && <p className="text-sm text-gray-500">{forgotMsg}</p>}
          </form>
          <button onClick={() => setShowForgot(false)} className="btn-ghost w-full mt-4">返回登录</button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm panel p-8">
        <div className="mb-8">
          <p className="text-sm font-semibold text-gray-900 tracking-tight">AutoMage</p>
          <p className="text-sm text-gray-500 mt-1">数据中台 · 组织运行控制台</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="input" value={username} onChange={e => setUsername(e.target.value)} placeholder="用户名" autoFocus required />
          <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="密码" required />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? '登录中...' : '登录'}</button>
        </form>
        <div className="flex justify-between mt-4 text-xs">
          <button onClick={() => setShowForgot(true)} className="text-gray-400 hover:text-indigo-600">忘记密码？</button>
          <Link to="/register" className="text-gray-400 hover:text-indigo-600">员工注册</Link>
        </div>
      </div>
    </div>
  )
}
