# api_ready_mock 使用说明

这个文件夹里的 JSON 主要服务于：

1. Mock 语义说明
2. 结构参考
3. 样例字段映射

不代表当前本地真实环境必须直接照抄使用。

## 重要提醒

该目录中很多文件仍使用旧示例账号，例如：

- `user_agent_001`
- `user_backend_001`
- `user_manager_001`
- `user_executive_001`

如果当前联调目标是本地真实环境 `http://localhost:8000`，请不要直接照抄这些账号。

当前真实环境统一使用：

- Staff：`zhangsan`
- Manager：`lijingli`
- Executive：`chenzong`

其余统一口径：

- `org_id=org_automage_mvp`
- `department_id / dept_id=dept_mvp_core`
- `staff_agent_mvp_001 -> manager_agent_mvp_001 -> executive_agent_boss_001`

## 建议

如果前端要直接联调真实接口，请优先使用：

- `00_联调统一口径总表.md`
- `10_前端最终联调参数表.md`

而不是直接把这个目录下的旧 Mock JSON 原样发到真实库。
