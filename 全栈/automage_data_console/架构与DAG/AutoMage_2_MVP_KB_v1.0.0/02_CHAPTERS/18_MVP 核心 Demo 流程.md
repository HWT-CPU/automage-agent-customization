# MVP 核心 Demo 流程

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P358-P385
> 对应页面文件：`01_PAGES/page_0358.md` — `01_PAGES/page_0385.md`

## 原文整理

<!-- 来自 page_0358.md 全文开始 -->

# Page 0358

## 原始文本块

### block_p0358_b001

2026 年5 月3 日

### block_p0358_b002

17MVP 核心Demo 流程

### block_p0358_b003

17.1Demo 目标

### block_p0358_b004

MVP 核心Demo 的目标，是用一条最短但完整的链路证明AutoMage-2 的三级Agent 架

### block_p0358_b005

构可以跑通：

### block_p0358_b006

员工提交工作数据

### block_p0358_b007

↓

### block_p0358_b008

Staff Agent 结构化

### block_p0358_b009

↓

### block_p0358_b010

Manager Agent 部门汇总

### block_p0358_b011

↓

### block_p0358_b012

Executive Agent / Dream 生成老板决策

### block_p0358_b013

↓

### block_p0358_b014

老板确认方案

### block_p0358_b015

↓

### block_p0358_b016

系统生成任务

### block_p0358_b017

↓

### block_p0358_b018

任务下发给执行人

### block_p0358_b019

本Demo 不追求覆盖所有企业管理场景，也不追求界面完整，而是验证AutoMage-2 最

### block_p0358_b020

核心的产品假设：

### block_p0358_b021

1. 一线员工的自然语言工作记录可以被整理成Staff Schema。

### block_p0358_b022

2. Staff Schema 可以被后端校验并写入数据库。

### block_p0358_b023

3. Manager Agent 可以读取本部门数据并生成部门汇总。

### block_p0358_b024

4. Executive Agent 可以基于部门汇总生成老板决策项。

### block_p0358_b025

5. 老板确认后，系统可以自动生成正式任务。

### block_p0358_b026

6. Staff Agent 可以读取并展示下发给员工的任务。

### block_p0358_b027

7. 整个过程有来源、有状态、有签名、有审计记录。

### block_p0358_b028

Demo 的重点不是“AI 会不会写总结”，而是证明系统可以形成组织级闭环：

### block_p0358_b029

事实数据→汇总判断→老板决策→任务执行→数据回流

### block_p0358_b030

只要这条链路跑通，AutoMage-2 就具备了继续扩展行业模板、自动采集、复杂Dream、

### block_p0358_b031

老板看板和组织诊断的基础。

### block_p0358_b032

17.2Demo 角色

### block_p0358_b033

本次Demo 建议使用4 类角色，尽量减少人员复杂度。

### block_p0358_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0358_b035

AutoMage-2-MVP 架构设计文档·杨卓358

### block_p0358_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 358

## 表格

无。

## 备注

无。

<!-- 来自 page_0358.md 全文结束 -->

<!-- 来自 page_0359.md 全文开始 -->

# Page 0359

## 原始文本块

### block_p0359_b001

2026 年5 月3 日

### block_p0359_b002

角色示例身份主要动作

### block_p0359_b003

一线员工杨卓提交日报、确认Staff Schema、接

### block_p0359_b004

收任务

### block_p0359_b005

部门负责人架构组Manager查看部门汇总、确认上推事项

### block_p0359_b006

老板/ 高管Executive 用户接收决策卡片、选择方案

### block_p0359_b007

系统管理员/ 演示者Demo 操作人初始化数据、触发定时任务、检查

### block_p0359_b008

数据库

### block_p0359_b009

对应Agent 节点如下：

### block_p0359_b010

Agent 节点绑定对象Demo 职责

### block_p0359_b011

Staff Agent杨卓整理员工日报，提交Staff Schema，

### block_p0359_b012

查询任务

### block_p0359_b013

Manager Agent架构组读取部门StaffSchema，生成

### block_p0359_b014

Manager Schema

### block_p0359_b015

Executive Agent老板读取部门汇总，生成老板决策项

### block_p0359_b016

Dream组织级节点生成组织摘要、风险和任务草案

### block_p0359_b017

Demo 中不需要真实接入全公司员工。可以只模拟一个部门、一个员工、一个Manager、

### block_p0359_b018

一个老板，但系统数据结构应按正式链路设计，避免做成一次性假数据演示。

### block_p0359_b019

17.3Demo 前置数据

### block_p0359_b020

Demo 前需要准备一组最小可运行数据。

### block_p0359_b021

17.3.1组织与用户数据

### block_p0359_b022

至少准备：

### block_p0359_b023

数据示例

### block_p0359_b024

组织AutoMage Demo 公司

### block_p0359_b025

部门架构组

### block_p0359_b026

员工杨卓

### block_p0359_b027

Manager架构组负责人

### block_p0359_b028

Executive老板/ 高管用户

### block_p0359_b029

示例：

### block_p0359_b030

org_id = 1

### block_p0359_b031

department_id = 12

### block_p0359_b032

staff_user_id = 10086

### block_p0359_b033

manager_user_id = 20001

### block_p0359_b034

executive_user_id = 30001

### block_p0359_b035

17.3.2Agent 节点数据

### block_p0359_b036

至少准备三个Agent 节点：

### block_p0359_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0359_b038

AutoMage-2-MVP 架构设计文档·杨卓359

### block_p0359_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 359

## 表格

无。

## 备注

无。

<!-- 来自 page_0359.md 全文结束 -->

<!-- 来自 page_0360.md 全文开始 -->

# Page 0360

## 原始文本块

### block_p0360_b001

2026 年5 月3 日

### block_p0360_b002

staff_node_10086

### block_p0360_b003

manager_node_dept_12

### block_p0360_b004

executive_node_org_1

### block_p0360_b005

对应绑定关系：

### block_p0360_b006

node_idAgent 类型绑定对象

### block_p0360_b007

staff_node_10086Staff Agent杨卓

### block_p0360_b008

manager_node_dept_12Manager Agent架构组

### block_p0360_b009

executive_node_org_1Executive Agent组织/ 老板

### block_p0360_b010

如果当前还没有agent_nodes 表，可以先在Mock 配置或meta 中维护节点信息。但接

### block_p0360_b011

口返回和日志中应保持节点ID 一致，方便后续迁移到正式表。

### block_p0360_b012

17.3.3Schema 与模板数据

### block_p0360_b013

至少准备以下Schema：

### block_p0360_b014

Schema用途

### block_p0360_b015

schema_v1_staff员工日报

### block_p0360_b016

schema_v1_manager部门汇总

### block_p0360_b017

schema_v1_executive老板决策

### block_p0360_b018

schema_v1_task任务

### block_p0360_b019

schema_v1_incident异常

### block_p0360_b020

如果当前使用form_templates 承载模板，建议创建对应模板记录：

### block_p0360_b021

模板说明

### block_p0360_b022

Staff Daily Report Template员工日报模板

### block_p0360_b023

Manager Daily Summary Template部门汇总模板

### block_p0360_b024

Executive Decision Template老板决策模板

### block_p0360_b025

17.3.4Demo 业务场景数据

### block_p0360_b026

建议Demo 使用一个清晰、具体、能体现三级决策价值的场景：

### block_p0360_b027

当前Agent mock 流程中已经存在decision_logs 概念，

### block_p0360_b028

但正式DDL 尚未建立独立决策表。

### block_p0360_b029

如果不确认该结构，Executive 决策确认和任务下发链路会受影响。

### block_p0360_b030

这个场景适合Demo 的原因是：

### block_p0360_b031

1. 它来自一线开发工作。

### block_p0360_b032

2. 它会影响部门汇总。

### block_p0360_b033

3. 它需要老板或项目负责人确认。

### block_p0360_b034

4. 它可以整理成A/B 方案。

### block_p0360_b035

5. 它能在确认后生成明确任务。

### block_p0360_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0360_b037

AutoMage-2-MVP 架构设计文档·杨卓360

### block_p0360_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 360

## 表格

无。

## 备注

无。

<!-- 来自 page_0360.md 全文结束 -->

<!-- 来自 page_0361.md 全文开始 -->

# Page 0361

## 原始文本块

### block_p0361_b001

2026 年5 月3 日

### block_p0361_b002

6. 它能体现数据库、Agent、任务和审计之间的闭环。

### block_p0361_b003

老板决策项可以设计为：

### block_p0361_b004

是否新增独立decision_logs 表？

### block_p0361_b005

方案：

### block_p0361_b006

方案内容

### block_p0361_b007

方案A新增独立decision_logs / decisions 表

### block_p0361_b008

方案B暂时复用audit_logs 和tasks.meta

### block_p0361_b009

推荐方案：

### block_p0361_b010

方案A

### block_p0361_b011

17.4Demo 流程总览

### block_p0361_b012

完整Demo 分为12 步：

