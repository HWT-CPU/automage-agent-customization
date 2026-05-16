import { motion } from 'framer-motion'
import heroMockup from '../assets/hero-product-mockup.svg'

interface Props {
  title: string
  subtitle: string
  cards: Array<{ label: string; value: string }>
}

export function HeroSection({ title, subtitle, cards }: Props) {
  return (
    <section className="relative overflow-hidden rounded-[36px] border border-slate-200 bg-white p-8 shadow-[0_30px_80px_rgba(15,23,42,0.12)] md:p-12">
      <div className="absolute -right-28 -top-20 h-80 w-80 rounded-full bg-indigo-300/30 blur-3xl" />
      <div className="absolute -bottom-16 right-32 h-64 w-64 rounded-full bg-cyan-300/20 blur-3xl" />
      <div className="relative grid items-center gap-8 lg:grid-cols-2">
        <div className="space-y-6">
          <p className="inline-flex rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700">{title}</p>
          <h1 className="hero-display-title text-5xl font-semibold leading-[0.95] md:text-6xl lg:text-7xl">
            <span className="block">Agent 时代的组织</span>
            <span className="hero-display-emphasis">运行中枢</span>
          </h1>
          <p className="max-w-xl text-base text-slate-600 md:text-lg">{subtitle}</p>
          <div className="flex flex-wrap gap-3">
            <a href="#dashboard" className="squeeze-btn">
              查看老板控制台
            </a>
            <a href="#workflow" className="squeeze-btn">
              查看闭环流程
            </a>
          </div>
          <div className="flex flex-wrap gap-2 text-sm">
            {['Schema Contract', 'Workflow First', 'Database as Source of Truth'].map((item) => (
              <span key={item} className="rounded-full border border-slate-300 bg-slate-50 px-3 py-1 text-slate-700">
              {item}
            </span>
          ))}
          </div>
        </div>

        <div className="relative">
          <img src={heroMockup} alt="AutoMage-2 产品主视觉" className="w-full rounded-2xl" />
          <div className="pointer-events-none absolute inset-0">
            {cards.map((card, index) => (
              <motion.div
                key={card.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: [0, -6, 0] }}
                transition={{ duration: 4 + index, repeat: Infinity, ease: 'easeInOut' }}
                className={`absolute rounded-xl border bg-white/95 px-3 py-2 text-xs shadow-lg ${
                  index === 0
                    ? 'left-2 top-2 border-cyan-200'
                    : index === 1
                      ? 'right-2 top-12 border-emerald-200'
                      : index === 2
                        ? 'left-8 bottom-12 border-violet-200'
                        : 'right-8 bottom-4 border-rose-200'
                }`}
              >
                <p className="text-slate-500">{card.label}</p>
                <p className="font-semibold text-slate-800">{card.value}</p>
              </motion.div>
            ))}
        </div>
        </div>
      </div>
    </section>
  )
}
