# api_ready_mock_real_env 使用说明

这个目录是在 api_ready_mock 的基础上转换出来的“当前真实环境版”。

适用场景：
- 当前联调目标是本地真实环境 `http://localhost:8000`
- 需要一套不再混用旧 Mock 账号的 JSON 样例

当前统一身份口径：
- Staff: `zhangsan`
- Manager: `lijingli`
- Executive: `chenzong`
- org_id: `org_automage_mvp`
- department_id / dept_id: `dept_mvp_core`
- staff node_id: `staff_agent_mvp_001`
- manager node_id: `manager_agent_mvp_001`
- executive node_id: `executive_agent_boss_001`

说明：
- 这是“参数口径转换版”，不是重新设计过的数据语义版。
- 个别历史描述字段、中文乱码字段、角色说明字段可能仍保留原始 Mock 文案。
- 当前主要目标是让前端不要再因为账号/节点口径错误而误调用真实环境。