### block_p0361_b013

Step 1：Staff Agent 初始化

### block_p0361_b014

Step 2：员工提交每日工作Schema

### block_p0361_b015

Step 3：Staff Schema 写入数据库

### block_p0361_b016

Step 4：Manager Agent 定时读取部门数据

### block_p0361_b017

Step 5：Manager 生成部门汇总Schema

### block_p0361_b018

Step 6：Executive Agent 读取部门汇总

### block_p0361_b019

Step 7：Dream 生成老板决策项

### block_p0361_b020

Step 8：IM 推送老板决策卡片

### block_p0361_b021

Step 9：老板选择方案

### block_p0361_b022

Step 10：系统自动生成任务

### block_p0361_b023

Step 11：任务下发到Staff Agent

### block_p0361_b024

Step 12：员工查询今日任务

### block_p0361_b025

Demo 主链路图如下：

### block_p0361_b026

杨卓

### block_p0361_b027

↓

### block_p0361_b028

Staff Agent

### block_p0361_b029

↓

### block_p0361_b030

schema_v1_staff

### block_p0361_b031

↓

### block_p0361_b032

/api/v1/report/staff

### block_p0361_b033

↓

### block_p0361_b034

work_records / work_record_items

### block_p0361_b035

↓

### block_p0361_b036

Manager Agent

### block_p0361_b037

↓

### block_p0361_b038

schema_v1_manager

### block_p0361_b039

↓

### block_p0361_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0361_b041

AutoMage-2-MVP 架构设计文档·杨卓361

### block_p0361_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 361

## 表格

无。

## 备注

无。

<!-- 来自 page_0361.md 全文结束 -->

<!-- 来自 page_0362.md 全文开始 -->

# Page 0362

## 原始文本块

### block_p0362_b001

2026 年5 月3 日

### block_p0362_b002

/api/v1/report/manager

### block_p0362_b003

↓

### block_p0362_b004

summaries / summary_source_links

### block_p0362_b005

↓

### block_p0362_b006

Executive Agent / Dream

### block_p0362_b007

↓

### block_p0362_b008

schema_v1_executive

### block_p0362_b009

↓

### block_p0362_b010

老板决策卡片

### block_p0362_b011

↓

### block_p0362_b012

/api/v1/decision/commit

### block_p0362_b013

↓

### block_p0362_b014

decisions / tasks / task_assignments

### block_p0362_b015

↓

### block_p0362_b016

Staff Agent 查询任务

### block_p0362_b017

17.5Step 1：Staff Agent 初始化

### block_p0362_b018

17.5.1目标

### block_p0362_b019

验证Staff Agent 可以正确识别当前用户、组织、部门和权限范围。

### block_p0362_b020

17.5.2调用接口

### block_p0362_b021

POST /api/v1/agent/init

### block_p0362_b022

请求示例：

### block_p0362_b023

{

### block_p0362_b024

"org_id": 1,

### block_p0362_b025

"user_id": 10086,

### block_p0362_b026

"agent_type": "staff",

### block_p0362_b027

"client_type": "im",

### block_p0362_b028

"client_user_id": "feishu_open_id_yangzhuo",

### block_p0362_b029

"agent_template_version": "staff_agent_v0.1"

### block_p0362_b030

}

### block_p0362_b031

响应示例：

### block_p0362_b032

{

### block_p0362_b033

"success": true,

### block_p0362_b034

"code": "OK",

### block_p0362_b035

"message": "success",

### block_p0362_b036

"data": {

### block_p0362_b037

"agent_session_id": "agent_sess_001",

### block_p0362_b038

"node_id": "staff_node_10086",

### block_p0362_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0362_b040

AutoMage-2-MVP 架构设计文档·杨卓362

### block_p0362_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 362

## 表格

无。

## 备注

无。

<!-- 来自 page_0362.md 全文结束 -->

<!-- 来自 page_0363.md 全文开始 -->

# Page 0363

## 原始文本块

### block_p0363_b001

2026 年5 月3 日

### block_p0363_b002

"agent_type": "staff",

### block_p0363_b003

"org_id": 1,

### block_p0363_b004

"user_id": 10086,

### block_p0363_b005

"department_id": 12,

### block_p0363_b006

"role": "staff",

### block_p0363_b007

"permissions": {

### block_p0363_b008

"can_read_own_reports": true,

### block_p0363_b009

"can_submit_staff_report": true,

### block_p0363_b010

"can_read_department_reports": false,

### block_p0363_b011

"can_generate_manager_summary": false

### block_p0363_b012

},

### block_p0363_b013

"supported_schemas": [

### block_p0363_b014

{

### block_p0363_b015

"schema_id": "schema_v1_staff",

### block_p0363_b016

"schema_version": "1.0.0"

### block_p0363_b017

}

### block_p0363_b018

]

### block_p0363_b019

}

### block_p0363_b020

}

### block_p0363_b021

17.5.3成功表现

### block_p0363_b022

Staff Agent 能明确知道：

### block_p0363_b023

1. 当前用户是杨卓。

### block_p0363_b024

2. 当前组织是AutoMage Demo 公司。

### block_p0363_b025

3. 当前部门是架构组。

### block_p0363_b026

4. 当前节点是staff_node_10086。

### block_p0363_b027

5. 当前Agent 只能提交本人日报和查询本人任务。

### block_p0363_b028

6. 当前Agent 不能读取部门汇总和他人日报。

### block_p0363_b029

Demo 展示时，可以让Staff Agent 返回一句：

### block_p0363_b030

杨卓，你好。我已初始化为你的Staff Agent。今天我会协助你提交工作记录，并在任务下发后提醒你处理。

### block_p0363_b031

17.6Step 2：员工提交每日工作Schema

### block_p0363_b032

17.6.1目标

### block_p0363_b033

验证Staff Agent 可以把员工自然语言输入整理为标准Staff Schema，并让员工确认。

### block_p0363_b034

17.6.2员工输入示例

### block_p0363_b035

今天完成了Staff 日报Schema 的字段整理，补充了签名字段和数据库映射说明。

### block_p0363_b036

遇到的问题是Decision 表结构还没确认，目前DDL 里没有独立decision_logs 表。

### block_p0363_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0363_b038

AutoMage-2-MVP 架构设计文档·杨卓363

### block_p0363_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 363

## 表格

无。

## 备注

无。

<!-- 来自 page_0363.md 全文结束 -->

<!-- 来自 page_0364.md 全文开始 -->

# Page 0364

## 原始文本块

### block_p0364_b001

2026 年5 月3 日

### block_p0364_b002

我已经先在文档里列了最小字段草案，但需要后端确认是否新增独立表。

### block_p0364_b003

明天计划继续完善Manager Schema 和Executive 决策链路。

### block_p0364_b004

17.6.3Staff Agent 整理结果

### block_p0364_b005

Staff Agent 应整理出如下结构：

### block_p0364_b006

{

### block_p0364_b007

"schema_id": "schema_v1_staff",

### block_p0364_b008

"schema_version": "1.0.0",

### block_p0364_b009

"timestamp": "2026-05-03T18:12:30+08:00",

### block_p0364_b010

"org_id": 1,

### block_p0364_b011

"department_id": 12,

### block_p0364_b012

"user_id": 10086,

### block_p0364_b013

"node_id": "staff_node_10086",

### block_p0364_b014

"record_date": "2026-05-03",

### block_p0364_b015

"work_progress": [

### block_p0364_b016

{

### block_p0364_b017

"title": " 完成Staff 日报Schema 字段整理",

### block_p0364_b018

"description": " 补充Staff 日报字段、签名字段和数据库映射说明。",

### block_p0364_b019

"status": "completed"

### block_p0364_b020

}

### block_p0364_b021

],

### block_p0364_b022

"issues_faced": [

### block_p0364_b023

{

### block_p0364_b024

"title": "Decision 表结构尚未确认",

### block_p0364_b025

"description": "当前DDL 中没有独立decision_logs 表，影响Executive

### block_p0364_b026

决策确认和任务来源追踪。",,→

### block_p0364_b027

"severity": "medium"

### block_p0364_b028

}

### block_p0364_b029

],

### block_p0364_b030

"solution_attempt": [

### block_p0364_b031

{

### block_p0364_b032

"issue_title": "Decision 表结构尚未确认",

### block_p0364_b033

"attempt": " 先在文档中列出Decision 最小字段草案。",

### block_p0364_b034

"result": " 等待后端确认"

### block_p0364_b035

}

### block_p0364_b036

],

### block_p0364_b037

"need_support": true,

### block_p0364_b038

"support_detail": " 需要后端确认是否新增独立decision_logs 表。",

### block_p0364_b039

"next_day_plan": [

### block_p0364_b040

{

### block_p0364_b041

"title": " 完善Manager Schema 和Executive 决策链路",

### block_p0364_b042

"priority": "high",

### block_p0364_b043

"expected_output": " 形成可用于联调的Schema 与数据库映射说明"

### block_p0364_b044

}

### block_p0364_b045

],

### block_p0364_b046

"risk_level": "medium",

### block_p0364_b047 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0364_b048

AutoMage-2-MVP 架构设计文档·杨卓364

### block_p0364_b049 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 364

## 表格

无。

## 备注

无。

<!-- 来自 page_0364.md 全文结束 -->

<!-- 来自 page_0365.md 全文开始 -->

# Page 0365

## 原始文本块

### block_p0365_b001

2026 年5 月3 日

### block_p0365_b002

"employee_comment": "Decision 表结构需要后端确认后才能定稿。",

### block_p0365_b003

"signature": {

### block_p0365_b004

"signature_required": true,

### block_p0365_b005

"signature_status": "pending",

### block_p0365_b006

"signature_source": "im"

### block_p0365_b007

},

### block_p0365_b008

"meta": {

### block_p0365_b009

"input_channel": "feishu",

### block_p0365_b010

"agent_template_version": "staff_agent_v0.1"

### block_p0365_b011

}

### block_p0365_b012

}

