# Staff 每日日报 Schema 设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P083-P098
> 对应页面文件：`01_PAGES/page_0083.md` — `01_PAGES/page_0098.md`

## 原文整理

<!-- 来自 page_0083.md 全文开始 -->

# Page 0083

## 原始文本块

### block_p0083_b001

2026 年5 月3 日

### block_p0083_b002

5Staff 每日日报Schema 设计

### block_p0083_b003

5.1Schema 基本信息

### block_p0083_b004

Staff 每日日报Schema 是AutoMage-2 MVP 阶段最基础的数据契约，用于记录一线员工

### block_p0083_b005

每天的工作进展、问题、解决尝试、资源消耗、明日计划和需要上级支持的事项。

### block_p0083_b006

该Schema 的核心作用不是让员工写一篇传统日报，而是将员工当天的工作过程转化为系

### block_p0083_b007

统可以解析、存储、汇总和追踪的结构化数据。Manager Agent 后续会基于这些Staff Schema

### block_p0083_b008

生成部门级汇总，Executive Agent 再基于部门汇总生成老板侧决策项。

### block_p0083_b009

字段内容

### block_p0083_b010

Schema 名称Staff 每日日报Schema

### block_p0083_b011

Schema IDschema_v1_staff

### block_p0083_b012

当前版本1.0.0

### block_p0083_b013

使用节点Staff Agent

### block_p0083_b014

数据提交人一线员工

### block_p0083_b015

数据确认人一线员工本人

### block_p0083_b016

主要触发方式每日下班前IM 触发

### block_p0083_b017

主要写入对象work_records、work_record_items

### block_p0083_b018

主要读取对象Manager Agent

### block_p0083_b019

核心目标沉淀员工每日工作记录，为部门汇总和任务闭环提供原始数据

### block_p0083_b020

MVP 阶段建议Staff Schema 采用「员工填写+ Agent 整理+ 员工确认+ 后端校验」的

### block_p0083_b021

方式生成。也就是说，Agent 可以帮助员工把自然语言内容整理为标准结构，但不能在员工未

### block_p0083_b022

确认的情况下直接伪造或提交日报。

### block_p0083_b023

Staff Schema 的典型流程如下：

### block_p0083_b024

IM 定时提醒员工

### block_p0083_b025

↓

### block_p0083_b026

员工填写今日工作内容

### block_p0083_b027

↓

### block_p0083_b028

Staff Agent 整理为schema_v1_staff

### block_p0083_b029

↓

### block_p0083_b030

员工确认

### block_p0083_b031

↓

### block_p0083_b032

后端校验

### block_p0083_b033

↓

### block_p0083_b034

写入work_records / work_record_items

### block_p0083_b035

↓

### block_p0083_b036

Manager Agent 定时读取并汇总

### block_p0083_b037

MVP 阶段不要求Staff Agent 自动监听员工屏幕、自动读取所有工作行为，也不要求完

### block_p0083_b038

全自动判断员工工作真实性。当前阶段优先保证数据格式稳定、提交流程可跑通、上级节点

### block_p0083_b039

可读取和可汇总。

### block_p0083_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0083_b041

AutoMage-2-MVP 架构设计文档·杨卓83

### block_p0083_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 83

## 表格

无。

## 备注

无。

<!-- 来自 page_0083.md 全文结束 -->

<!-- 来自 page_0084.md 全文开始 -->

# Page 0084

## 原始文本块

### block_p0084_b001

2026 年5 月3 日

### block_p0084_b002

5.2Staff Schema 字段总览

### block_p0084_b003

Staff Schema 字段分为五类：基础身份字段、工作内容字段、风险与支持字段、产出物字

### block_p0084_b004

段、签名与审计字段。

### block_p0084_b005

字段名类型必填说明

### block_p0084_b006

schema_idstring是Schema 标识，固定为schema_v1_staff

### block_p0084_b007

schema_versionstring是Schema 版本，MVP 阶段默认1.0.0

### block_p0084_b008

timestampstring是提交时间，ISO8601 格式

### block_p0084_b009

org_idstring / number是所属组织ID

### block_p0084_b010

department_idstring / number是所属部门ID

### block_p0084_b011

user_idstring / number是员工用户ID

### block_p0084_b012

node_idstring是Staff Agent 节点ID

### block_p0084_b013

record_datestring是日报对应日期，格式为YYYY-MM-DD

### block_p0084_b014

work_progressarray是今日完成事项列表

### block_p0084_b015

issues_facedarray否今日遇到的问题

### block_p0084_b016

solution_attemptarray否已尝试的解决方案

### block_p0084_b017

need_supportboolean是是否需要上级支持

### block_p0084_b018

support_detailstring条件必填当need_support = true 时必填

### block_p0084_b019

next_day_planarray是明日计划

### block_p0084_b020

resource_usageobject否工时、工具、预算、资料等资源消耗

### block_p0084_b021

artifactsarray否今日产出物，如文档、代码、链接、附件

### block_p0084_b022

related_task_idsarray否关联任务ID

### block_p0084_b023

risk_levelstring是风险等级，默认low

### block_p0084_b024

employee_commentstring否员工补充说明

### block_p0084_b025

signatureobject是员工确认与签名信息

### block_p0084_b026

metaobject否扩展字段

### block_p0084_b027

其中，work_progress、next_day_plan、need_support、risk_level 是Staff Schema 的

