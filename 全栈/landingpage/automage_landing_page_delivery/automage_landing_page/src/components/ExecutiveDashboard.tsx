import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import dashboardPreview from '../assets/dashboard-preview-dark.svg'

interface Card {
  title: string
  value: string
  tone: 'green' | 'yellow' | 'red'
  description: string
}

interface Props {
  cards: Card[]
  taskStats: Array<{ name: string; value: number }>
}

export function ExecutiveDashboard({ cards, taskStats }: Props) {
  const walletCards = cards.slice(0, 3)

  return (
    <section id="dashboard" className="space-y-4 scroll-mt-24">
      <h2 className="section-title">老板侧 P0 Dashboard</h2>
      <p className="text-sm text-slate-600">深色控制台作为产品截图嵌入页面，保留老板每日关注的核心决策与风险状态。</p>

      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white p-3 shadow-[0_24px_50px_rgba(15,23,42,0.12)]">
        <img src={dashboardPreview} alt="老板侧深色控制台预览" className="w-full rounded-2xl" />
      </div>

      <div className="exec-wallet-wrap">
        <div className="exec-wallet">
          <div className="exec-wallet-back" />

          {walletCards.map((item, index) => (
            <div
              key={item.title}
              className={`exec-wallet-card ${index === 0 ? 'exec-stripe' : index === 1 ? 'exec-wise' : 'exec-paypal'}`}
            >
              <div className="exec-wallet-card-inner">
                <div className="exec-wallet-card-top">
                  <span>{item.title}</span>
                  <div className="exec-wallet-chip" />
                </div>
                <div className="exec-wallet-card-bottom">
                  <div className="exec-wallet-card-info">
                    <span className="label">Status</span>
                    <span className="value">{item.description}</span>
                  </div>
                  <div className="exec-wallet-number-wrapper">
                    <span className="hidden-stars">****</span>
                    <span className="card-number">{item.value}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          <div className="exec-wallet-pocket">
            <svg className="exec-wallet-pocket-svg" viewBox="0 0 280 160" fill="none">
              <path
                d="M 0 20 C 0 10, 5 10, 10 10 C 20 10, 25 25, 40 25 L 240 25 C 255 25, 260 10, 270 10 C 275 10, 280 10, 280 20 L 280 120 C 280 155, 260 160, 240 160 L 40 160 C 20 160, 0 155, 0 120 Z"
                fill="#1e341e"
              />
              <path
                d="M 8 22 C 8 16, 12 16, 15 16 C 23 16, 27 29, 40 29 L 240 29 C 253 29, 257 16, 265 16 C 268 16, 272 16, 272 22 L 272 120 C 272 150, 255 152, 240 152 L 40 152 C 25 152, 8 152, 8 120 Z"
                stroke="#3d5635"
                strokeWidth="1.5"
                strokeDasharray="6 4"
              />
            </svg>
            <div className="exec-wallet-pocket-content">
              <div className="relative h-6 w-full">
                <div className="exec-wallet-balance-stars">******</div>
                <div className="exec-wallet-balance-real">{walletCards[0]?.value ?? 'N/A'}</div>
              </div>
              <div className="exec-wallet-balance-label">Executive Focus</div>
              <div className="exec-wallet-eye-wrapper">
                <svg className="exec-wallet-eye eye-slash" width="20" height="20" viewBox="0 0 24 24" fill="none" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                  <line x1="3" y1="3" x2="21" y2="21" />
                </svg>
                <svg className="exec-wallet-eye eye-open" width="20" height="20" viewBox="0 0 24 24" fill="none" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="h-64 rounded-2xl border border-slate-200 bg-white p-4">
        <p className="mb-3 text-sm text-slate-700">今日任务状态分布</p>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={taskStats}>
            <XAxis dataKey="name" stroke="#475569" />
            <YAxis stroke="#475569" allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="value" fill="#38bdf8" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