### block_p0365_b013

17.6.4员工确认

### block_p0365_b014

Staff Agent 展示简化确认内容：

### block_p0365_b015

我整理成以下日报，请确认：

### block_p0365_b016

今日完成：

### block_p0365_b017

- 完成Staff 日报Schema 字段整理，补充签名字段和数据库映射说明。

### block_p0365_b018

遇到问题：

### block_p0365_b019

- Decision 表结构尚未确认，当前DDL 中没有独立decision_logs 表。

### block_p0365_b020

已尝试：

### block_p0365_b021

- 已先在文档中列出Decision 最小字段草案。

### block_p0365_b022

需要支持：

### block_p0365_b023

- 需要后端确认是否新增独立decision_logs 表。

### block_p0365_b024

明日计划：

### block_p0365_b025

- 完善Manager Schema 和Executive 决策链路。

### block_p0365_b026

风险等级：medium

### block_p0365_b027

请确认是否提交。

### block_p0365_b028

员工回复：

### block_p0365_b029

确认提交

### block_p0365_b030

确认后，Staff Agent 将signature.signature_status 更新为signed，并准备提交后端。

### block_p0365_b031

17.7Step 3：Staff Schema 写入数据库

### block_p0365_b032

17.7.1目标

### block_p0365_b033

验证Staff Schema 可以通过API 校验、签名、幂等并写入数据库。

### block_p0365_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0365_b035

AutoMage-2-MVP 架构设计文档·杨卓365

### block_p0365_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 365

## 表格

无。

## 备注

无。

<!-- 来自 page_0365.md 全文结束 -->

<!-- 来自 page_0366.md 全文开始 -->

# Page 0366

## 原始文本块

### block_p0366_b001

2026 年5 月3 日

### block_p0366_b002

17.7.2调用接口

### block_p0366_b003

POST /api/v1/report/staff

### block_p0366_b004

请求头：

### block_p0366_b005

Idempotency-Key: staff_report:1:10086:2026-05-03

### block_p0366_b006

请求体：

### block_p0366_b007

{

### block_p0366_b008

"schema": {

### block_p0366_b009

"schema_id": "schema_v1_staff",

### block_p0366_b010

"schema_version": "1.0.0",

### block_p0366_b011

"timestamp": "2026-05-03T18:12:30+08:00",

### block_p0366_b012

"org_id": 1,

### block_p0366_b013

"department_id": 12,

### block_p0366_b014

"user_id": 10086,

### block_p0366_b015

"node_id": "staff_node_10086",

### block_p0366_b016

"record_date": "2026-05-03",

### block_p0366_b017

"work_progress": [

### block_p0366_b018

{

### block_p0366_b019

"title": " 完成Staff 日报Schema 字段整理",

### block_p0366_b020

"description": " 补充Staff 日报字段、签名字段和数据库映射说明。",

### block_p0366_b021

"status": "completed"

### block_p0366_b022

}

### block_p0366_b023

],

### block_p0366_b024

"issues_faced": [

### block_p0366_b025

{

### block_p0366_b026

"title": "Decision 表结构尚未确认",

### block_p0366_b027

"description": "当前DDL 中没有独立decision_logs 表，影响Executive

### block_p0366_b028

决策确认和任务来源追踪。",,→

### block_p0366_b029

"severity": "medium"

### block_p0366_b030

}

### block_p0366_b031

],

### block_p0366_b032

"solution_attempt": [

### block_p0366_b033

{

### block_p0366_b034

"issue_title": "Decision 表结构尚未确认",

### block_p0366_b035

"attempt": " 先在文档中列出Decision 最小字段草案。",

### block_p0366_b036

"result": " 等待后端确认"

### block_p0366_b037

}

### block_p0366_b038

],

### block_p0366_b039

"need_support": true,

### block_p0366_b040

"support_detail": " 需要后端确认是否新增独立decision_logs 表。",

### block_p0366_b041

"next_day_plan": [

### block_p0366_b042

{

### block_p0366_b043

"title": " 完善Manager Schema 和Executive 决策链路",

### block_p0366_b044

"priority": "high",

### block_p0366_b045 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0366_b046

AutoMage-2-MVP 架构设计文档·杨卓366

### block_p0366_b047 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 366

## 表格

无。

## 备注

无。

<!-- 来自 page_0366.md 全文结束 -->

<!-- 来自 page_0367.md 全文开始 -->

# Page 0367

## 原始文本块

### block_p0367_b001

2026 年5 月3 日

### block_p0367_b002

"expected_output": " 形成可用于联调的Schema 与数据库映射说明"

### block_p0367_b003

}

### block_p0367_b004

],

### block_p0367_b005

"risk_level": "medium",

### block_p0367_b006

"employee_comment": "Decision 表结构需要后端确认后才能定稿。",

### block_p0367_b007

"signature": {

### block_p0367_b008

"signature_required": true,

### block_p0367_b009

"signature_status": "signed",

### block_p0367_b010

"signed_by": 10086,

### block_p0367_b011

"signed_at": "2026-05-03T18:13:00+08:00",

### block_p0367_b012

"payload_hash": "sha256:staff_report_demo_hash",

### block_p0367_b013

"signature_source": "im"

### block_p0367_b014

},

### block_p0367_b015

"meta": {

### block_p0367_b016

"input_channel": "feishu",

### block_p0367_b017

"agent_template_version": "staff_agent_v0.1"

### block_p0367_b018

}

### block_p0367_b019

}

### block_p0367_b020

}

### block_p0367_b021

17.7.3后端处理

### block_p0367_b022

后端应完成：

### block_p0367_b023

1. 校验Staff Agent 权限。

### block_p0367_b024

2. 校验schema_id = schema_v1_staff。

### block_p0367_b025

3. 校验user_id = 当前用户。

### block_p0367_b026

4. 校验department_id = 当前用户部门。

### block_p0367_b027

5. 校验必填字段。

### block_p0367_b028

6. 校验need_support = true 时support_detail 必填。

### block_p0367_b029

7. 校验签名人等于员工本人。

### block_p0367_b030

8. 校验幂等键。

### block_p0367_b031

9. 写入work_records。

### block_p0367_b032

10. 写入work_record_items。

### block_p0367_b033

11. 记录审计日志。

### block_p0367_b034

12. 由于存在支持需求，可生成异常候选或Incident。

### block_p0367_b035

17.7.4响应示例

### block_p0367_b036

{

### block_p0367_b037

"success": true,

### block_p0367_b038

"code": "OK",

### block_p0367_b039

"message": "Staff 日报提交成功",

### block_p0367_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0367_b041

AutoMage-2-MVP 架构设计文档·杨卓367

### block_p0367_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 367

## 表格

无。

## 备注

无。

<!-- 来自 page_0367.md 全文结束 -->

<!-- 来自 page_0368.md 全文开始 -->

# Page 0368

## 原始文本块

### block_p0368_b001

2026 年5 月3 日

### block_p0368_b002

"data": {

### block_p0368_b003

"work_record_id": 301,

### block_p0368_b004

"record_date": "2026-05-03",

### block_p0368_b005

"status": "submitted",

### block_p0368_b006

"created_incident_ids": [501],

### block_p0368_b007

"created_task_ids": [],

### block_p0368_b008

"audit_log_id": 7001

### block_p0368_b009

}

### block_p0368_b010

}

### block_p0368_b011

17.7.5成功表现

### block_p0368_b012

数据库中应能看到：

### block_p0368_b013

表结果

### block_p0368_b014

work_records新增一条员工日报主记录

### block_p0368_b015

work_record_items新增多条字段明细

### block_p0368_b016

incidents可选新增一条支持需求或阻塞异常

### block_p0368_b017

audit_logs记录Staff 日报提交和签名动作

### block_p0368_b018

17.8Step 4：Manager Agent 定时读取部门数据

### block_p0368_b019

17.8.1目标

### block_p0368_b020