### block_p0084_b028

核心字段。Manager Agent 后续会重点读取这些字段，用于判断部门进展、阻塞事项和是否

### block_p0084_b029

存在需要上推的风险。

### block_p0084_b030

5.3字段定义明细

### block_p0084_b031

5.3.1schema_id：Schema 标识

### block_p0084_b032

schema_id 用于标识当前数据遵循哪一套Schema 结构。

### block_p0084_b033

MVP 阶段Staff 日报固定使用：

### block_p0084_b034

"schema_id": "schema_v1_staff"

### block_p0084_b035

该字段必须由Agent 自动填充，不建议让员工手动填写。后端收到数据后，应首先校验

### block_p0084_b036

schema_id 是否存在、是否为系统支持的Schema。

### block_p0084_b037

5.3.2schema_version：Schema 版本

### block_p0084_b038

schema_version 用于标识当前Staff Schema 的具体版本。

### block_p0084_b039

MVP 阶段默认值为：

### block_p0084_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0084_b041

AutoMage-2-MVP 架构设计文档·杨卓84

### block_p0084_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 84

## 表格

无。

## 备注

无。

<!-- 来自 page_0084.md 全文结束 -->

<!-- 来自 page_0085.md 全文开始 -->

# Page 0085

## 原始文本块

### block_p0085_b001

2026 年5 月3 日

### block_p0085_b002

"schema_version": "1.0.0"

### block_p0085_b003

后续如果Staff Schema 新增字段、调整字段含义或修改校验规则，应通过版本号区分，而

### block_p0085_b004

不是直接改变原字段含义。

### block_p0085_b005

5.3.3timestamp：提交时间

### block_p0085_b006

timestamp 表示员工日报被提交或确认的时间，使用ISO8601 格式。

### block_p0085_b007

示例：

### block_p0085_b008

"timestamp": "2026-05-03T18:12:30+08:00"

### block_p0085_b009

该字段用于排序、审计和判断日报是否按时提交。后端可以以服务器接收时间为准进行

### block_p0085_b010

二次记录，但Schema 中仍应保留Agent 侧生成时间。

### block_p0085_b011

5.3.4org_id：组织ID

### block_p0085_b012

org_id 表示该日报所属组织，用于多租户隔离和数据权限控制。

### block_p0085_b013

示例：

### block_p0085_b014

"org_id": 1

### block_p0085_b015

所有Staff Schema 必须绑定组织ID。Staff Agent 不能提交没有org_id 的数据，Manager

### block_p0085_b016

Agent 也不能跨组织读取Staff Schema。

### block_p0085_b017

5.3.5department_id：部门ID

### block_p0085_b018

department_id 表示员工所属部门，用于Manager Agent 按部门读取和汇总数据。

### block_p0085_b019

示例：

### block_p0085_b020

"department_id": 12

### block_p0085_b021

该字段是Manager 汇总的核心过滤条件。后端应校验该员工是否确实属于该部门，避免

### block_p0085_b022

员工伪造部门ID 或Agent 错填部门信息。

### block_p0085_b023

5.3.6user_id：员工ID

### block_p0085_b024

user_id 表示提交日报的员工用户ID。

### block_p0085_b025

示例：

### block_p0085_b026

"user_id": 10086

### block_p0085_b027

该字段必须与当前登录用户或当前Agent 绑定用户一致。Staff Agent 只能为自己的绑定

### block_p0085_b028

员工提交日报，不能代替其他员工提交日报。

### block_p0085_b029 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0085_b030

AutoMage-2-MVP 架构设计文档·杨卓85

### block_p0085_b031 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 85

## 表格

无。

## 备注

无。

<!-- 来自 page_0085.md 全文结束 -->

<!-- 来自 page_0086.md 全文开始 -->

# Page 0086

## 原始文本块

### block_p0086_b001

2026 年5 月3 日

### block_p0086_b002

5.3.7node_id：Agent 节点ID

### block_p0086_b003

node_id 表示生成该Schema 的Staff Agent 节点。

### block_p0086_b004

示例：

### block_p0086_b005

"node_id": "staff_node_10086"

### block_p0086_b006

该字段用于区分「谁是提交人」和「哪个Agent 生成了数据」。在后续审计和排查中，系

### block_p0086_b007

统需要知道是哪个Agent 版本、哪个节点、哪次运行生成了该数据。

### block_p0086_b008

5.3.8record_date：日报日期

### block_p0086_b009

record_date 表示这条日报对应哪一天的工作，而不是单纯表示提交时间。

### block_p0086_b010

示例：

### block_p0086_b011

"record_date": "2026-05-03"

### block_p0086_b012

如果员工在第二天补交前一天日报，timestamp 是补交时间，record_date 是实际日报

### block_p0086_b013

日期。二者不能混淆。

### block_p0086_b014

5.3.9work_progress：今日完成事项

### block_p0086_b015

work_progress 是Staff Schema 中最核心的字段，用于记录员工当天完成或推进的具体

### block_p0086_b016

工作。

### block_p0086_b017

建议使用数组结构，每一项代表一件相对独立的工作事项。

### block_p0086_b018

示例：

### block_p0086_b019

