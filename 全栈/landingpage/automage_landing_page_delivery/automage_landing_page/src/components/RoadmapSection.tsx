const roadmap = {
  p0: ['老板侧总览', '三层 Agent 闭环', '决策卡片', '任务看板', '风险异常', '联调状态'],
  p1: ['Agent 真接后端', '飞书 / OpenClaw 事件接入', '新员工节点注册', 'Gateway 路由', '更完整权限', '任务回流自动化'],
  p2: ['更完整 Dream', '签名服务', 'Policy Engine', '行业化 Schema', '绩效与组织诊断', '多组织 / 多部门可视化'],
}

export function RoadmapSection() {
  return (
    <section id="roadmap" className="space-y-4 scroll-mt-24">
      <h2 className="section-title">Roadmap</h2>
      <div className="grid gap-3 md:grid-cols-3">
        {Object.entries(roadmap).map(([key, values]) => (
          <div
            key={key}
            className="rounded-2xl border border-slate-200 bg-white p-5 transition-all hover:-translate-y-1 hover:border-indigo-300 hover:shadow-[0_18px_40px_rgba(79,70,229,0.16)]"
          >
            <h3 className="text-lg font-semibold text-slate-900">{key.toUpperCase()}</h3>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
              {values.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}