验证Manager Agent 可以读取本部门Staff Schema，但不能读取其他部门或未确认数据。

### block_p0368_b021

17.8.2触发方式

### block_p0368_b022

Demo 中可以用按钮或脚本模拟定时任务：

### block_p0368_b023

触发Manager Agent 汇总架构组2026-05-03 日报

### block_p0368_b024

17.8.3Manager Agent 读取条件

### block_p0368_b025

Manager Agent 应读取：

### block_p0368_b026

org_id = 1

### block_p0368_b027

department_id = 12

### block_p0368_b028

record_date = 2026-05-03

### block_p0368_b029

status = submitted / confirmed

### block_p0368_b030

deleted_at is null

### block_p0368_b031

至少读取到刚才的work_record_id = 301。

### block_p0368_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0368_b033

AutoMage-2-MVP 架构设计文档·杨卓368

### block_p0368_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 368

## 表格

无。

## 备注

无。

<!-- 来自 page_0368.md 全文结束 -->

<!-- 来自 page_0369.md 全文开始 -->

# Page 0369

## 原始文本块

### block_p0369_b001

2026 年5 月3 日

### block_p0369_b002

17.8.4读取结果示例

### block_p0369_b003

{

### block_p0369_b004

"records": [

### block_p0369_b005

{

### block_p0369_b006

"work_record_id": 301,

### block_p0369_b007

"user_id": 10086,

### block_p0369_b008

"record_date": "2026-05-03",

### block_p0369_b009

"work_progress": [

### block_p0369_b010

{

### block_p0369_b011

"title": " 完成Staff 日报Schema 字段整理",

### block_p0369_b012

"status": "completed"

### block_p0369_b013

}

### block_p0369_b014

],

### block_p0369_b015

"issues_faced": [

### block_p0369_b016

{

### block_p0369_b017

"title": "Decision 表结构尚未确认",

### block_p0369_b018

"severity": "medium"

### block_p0369_b019

}

### block_p0369_b020

],

### block_p0369_b021

"need_support": true,

### block_p0369_b022

"support_detail": " 需要后端确认是否新增独立decision_logs 表。",

### block_p0369_b023

"risk_level": "medium"

### block_p0369_b024

}

### block_p0369_b025

]

### block_p0369_b026

}

### block_p0369_b027

17.8.5成功表现

### block_p0369_b028

Manager Agent 应能说明：

### block_p0369_b029

已读取架构组2026-05-03 的1 条有效Staff 日报。

### block_p0369_b030

其中1 条包含支持需求，主要问题为Decision 表结构尚未确认。

### block_p0369_b031

同时，后端应拒绝Manager Agent 读取其他部门员工明细。这个权限点可以作为可选演

### block_p0369_b032

示，不建议占用主Demo 时间。

### block_p0369_b033

17.9Step 5：Manager 生成部门汇总Schema

### block_p0369_b034

17.9.1目标

### block_p0369_b035

验证Manager Agent 可以将Staff Schema 聚合为Manager Schema，并识别出需要上推

### block_p0369_b036

老板的事项。

### block_p0369_b037

17.9.2Manager Schema 示例

### block_p0369_b038

{

### block_p0369_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0369_b040

AutoMage-2-MVP 架构设计文档·杨卓369

### block_p0369_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 369

## 表格

无。

## 备注

无。

<!-- 来自 page_0369.md 全文结束 -->

<!-- 来自 page_0370.md 全文开始 -->

# Page 0370

## 原始文本块

### block_p0370_b001

2026 年5 月3 日

### block_p0370_b002

"schema_id": "schema_v1_manager",

### block_p0370_b003

"schema_version": "1.0.0",

### block_p0370_b004

"timestamp": "2026-05-03T21:10:00+08:00",

### block_p0370_b005

"org_id": 1,

### block_p0370_b006

"dept_id": 12,

### block_p0370_b007

"manager_user_id": 20001,

### block_p0370_b008

"manager_node_id": "manager_node_dept_12",

### block_p0370_b009

"summary_date": "2026-05-03",

### block_p0370_b010

"staff_report_count": 1,

### block_p0370_b011

"missing_report_count": 0,

### block_p0370_b012

"missing_staff_ids": [],

### block_p0370_b013

"overall_health": "yellow",

### block_p0370_b014

"aggregated_summary": "今日架构组主要完成Staff 日报Schema 字段整理，

### block_p0370_b015

并补充签名字段和数据库映射说明。当前主要阻塞点是Decision 表结构尚未确认，可能影响

### block_p0370_b016

Executive 决策确认、任务来源追踪和审计闭环。",

### block_p0370_b017

,→

### block_p0370_b018

,→

### block_p0370_b019

"top_3_risks": [

### block_p0370_b020

{

### block_p0370_b021

"title": "Decision 表结构未确认",

### block_p0370_b022

"description": "当前DDL 中尚未建立独立decision_logs 表，

### block_p0370_b023

可能影响老板决策确认和任务生成链路。",,→

### block_p0370_b024

"severity": "high",

### block_p0370_b025

"source_record_ids": [301],

### block_p0370_b026

"suggested_action": " 建议确认是否新增独立Decision 记录表。"

### block_p0370_b027

}

### block_p0370_b028

],

### block_p0370_b029

"workforce_efficiency": {

### block_p0370_b030

"score": 80,

### block_p0370_b031

"level": "medium",

### block_p0370_b032

"basis": " 今日有效日报1 条，主要工作按计划完成，但存在影响主链路的结构确认问题。"

### block_p0370_b033

},

### block_p0370_b034

"pending_approvals": 1,

### block_p0370_b035

"highlight_staff": [

### block_p0370_b036

{

### block_p0370_b037

"user_id": 10086,

### block_p0370_b038

"display_name": " 杨卓",

### block_p0370_b039

"reason": " 完成Staff Schema 字段整理，并主动提出Decision 表结构缺口。",

### block_p0370_b040

"source_record_ids": [301]

### block_p0370_b041

}

### block_p0370_b042

],

### block_p0370_b043

"blocked_items": [

### block_p0370_b044

{

### block_p0370_b045

"title": "Decision 表结构未定",

### block_p0370_b046

"description": "当前无法确定老板确认结果应落入独立决策表，还是暂时复用audit_logs 和

### block_p0370_b047

tasks.meta。",,→

### block_p0370_b048

"owner_user_id": 20002,

### block_p0370_b049

"severity": "high",

### block_p0370_b050

"need_support": true,

### block_p0370_b051 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0370_b052

AutoMage-2-MVP 架构设计文档·杨卓370

### block_p0370_b053 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 370

## 表格

无。

## 备注

无。

<!-- 来自 page_0370.md 全文结束 -->

<!-- 来自 page_0371.md 全文开始 -->

# Page 0371

## 原始文本块

### block_p0371_b001

2026 年5 月3 日

### block_p0371_b002

"suggested_next_step": " 由老板或项目负责人确认是否新增独立Decision 表。"

### block_p0371_b003

}

### block_p0371_b004

],

### block_p0371_b005

"manager_decisions": [],

### block_p0371_b006

"need_executive_decision": [

### block_p0371_b007

{

### block_p0371_b008

"decision_title": " 是否新增独立Decision 记录表",

### block_p0371_b009

"context": "当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL

### block_p0371_b010

尚未建立独立决策表。如果不新增，短期可用audit_logs 和tasks.meta 承载，

### block_p0371_b011

但后续老板决策追踪和复盘会不够清晰。",

### block_p0371_b012

,→

### block_p0371_b013

,→

### block_p0371_b014

"options": [

### block_p0371_b015

{

### block_p0371_b016

"option_id": "A",

### block_p0371_b017

"title": " 新增独立decisions / decision_logs 表",

### block_p0371_b018

"pros": [" 决策对象清晰", " 便于审计", " 方便任务来源追踪"],

### block_p0371_b019

"cons": [" 需要增加后端开发工作量"]

### block_p0371_b020

},

### block_p0371_b021

{

### block_p0371_b022

"option_id": "B",

### block_p0371_b023

"title": " 暂时复用audit_logs 和tasks.meta",

### block_p0371_b024

"pros": [" 短期开发更快"],

### block_p0371_b025

"cons": [" 决策对象不独立", " 后续统计和复盘不方便"]

### block_p0371_b026

}

### block_p0371_b027

],

### block_p0371_b028

"recommended_option": "A",

### block_p0371_b029

"reason": "AutoMage-2 的核心价值在于决策可追溯，独立决策对象更符合长期架构。",

### block_p0371_b030

"source_record_ids": [301],

### block_p0371_b031

"urgency": "high"

### block_p0371_b032

}

### block_p0371_b033

],

### block_p0371_b034

"next_day_adjustment": [

### block_p0371_b035

{

### block_p0371_b036

"title": " 优先确认Decision 数据结构",

### block_p0371_b037

"reason": " 该事项影响Executive 决策确认和任务下发闭环。",

### block_p0371_b038

"target_user_ids": [10086, 20002],

### block_p0371_b039

"priority": "high",

### block_p0371_b040

"expected_output": " 形成是否新增Decision 表的最终结论和字段草案。"

### block_p0371_b041

}

### block_p0371_b042

],

### block_p0371_b043

"source_record_ids": [301],

### block_p0371_b044

"related_task_ids": [],

### block_p0371_b045

"related_incident_ids": [501],

### block_p0371_b046

"signature": {

### block_p0371_b047

"signature_required": true,

### block_p0371_b048

"signature_status": "signed",

### block_p0371_b049

"signed_by": 20001,

### block_p0371_b050

"signed_at": "2026-05-03T21:25:00+08:00",

### block_p0371_b051 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0371_b052

AutoMage-2-MVP 架构设计文档·杨卓371

### block_p0371_b053 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 371

## 表格

无。

## 备注

无。

<!-- 来自 page_0371.md 全文结束 -->

<!-- 来自 page_0372.md 全文开始 -->

# Page 0372

## 原始文本块

### block_p0372_b001

2026 年5 月3 日

### block_p0372_b002

"payload_hash": "sha256:manager_summary_demo_hash",

### block_p0372_b003

"signature_source": "im"

### block_p0372_b004

},

### block_p0372_b005

"meta": {

### block_p0372_b006

"input_channel": "scheduled_job",

### block_p0372_b007

"agent_template_version": "manager_agent_v0.1"

### block_p0372_b008

}

### block_p0372_b009

}

