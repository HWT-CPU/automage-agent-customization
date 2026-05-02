# AutoMage Agent 客制化仓库创建建议

## 一、仓库定位

根据会议内容，建议创建一个独立的 Agent 客制化仓库。

这个仓库不应该承载完整后端服务，也不应该承载数据库本体，而是专门用于 AutoMage-2 的 Harness / Hermes 三层 Agent 客制化开发。

推荐定位：

```text
AutoMage-2 三级企业 Agent 客制化模板、user.md 配置、Skill 插件与 IM 决策流仓库。
```

主要包含：

- 一线员工 Agent 模板。
- 业务领导 Agent 模板。
- 公司领导 / 老板 Agent 模板。
- `user.md` 员工个性化配置模板。
- Skill 插件。
- 后端 API Client。
- OpenClaw / 飞书 / IM 适配占位。
- 本地 Mock 端到端演示。

## 二、推荐仓库名

优先推荐：

```text
automage-agent-customization
```

原因：

- 不强绑定 Harness / Hermes 的具体技术名称。
- 能表达“Agent 客制化”的核心定位。
- 后续如果底层 Agent Runtime 变动，仓库名不需要调整。

备选名称：

```text
automage-harness-customization
automage-harness-agent-templates
automage-hermes-agents
automage-agent-templates
```

## 三、GitHub Description 建议

英文描述：

```text
AutoMage-2 three-level enterprise agent customization templates, user.md profiles, skills, and IM integration mock flows.
```

中文理解：

```text
AutoMage-2 三级企业 Agent 客制化模板、user.md 配置、Skill 插件与 IM 集成演示。
```

## 四、仓库可见性建议

建议初期使用：

```text
Private
```

原因：

- 包含企业业务流程设计。
- 包含老板侧决策交互设计。
- 后续可能涉及员工岗位、职责、日报字段。
- 后续可能接入飞书、OpenClaw、后端鉴权和真实企业数据。

等产品化后，可以再考虑拆分部分通用模板或工具为公开仓库。

## 五、仓库应该包含的内容

### 1. 三级 Agent 模板

```text
automage_agents/templates/
  base/
    agents.md
  line_worker/
    agents.md
  manager/
    agents.md
  executive/
    agents.md
```

对应会议中的三类角色：

- 一线员工。
- 业务领导。
- 公司领导 / 老板。

一线员工模板重点：

- 每天填写日报。
- 描述岗位职责。
- 描述每日输入。
- 描述每日输出。
- 配置个人岗位上下文。

业务领导模板重点：

- 接收每日汇总。
- 查看部门日报。
- 判断风险。
- 做每日管理决策。
- 向员工或团队下发任务。

老板侧模板重点：

- 每天早上在 IM 中收到决策项。
- 看到 A/B 方案或选择题。
- 选择方案。
- 补充自己的想法。
- 确认后由系统拆解为可执行规划。
- 将战略意图传达到业务领导和员工侧。

### 2. `user.md` 模板

```text
automage_agents/templates/user.md
```

这是仓库的核心内容之一。

每个员工开箱即用时，需要填写自己的 `user.md`，包括：

- 用户是谁。
- 岗位是什么。
- 岗位职责有哪些。
- 每天输入是什么。
- 每天输出是什么。
- 个性化内容。
- 用户名。
- 岗位上下文。
- 权限边界。

该部分后续需要和后端联调，尤其是：

- `user.md` 的存储方式。
- `user.md` 与用户表的关系。
- `user_id` / `node_id` / `role_id` 的绑定。
- 鉴权机制。
- 用户配置更新流程。

### 3. Skill 插件

```text
automage_agents/skills/
```

用于放 Agent 可调用的业务能力，例如：

- 员工日报提交。
- 查询个人任务。
- 部门日报汇总。
- 风险识别。
- 任务分发。
- Dream 决策草案。
- 决策提交。
- Schema 校验。
- Self-correction 占位。

### 4. 后端 API Client

```text
automage_agents/api/
```

这个仓库只放调用后端接口的客户端封装，不放后端服务本体。

后端仓库应该由后端同学负责，包括：

- 数据库。
- 鉴权机制。
- REST API 服务。
- 用户配置存储。
- `user.md` 解析与持久化。
- 任务队列表。
- 日报表。
- 决策日志表。

### 5. OpenClaw / 飞书 / IM 适配

```text
automage_agents/integrations/
  openclaw/
  feishu/
```