"work_progress": [

### block_p0086_b020

{

### block_p0086_b021

"title": " 完成Staff 日报Schema 初稿",

### block_p0086_b022

"description": "整理了一线员工日报所需字段，包括工作进展、问题、

### block_p0086_b023

明日计划和签名字段。",,→

### block_p0086_b024

"status": "completed",

### block_p0086_b025

"related_task_id": 201

### block_p0086_b026

},

### block_p0086_b027

{

### block_p0086_b028

"title": " 与后端对齐work_records 字段映射",

### block_p0086_b029

"description": "确认Staff Schema 中的固定字段进入work_records，

### block_p0086_b030

弹性字段进入work_record_items。",,→

### block_p0086_b031

"status": "in_progress",

### block_p0086_b032

"related_task_id": 202

### block_p0086_b033

}

### block_p0086_b034

]

### block_p0086_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0086_b036

AutoMage-2-MVP 架构设计文档·杨卓86

### block_p0086_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 86

## 表格

无。

## 备注

无。

<!-- 来自 page_0086.md 全文结束 -->

<!-- 来自 page_0087.md 全文开始 -->

# Page 0087

## 原始文本块

### block_p0087_b001

2026 年5 月3 日

### block_p0087_b002

建议每条工作事项包含：

### block_p0087_b003

子字段类型必填说明

### block_p0087_b004

titlestring是工作事项标题

### block_p0087_b005

descriptionstring是工作事项说明

### block_p0087_b006

statusstring是完成状态

### block_p0087_b007

related_task_idnumber / string否关联任务ID

### block_p0087_b008

status 建议使用以下枚举：

### block_p0087_b009

值含义

### block_p0087_b010

completed已完成

### block_p0087_b011

in_progress进行中

### block_p0087_b012

blocked阻塞

### block_p0087_b013

cancelled已取消

### block_p0087_b014

work_progress 不能为空。即使员工当天主要在处理零散事项，也应至少提交一条有效

### block_p0087_b015

记录。

### block_p0087_b016

5.3.10issues_faced：遇到的问题

### block_p0087_b017

issues_faced 用于记录员工当天遇到的问题、阻塞或不确定事项。

### block_p0087_b018

示例：

### block_p0087_b019

"issues_faced": [

### block_p0087_b020

{

### block_p0087_b021

"title": "Decision 表结构尚未最终确定",

### block_p0087_b022

"description": "当前DDL 中没有独立decision_logs 表，Agent mock 代码中已有

### block_p0087_b023

decision_logs 概念，需要后端确认最终承载方式。",,→

### block_p0087_b024

"severity": "medium"

### block_p0087_b025

}

### block_p0087_b026

]

### block_p0087_b027

建议子字段包括：

### block_p0087_b028

子字段类型必填说明

### block_p0087_b029

titlestring是问题标题

### block_p0087_b030

descriptionstring是问题说明

### block_p0087_b031

severitystring否严重程度

### block_p0087_b032

severity 建议使用：

### block_p0087_b033

值含义

### block_p0087_b034

low轻微问题

### block_p0087_b035

medium需要关注

### block_p0087_b036

high影响进度

### block_p0087_b037

critical严重影响交付或决策

### block_p0087_b038

如果当天没有明显问题，可以提交空数组[]。不建议填「无」「没有」「正常」这类自然

### block_p0087_b039

语言字符串。

### block_p0087_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0087_b041

AutoMage-2-MVP 架构设计文档·杨卓87

### block_p0087_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 87

## 表格

无。

## 备注

无。

<!-- 来自 page_0087.md 全文结束 -->

<!-- 来自 page_0088.md 全文开始 -->

# Page 0088

## 原始文本块

### block_p0088_b001

2026 年5 月3 日

### block_p0088_b002

5.3.11solution_attempt：已尝试的解决方案

### block_p0088_b003

solution_attempt 用于记录员工针对问题已经尝试过的处理方式。

### block_p0088_b004

示例：

### block_p0088_b005

"solution_attempt": [

### block_p0088_b006

{

### block_p0088_b007

"issue_title": "Decision 表结构尚未最终确定",

### block_p0088_b008

"attempt": "先在文档中列出Decision Schema 的最小字段，

### block_p0088_b009

并建议后端新增独立决策表。",,→

### block_p0088_b010

"result": " 待后端确认"

### block_p0088_b011

}

### block_p0088_b012

]

### block_p0088_b013

该字段的价值在于避免上级重复询问「你有没有试过什么方法」。Manager Agent 在汇总

### block_p0088_b014

时也可以根据这个字段判断问题是否已经被员工处理过，是否确实需要上级介入。

### block_p0088_b015

如果issues_faced 为空，则solution_attempt 可以为空数组。

### block_p0088_b016

5.3.12need_support：是否需要上级支持

### block_p0088_b017

need_support 表示员工是否需要Manager、其他部门或老板层面的支持。

### block_p0088_b018

示例：

### block_p0088_b019

"need_support": true

### block_p0088_b020

该字段必须是boolean，不能使用" 是"、" 否"、" 需要"、" 不需要" 等字符串。

### block_p0088_b021

need_support = true 时，系统应进一步检查support_detail 是否填写。如果未填写，

### block_p0088_b022

Agent 应追问员工补充。

### block_p0088_b023

5.3.13support_detail：需要支持的具体内容

### block_p0088_b024

当need_support = true 时，support_detail 必填。

### block_p0088_b025

示例：

### block_p0088_b026