### block_p0372_b010

17.9.3提交接口

### block_p0372_b011

POST /api/v1/report/manager

### block_p0372_b012

请求头：

### block_p0372_b013

Idempotency-Key: manager_summary:1:12:2026-05-03

### block_p0372_b014

17.9.4响应示例

### block_p0372_b015

{

### block_p0372_b016

"success": true,

### block_p0372_b017

"code": "OK",

### block_p0372_b018

"message": "Manager 汇总提交成功",

### block_p0372_b019

"data": {

### block_p0372_b020

"summary_id": 801,

### block_p0372_b021

"summary_type": "department_daily_summary",

### block_p0372_b022

"summary_date": "2026-05-03",

### block_p0372_b023

"status": "submitted",

### block_p0372_b024

"created_decision_candidate_ids": ["decision_tmp_001"],

### block_p0372_b025

"created_task_ids": [],

### block_p0372_b026

"audit_log_id": 7002

### block_p0372_b027

}

### block_p0372_b028

}

### block_p0372_b029

17.9.5成功表现

### block_p0372_b030

数据库中应能看到：

### block_p0372_b031

表结果

### block_p0372_b032

summaries新增部门汇总

### block_p0372_b033

summary_source_links记录summary 801 来源于work_record 301

### block_p0372_b034

audit_logs记录Manager 汇总生成和确认

### block_p0372_b035

incidents可关联更新Decision 表结构异常

### block_p0372_b036

决策候选对象可进入Executive / Dream 后续处理

### block_p0372_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0372_b038

AutoMage-2-MVP 架构设计文档·杨卓372

### block_p0372_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 372

## 表格

无。

## 备注

无。

<!-- 来自 page_0372.md 全文结束 -->

<!-- 来自 page_0373.md 全文开始 -->

# Page 0373

## 原始文本块

### block_p0373_b001

2026 年5 月3 日

### block_p0373_b002

17.10Step 6：Executive Agent 读取部门汇总

### block_p0373_b003

17.10.1目标

### block_p0373_b004

验证Executive Agent 可以读取Manager Summary，并基于部门汇总生成组织级视角。

### block_p0373_b005

17.10.2读取接口

### block_p0373_b006

GET /api/v1/summaries?org_id=1&summary_type=department_daily_summary&summary_date=2026-05-03

### block_p0373_b007

17.10.3返回数据

### block_p0373_b008

至少返回：

### block_p0373_b009

{

### block_p0373_b010

"summary_id": 801,

### block_p0373_b011

"org_id": 1,

### block_p0373_b012

"department_id": 12,

### block_p0373_b013

"summary_type": "department_daily_summary",

### block_p0373_b014

"scope_type": "department",

### block_p0373_b015

"summary_date": "2026-05-03",

### block_p0373_b016

"title": "2026-05-03 架构组部门日报",

### block_p0373_b017

"content": "今日架构组主要完成Staff 日报Schema 字段整理，并补充签名字段和数据库映射说明。

### block_p0373_b018

当前主要阻塞点是Decision 表结构尚未确认。",,→

### block_p0373_b019

"source_count": 1,

### block_p0373_b020

"status": "submitted",

### block_p0373_b021

"meta": {

### block_p0373_b022

"schema_id": "schema_v1_manager",

### block_p0373_b023

"overall_health": "yellow",

### block_p0373_b024

"top_3_risks": [

### block_p0373_b025

{

### block_p0373_b026

"title": "Decision 表结构未确认",

### block_p0373_b027

"severity": "high"

### block_p0373_b028

}

### block_p0373_b029

],

### block_p0373_b030

"need_executive_decision": [

### block_p0373_b031

{

### block_p0373_b032

"decision_title": " 是否新增独立Decision 记录表",

### block_p0373_b033

"recommended_option": "A"

### block_p0373_b034

}

### block_p0373_b035

]

### block_p0373_b036

}

### block_p0373_b037

}

### block_p0373_b038

17.10.4成功表现

### block_p0373_b039

Executive Agent 应能输出：

### block_p0373_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0373_b041

AutoMage-2-MVP 架构设计文档·杨卓373

### block_p0373_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 373

## 表格

无。

## 备注

无。

<!-- 来自 page_0373.md 全文结束 -->

<!-- 来自 page_0374.md 全文开始 -->

# Page 0374

## 原始文本块

### block_p0374_b001

2026 年5 月3 日

### block_p0374_b002

已读取1 条部门汇总。架构组整体状态为yellow，当前最关键风险是Decision 表结构未确认。该事项已由

### block_p0374_b003

Manager 上推为老板待决策事项。,→

### block_p0374_b004

17.11Step 7：Dream 生成老板决策项

### block_p0374_b005

17.11.1目标

### block_p0374_b006

验证Dream 可以基于Manager Schema 生成Executive Schema 和老板决策卡片。

### block_p0374_b007

17.11.2Executive Schema 示例

### block_p0374_b008