会议中强调，最终老板侧要在 IM 中看到内容，因此这个模块非常重要。

当前阶段可以先使用 Mock：

- Mock 飞书日报卡片。
- Mock 老板 A/B 决策卡片。
- Mock 飞书事件回调。
- Mock OpenClaw Adapter。

后续再替换成真实：

- 飞书 App。
- 飞书事件订阅。
- 飞书卡片回调。
- OpenClaw Channel。
- OpenClaw 插件生命周期。
- 真实 Cron 推送。

### 6. 本地 Mock 演示

```text
scripts/demo_mock_flow.py
```

该脚本用于演示完整业务闭环：

```text
员工提交日报
→ 业务领导看到部门汇总
→ 老板早上收到决策卡片
→ 老板选择方案
→ 系统拆解任务
→ 员工收到任务
```

这个脚本适合用于：

- 团队内部演示。
- 产品流程验证。
- 后续联调前自测。
- 给非技术成员解释系统价值。

## 六、推荐仓库目录结构

```text
automage-agent-customization/
  automage_agents/
    agents/
      __init__.py
      registry.py
      renderer.py

    api/
      __init__.py
      client.py
      errors.py
      mock_client.py
      models.py

    config/
      __init__.py
      loader.py
      settings.py

    core/
      __init__.py
      enums.py
      exceptions.py
      models.py

    demo/
      __init__.py
      factory.py

    integrations/
      __init__.py
      feishu/
        __init__.py
        events.py
        messages.py
      openclaw/
        __init__.py
        adapter.py
      router.py

    schemas/
      __init__.py
      placeholders.py

    skills/
      __init__.py
      common.py
      context.py
      executive.py
      manager.py
      registry.py
      result.py
      schema_tools.py
      staff.py

    templates/
      user.md
      base/
        agents.md
      line_worker/
        agents.md
      manager/
        agents.md
      executive/
        agents.md

    utils/
      __init__.py
      paths.py

  configs/
    automage.example.toml

  docs/
    AI中枢系统需求与接口文档.pdf
    会议纪要.md
    开发清单.md
    开发参考01.md
    里程碑交付.docx
    项目参考01.md
    ...

  examples/
    user.staff.example.toml
    user.manager.example.toml
    user.executive.example.toml
    rendered/
      staff.agents.md

  scripts/
    render_agents.py
    demo_mock_flow.py

  tests/

  README.md
  pyproject.toml
  .gitignore
```

## 七、README 建议内容

仓库首页建议使用标题：

```markdown
# AutoMage Agent Customization
```

建议包含以下章节：

### 1. 项目定位

```markdown
本仓库用于 AutoMage-2 的三级企业 Agent 客制化开发，覆盖一线员工、业务领导、公司领导三类 Agent 模板、user.md 配置、Skill 插件、后端 API Client 与 IM 集成 Mock 流程。
```

### 2. 三层 Agent 架构

```markdown
- Staff Agent：一线员工执行与日报提交。
- Manager Agent：业务领导日报汇总、风险识别、任务分发。
- Executive Agent：老板侧决策项推送、A/B 方案选择、战略任务确认。
```

### 3. 核心交互目标

```markdown
老板侧目标是每天早上在 IM 中收到带决策项的推送，只需要做选择题或补充意见。系统根据老板确认结果拆解为可执行规划，并传达到业务领导与员工侧。
```

### 4. `user.md` 说明

```markdown
每个员工需要填写 user.md，包括岗位、职责、输入、输出、个性化上下文等。后续 user.md 将与后端用户系统和鉴权机制联调。
```

### 5. 本地演示方式

```powershell
python scripts/demo_mock_flow.py
```

### 6. 后续联调事项

```markdown
- 后端：数据库、鉴权、用户配置存储、API 契约。
- Schema：日报与管理汇总字段。
- Dream：老板侧决策机制。
- OpenClaw / Feishu：真实 IM Channel。
- Harness / Hermes：真实 Agent Runtime 与 Skill 注册方式。
```

## 八、建议补充的基础文件

建 GitHub 仓库前，建议至少保留：

```text
README.md
pyproject.toml
.gitignore
```

原因：

- `README.md` 是 GitHub 首页说明。
- `pyproject.toml` 是 Python 项目元信息。
- `.gitignore` 用来避免提交缓存、密钥、虚拟环境等文件。

