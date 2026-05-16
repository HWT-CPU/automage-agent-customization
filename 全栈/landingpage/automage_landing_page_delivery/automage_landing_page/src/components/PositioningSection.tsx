export function PositioningSection() {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white px-6 py-14 text-center shadow-[0_20px_45px_rgba(15,23,42,0.08)] md:px-12">
      <p className="mx-auto max-w-5xl text-2xl font-semibold leading-relaxed text-slate-900 md:text-4xl">
        AutoMage-2 不是让 AI 直接替代管理者，而是把组织运行中的事实、判断、决策和执行变成可验证的数据链路。
      </p>
      <div className="mt-10 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-left">
          <p className="text-sm font-semibold text-slate-900">Staff 产生一线事实</p>
          <p className="mt-2 text-sm text-slate-600">从一线事实到老板决策，不再靠层层转述。</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-left">
          <p className="text-sm font-semibold text-slate-900">Manager 归并判断</p>
          <p className="mt-2 text-sm text-slate-600">聚合风险、阻塞与依赖，减少噪声上推。</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-left">
          <p className="text-sm font-semibold text-slate-900">Executive 确认关键选择</p>
          <p className="mt-2 text-sm text-slate-600">决策确认后自动转为可追踪任务并回流。</p>
        </div>
      </div>
    </section>
  )
}