{

### block_p0374_b009

"schema_id": "schema_v1_executive",

### block_p0374_b010

"schema_version": "1.0.0",

### block_p0374_b011

"timestamp": "2026-05-04T08:00:00+08:00",

### block_p0374_b012

"org_id": 1,

### block_p0374_b013

"executive_user_id": 30001,

### block_p0374_b014

"executive_node_id": "executive_node_org_1",

### block_p0374_b015

"summary_date": "2026-05-03",

### block_p0374_b016

"business_summary": "昨日架构组完成Staff 日报Schema 字段整理和数据库映射说明，整体推进正常。

### block_p0374_b017

当前最主要风险是Decision 表结构尚未确认，可能影响老板决策确认、

### block_p0374_b018

任务来源追踪和后续审计闭环。",

### block_p0374_b019

,→

### block_p0374_b020

,→

### block_p0374_b021

"key_risks": [

### block_p0374_b022

{

### block_p0374_b023

"title": "Decision 表结构未确认",

### block_p0374_b024

"description": "当前DDL 尚未建立独立Decision 记录表，若继续复用audit_logs 和

### block_p0374_b025

tasks.meta，短期可跑通，但长期追踪和复盘不清晰。",,→

### block_p0374_b026

"severity": "high",

### block_p0374_b027

"affected_departments": [12],

### block_p0374_b028

"source_summary_ids": [801],

### block_p0374_b029

"suggested_action": " 建议老板确认是否新增独立Decision 表。"

### block_p0374_b030

}

### block_p0374_b031

],

### block_p0374_b032

"decision_required": true,

### block_p0374_b033

"decision_items": [

### block_p0374_b034

{

### block_p0374_b035

"decision_id": "decision_0001",

### block_p0374_b036

"title": " 是否新增独立Decision 记录表",

### block_p0374_b037

"context": "当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL

### block_p0374_b038

尚未建立独立决策表。如果不新增，短期可用audit_logs 和tasks.meta 承载，

### block_p0374_b039

但后续老板决策追踪和复盘会不够清晰。",

### block_p0374_b040

,→

### block_p0374_b041

,→

### block_p0374_b042

"decision_level": "L3",

### block_p0374_b043

"urgency": "high",

### block_p0374_b044

"option_a": {

### block_p0374_b045

"option_id": "A",

### block_p0374_b046

"title": " 新增独立decisions / decision_logs 表",

### block_p0374_b047 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0374_b048

AutoMage-2-MVP 架构设计文档·杨卓374

### block_p0374_b049 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 374

## 表格

无。

## 备注

无。

<!-- 来自 page_0374.md 全文结束 -->

<!-- 来自 page_0375.md 全文开始 -->

# Page 0375

## 原始文本块

### block_p0375_b001

2026 年5 月3 日

### block_p0375_b002

"description": " 为老板决策、候选方案、确认结果和任务来源建立独立数据对象。",

### block_p0375_b003

"pros": [" 决策对象清晰", " 便于审计", " 方便任务来源追踪"],

### block_p0375_b004

"cons": [" 需要增加后端开发工作量"]

### block_p0375_b005

},

### block_p0375_b006

"option_b": {

### block_p0375_b007

"option_id": "B",

### block_p0375_b008

"title": " 暂时复用audit_logs 和tasks.meta",

### block_p0375_b009

"description": "MVP 阶段不新增表，先用审计日志和任务meta 承载决策结果。",

### block_p0375_b010

"pros": [" 短期开发更快", " 减少表结构变更"],

### block_p0375_b011

"cons": [" 决策对象不独立", " 后续统计和复盘不方便"]

### block_p0375_b012

},

### block_p0375_b013

"recommended_option": "A",

### block_p0375_b014

"reasoning_summary": "AutoMage-2 的核心价值在于决策可追溯，独立Decision

### block_p0375_b015

表更利于后续任务生成、老板看板和审计复盘。",,→

### block_p0375_b016

"expected_impact": {

### block_p0375_b017

"cost": "medium",

### block_p0375_b018

"timeline": " 短期增加0.5-1 天后端工作量",

### block_p0375_b019

"risk": " 降低后续决策追踪混乱风险",

### block_p0375_b020

"affected_modules": ["database", "backend", "executive_agent"]

### block_p0375_b021

},

### block_p0375_b022

"generated_tasks": [

### block_p0375_b023

{

### block_p0375_b024

"task_title": " 补充decisions 表结构草案",

### block_p0375_b025

"task_description": "根据老板确认的方案A，设计独立decisions 表，字段需覆盖决策标题、

### block_p0375_b026

背景、候选方案、推荐方案、确认人、确认时间和生成任务。",,→

### block_p0375_b027

"assignee_role": "backend",

### block_p0375_b028

"department_id": 12,

### block_p0375_b029

"priority": "high",

### block_p0375_b030

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0375_b031

"source_decision_id": "decision_0001"

### block_p0375_b032

}

### block_p0375_b033

],

### block_p0375_b034

"source_summary_ids": [801]

### block_p0375_b035

}

### block_p0375_b036

],

### block_p0375_b037

"source_summary_ids": [801],

### block_p0375_b038

"human_confirm_status": "pending",

### block_p0375_b039

"confirmed_by": null,

### block_p0375_b040

"confirmed_at": null,

### block_p0375_b041

"confirmed_option": null,

### block_p0375_b042

"signature": {

### block_p0375_b043

"signature_required": true,

### block_p0375_b044

"signature_status": "pending",

### block_p0375_b045

"signature_source": "im"

### block_p0375_b046

}

### block_p0375_b047

}

### block_p0375_b048 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0375_b049

AutoMage-2-MVP 架构设计文档·杨卓375

### block_p0375_b050 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 375

## 表格

无。

## 备注

无。

<!-- 来自 page_0375.md 全文结束 -->

<!-- 来自 page_0376.md 全文开始 -->

# Page 0376

## 原始文本块

### block_p0376_b001

2026 年5 月3 日

### block_p0376_b002

17.11.3成功表现

### block_p0376_b003

系统应生成：

### block_p0376_b004

对象结果

### block_p0376_b005

Executive Schema包含组织摘要、关键风险、决策项

### block_p0376_b006

Decision 候选对象decision_0001，状态为pending

### block_p0376_b007

任务草案存在于决策项中，但尚未正式下发

### block_p0376_b008

审计日志记录Dream / Executive 生成决策项

### block_p0376_b009

注意：此时任务还不能正式创建，因为老板尚未确认。

### block_p0376_b010

17.12Step 8：IM 推送老板决策卡片

### block_p0376_b011

17.12.1目标

### block_p0376_b012

验证Executive Agent 可以将Executive Schema 转换为老板可读的IM 决策卡片。

### block_p0376_b013

17.12.2决策卡片内容

### block_p0376_b014

【今日老板待决策】

### block_p0376_b015

日期：2026-05-04

### block_p0376_b016

状态：需要确认1 项决策

### block_p0376_b017

一、公司整体情况

### block_p0376_b018

昨日架构组完成Staff 日报Schema 字段整理和数据库映射说明，整体推进正常。当前主要风险是

### block_p0376_b019

Decision 表结构尚未确认，可能影响老板决策确认、任务来源追踪和审计闭环。,→

### block_p0376_b020

二、关键风险

### block_p0376_b021

风险：Decision 表结构未确认

### block_p0376_b022

等级：高

### block_p0376_b023

影响：可能影响Executive 决策确认、任务下发和后续复盘。

### block_p0376_b024

三、待决策事项

### block_p0376_b025

事项：是否新增独立Decision 记录表

### block_p0376_b026

背景：

### block_p0376_b027

当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL 尚未建立独立决策表。

### block_p0376_b028

方案A：新增独立decisions / decision_logs 表

### block_p0376_b029

优点：决策对象清晰、便于审计、方便任务来源追踪

### block_p0376_b030

缺点：需要增加后端开发工作量

### block_p0376_b031

方案B：暂时复用audit_logs 和tasks.meta

### block_p0376_b032

优点：短期开发更快、减少表结构变更

### block_p0376_b033

缺点：决策对象不独立，后续统计和复盘不方便

### block_p0376_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0376_b035

AutoMage-2-MVP 架构设计文档·杨卓376

### block_p0376_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 376

## 表格

无。

## 备注

无。

<!-- 来自 page_0376.md 全文结束 -->

<!-- 来自 page_0377.md 全文开始 -->

# Page 0377

## 原始文本块

### block_p0377_b001

2026 年5 月3 日

### block_p0377_b002

推荐：方案A

### block_p0377_b003

理由：AutoMage-2 的核心价值在于决策可追溯，独立Decision 表更利于后续任务生成、

### block_p0377_b004

老板看板和审计复盘。,→

### block_p0377_b005

确认后将生成任务：

### block_p0377_b006

- 补充decisions 表结构草案

### block_p0377_b007

- 负责人角色：后端

### block_p0377_b008

- 截止时间：今日18:00

### block_p0377_b009

17.12.3卡片按钮

### block_p0377_b010

建议按钮：

### block_p0377_b011

按钮动作

### block_p0377_b012

选择方案Aaction = confirm，confirmed_option = A

### block_p0377_b013

选择方案Baction = confirm，confirmed_option = B

### block_p0377_b014

需要补充信息action = need_more_info

### block_p0377_b015

暂不处理action = reject 或cancel

### block_p0377_b016

查看来源展示source_summary_ids = [801]

### block_p0377_b017

17.12.4成功表现

### block_p0377_b018

老板能在IM 中看到：

### block_p0377_b019

1. 为什么需要决策。

### block_p0377_b020

2. 有哪些方案。

### block_p0377_b021

3. Agent 推荐哪个方案。

### block_p0377_b022

4. 推荐理由是什么。

### block_p0377_b023

5. 确认后会生成什么任务。

### block_p0377_b024

17.13Step 9：老板选择方案

### block_p0377_b025

17.13.1目标

### block_p0377_b026

验证老板确认动作可以被后端记录，并触发决策状态变化。

### block_p0377_b027

17.13.2老板操作

### block_p0377_b028

老板点击：

### block_p0377_b029

选择方案A

### block_p0377_b030

17.13.3调用接口

### block_p0377_b031

POST /api/v1/decision/commit

### block_p0377_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0377_b033

AutoMage-2-MVP 架构设计文档·杨卓377

### block_p0377_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 377

## 表格

无。

## 备注

无。

<!-- 来自 page_0377.md 全文结束 -->

<!-- 来自 page_0378.md 全文开始 -->

# Page 0378

## 原始文本块

### block_p0378_b001

2026 年5 月3 日

### block_p0378_b002

请求头：

### block_p0378_b003

Idempotency-Key: decision_confirm:decision_0001:30001

### block_p0378_b004

请求体：

### block_p0378_b005

{

### block_p0378_b006

"decision_id": "decision_0001",

### block_p0378_b007

"org_id": 1,

### block_p0378_b008

"executive_user_id": 30001,

### block_p0378_b009

"action": "confirm",

### block_p0378_b010

"confirmed_option": "A",

### block_p0378_b011

"confirmed_custom_plan": null,

### block_p0378_b012

"confirm_source": "im",

### block_p0378_b013

"comment": " 选择方案A，新增独立Decision 记录表。",

### block_p0378_b014

"signature": {

### block_p0378_b015

"signature_required": true,

### block_p0378_b016

"signature_source": "im"

### block_p0378_b017

}

### block_p0378_b018

}

### block_p0378_b019

17.13.4后端处理