如果将会议纪要、需求文档、参考资料统一整理到 `docs/` 目录，也建议仓库根目录仍保留 `README.md`、`pyproject.toml` 和 `.gitignore`。

推荐约定：

```text
README.md         # 仓库首页说明，放根目录
pyproject.toml    # Python 项目元信息，放根目录
.gitignore        # Git 忽略规则，放根目录
docs/             # 会议纪要、需求文档、参考资料、PDF、DOCX
```

## 九、`.gitignore` 建议

```gitignore
__pycache__/
*.py[cod]
*.pyo
*.pyd

.venv/
venv/
env/

.pytest_cache/
.mypy_cache/
.ruff_cache/

.env
*.env
*.secret
*.key

.DS_Store
Thumbs.db

*.log

.vscode/
.idea/

_pdf_pages/
```

如果需要团队共享 VS Code 配置，可以删除：

```gitignore
.vscode/
```

## 十、不建议提交到 GitHub 的内容

不要提交：

```text
真实飞书 App Secret
真实 API Token
真实员工信息
真实客户信息
真实日报数据
真实数据库配置
.env
```

会议纪要、需求文档、PDF、DOCX、参考资料可以统一放入 `docs/` 目录，但是否提交到 GitHub 需要看团队是否允许。

如果涉及内部讨论，建议不要放进代码仓库，或者单独放到私有文档系统。

## 十一、GitHub 网页创建仓库步骤

进入 GitHub 后点击：

```text
New repository
```

填写：

```text
Repository name: automage-agent-customization
Description: AutoMage-2 three-level enterprise agent customization templates, user.md profiles, skills, and IM integration mock flows.
Visibility: Private
```

不要勾选：

```text
Add README
Add .gitignore
Add license
```

因为这些文件建议在本地自己准备，避免和本地项目冲突。

## 十二、本地 Git 初始化和推送步骤

在 PowerShell 中进入项目目录：

```powershell
# 当前项目目录
D:\Auto-mage2
```

初始化 Git：

```powershell
git init
```

查看状态：

```powershell
git status
```

添加文件：

```powershell
git add .
```

首次提交：

```powershell
git commit -m "Initial AutoMage agent customization skeleton"
```

关联远程仓库：

```powershell
git remote add origin https://github.com/HWT-CPU/automage-agent-customization.git
```

设置主分支并推送：

```powershell
git branch -M main
git push -u origin main
```

推送成功后，刷新 GitHub 仓库页面即可看到代码。

## 十三、建议分支策略

初期可以采用简单分支策略：

```text
main
dev
feature/staff-agent-template
feature/manager-agent-template
feature/executive-agent-template
feature/openclaw-feishu-adapter
feature/backend-api-contract
```

### `main`

稳定版本。

### `dev`

日常集成版本。

### `feature/*`

每个人做自己的功能。

## 十四、建议 GitHub Issue 拆分

### Agent 模板

```text
[Agent] Staff Agent 模板完善
[Agent] Manager Agent 模板完善
[Agent] Executive Agent 老板侧决策模板完善
```

### user.md

```text
[User Profile] user.md 字段设计与后端联调
```

### 后端联调

```text
[API] agent/init 接口联调
[API] staff report 接口联调
[API] manager report 接口联调
[API] decision commit 接口联调
[Auth] 鉴权机制联调
```

### IM 侧

```text
[IM] 老板侧每日决策卡片设计
[IM] 业务领导侧日报汇总卡片设计
[IM] 员工侧日报填写卡片设计
```

### Mock Demo

```text
[Demo] 本地端到端 mock 流程维护
```

## 十五、推荐仓库边界

该仓库负责：

- 三级 Agent 模板。
- `user.md`。
- Skill 插件。
- 后端 API Client。
- IM / OpenClaw / 飞书适配。
- Mock 演示。

该仓库不负责：

- 后端数据库本体。
- 后端服务本体。
- 真实飞书密钥管理。
- 真实员工数据存储。
- 真实客户数据存储。
- 内部敏感会议材料归档。

## 十六、最终建议

建议创建仓库：

```text
automage-agent-customization
```

仓库定位：

```text
AutoMage-2 三级 Agent 客制化模板与 IM 决策流仓库。
```

当前本地代码已经适合作为初版提交到该仓库。

建仓前建议补齐：

```text
README.md
pyproject.toml
.gitignore
```

然后再执行本地 Git 初始化、提交和推送。