"support_detail": "需要后端确认是否新增decision_logs 表，以及Executive

### block_p0088_b027

决策结果是否直接映射到tasks。",→

### block_p0088_b028

如果need_support = false，该字段可以为空字符串或不传。

### block_p0088_b029

该字段后续可能触发Incident 或Task。如果员工提出的是明确待处理事项，Manager

### block_p0088_b030

Agent 可以将其转换为部门任务；如果涉及超权限决策，可以继续上推给Executive Agent。

### block_p0088_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0088_b032

AutoMage-2-MVP 架构设计文档·杨卓88

### block_p0088_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 88

## 表格

无。

## 备注

无。

<!-- 来自 page_0088.md 全文结束 -->

<!-- 来自 page_0089.md 全文开始 -->

# Page 0089

## 原始文本块

### block_p0089_b001

2026 年5 月3 日

### block_p0089_b002

5.3.14next_day_plan：明日计划

### block_p0089_b003

next_day_plan 用于记录员工下一工作日计划完成的事项。

### block_p0089_b004

示例：

### block_p0089_b005

"next_day_plan": [

### block_p0089_b006

{

### block_p0089_b007

"title": " 完善Manager Schema 字段定义",

### block_p0089_b008

"priority": "high",

### block_p0089_b009

"expected_output": " 形成可提交给后端和Agent 客制化使用的字段说明"

### block_p0089_b010

},

### block_p0089_b011

{

### block_p0089_b012

"title": " 补充Staff Schema 错误示例",

### block_p0089_b013

"priority": "medium",

### block_p0089_b014

"expected_output": " 明确Agent 生成失败和后端校验失败的处理方式"

### block_p0089_b015

}

### block_p0089_b016

]

### block_p0089_b017

建议子字段包括：

### block_p0089_b018

子字段类型必填说明

### block_p0089_b019

titlestring是明日计划事项

### block_p0089_b020

prioritystring否优先级

### block_p0089_b021

expected_outputstring否预期产出

### block_p0089_b022

priority 建议使用：low / medium / high / urgent。

### block_p0089_b023

next_day_plan 是任务下发和次日跟进的重要参考，不建议为空。

### block_p0089_b024

5.3.15resource_usage：资源消耗

### block_p0089_b025

resource_usage 用于记录员工当天消耗的主要资源，包括工时、工具、预算、资料、外

### block_p0089_b026

部协作等。

### block_p0089_b027

示例：

### block_p0089_b028

"resource_usage": {

### block_p0089_b029

"work_hours": 7.5,

### block_p0089_b030

"tools": ["ChatGPT", "PostgreSQL", "Markdown"],

### block_p0089_b031

"budget_used": 0,

### block_p0089_b032

"external_support": [],

### block_p0089_b033

"notes": " 主要消耗在Schema 字段梳理和文档撰写上"

### block_p0089_b034

}

### block_p0089_b035

建议子字段包括：work_hours、tools、budget_used、external_support、notes（含义

### block_p0089_b036

见原文表格）。

### block_p0089_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0089_b038

AutoMage-2-MVP 架构设计文档·杨卓89

### block_p0089_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 89

## 表格

无。

## 备注

无。

<!-- 来自 page_0089.md 全文结束 -->

<!-- 来自 page_0090.md 全文开始 -->

# Page 0090

## 原始文本块

### block_p0090_b001

2026 年5 月3 日

### block_p0090_b002

MVP 阶段该字段可以作为辅助字段，不强制用于绩效计算。后续如果要做资源效率分析，

### block_p0090_b003

可以逐步规范化。

### block_p0090_b004

5.3.16artifacts：产出物

### block_p0090_b005

artifacts 用于记录员工当天产出的文档、代码、表格、图片、链接、附件等。

### block_p0090_b006

示例：

### block_p0090_b007

"artifacts": [

### block_p0090_b008

{

### block_p0090_b009

"title": "AutoMage-2 Staff Schema 设计稿",

### block_p0090_b010

"artifact_type": "document",

### block_p0090_b011

"url": "https://example.com/docs/staff-schema",

### block_p0090_b012

"description": " 用于后端和Agent 客制化对齐的一线日报Schema 文档"

### block_p0090_b013

}

### block_p0090_b014

]

### block_p0090_b015

建议子字段：title、artifact_type、url、file_id、description。artifact_type 建

### block_p0090_b016

议使用document / code / spreadsheet / image / link / file / other。

### block_p0090_b017

如果员工当天没有明确产出物，可以为空数组。

### block_p0090_b018

5.3.17related_task_ids：关联任务ID

### block_p0090_b019

示例："related_task_ids": [201, 202]。若无关联任务，可为空数组。

### block_p0090_b020

5.3.18risk_level：风险等级

### block_p0090_b021

示例："risk_level": "medium"。枚举：low / medium / high / critical（含义见原文）。

### block_p0090_b022

MVP 阶段可由Staff Agent 初步判断，但应允许员工修改；最终提交前需员工确认。

### block_p0090_b023

5.3.19employee_comment：员工补充说明

### block_p0090_b024

可选字段，不应用于承载关键结构化信息。

### block_p0090_b025

5.3.20signature：数字签名信息

### block_p0090_b026

示例：

### block_p0090_b027