### block_p0378_b020

后端应完成：

### block_p0378_b021

1. 校验老板身份。

### block_p0378_b022

2. 校验decision_id 存在。

### block_p0378_b023

3. 校验决策状态为pending。

### block_p0378_b024

4. 校验方案A 存在。

### block_p0378_b025

5. 记录confirmed_option = A。

### block_p0378_b026

6. 记录confirmed_by = 30001。

### block_p0378_b027

7. 记录confirmed_at。

### block_p0378_b028

8. 生成payload_hash。

### block_p0378_b029

9. 更新签名状态。

### block_p0378_b030

10. 写入审计日志。

### block_p0378_b031

11. 准备生成任务。

### block_p0378_b032

17.13.5响应示例

### block_p0378_b033

{

### block_p0378_b034

"success": true,

### block_p0378_b035

"code": "OK",

### block_p0378_b036

"message": " 决策确认成功",

### block_p0378_b037

"data": {

### block_p0378_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0378_b039

AutoMage-2-MVP 架构设计文档·杨卓378

### block_p0378_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 378

## 表格

无。

## 备注

无。

<!-- 来自 page_0378.md 全文结束 -->

<!-- 来自 page_0379.md 全文开始 -->

# Page 0379

## 原始文本块

### block_p0379_b001

2026 年5 月3 日

### block_p0379_b002

"decision_id": "decision_0001",

### block_p0379_b003

"status": "confirmed",

### block_p0379_b004

"confirmed_option": "A",

### block_p0379_b005

"confirmed_by": 30001,

### block_p0379_b006

"confirmed_at": "2026-05-04T08:16:30+08:00",

### block_p0379_b007

"generated_task_ids": [9001],

### block_p0379_b008

"signature": {

### block_p0379_b009

"signature_status": "signed",

### block_p0379_b010

"payload_hash": "sha256:decision_demo_hash",

### block_p0379_b011

"verify_status": "verified"

### block_p0379_b012

},

### block_p0379_b013

"audit_log_id": 7003

### block_p0379_b014

}

### block_p0379_b015

}

### block_p0379_b016

17.14Step 10：系统自动生成任务

### block_p0379_b017

17.14.1目标

### block_p0379_b018

验证老板确认后，系统可以根据确认方案生成正式任务。

### block_p0379_b019

17.14.2任务生成规则

### block_p0379_b020

老板选择方案A 后，系统读取方案A 对应的generated_tasks，创建正式Task。

### block_p0379_b021

生成任务示例：

### block_p0379_b022

{

### block_p0379_b023

"schema_id": "schema_v1_task",

### block_p0379_b024

"schema_version": "1.0.0",

### block_p0379_b025

"org_id": 1,

### block_p0379_b026

"department_id": 12,

### block_p0379_b027

"task_title": " 补充decisions 表结构草案",

### block_p0379_b028

"task_description": "根据老板确认的方案A，设计独立decisions 表，字段需覆盖决策标题、背景、

### block_p0379_b029

候选方案、推荐方案、确认人、确认时间、来源Summary 和生成任务。",,→

### block_p0379_b030

"source_type": "executive_decision",

### block_p0379_b031

"source_id": "decision_0001",

### block_p0379_b032

"source_decision_id": "decision_0001",

### block_p0379_b033

"creator_user_id": 30001,

### block_p0379_b034

"created_by_node_id": "executive_node_org_1",

### block_p0379_b035

"assignee_user_id": 20002,

### block_p0379_b036

"assignee_role": "backend",

### block_p0379_b037

"assignment_type": "owner",

### block_p0379_b038

"priority": "high",

### block_p0379_b039

"status": "pending",

### block_p0379_b040

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0379_b041

"confirm_required": true,

### block_p0379_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0379_b043

AutoMage-2-MVP 架构设计文档·杨卓379

### block_p0379_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 379

## 表格

无。

## 备注

无。

<!-- 来自 page_0379.md 全文结束 -->

<!-- 来自 page_0380.md 全文开始 -->

# Page 0380

## 原始文本块

### block_p0380_b001

2026 年5 月3 日

### block_p0380_b002

"meta": {

### block_p0380_b003

"confirmed_option": "A",

### block_p0380_b004

"source_summary_ids": [801],

### block_p0380_b005

"push_channel": "feishu"

### block_p0380_b006

}

### block_p0380_b007

}

### block_p0380_b008

17.14.3写入数据库

### block_p0380_b009

系统应写入：

### block_p0380_b010

表结果

### block_p0380_b011

tasks创建任务9001

### block_p0380_b012

task_assignments分配给后端负责人或Manager

### block_p0380_b013

task_updates记录任务创建动态

### block_p0380_b014

audit_logs记录老板决策生成任务

### block_p0380_b015

17.14.4幂等要求

### block_p0380_b016

同一个决策和同一个确认方案不能重复生成任务。

### block_p0380_b017

幂等键建议：

### block_p0380_b018

task_from_decision:decision_0001:A

### block_p0380_b019

如果老板重复点击方案A，系统应返回已有任务：

### block_p0380_b020

{

### block_p0380_b021

"success": true,

### block_p0380_b022

"code": "IDEMPOTENT_REPLAY",

### block_p0380_b023

"message": " 该决策已确认并生成任务，返回原任务结果",

### block_p0380_b024

"data": {

### block_p0380_b025

"generated_task_ids": [9001]

### block_p0380_b026

}

### block_p0380_b027

}

### block_p0380_b028

17.15Step 11：任务下发到Staff Agent

### block_p0380_b029

17.15.1目标

### block_p0380_b030

验证任务可以推送给执行节点，并能被Staff Agent 或Manager Agent 接收。

### block_p0380_b031

17.15.2下发逻辑

### block_p0380_b032

如果任务有明确assignee_user_id，直接下发给对应StaffAgent。如果只有

### block_p0380_b033

assignee_role，先下发给对应Manager Agent，由Manager 分配给具体员工。

### block_p0380_b034

Demo 中可以采用两种方式之一：

### block_p0380_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0380_b036

AutoMage-2-MVP 架构设计文档·杨卓380

### block_p0380_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 380

## 表格

无。

## 备注

无。

<!-- 来自 page_0380.md 全文结束 -->

<!-- 来自 page_0381.md 全文开始 -->

# Page 0381

## 原始文本块

### block_p0381_b001

2026 年5 月3 日

### block_p0381_b002

方式说明

### block_p0381_b003

简化方式直接分配给杨卓，方便演示Staff Agent 查询

### block_p0381_b004

正式方式先分配给后端Manager，再拆给后端负责人

### block_p0381_b005

为了Demo 流程更直观，建议直接分配给一个可展示的执行人，例如杨卓或后端负责人。

### block_p0381_b006

17.15.3Staff Agent 收到任务通知

### block_p0381_b007

你收到1 个新任务：

### block_p0381_b008

任务：补充decisions 表结构草案

### block_p0381_b009

来源：老板确认的方案A

### block_p0381_b010

优先级：高

### block_p0381_b011

截止时间：今日18:00

### block_p0381_b012

要求：字段需覆盖决策标题、背景、候选方案、推荐方案、确认人、确认时间、来源Summary 和生成任务。

### block_p0381_b013

17.15.4成功表现

### block_p0381_b014

任务下发后：

### block_p0381_b015

1. tasks.status = pending。

### block_p0381_b016

2. task_assignments 中有执行人。

### block_p0381_b017

3. Staff Agent 可以通过任务接口查询到。

### block_p0381_b018

4. 任务来源可以追溯到decision_0001。

### block_p0381_b019

5. decision_0001 可以追溯到summary_id = 801。

### block_p0381_b020

6. summary_id = 801 可以追溯到work_record_id = 301。

### block_p0381_b021

这条追溯链是Demo 的重点。

### block_p0381_b022

17.16Step 12：员工查询今日任务

### block_p0381_b023

17.16.1目标

### block_p0381_b024

验证Staff Agent 可以读取员工自己的任务，并以自然语言展示给员工。

### block_p0381_b025

17.16.2调用接口

### block_p0381_b026

GET /api/v1/tasks?org_id=1&assignee_user_id=10086&status=pending&page=1&page_size=20

### block_p0381_b027

17.16.3响应示例

### block_p0381_b028

