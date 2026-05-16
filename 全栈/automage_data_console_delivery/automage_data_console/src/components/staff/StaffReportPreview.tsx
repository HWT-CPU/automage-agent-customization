import { JsonViewer } from '../common/JsonViewer'

export function StaffReportPreview({ payload }: { payload: unknown }) {
  return <JsonViewer title="Staff 提交请求/响应快照" data={payload} />
}
