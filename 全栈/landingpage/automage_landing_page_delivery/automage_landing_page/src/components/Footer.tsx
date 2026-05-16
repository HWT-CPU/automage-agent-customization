interface Props {
  apiBase: string
}

export function Footer({ apiBase }: Props) {
  return (
    <footer className="mt-10 rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-600">
      <p>
        AutoMage-2 不是让 AI 直接替代管理者，而是把事实、判断、决策和执行变成可验证数据链路。当前为 MVP / P0 展示版。
      </p>
      <p className="mt-2">API Base: {apiBase} ｜ 主风险：manager_cross_dept 当前未拒绝（非阻塞，里程碑三前关闭）。</p>
    </footer>
  )
}