{

### block_p0381_b029

"success": true,

### block_p0381_b030

"code": "OK",

### block_p0381_b031

"message": "success",

### block_p0381_b032

"data": {

### block_p0381_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0381_b034

AutoMage-2-MVP 架构设计文档·杨卓381

### block_p0381_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 381

## 表格

无。

## 备注

无。

<!-- 来自 page_0381.md 全文结束 -->

<!-- 来自 page_0382.md 全文开始 -->

# Page 0382

## 原始文本块

### block_p0382_b001

2026 年5 月3 日

### block_p0382_b002

"items": [

### block_p0382_b003

{

### block_p0382_b004

"task_id": 9001,

### block_p0382_b005

"org_id": 1,

### block_p0382_b006

"department_id": 12,

### block_p0382_b007

"task_title": " 补充decisions 表结构草案",

### block_p0382_b008

"task_description": " 根据老板确认的方案A，设计独立decisions 表结构。",

### block_p0382_b009

"source_type": "executive_decision",

### block_p0382_b010

"source_decision_id": "decision_0001",

### block_p0382_b011

"assignee_user_id": 10086,

### block_p0382_b012

"assignee_role": "backend",

### block_p0382_b013

"priority": "high",

### block_p0382_b014

"status": "pending",

### block_p0382_b015

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0382_b016

"confirm_required": true,

### block_p0382_b017

"created_at": "2026-05-04T08:16:35+08:00"

### block_p0382_b018

}

### block_p0382_b019

],

### block_p0382_b020

"pagination": {

### block_p0382_b021

"page": 1,

### block_p0382_b022

"page_size": 20,

### block_p0382_b023

"total": 1,

### block_p0382_b024

"has_more": false

### block_p0382_b025

}

### block_p0382_b026

}

### block_p0382_b027

}

### block_p0382_b028

17.16.4Staff Agent 展示

### block_p0382_b029

今日待处理任务：

### block_p0382_b030

1. 补充decisions 表结构草案

### block_p0382_b031

优先级：高

### block_p0382_b032

截止时间：今日18:00

### block_p0382_b033

来源：老板确认的方案A

### block_p0382_b034

要求：设计独立decisions 表，字段需覆盖决策标题、背景、候选方案、推荐方案、确认人、确认时间、来源

### block_p0382_b035

Summary 和生成任务。,→

### block_p0382_b036

你可以回复“开始处理第1 个任务”来更新状态。

### block_p0382_b037

17.16.5可选演示：员工开始处理

### block_p0382_b038

员工回复：

### block_p0382_b039

开始处理第1 个任务

### block_p0382_b040

系统更新任务状态：

### block_p0382_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0382_b042

AutoMage-2-MVP 架构设计文档·杨卓382

### block_p0382_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 382

## 表格

无。

## 备注

无。

<!-- 来自 page_0382.md 全文结束 -->

<!-- 来自 page_0383.md 全文开始 -->

# Page 0383

## 原始文本块

### block_p0383_b001

2026 年5 月3 日

### block_p0383_b002

pending →in_progress

### block_p0383_b003

写入task_updates 和audit_logs。

### block_p0383_b004

17.17Demo 成功判定标准

### block_p0383_b005

Demo 是否成功，不看界面是否精美，而看核心数据闭环是否真实跑通。

### block_p0383_b006

17.17.1主链路成功标准

### block_p0383_b007

必须满足以下条件：

### block_p0383_b008

检查项成功标准

### block_p0383_b009

Staff Agent 初始化能返回用户、部门、节点和权限

### block_p0383_b010

Staff 日报提交schema_v1_staff 成功写入work_records

### block_p0383_b011

Staff 字段明细work_record_items 中存在日报字段

### block_p0383_b012

员工签名Staff 日报有签名状态和确认人

### block_p0383_b013

Manager 汇总生成schema_v1_manager 成功写入summaries

### block_p0383_b014

来源追溯summary_source_links 能追溯到Staff 日报

### block_p0383_b015

Executive 决策生成能生成老板决策项和A/B 方案

### block_p0383_b016

老板确认决策状态变为confirmed

### block_p0383_b017

任务生成老板确认后生成正式任务

### block_p0383_b018

任务分配task_assignments 中存在执行人

### block_p0383_b019

Staff 查询任务员工能通过Staff Agent 看到任务

### block_p0383_b020

审计记录关键动作均有audit_logs

### block_p0383_b021

17.17.2数据追溯成功标准

### block_p0383_b022

Demo 最后应能展示一条完整来源链：

### block_p0383_b023

任务9001

### block_p0383_b024

来源于decision_0001

### block_p0383_b025

来源于Manager Summary 801

### block_p0383_b026

来源于Staff Work Record 301

### block_p0383_b027

来源于杨卓确认提交的Staff Schema

### block_p0383_b028

如果能展示这条链，说明AutoMage-2 的核心价值已经表达出来：

### block_p0383_b029

老板任务不是凭空来的；

### block_p0383_b030

它来自员工真实工作记录；

### block_p0383_b031

经过部门汇总；

### block_p0383_b032

经过老板确认；

### block_p0383_b033

最后下发给执行人。

### block_p0383_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0383_b035

AutoMage-2-MVP 架构设计文档·杨卓383

### block_p0383_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 383

## 表格

无。

## 备注

无。

<!-- 来自 page_0383.md 全文结束 -->

<!-- 来自 page_0384.md 全文开始 -->

# Page 0384

## 原始文本块

### block_p0384_b001

2026 年5 月3 日

### block_p0384_b002

17.17.3权限成功标准

### block_p0384_b003

至少验证以下权限点：

### block_p0384_b004

1. Staff Agent 只能提交本人日报。

### block_p0384_b005

2. Staff Agent 只能查询本人任务。

### block_p0384_b006

3. Manager Agent 只能读取本部门Staff 数据。

### block_p0384_b007

4. Executive Agent 读取的是部门汇总，而不是默认读取所有员工明细。

### block_p0384_b008

5. 老板决策必须由Executive 用户确认。

### block_p0384_b009

6. 未确认决策不能生成正式任务。

### block_p0384_b010

Demo 中不一定逐条展示失败场景，但后端接口必须具备这些校验。

### block_p0384_b011

17.17.4签名成功标准

### block_p0384_b012

至少验证：

### block_p0384_b013

1. 员工日报有员工确认记录。

### block_p0384_b014

2. Manager 汇总有Manager 确认或待确认状态。

### block_p0384_b015

3. 老板决策有老板确认记录。

### block_p0384_b016

4. 确认动作有payload_hash 或等价内容哈希。

### block_p0384_b017

5. 签名动作写入审计日志。

### block_p0384_b018

6. 未签名老板决策不能生成任务。

### block_p0384_b019

17.17.5幂等成功标准

### block_p0384_b020

至少验证：

### block_p0384_b021

1. 员工重复提交同一天日报不会产生重复主记录。

### block_p0384_b022

2. 老板重复点击确认不会生成重复任务。

### block_p0384_b023

3. Dream 或任务生成重试不会产生重复决策卡片。

### block_p0384_b024

4. 幂等重放能返回已有结果。

### block_p0384_b025

17.17.6演示话术建议

### block_p0384_b026

Demo 结束时可以这样总结：

### block_p0384_b027

这条Demo 链路证明了AutoMage-2 不是普通日报系统。

### block_p0384_b028

员工只提交一次工作记录，系统会自动转成结构化Staff Schema；

### block_p0384_b029

Manager Agent 基于真实日报生成部门汇总；

### block_p0384_b030

Executive Agent 和Dream 把部门风险整理成老板可判断的A/B 决策；

### block_p0384_b031

老板确认后，系统自动生成任务并下发给执行人；

### block_p0384_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0384_b033

AutoMage-2-MVP 架构设计文档·杨卓384

### block_p0384_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 384

## 表格

无。

## 备注

无。

<!-- 来自 page_0384.md 全文结束 -->

<!-- 来自 page_0385.md 全文开始 -->

# Page 0385

## 原始文本块

### block_p0385_b001

2026 年5 月3 日

### block_p0385_b002

最后任务还能追溯回最初的员工日报。

### block_p0385_b003

这就是AutoMage-2 MVP 要验证的核心闭环：

### block_p0385_b004

一线事实→部门判断→老板决策→任务执行。

### block_p0385_b005

17.18本章小结

### block_p0385_b006

MVP Demo 的核心不在于展示所有功能，而在于用一条清晰链路证明系统成立：

### block_p0385_b007

Staff Agent

### block_p0385_b008

→Manager Agent

### block_p0385_b009

→Executive Agent / Dream

### block_p0385_b010

→老板确认

### block_p0385_b011

→任务下发

### block_p0385_b012

→Staff Agent 接收

### block_p0385_b013

只要Demo 能稳定跑通以下结果，MVP 就具备可交付价值：

### block_p0385_b014

1. 员工日报能结构化。

### block_p0385_b015

2. 部门汇总能自动生成。

### block_p0385_b016

3. 老板决策能被整理成A/B 方案。

### block_p0385_b017

4. 老板确认能生成正式任务。

### block_p0385_b018

5. 任务能下发到执行人。

### block_p0385_b019

6. 全链路能追溯来源、签名和审计。

### block_p0385_b020

后续所有复杂能力，包括自动采集、行业模板、老板看板、长期Dream、跨部门协作和

### block_p0385_b021

组织诊断，都可以建立在这条最小闭环之上。

### block_p0385_b022 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0385_b023

AutoMage-2-MVP 架构设计文档·杨卓385

### block_p0385_b024 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 385

## 表格

无。

## 备注

无。

<!-- 来自 page_0385.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

