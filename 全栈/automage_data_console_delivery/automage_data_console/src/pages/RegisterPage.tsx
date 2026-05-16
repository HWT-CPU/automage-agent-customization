import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Building2, CheckCircle2, QrCode, UserPlus } from 'lucide-react'

export function RegisterPage() {
  const [step, setStep] = useState<'form' | 'qrcode' | 'done'>('form')
  const [form, setForm] = useState({
    username: '',
    password: '',
    display_name: '',
    phone: '',
    job_title: '',
    department_id: 'dept_mvp_core',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [userId, setUserId] = useState<string | null>(null)
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null)

  const checkUsername = async (username: string) => {
    if (username.length < 2) {
      setUsernameAvailable(null)
      return
    }
    try {
      const res = await fetch(`/api/v1/onboarding/check-username?username=${encodeURIComponent(username)}`)
      const d = await res.json()
      setUsernameAvailable(d.data?.available ?? null)
    } catch {
      setUsernameAvailable(null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/v1/onboarding/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const d = await res.json()
      if (!res.ok) throw new Error(d.detail || '注册失败')
      setUserId(d.data?.user_id ?? null)
      setStep('qrcode')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '注册失败')
    } finally {
      setLoading(false)
    }
  }

  const completeOnboarding = async () => {
    if (!userId) return
    setLoading(true)
    try {
      await fetch(`/api/v1/onboarding/${userId}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collected_info: { phone: form.phone, job_title: form.job_title, display_name: form.display_name },
        }),
      })
      setStep('done')
    } catch {
      setError('激活失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const shell = (children: ReactNode) => (
    <div className="login-bg flex min-h-screen items-center justify-center px-4 py-10">{children}</div>
  )

  if (step === 'form') {
    return shell(
      <div className="panel w-full max-w-md p-10">
        <div className="mb-8 flex gap-4 border-b border-slate-100 pb-8">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white">
            <UserPlus className="h-6 w-6" strokeWidth={1.5} aria-hidden />
          </span>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-slate-900">新员工注册</h1>
            <p className="mt-1 text-sm text-slate-500">创建账户后将引导完成飞书绑定与激活</p>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">用户名 *</label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => {
                setForm({ ...form, username: e.target.value })
                checkUsername(e.target.value)
              }}
              className="input"
              required
            />
            {usernameAvailable === false && <p className="mt-1 text-xs text-rose-600">用户名已被使用</p>}
            {usernameAvailable === true && <p className="mt-1 text-xs text-emerald-700">可用</p>}
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">密码 *</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="input"
              required
              minLength={4}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">显示姓名 *</label>
            <input
              type="text"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
              className="input"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">手机号</label>
            <input
              type="tel"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="input"
              placeholder="用于飞书绑定"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">岗位</label>
            <input
              type="text"
              value={form.job_title}
              onChange={(e) => setForm({ ...form, job_title: e.target.value })}
              className="input"
              placeholder="例如：销售专员"
            />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" disabled={loading || usernameAvailable === false} className="btn-primary w-full">
            {loading ? '提交中…' : '下一步：绑定飞书'}
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-slate-500">
          已有账户？{' '}
          <Link to="/login" className="link font-medium text-slate-800 no-underline hover:underline">
            返回登录
          </Link>
        </p>
      </div>,
    )
  }

  if (step === 'qrcode') {
    return shell(
      <div className="panel w-full max-w-lg p-10">
        <div className="mb-6 flex items-start gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700">
            <QrCode className="h-5 w-5" strokeWidth={1.75} aria-hidden />
          </span>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">绑定飞书</h1>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">
              注册信息已保存。请通过飞书联系 <span className="font-medium text-slate-800">墨智</span> 完成入职流程。
            </p>
          </div>
        </div>

        <div className="callout mb-4 text-left">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">方式一 · 扫码添加</p>
          <div className="flex flex-col items-center sm:flex-row sm:items-start sm:gap-6">
            <img
              src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://applink.feishu.cn/client/bot/open?appId=cli_aa8bbf4af4f8dbee"
              alt="飞书扫码添加 Auto01"
              className="h-48 w-48 rounded-lg border border-slate-200 bg-white"
            />
            <p className="mt-3 max-w-xs text-center text-xs text-slate-500 sm:mt-0 sm:text-left">
              打开飞书扫一扫，添加机器人 <span className="font-medium text-slate-700">Auto01</span>
            </p>
          </div>
        </div>

        <div className="callout-warn mb-6 text-left">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-900/80">方式二 · 搜索添加</p>
          <p className="text-sm text-amber-950">在飞书中搜索「Auto01」，发送：</p>
          <code className="mt-2 block rounded border border-amber-200/60 bg-white/80 px-3 py-2 text-xs text-slate-800">
            入职 {form.display_name}，手机号 {form.phone || '未填'}
          </code>
        </div>

        <p className="mb-6 text-center text-xs leading-relaxed text-slate-500">
          墨智将在飞书中确认岗位职责与直属上级等信息，完成后账户自动激活。
        </p>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button type="button" onClick={completeOnboarding} disabled={loading} className="btn-secondary sm:min-w-[10rem]">
            {loading ? '处理中…' : '跳过飞书，直接激活'}
          </button>
          <Link to="/login" className="btn-primary inline-flex justify-center text-center sm:min-w-[10rem]">
            前往登录
          </Link>
        </div>
      </div>,
    )
  }

  return shell(
    <div className="panel w-full max-w-md p-10 text-center">
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/80">
        <CheckCircle2 className="h-7 w-7" strokeWidth={1.75} aria-hidden />
      </div>
      <h1 className="text-lg font-semibold text-slate-900">入职完成</h1>
      <p className="mt-2 text-sm text-slate-600">
        欢迎 <span className="font-medium text-slate-900">{form.display_name}</span>
      </p>
      <p className="mt-2 text-sm text-slate-500">账户已激活，请使用控制台登录。</p>
      <Link to="/login" className="btn-primary mt-8 inline-flex w-full justify-center sm:w-auto sm:min-w-[12rem]">
        <Building2 className="h-4 w-4 opacity-90" aria-hidden />
        前往登录
      </Link>
    </div>,
  )
}
