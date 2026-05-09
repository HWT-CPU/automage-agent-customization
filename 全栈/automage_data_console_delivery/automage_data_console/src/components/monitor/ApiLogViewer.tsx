import { useRuntimeStore } from '../../store/useRuntimeStore'

export function ApiLogViewer() {
  const { apiLogs } = useRuntimeStore()
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">请求日志</p>
      <div className="max-h-72 overflow-auto">
        <table className="min-w-full text-left text-xs">
          <thead className="text-slate-500">
            <tr>
              <th className="pb-2">time</th>
              <th className="pb-2">method</th>
              <th className="pb-2">path</th>
              <th className="pb-2">status</th>
              <th className="pb-2">request_id</th>
              <th className="pb-2">idempotency_key</th>
              <th className="pb-2">fallback</th>
            </tr>
          </thead>
          <tbody>
            {apiLogs.map((log) => (
              <tr key={`${log.requestId}-${log.path}`} className="border-t border-slate-200/70">
                <td className="py-1">{log.timestamp.slice(11, 19)}</td>
                <td className="py-1">{log.method}</td>
                <td className="py-1">{log.path}</td>
                <td className="py-1">{log.status}</td>
                <td className="py-1">{log.requestId}</td>
                <td className="py-1">{log.idempotencyKey}</td>
                <td className="py-1">{String(log.fallback)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
