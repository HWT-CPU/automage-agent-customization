import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { ConfirmDialog } from '../common/ConfirmDialog'

export function TaskUpdateForm({
  taskId,
}: {
  taskId?: string
}) {
  const { identity } = useIdentityStore()
  const queryClient = useQueryClient()
  const [status, setStatus] = useState('in_progress')
  const [comment, setComment] = useState('进展更新（Data Console）')
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)

  const submit = async () => {
    if (!taskId) {
      setMsg('请先在上方看板选择一个 task_id')
      return
    }
    setConfirmOpen(false)
    const res = await apiClient.updateTask(taskId, { status, description: comment }, identity)
    if (res.ok) {
      setMsg('PATCH 成功')
      void queryClient.invalidateQueries({ queryKey: ['tasks'] })
    } else {
      setMsg(res.msg ?? `失败 HTTP ${res.status}`)
    }
  }

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-2">任务更新</p>
      <p className="mb-2 text-xs text-slate-500">PATCH /api/v1/tasks/`{'{'}task_id{'}'}` — 联调样例使用 status: done / in_progress</p>
      <div className="grid gap-2 md:grid-cols-2">
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg border border-slate-200 p-2 text-sm">
          <option value="in_progress">in_progress</option>
          <option value="blocked">blocked</option>
          <option value="done">done</option>
          <option value="pending">pending</option>
        </select>
        <input value={comment} onChange={(e) => setComment(e.target.value)} className="rounded-lg border border-slate-200 p-2 text-sm" placeholder="描述 / 备注" />
      </div>
      <p className="mt-2 text-xs font-mono text-slate-600">当前 task_id: {taskId ?? '（未选择）'}</p>
      <button type="button" className="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white" onClick={() => setConfirmOpen(true)}>
        PATCH 提交（需 Real Write）
      </button>
      {msg ? <p className="mt-2 text-sm text-slate-700">{msg}</p> : null}
      <ConfirmDialog
        open={confirmOpen}
        title="真实写入：更新任务"
        description={`PATCH /api/v1/tasks/${taskId ?? ''}，body: status=${status}。请确认已开启 Real Write。`}
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => void submit()}
      />
    </div>
  )
}
