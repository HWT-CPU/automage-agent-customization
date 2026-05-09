interface Props {
  apiBase: string
}

const columns = [
  {
    title: '产品',
    items: [
      { label: '闭环流程', href: '#workflow' },
      { label: '三层 Agent', href: '#agents' },
      { label: '老板控制台', href: '#dashboard' },
      { label: '老板决策卡', href: '#decision' },
      { label: '任务追踪', href: '#tasks' },
    ],
  },
  {
    title: '解决方案',
    items: [
      { label: '联调状态矩阵', href: '#integration-status' },
      { label: '数据可信链路', href: '#integration' },
      { label: '实施路线图', href: '#roadmap' },
    ],
  },
  {
    title: '资源',
    items: [
      { label: 'GitHub 仓库（待替换）', href: '#' },
      { label: '项目交付目录（待替换）', href: '#' },
      { label: '接口健康检查', href: '#integration-status' },
    ],
  },
  {
    title: '公司',
    items: [
      { label: '关于 AutoMage', href: '#dashboard' },
      { label: '联系邮箱（待补充）', href: '#' },
      { label: '商务电话（待补充）', href: '#' },
      { label: '办公地址（待补充）', href: '#' },
    ],
  },
  {
    title: '法务',
    items: [
      { label: '隐私政策（待补充）', href: '#' },
      { label: '服务条款（待补充）', href: '#' },
      { label: '数据处理协议 DPA（待补充）', href: '#' },
      { label: '安全与合规说明', href: '#integration' },
    ],
  },
]

export function PremiumFooter({ apiBase }: Props) {
  return (
    <footer className="true-footer mt-14 text-slate-300">
      <div className="true-footer-inner px-4 pb-6 pt-16 md:px-10 md:pt-20">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_2.4fr]">
          <div>
            <p className="text-2xl font-semibold text-white">AutoMage-2</p>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              AutoMage 企业级组织运行系统。<br />
              覆盖日报采集、管理归并、老板决策与任务回流，帮助组织建立可追踪、可验证、可审计的数据闭环。
            </p>
            <p className="mt-4 text-xs text-slate-400">API Base: {apiBase}</p>
            <div className="mt-5 flex flex-wrap gap-3 text-xs">
              <a href="#" className="text-slate-300 transition hover:text-white">
                联系邮箱：待补充
              </a>
              <a href="#" className="text-slate-300 transition hover:text-white">
                商务电话：待补充
              </a>
              <a href="#" className="text-slate-300 transition hover:text-white">
                外链地址：待补充
              </a>
            </div>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
            {columns.map((col) => (
              <div key={col.title}>
                <p className="text-sm font-semibold text-white">{col.title}</p>
                <ul className="mt-3 space-y-2 text-sm">
                  {col.items.map((item) => (
                    <li key={item.label}>
                      <a
                        href={item.href}
                        className="text-slate-400 transition hover:text-white"
                        target={item.href.startsWith('http') ? '_blank' : undefined}
                        rel={item.href.startsWith('http') ? 'noreferrer' : undefined}
                      >
                        {item.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="border-t border-slate-800/60 px-4 py-4 text-xs text-slate-400 md:px-10">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <p>© 2026 AutoMage Technologies. All rights reserved.</p>
          <div className="flex flex-wrap gap-3">
            <a className="hover:text-white" href="#">
              ICP 备案号：待补充
            </a>
            <a className="hover:text-white" href="#">
              公网安备号：待补充
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