"signature": {

### block_p0090_b028

"signature_required": true,

### block_p0090_b029

"signature_status": "signed",

### block_p0090_b030

"signed_by": 10086,

### block_p0090_b031

"signed_at": "2026-05-03T18:13:00+08:00",

### block_p0090_b032

"payload_hash": "sha256:example_hash",

### block_p0090_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0090_b034

AutoMage-2-MVP 架构设计文档·杨卓90

### block_p0090_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 90

## 表格

无。

## 备注

无。

<!-- 来自 page_0090.md 全文结束 -->

<!-- 来自 page_0091.md 全文开始 -->

# Page 0091

## 原始文本块

### block_p0091_b001

2026 年5 月3 日

### block_p0091_b002

"signature_source": "im"

### block_p0091_b003

}

### block_p0091_b004

MVP 阶段可先采用简化签名机制，重点明确谁确认、何时确认、确认时内容、后续是否

### block_p0091_b005

变更。若signature_status != signed，该日报不应进入Manager 正式汇总。

### block_p0091_b006

5.3.21meta：扩展字段

### block_p0091_b007

示例：

### block_p0091_b008

"meta": {

### block_p0091_b009

"input_channel": "feishu",

### block_p0091_b010

"agent_template_version": "staff_agent_v0.1",

### block_p0091_b011

"locale": "zh-CN"

### block_p0091_b012

}

### block_p0091_b013

meta 只能存放低频扩展数据；高频查询、权限、决策相关字段应提升为正式字段。

### block_p0091_b014

5.4Staff Schema JSON 示例

### block_p0091_b015

下面是一个完整Staff Schema 示例，可作为Agent 输出和后端联调参考。

### block_p0091_b016

{

### block_p0091_b017

"schema_id": "schema_v1_staff",

### block_p0091_b018

"schema_version": "1.0.0",

### block_p0091_b019

"timestamp": "2026-05-03T18:12:30+08:00",

### block_p0091_b020

"org_id": 1,

### block_p0091_b021

"department_id": 12,

### block_p0091_b022

"user_id": 10086,

### block_p0091_b023

"node_id": "staff_node_10086",

### block_p0091_b024

"record_date": "2026-05-03",

### block_p0091_b025

"work_progress": [

### block_p0091_b026

{

### block_p0091_b027

"title": " 完成Staff 日报Schema 初稿",

### block_p0091_b028

"description": "整理了一线员工日报所需字段，包括工作进展、问题、明日计划、

### block_p0091_b029

资源消耗和签名字段。",,→

### block_p0091_b030

"status": "completed",

### block_p0091_b031

"related_task_id": 201

### block_p0091_b032

},

### block_p0091_b033

{

### block_p0091_b034

"title": " 与后端对齐work_records 字段映射",

### block_p0091_b035

"description": "确认Staff Schema 中的固定字段进入work_records，弹性字段进入

### block_p0091_b036

work_record_items。",,→

### block_p0091_b037

"status": "in_progress",

### block_p0091_b038

"related_task_id": 202

### block_p0091_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0091_b040

AutoMage-2-MVP 架构设计文档·杨卓91

### block_p0091_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 91

## 表格

无。

## 备注

无。

<!-- 来自 page_0091.md 全文结束 -->

<!-- 来自 page_0092.md 全文开始 -->

# Page 0092

## 原始文本块

### block_p0092_b001

2026 年5 月3 日

### block_p0092_b002

}

### block_p0092_b003

],

### block_p0092_b004

"issues_faced": [

### block_p0092_b005

{

### block_p0092_b006

"title": "Decision 表结构尚未最终确定",

### block_p0092_b007

"description": "当前DDL 中没有独立decision_logs 表，Agent mock 代码中已有

### block_p0092_b008

decision_logs 概念，需要后端确认最终承载方式。",,→

### block_p0092_b009

"severity": "medium"

### block_p0092_b010

}

### block_p0092_b011

],

### block_p0092_b012

"solution_attempt": [

### block_p0092_b013

{

### block_p0092_b014

"issue_title": "Decision 表结构尚未最终确定",

### block_p0092_b015

"attempt": " 先在文档中列出Decision Schema 的最小字段，并建议后端新增独立决策表。",

### block_p0092_b016

"result": " 待后端确认"

### block_p0092_b017

}

### block_p0092_b018

],

### block_p0092_b019

"need_support": true,

### block_p0092_b020

"support_detail": "需要后端确认是否新增decision_logs 表，以及Executive

### block_p0092_b021

决策结果是否直接映射到tasks。",,→

### block_p0092_b022

"next_day_plan": [

### block_p0092_b023

{

### block_p0092_b024

"title": " 完善Manager Schema 字段定义",

### block_p0092_b025

"priority": "high",

### block_p0092_b026

"expected_output": " 形成可提交给后端和Agent 客制化使用的字段说明"

### block_p0092_b027

},

### block_p0092_b028

{

### block_p0092_b029

"title": " 补充Staff Schema 错误示例",

### block_p0092_b030

"priority": "medium",

### block_p0092_b031

"expected_output": " 明确Agent 生成失败和后端校验失败的处理方式"

### block_p0092_b032

}

### block_p0092_b033

],

### block_p0092_b034

"resource_usage": {

### block_p0092_b035

"work_hours": 7.5,

### block_p0092_b036

"tools": ["ChatGPT", "PostgreSQL", "Markdown"],

### block_p0092_b037

"budget_used": 0,

### block_p0092_b038

"external_support": [],

### block_p0092_b039

"notes": " 主要消耗在Schema 字段梳理和文档撰写上"

### block_p0092_b040

},

### block_p0092_b041

"artifacts": [

### block_p0092_b042

{

### block_p0092_b043

"title": "AutoMage-2 Staff Schema 设计稿",

### block_p0092_b044

"artifact_type": "document",

### block_p0092_b045

"url": "https://example.com/docs/staff-schema",

### block_p0092_b046

"description": " 用于后端和Agent 客制化对齐的一线日报Schema 文档"

### block_p0092_b047

}

### block_p0092_b048

],

### block_p0092_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0092_b050

AutoMage-2-MVP 架构设计文档·杨卓92

### block_p0092_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 92

## 表格

无。

## 备注

无。

<!-- 来自 page_0092.md 全文结束 -->

<!-- 来自 page_0093.md 全文开始 -->

# Page 0093

## 原始文本块

### block_p0093_b001

2026 年5 月3 日

### block_p0093_b002

"related_task_ids": [201, 202],

### block_p0093_b003

"risk_level": "medium",

### block_p0093_b004

"employee_comment": "今天主要时间用于梳理字段和对齐后端表结构，

### block_p0093_b005

部分内容还需要等产品确认后再定稿。",,→

### block_p0093_b006

"signature": {

### block_p0093_b007

"signature_required": true,

### block_p0093_b008

"signature_status": "signed",

### block_p0093_b009

"signed_by": 10086,

### block_p0093_b010

"signed_at": "2026-05-03T18:13:00+08:00",

### block_p0093_b011

"payload_hash": "sha256:example_hash",

### block_p0093_b012

"signature_source": "im"

### block_p0093_b013

},

### block_p0093_b014

"meta": {

### block_p0093_b015

"input_channel": "feishu",

### block_p0093_b016

"agent_template_version": "staff_agent_v0.1",

### block_p0093_b017

"locale": "zh-CN"

### block_p0093_b018

}

### block_p0093_b019

}

