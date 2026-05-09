interface Props {
  open: boolean
  title: string
  description: string
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({ open, title, description, onCancel, onConfirm }: Props) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/30 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-5 shadow-xl">
        <p className="text-lg font-semibold text-slate-900">{title}</p>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
        <div className="mt-4 flex justify-end gap-2">
          <button type="button" onClick={onCancel} className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
            取消
          </button>
          <button type="button" onClick={onConfirm} className="rounded-lg bg-rose-600 px-3 py-2 text-sm text-white">
            确认执行
          </button>
        </div>
      </div>
    </div>
  )
}