### block_p0093_b020

5.5Staff Schema 校验规则

### block_p0093_b021

Staff Schema 需要经过Agent 本地校验和后端最终校验。

### block_p0093_b022

5.5.1基础字段校验

### block_p0093_b023

字段校验规则

### block_p0093_b024

schema_id必须为schema_v1_staff

### block_p0093_b025

schema_version必须是当前支持版本

### block_p0093_b026

timestamp必须为合法ISO8601 时间

### block_p0093_b027

org_id必须存在，且当前用户属于该组织

### block_p0093_b028

department_id必须存在，且当前用户属于该部门

### block_p0093_b029

user_id必须与当前提交人一致

### block_p0093_b030

node_id必须与当前Staff Agent 绑定关系一致

### block_p0093_b031

record_date必须为合法日期

### block_p0093_b032

5.5.2工作内容校验

### block_p0093_b033

work_progress 必须：为数组、至少一条、每条含title、description、status，status

### block_p0093_b034

在允许枚举内；单条description 不宜过长。

### block_p0093_b035

next_day_plan 必须：为数组、至少一条、每条含title；若填priority 须在允许枚举

### block_p0093_b036

内。

### block_p0093_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0093_b038

AutoMage-2-MVP 架构设计文档·杨卓93

### block_p0093_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 93

## 表格

无。

## 备注

无。

<!-- 来自 page_0093.md 全文结束 -->

<!-- 来自 page_0094.md 全文开始 -->

# Page 0094

## 原始文本块

### block_p0094_b001

2026 年5 月3 日

### block_p0094_b002

5.5.3支持需求校验

### block_p0094_b003

need_support 必须为boolean。若为true 则必须填写非空support_detail，否则后端

### block_p0094_b004

返回422。

### block_p0094_b005

5.5.4风险等级校验

### block_p0094_b006

risk_level 枚举：low / medium / high / critical。内容与等级明显不符时Agent 可

### block_p0094_b007

提醒，MVP 阶段不建议强制自动改写。

### block_p0094_b008

5.5.5签名校验

### block_p0094_b009

正式写入前校验signature 存在、signature_status 为signed、signed_by 等于当前

### block_p0094_b010

员工、signed_at 与payload_hash 存在且与内容一致（MVP 可简化哈希）。

### block_p0094_b011

5.5.6权限校验

### block_p0094_b012

后端须校验：用户有权提交该user_id 日报；Agent 绑定；员工属于department_id 与

### block_p0094_b013

org_id；账号有效；日期策略（补交等）。权限校验不能仅靠Prompt。

### block_p0094_b014

5.5.7重复提交校验

### block_p0094_b015

建议唯一键：org_id + user_id + record_date + schema_id。已存在时可「允许更新

### block_p0094_b016

+ 审计日志」或「修订版本」；MVP 建议允许更新并记审计。

### block_p0094_b017

5.6Staff Schema 必填字段

### block_p0094_b018

字段必填原因

### block_p0094_b019

schema_id / schema_version后端识别结构与校验规则

### block_p0094_b020

timestamp审计与排序

### block_p0094_b021

org_id/department_id/

### block_p0094_b022

user_id / node_id

### block_p0094_b023

组织隔离、汇总、身份与节点追踪

### block_p0094_b024

record_date日报归属日期

### block_p0094_b025

work_progress日报核心内容

### block_p0094_b026

need_support是否触发异常或上推

### block_p0094_b027

next_day_plan次日计划与任务衔接

### block_p0094_b028

risk_level部门风险汇总

### block_p0094_b029

signature确认与责任追溯

### block_p0094_b030

条件必填：support_detail（当need_support=true）；issues_faced（当risk_level

### block_p0094_b031

为high/critical 时建议）；solution_attempt（当存在issues_faced 时建议）；artifacts

### block_p0094_b032

（声明有产出物时建议）。

### block_p0094_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0094_b034

AutoMage-2-MVP 架构设计文档·杨卓94

### block_p0094_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 94

## 表格

无。

## 备注

无。

<!-- 来自 page_0094.md 全文结束 -->

<!-- 来自 page_0095.md 全文开始 -->

# Page 0095

## 原始文本块

### block_p0095_b001

2026 年5 月3 日

### block_p0095_b002

5.7Staff Schema 可选字段

### block_p0095_b003

可选字段：issues_faced、solution_attempt、resource_usage、artifacts、

### block_p0095_b004

related_task_ids、employee_comment、meta。Agent仍应尽量引导补充以提升Man-

### block_p0095_b005

ager 汇总质量。

### block_p0095_b006

5.8Staff Schema 错误示例

### block_p0095_b007

5.8.1错误示例一：把boolean 写成字符串

### block_p0095_b008

{ "need_support": " 需要" }

### block_p0095_b009

正确："need_support": true。

### block_p0095_b010

5.8.2错误示例二：工作进展不是数组

### block_p0095_b011

错误：work_progress 为单字符串。正确：为对象数组且含title、description、status。

### block_p0095_b012

5.8.3错误示例三：需要支持但未填写支持内容

### block_p0095_b013

need_support: true 且support_detail 为空—应422。

### block_p0095_b014

5.8.4错误示例四：缺少签名信息

### block_p0095_b015

缺少signature 则无法证明员工确认，不应进入Manager 正式汇总。

### block_p0095_b016

5.8.5错误示例五：把关键数据塞进补充说明

### block_p0095_b017

应将内容拆入work_progress、issues_faced、need_support、support_detail、

### block_p0095_b018

next_day_plan 等结构化字段。

### block_p0095_b019

5.9Staff Agent 生成Schema 的Prompt 约束

### block_p0095_b020

5.9.1角色约束

### block_p0095_b021

Staff Agent 为「岗位执行辅助节点」，非上级、非绩效评估人；不得编造、不得擅自改已

### block_p0095_b022

确认信息、不得越权读他人数据。

### block_p0095_b023

5.9.2信息收集约束

### block_p0095_b024

至少收集：完成事项、进行中事项、问题、是否尝试解决、是否需支持、明日计划、产出

### block_p0095_b025

物、是否关联任务。回答过简时应追问具体事项名称、结果与状态。

### block_p0095_b026 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0095_b027

AutoMage-2-MVP 架构设计文档·杨卓95

### block_p0095_b028 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 95

## 表格

无。

## 备注

无。

<!-- 来自 page_0095.md 全文结束 -->

<!-- 来自 page_0096.md 全文开始 -->

# Page 0096

## 原始文本块

### block_p0096_b001

2026 年5 月3 日

### block_p0096_b002

5.9.3输出格式约束

### block_p0096_b003

最终须输出符合schema_v1_staff 的可解析JSON，不得以Markdown 表格或自然语言

### block_p0096_b004

总结作为正式提交体。

### block_p0096_b005

5.9.4不编造约束

### block_p0096_b006

缺失字段须追问，不得自动填充例如默认明日计划。

### block_p0096_b007

5.9.5风险提示约束

### block_p0096_b008

出现延期、投诉、阻塞等信息时应提醒确认risk_level 与need_support。

### block_p0096_b009

5.9.6员工确认约束

### block_p0096_b010

提交前须展示结构化摘要并要求员工确认后再写签名并调接口。

### block_p0096_b011

5.10Staff Agent 提交失败后的重试逻辑

### block_p0096_b012

5.10.1422 Schema 校验失败

### block_p0096_b013

读后端返回的具体错误字段，向员工说明缺失或错误内容，只追问需补充字段，重生成

### block_p0096_b014

Schema 后再次提交。

### block_p0096_b015

日报暂未提交成功，原因是「需要上级支持」已选择是，但没有填写具体支持内容。

### block_p0096_b016

请补充需要谁支持、支持什么事项。

### block_p0096_b017

5.10.2401 鉴权失败

### block_p0096_b018

勿重复提交；提示重登或重初始化Agent；记日志；必要时通知管理员。

### block_p0096_b019

5.10.3403 权限不足

### block_p0096_b020

停止提交；提示身份与归属不一致；禁止Agent 自改user_id/department_id 重试。

### block_p0096_b021

5.10.4409 重复提交

### block_p0096_b022

提示已有日报；选择查看、修改或取消；修改走更新/修订并记审计。

### block_p0096_b023

5.10.55xx 服务错误

### block_p0096_b024

保留草稿；指数退避重试；多次失败提示稍后；通知运维。

### block_p0096_b025 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0096_b026

AutoMage-2-MVP 架构设计文档·杨卓96

### block_p0096_b027 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 96

## 表格

无。

## 备注

无。

<!-- 来自 page_0096.md 全文结束 -->

<!-- 来自 page_0097.md 全文开始 -->

# Page 0097

## 原始文本块

### block_p0097_b001

2026 年5 月3 日

### block_p0097_b002

5.10.6网络超时

### block_p0097_b003

使用同一幂等键重试，避免重复写入。建议请求体含："idempotency_key":

### block_p0097_b004

"staff_report_10086_2026-05-03"。

### block_p0097_b005

5.11Staff Schema 与数据库字段映射

### block_p0097_b006

MVP建议映射：work_records、work_record_items、artifacts/artifact_links、

### block_p0097_b007

incidents、tasks、audit_logs。

### block_p0097_b008

5.11.1映射到work_records

### block_p0097_b009

work_records 存储Staff 日报主记录。

### block_p0097_b010

Staff Schema 字段数据库字段说明

### block_p0097_b011

org_idwork_records.org_id组织ID

### block_p0097_b012

department_idwork_records.department_id部门ID

### block_p0097_b013

user_idwork_records.user_id员工ID

### block_p0097_b014

record_datework_records.record_date日报日期

### block_p0097_b015

schema_id / schema_versionwork_records.metaSchema 标识和版本

### block_p0097_b016

work_progress 摘要work_records.title可生成简短标题，不建议存整段日报

### block_p0097_b017

提交状态work_records.status草稿、已提交、已确认等

### block_p0097_b018

timestampwork_records.submitted_at提交时间

### block_p0097_b019

来源方式work_records.source_typeIM、Web、Agent 等

### block_p0097_b020

扩展数据work_records.meta低频扩展字段

### block_p0097_b021

work_records.title 可由Agent 自动生成，例如：2026-05-03 杨卓每日工作记录。

### block_p0097_b022

5.11.2映射到work_record_items

### block_p0097_b023

work_record_items 存储Staff Schema 中具体字段内容。

### block_p0097_b024

Staff Schema 字段field_keyfield_label

### block_p0097_b025

work_progresswork_progress今日完成事项

### block_p0097_b026

issues_facedissues_faced遇到的问题

### block_p0097_b027

solution_attemptsolution_attempt已尝试的解决方案

### block_p0097_b028

need_supportneed_support是否需要上级支持

### block_p0097_b029

support_detailsupport_detail支持需求说明

### block_p0097_b030

next_day_plannext_day_plan明日计划

### block_p0097_b031

resource_usageresource_usage资源消耗

### block_p0097_b032

risk_levelrisk_level风险等级

### block_p0097_b033

employee_commentemployee_comment员工补充说明

### block_p0097_b034

signaturesignature签名信息

### block_p0097_b035

结构化对象或数组入value_json；短文本可入value_text。同一work_record_id 下每

### block_p0097_b036

个field_key 唯一。

### block_p0097_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0097_b038

AutoMage-2-MVP 架构设计文档·杨卓97

### block_p0097_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 97

## 表格

无。

## 备注

无。

<!-- 来自 page_0097.md 全文结束 -->

<!-- 来自 page_0098.md 全文开始 -->

# Page 0098

## 原始文本块

### block_p0098_b001

2026 年5 月3 日

### block_p0098_b002

5.11.3映射到artifacts

### block_p0098_b003

标题、类型、URL/文件与user_id、work_record_id 关联；链接优先artifact_links，

### block_p0098_b004

附件入artifacts。

### block_p0098_b005

5.11.4映射到incidents

### block_p0098_b006

当need_support=true、高风险、work_progress 阻塞、严重问题或明确请求介入时可

### block_p0098_b007

生成；support_detail/问题描述→标题与说明；risk_level →severity；来源链关联

### block_p0098_b008

work_record_id。

### block_p0098_b009

5.11.5映射到tasks

### block_p0098_b010

明日计划、支持事项、Manager 下发、老板决策等场景；不宜将全部next_day_plan 自

### block_p0098_b011

动转正任务，宜确认后生成。

### block_p0098_b012

5.11.6映射到audit_logs

### block_p0098_b013

建议动作：staff_schema_generated、staff_schema_confirmed、

### block_p0098_b014

staff_schema_submitted、staff_schema_validation_failed、staff_schema_updated、

### block_p0098_b015

staff_schema_signed、staff_schema_read_by_manager 等；记录操作人、Agent、对象类

### block_p0098_b016

型与ID、时间、结果、payload 摘要。

### block_p0098_b017

5.11.7当前数据库映射建议

### block_p0098_b018

Staff Schema

### block_p0098_b019

↓

### block_p0098_b020

work_records：日报主记录

### block_p0098_b021

↓

### block_p0098_b022

work_record_items：日报字段明细

### block_p0098_b023

↓

### block_p0098_b024

artifacts：产出物

### block_p0098_b025

↓

### block_p0098_b026

incidents：需要支持或高风险事项

### block_p0098_b027

↓

### block_p0098_b028

tasks：确认后的后续任务

### block_p0098_b029

↓

### block_p0098_b030

audit_logs：提交、确认、修改和读取记录

### block_p0098_b031

高频查询字段（如risk_level、need_support、work_progress.status）不宜长期仅存

### block_p0098_b032

JSON，应适时提升为显式列或索引。

### block_p0098_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0098_b034

AutoMage-2-MVP 架构设计文档·杨卓98

### block_p0098_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 98

## 表格

无。

## 备注

无。

<!-- 来自 page_0098.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

