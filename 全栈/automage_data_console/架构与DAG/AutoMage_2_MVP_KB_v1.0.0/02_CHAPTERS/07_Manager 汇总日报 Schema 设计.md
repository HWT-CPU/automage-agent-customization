# Manager 汇总日报 Schema 设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P099-P126
> 对应页面文件：`01_PAGES/page_0099.md` — `01_PAGES/page_0126.md`

## 原文整理

<!-- 来自 page_0099.md 全文开始 -->

# Page 0099

## 原始文本块

### block_p0099_b001

2026 年5 月3 日

### block_p0099_b002

6Manager 汇总日报Schema 设计

### block_p0099_b003

6.1Schema 基本信息

### block_p0099_b004

Manager 汇总日报Schema 是AutoMage-2 MVP 阶段的部门级数据契约，用于承接本部

### block_p0099_b005

门下属员工的Staff Schema，并将分散的一线工作记录整理为部门级汇总、风险判断、阻塞事

### block_p0099_b006

项、待处理问题和需上推老板的决策项。

### block_p0099_b007

Manager Schema 的核心价值不是“把员工日报合并成一篇部门日报”，而是完成一次部

### block_p0099_b008

门级过滤：哪些信息只是普通进展，哪些信息需要部门负责人处理，哪些问题已经超出部门

### block_p0099_b009

权限，需要进入Executive Agent 的老板决策流程。

### block_p0099_b010

字段内容

### block_p0099_b011

Schema 名称Manager 汇总日报Schema

### block_p0099_b012

Schema IDschema_v1_manager

### block_p0099_b013

当前版本1.0.0

### block_p0099_b014

使用节点Manager Agent

### block_p0099_b015

数据生成方部门级Manager Agent

### block_p0099_b016

数据确认人部门负责人/ 中层负责人

### block_p0099_b017

主要触发方式每日定时读取部门Staff Schema

### block_p0099_b018

数据来源本部门下属员工日报、部门任务、异常记录

### block_p0099_b019

主要写入对象summaries、summary_source_links

### block_p0099_b020

主要读取对象Executive Agent

### block_p0099_b021

核心目标将一线员工数据整理为部门级态势，为老板决策和任务

### block_p0099_b022

下发提供输入

### block_p0099_b023

Manager Schema 的典型流程如下：

### block_p0099_b024

Manager Agent 定时触发

### block_p0099_b025

↓

### block_p0099_b026

读取本部门Staff Schema

### block_p0099_b027

↓

### block_p0099_b028

过滤无效或未签名日报

### block_p0099_b029

↓

### block_p0099_b030

汇总部门进展、风险、阻塞和待决策事项

### block_p0099_b031

↓

### block_p0099_b032

生成schema_v1_manager

### block_p0099_b033

↓

### block_p0099_b034

部门负责人确认

### block_p0099_b035

↓

### block_p0099_b036

写入summaries / summary_source_links

### block_p0099_b037

↓

### block_p0099_b038

Executive Agent 定时读取

### block_p0099_b039

MVP 阶段建议Manager Schema 每天至少生成一次，时间可以设置在员工日报提交截止

### block_p0099_b040

之后。例如员工18:00 前提交日报，Manager Agent 在20:00 或21:00 进行部门汇总。

### block_p0099_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0099_b042

AutoMage-2-MVP 架构设计文档·杨卓99

### block_p0099_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 99

## 表格

无。

## 备注

无。

<!-- 来自 page_0099.md 全文结束 -->

<!-- 来自 page_0100.md 全文开始 -->

# Page 0100

## 原始文本块

### block_p0100_b001

2026 年5 月3 日

### block_p0100_b002

6.1.1Schema ID：schema_v1_manager

### block_p0100_b003

Manager 汇总日报固定使用：

### block_p0100_b004

"schema_id": "schema_v1_manager"

### block_p0100_b005

该字段用于告诉后端、Agent 和数据库当前数据遵循Manager 汇总日报结构。后端收到

### block_p0100_b006

数据后，应根据schema_id 和schema_version 选择对应校验规则。

### block_p0100_b007

6.1.2使用节点：Manager Agent

### block_p0100_b008

Manager Schema 由Manager Agent 生成。

### block_p0100_b009

Manager Agent 一般绑定一个部门负责人或部门节点。它只能读取自己权限范围内的数

### block_p0100_b010

据，即本组织、本部门及下属成员的Staff Schema、任务、异常和历史汇总。

### block_p0100_b011

Manager Agent 不应读取其他部门员工明细，也不应直接修改员工原始日报。

### block_p0100_b012

6.1.3触发方式：每日定时读取部门Staff Schema

### block_p0100_b013

MVP 阶段推荐使用定时任务触发Manager Schema 生成。

### block_p0100_b014

建议触发时间：

### block_p0100_b015

时间动作

### block_p0100_b016

18:00员工日报提交提醒

### block_p0100_b017

20:00Staff Agent 二次催填

### block_p0100_b018

21:00Manager Agent 读取本部门Staff Schema

### block_p0100_b019

21:10生成部门汇总草稿

### block_p0100_b020

21:30部门负责人确认或自动标记待确认

### block_p0100_b021

22:00Executive Agent 读取部门汇总

### block_p0100_b022

具体时间可根据企业作息调整，但流程顺序应保持稳定：先员工日报，后部门汇总，再老

### block_p0100_b023

板决策。

### block_p0100_b024

6.1.4数据来源：本部门下属员工日报

### block_p0100_b025

Manager Schema 的核心输入是本部门员工提交的Staff Schema。

### block_p0100_b026

除Staff Schema 外，Manager Agent 还可以读取以下数据作为辅助：

### block_p0100_b027

1. 本部门未完成任务。

### block_p0100_b028

2. 本部门进行中的异常记录。

### block_p0100_b029

3. 前一日部门汇总。

### block_p0100_b030

4. 老板或上级下发的未完成任务。

### block_p0100_b031

5. 与本部门相关的历史决策结果。

### block_p0100_b032

6. 当日缺失日报名单。

### block_p0100_b033

MVP 阶段不建议Manager Agent 读取太多外部数据，避免汇总逻辑变重。优先保证基

### block_p0100_b034

于Staff Schema 的部门日报可稳定生成。

### block_p0100_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0100_b036

AutoMage-2-MVP 架构设计文档·杨卓100

### block_p0100_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 100

## 表格

无。

## 备注

无。

<!-- 来自 page_0100.md 全文结束 -->

<!-- 来自 page_0101.md 全文开始 -->

# Page 0101

## 原始文本块

### block_p0101_b001

2026 年5 月3 日

### block_p0101_b002

6.1.5写入对象：部门汇总表/ summaries

### block_p0101_b003

Manager Schema 生成后，建议写入summaries 表，来源记录写入summary_source_links。

### block_p0101_b004

推荐映射方式：

### block_p0101_b005

Manager Schema 内容数据库对象

### block_p0101_b006

部门汇总主记录summaries

### block_p0101_b007

引用的员工日报IDsummary_source_links

### block_p0101_b008

需上推老板的事项Decision 相关表/ audit_logs / tasks

### block_p0101_b009

部门内处理事项tasks / incidents

### block_p0101_b010

操作与确认记录audit_logs

### block_p0101_b011

如果当前阶段暂未建立独立Decision 表，need_executive_decision 可以先存入

### block_p0101_b012

summaries.content 或summaries.meta，同时写入审计日志。后续建议补充独立决策表，方

### block_p0101_b013

便老板确认和任务下发。

### block_p0101_b014

6.2Manager Schema 字段总览

### block_p0101_b015

Manager Schema 字段分为六类：基础身份字段、汇总统计字段、部门态势字段、风险与

### block_p0101_b016

阻塞字段、决策与调整字段、来源与签名字段。

### block_p0101_b017 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0101_b018

AutoMage-2-MVP 架构设计文档·杨卓101

### block_p0101_b019 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 101

## 表格

无。

## 备注

无。

<!-- 来自 page_0101.md 全文结束 -->

<!-- 来自 page_0102.md 全文开始 -->

# Page 0102

## 原始文本块

### block_p0102_b001

2026 年5 月3 日

### block_p0102_b002

字段名类型是否必填说明

### block_p0102_b003

schema_idstring是Schema标识，固定为

### block_p0102_b004

schema_v1_manager

### block_p0102_b005

schema_versionstring是Schema 版本，MVP 阶段默认

### block_p0102_b006

1.0.0

### block_p0102_b007

timestampstring是汇总生成时间

### block_p0102_b008

org_idstring / number是所属组织ID

### block_p0102_b009

dept_idstring / number是部门ID

### block_p0102_b010

manager_user_idstring / number是中层负责人用户ID

### block_p0102_b011

manager_node_idstring是Manager Agent 节点ID

### block_p0102_b012

summary_datestring是汇总日期，格式为YYYY-MM-DD

### block_p0102_b013

staff_report_countnumber是已读取的一线日报数量

### block_p0102_b014

missing_report_count number是缺失日报数量

### block_p0102_b015

missing_staff_idsarray否未提交日报的员工ID

### block_p0102_b016

overall_healthstring是部门整体健康度

### block_p0102_b017

aggregated_summarystring是部门综合进展摘要

### block_p0102_b018

top_3_risksarray是三大风险

### block_p0102_b019

workforce_efficiency object否部门效能评分与说明

### block_p0102_b020

pending_approvalsnumber是待老板或上级决策事项数量

### block_p0102_b021

highlight_staffarray否表现突出员工

### block_p0102_b022

blocked_itemsarray否阻塞事项

### block_p0102_b023

manager_decisionsarray否Manager 权限内已处理决策

### block_p0102_b024

need_executive_decisionarray否需要上推老板的事项

### block_p0102_b025

next_day_adjustmentarray是次日部门调整建议

### block_p0102_b026

source_record_idsarray是引用的一线日报ID

### block_p0102_b027

related_task_idsarray否关联任务ID

### block_p0102_b028

related_incident_ids array否关联异常ID

### block_p0102_b029

signatureobject是Manager 确认签名

### block_p0102_b030

metaobject否扩展字段

### block_p0102_b031

其中，aggregated_summary、top_3_risks、blocked_items、need_executive_decision、

### block_p0102_b032

next_day_adjustment 是Manager Schema 的核心字段。Executive Agent 后续会重点读取这

### block_p0102_b033

些字段，用于生成老板侧摘要和决策项。

### block_p0102_b034

6.3字段定义明细

### block_p0102_b035

6.3.1timestamp：汇总生成时间

### block_p0102_b036

timestamp 表示Manager Schema 被生成的时间，使用ISO8601 格式。

### block_p0102_b037

示例：

### block_p0102_b038

"timestamp": "2026-05-03T21:10:00+08:00"

### block_p0102_b039

该字段用于判断部门汇总是否按时生成，也用于后续审计和排序。需要注意，timestamp

### block_p0102_b040

是生成时间，summary_date 是汇总所覆盖的业务日期，二者不能混用。

### block_p0102_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0102_b042

AutoMage-2-MVP 架构设计文档·杨卓102

### block_p0102_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 102

## 表格

无。

## 备注

无。

<!-- 来自 page_0102.md 全文结束 -->

<!-- 来自 page_0103.md 全文开始 -->

# Page 0103

## 原始文本块

### block_p0103_b001

2026 年5 月3 日

### block_p0103_b002

6.3.2manager_user_id：中层负责人ID

### block_p0103_b003

manager_user_id 表示该部门汇总对应的负责人用户ID。

### block_p0103_b004

示例：

### block_p0103_b005

"manager_user_id": 20001

### block_p0103_b006

该字段用于确认谁对本次部门汇总负责。即使汇总内容由Manager Agent 自动生成，也

### block_p0103_b007

需要绑定一个明确的人类负责人。

### block_p0103_b008

后端应校验该用户是否具备对应部门的管理权限。

### block_p0103_b009

6.3.3manager_node_id：中层Agent 节点ID

### block_p0103_b010

manager_node_id 表示生成该Manager Schema 的Agent 节点。

### block_p0103_b011

示例：

### block_p0103_b012

"manager_node_id": "manager_node_dept_12"

### block_p0103_b013

该字段用于追踪是哪一个Manager Agent 生成了汇总。后续如果不同部门使用不同Agent

### block_p0103_b014

模板，或者Agent 模板版本发生变化，该字段可以帮助排查问题。

### block_p0103_b015

6.3.4dept_id：部门ID

### block_p0103_b016

dept_id 表示该汇总所属部门。

### block_p0103_b017

示例：

### block_p0103_b018

"dept_id": 12

### block_p0103_b019

ManagerAgent只能生成自己权限范围内部门的ManagerSchema。后端应校验

### block_p0103_b020

manager_user_id、manager_node_id 与dept_id 之间的绑定关系。

### block_p0103_b021

如果一个Manager Agent 负责多个部门，建议每个部门单独生成一条Manager Schema，

### block_p0103_b022

而不是把多个部门混在一条汇总中。

### block_p0103_b023

6.3.5staff_report_count：读取的一线日报数量

### block_p0103_b024

staff_report_count 表示本次汇总实际读取并纳入统计的Staff Schema 数量。

### block_p0103_b025

示例：

### block_p0103_b026

"staff_report_count": 8

### block_p0103_b027

该字段用于判断部门数据覆盖率。如果部门共有10 名员工，但只读取到8 条有效日报，

### block_p0103_b028

则说明还有2 人缺失日报，需要在missing_report_count 中体现。

### block_p0103_b029

只应统计已通过校验、已签名或已确认的正式Staff Schema。草稿、未确认、校验失败的

### block_p0103_b030

数据不应计入正式汇总。

### block_p0103_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0103_b032

AutoMage-2-MVP 架构设计文档·杨卓103

### block_p0103_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 103

## 表格

无。

## 备注

无。

<!-- 来自 page_0103.md 全文结束 -->

<!-- 来自 page_0104.md 全文开始 -->

# Page 0104

## 原始文本块

### block_p0104_b001

2026 年5 月3 日

### block_p0104_b002

6.3.6missing_report_count：缺失日报数量

### block_p0104_b003

missing_report_count 表示本部门当日应提交但未提交日报的人数。

### block_p0104_b004

示例：

### block_p0104_b005

"missing_report_count": 2

### block_p0104_b006

该字段用于评估部门数据完整性。缺失日报不一定代表员工未工作，但会影响Manager

### block_p0104_b007

汇总准确性。

### block_p0104_b008

建议同时提供missing_staff_ids：

### block_p0104_b009

"missing_staff_ids": [10012, 10017]

### block_p0104_b010

如果缺失数量较高，Manager Agent 应在top_3_risks 或blocked_items 中提示数据不

### block_p0104_b011

完整风险。

### block_p0104_b012

6.3.7overall_health：部门整体健康度

### block_p0104_b013

overall_health 表示Manager Agent 对部门当天运行状态的整体判断。

### block_p0104_b014

示例：

### block_p0104_b015

"overall_health": "yellow"

### block_p0104_b016

建议枚举值如下：

### block_p0104_b017

值含义

### block_p0104_b018

green部门整体正常，无明显风险

### block_p0104_b019

yellow有风险或阻塞，但仍可控

### block_p0104_b020

red存在明显风险，可能影响交付或关键目标

### block_p0104_b021

gray数据不足，无法判断

### block_p0104_b022

判断规则不宜过度复杂，MVP 阶段可以先基于以下因素综合判断：

### block_p0104_b023

1. 缺失日报比例。

### block_p0104_b024

2. 高风险Staff Schema 数量。

### block_p0104_b025

3. 阻塞事项数量。

### block_p0104_b026

4. 逾期任务数量。

### block_p0104_b027

5. 是否存在需上推老板事项。

### block_p0104_b028

6. 是否存在关键产出缺失。

### block_p0104_b029

如果missing_report_count 较高，建议优先标记为gray 或yellow，而不是强行判断

### block_p0104_b030

部门正常。

### block_p0104_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0104_b032

AutoMage-2-MVP 架构设计文档·杨卓104

### block_p0104_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 104

## 表格

无。

## 备注

无。

<!-- 来自 page_0104.md 全文结束 -->

<!-- 来自 page_0105.md 全文开始 -->

# Page 0105

## 原始文本块

### block_p0105_b001

2026 年5 月3 日

### block_p0105_b002

6.3.8aggregated_summary：部门综合进展摘要

### block_p0105_b003

aggregated_summary 是Manager Schema 中最重要的自然语言摘要字段，用于概括部门

### block_p0105_b004

当天整体工作进展。

### block_p0105_b005

示例：

### block_p0105_b006

"aggregated_summary": "今日架构组主要完成了Staff Schema 字段定义、数据库映射梳理和部分Agent

### block_p0105_b007

Mock Flow 对齐。整体进展正常，但Decision 相关表结构尚未最终确定，

### block_p0105_b008

可能影响老板决策链路和任务下发联调。"

### block_p0105_b009

,→

### block_p0105_b010

,→

### block_p0105_b011

该字段应满足以下要求：

### block_p0105_b012

1. 语言简洁，不写流水账。

### block_p0105_b013

2. 不逐条复制员工日报。

### block_p0105_b014

3. 突出部门主要进展。

### block_p0105_b015

4. 明确当前风险和阻塞。

### block_p0105_b016

5. 能被Executive Agent 直接读取并进一步压缩。

### block_p0105_b017

建议控制在100 到300 字之间。过短会丢失信息，过长会增加老板侧摘要成本。

### block_p0105_b018

6.3.9top_3_risks：三大风险

### block_p0105_b019

top_3_risks 用于记录部门当天最重要的风险，最多三项。

### block_p0105_b020

示例：

### block_p0105_b021

"top_3_risks": [

### block_p0105_b022

{

### block_p0105_b023

"title": "Decision 表结构未确认",

### block_p0105_b024

"description": "Agent mock 代码中已有decision_logs 概念，但当前DDL 中未单独建表，

### block_p0105_b025

可能影响Executive 决策记录和任务生成。",,→

### block_p0105_b026

"severity": "high",

### block_p0105_b027

"source_record_ids": [301, 302],

### block_p0105_b028

"suggested_action": " 建议后端与架构负责人确认是否新增独立决策表。"

### block_p0105_b029

}

### block_p0105_b030

]

### block_p0105_b031

建议每个风险项包含：

### block_p0105_b032

子字段类型是否必填说明

### block_p0105_b033

titlestring是风险标题

### block_p0105_b034

descriptionstring是风险说明

### block_p0105_b035

severitystring是风险等级

### block_p0105_b036

source_record_idsarray否来源Staff 日报ID

### block_p0105_b037

suggested_actionstring否建议处理方式

### block_p0105_b038

风险等级建议使用：

### block_p0105_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0105_b040

AutoMage-2-MVP 架构设计文档·杨卓105

### block_p0105_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 105

## 表格

无。

## 备注

无。

<!-- 来自 page_0105.md 全文结束 -->

<!-- 来自 page_0106.md 全文开始 -->

# Page 0106

## 原始文本块

### block_p0106_b001

2026 年5 月3 日

### block_p0106_b002

值含义

### block_p0106_b003

low轻微风险

### block_p0106_b004

medium需要部门关注

### block_p0106_b005

high可能影响关键节点

### block_p0106_b006

critical需要老板或跨部门立即处理

### block_p0106_b007

top_3_risks不应列出所有问题，只保留最重要的三项。普通问题可以放入

### block_p0106_b008

blocked_items 或后续任务中。

### block_p0106_b009

6.3.10workforce_efficiency：部门效能评分

### block_p0106_b010

workforce_efficiency 用于表示部门当天的执行效率判断。

### block_p0106_b011

示例：

### block_p0106_b012

"workforce_efficiency": {

### block_p0106_b013

"score": 78,

### block_p0106_b014

"level": "medium",

### block_p0106_b015

"basis": "8 名员工提交日报，6 名员工完成主要任务，2 个事项仍处于阻塞状态，

### block_p0106_b016

整体产出符合预期但存在结构设计等待确认。",→

### block_p0106_b017

}

### block_p0106_b018

建议子字段包括：

### block_p0106_b019

子字段类型是否必填说明

### block_p0106_b020

scorenumber否0-100 分

### block_p0106_b021

levelstring是效能等级

### block_p0106_b022

basisstring是评分依据

### block_p0106_b023

level 建议使用：

### block_p0106_b024

值含义

### block_p0106_b025

high效率较高

### block_p0106_b026

medium正常推进

### block_p0106_b027

low推进偏慢

### block_p0106_b028

unknown数据不足

### block_p0106_b029

MVP 阶段不建议把该字段直接用于绩效考核。它只是部门态势判断的辅助信息，必须保

### block_p0106_b030

留依据说明，不能只给一个分数。

### block_p0106_b031

6.3.11pending_approvals：待老板决策事项数量

### block_p0106_b032

pending_approvals 表示本部门当天需要上推老板或更高层确认的事项数量。

### block_p0106_b033

示例：

### block_p0106_b034

"pending_approvals": 1

### block_p0106_b035

该字段应与need_executive_decision 数组数量保持一致。如果pending_approvals >

### block_p0106_b036

0，Executive Agent 应重点读取这些事项。

### block_p0106_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0106_b038

AutoMage-2-MVP 架构设计文档·杨卓106

### block_p0106_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 106

## 表格

无。

## 备注

无。

<!-- 来自 page_0106.md 全文结束 -->

<!-- 来自 page_0107.md 全文开始 -->

# Page 0107

## 原始文本块

### block_p0107_b001

2026 年5 月3 日

### block_p0107_b002

需要注意，pending_approvals 不代表所有待处理事项，只代表超出Manager 权限、需

### block_p0107_b003

要更高层确认的事项。

### block_p0107_b004

6.3.12highlight_staff：表现突出员工

### block_p0107_b005

highlight_staff 用于记录当天有明显贡献、关键产出或主动解决问题的员工。

### block_p0107_b006

示例：

### block_p0107_b007

"highlight_staff": [

### block_p0107_b008

{

### block_p0107_b009

"user_id": 10086,

### block_p0107_b010

"display_name": " 杨卓",

### block_p0107_b011

"reason": " 完成Staff Schema 字段定义，并主动梳理与数据库表的映射关系。",

### block_p0107_b012

"source_record_ids": [301]

### block_p0107_b013

}

### block_p0107_b014

]

### block_p0107_b015

建议子字段包括：

### block_p0107_b016

子字段类型是否必填说明

### block_p0107_b017

user_idnumber / string是员工ID

### block_p0107_b018

display_namestring否员工名称

### block_p0107_b019

reasonstring是突出原因

### block_p0107_b020

source_record_idsarray是来源日报ID

### block_p0107_b021

该字段不是为了做简单排名，而是为了让老板或部门负责人看到具体价值创造。Manager

### block_p0107_b022

Agent 不应只根据字数多少判断员工表现，而应结合任务完成、产出物、问题解决和关键贡

### block_p0107_b023

献。

### block_p0107_b024

6.3.13blocked_items：阻塞事项

### block_p0107_b025

blocked_items 用于记录部门内当前存在的阻塞事项。

### block_p0107_b026

示例：

### block_p0107_b027

"blocked_items": [

### block_p0107_b028

{

### block_p0107_b029

"title": " 决策记录表结构未定",

### block_p0107_b030

"description": "当前Agent 侧和数据库侧对decision_logs 的承载方式不一致，影响后续

### block_p0107_b031

Executive 决策确认和任务生成链路。",,→

### block_p0107_b032

"owner_user_id": 20002,

### block_p0107_b033

"severity": "high",

### block_p0107_b034

"need_support": true,

### block_p0107_b035

"suggested_next_step": " 召开一次后端与架构对齐会，确认是否新增decision_logs 表。"

### block_p0107_b036

}

### block_p0107_b037

]

### block_p0107_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0107_b039

AutoMage-2-MVP 架构设计文档·杨卓107

### block_p0107_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 107

## 表格

无。

## 备注

无。

<!-- 来自 page_0107.md 全文结束 -->

<!-- 来自 page_0108.md 全文开始 -->

# Page 0108

## 原始文本块

### block_p0108_b001

2026 年5 月3 日

### block_p0108_b002

建议子字段包括：

### block_p0108_b003

子字段类型是否必填说明

### block_p0108_b004

titlestring是阻塞事项标题

### block_p0108_b005

descriptionstring是阻塞说明

### block_p0108_b006

owner_user_idnumber / string否当前负责人

### block_p0108_b007

severitystring是严重程度

### block_p0108_b008

need_supportboolean是是否需要支持

### block_p0108_b009

suggested_next_stepstring否建议下一步

### block_p0108_b010

blocked_items 与top_3_risks 的区别是：风险可以是潜在问题，阻塞事项是已经影响

### block_p0108_b011

推进的问题。

### block_p0108_b012

6.3.14manager_decisions：权限内已处理决策

### block_p0108_b013

manager_decisions 用于记录Manager Agent 或部门负责人在权限范围内已经处理的事

### block_p0108_b014

项。

### block_p0108_b015

示例：

### block_p0108_b016

"manager_decisions": [

### block_p0108_b017

{

### block_p0108_b018

"decision_title": " 将Manager Schema 字段设计任务优先级调高",

### block_p0108_b019

"decision_reason": " 该任务影响Executive Agent 的输入结构，应优先完成。",

### block_p0108_b020

"action_taken": " 已将任务优先级调整为high，并安排明日上午完成初稿。",

### block_p0108_b021

"related_task_ids": [401],

### block_p0108_b022

"confirmed_by": 20001

### block_p0108_b023

}

### block_p0108_b024

]

### block_p0108_b025

该字段有两个作用：

### block_p0108_b026

第一，避免所有问题都上推老板。部门内可以解决的问题，应在部门层处理。

### block_p0108_b027

第二，体现中层管理者的真实价值。系统可以记录哪些事项是中层实际判断和处理过的，

### block_p0108_b028

而不是只统计会议或转发次数。

### block_p0108_b029

Manager 权限内决策可以包括：

### block_p0108_b030

1. 部门内任务优先级调整。

### block_p0108_b031

2. 部门人员临时协作安排。

### block_p0108_b032

3. 部门内阻塞事项处理。

### block_p0108_b033

4. 常规资源协调。

### block_p0108_b034

5. 对员工日报缺失的催办。

### block_p0108_b035

6. 对低中风险异常的处理。

### block_p0108_b036

涉及预算、跨部门冲突、战略方向、重大客户、重大延期等事项，不应放入

### block_p0108_b037

manager_decisions，而应进入need_executive_decision。

### block_p0108_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0108_b039

AutoMage-2-MVP 架构设计文档·杨卓108

### block_p0108_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 108

## 表格

无。

## 备注

无。

<!-- 来自 page_0108.md 全文结束 -->

<!-- 来自 page_0109.md 全文开始 -->

# Page 0109

## 原始文本块

### block_p0109_b001

2026 年5 月3 日

### block_p0109_b002

6.3.15need_executive_decision：需上推老板的事项

### block_p0109_b003

need_executive_decision 用于记录超出Manager 权限，需要老板或高管确认的事项。

### block_p0109_b004

示例：

### block_p0109_b005

"need_executive_decision": [

### block_p0109_b006

{

### block_p0109_b007

"decision_title": " 是否新增独立decision_logs 表",

### block_p0109_b008

"context": "当前Agent mock 流程中存在decision_logs，但现有DDL 未单独建表。若不新增，

### block_p0109_b009

短期可复用audit_logs，但后续老板决策追踪和任务来源会不够清晰。",,→

### block_p0109_b010

"options": [

### block_p0109_b011

{

### block_p0109_b012

"option_id": "A",

### block_p0109_b013

"title": " 新增独立decision_logs 表",

### block_p0109_b014

"pros": [" 审计清晰", " 便于追踪决策与任务关系", " 后续扩展空间大"],

### block_p0109_b015

"cons": [" 需要增加后端开发工作量"]

### block_p0109_b016

},

### block_p0109_b017

{

### block_p0109_b018

"option_id": "B",

### block_p0109_b019

"title": " 暂时复用audit_logs 和tasks",

### block_p0109_b020

"pros": [" 短期实现更快"],

### block_p0109_b021

"cons": [" 决策对象不够独立", " 后续复盘和统计不方便"]

### block_p0109_b022

}

### block_p0109_b023

],

### block_p0109_b024

"recommended_option": "A",

### block_p0109_b025

"reason": "AutoMage-2 的核心价值在于决策可追溯，独立决策表更符合长期架构。",

### block_p0109_b026

"source_record_ids": [301, 302],

### block_p0109_b027

"urgency": "high"

### block_p0109_b028

}

### block_p0109_b029

]

### block_p0109_b030

建议子字段包括：

### block_p0109_b031

子字段类型是否必填说明

### block_p0109_b032

decision_titlestring是决策标题

### block_p0109_b033

contextstring是背景说明

### block_p0109_b034

optionsarray是候选方案

### block_p0109_b035

recommended_optionstring否推荐方案

### block_p0109_b036

reasonstring否推荐理由

### block_p0109_b037

source_record_idsarray否来源记录

### block_p0109_b038

urgencystring是紧急程度

### block_p0109_b039

该字段是Executive Agent 生成老板决策项的重要输入。Manager Agent 应尽量把问题整

### block_p0109_b040

理成老板可判断的形式，而不是只写“需要老板决策”。

### block_p0109_b041

6.3.16next_day_adjustment：次日部门调整建议

### block_p0109_b042

next_day_adjustment 用于记录Manager Agent 对部门次日工作的调整建议。

### block_p0109_b043

示例：

### block_p0109_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0109_b045

AutoMage-2-MVP 架构设计文档·杨卓109

### block_p0109_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 109

## 表格

无。

## 备注

无。

<!-- 来自 page_0109.md 全文结束 -->

<!-- 来自 page_0110.md 全文开始 -->

# Page 0110

## 原始文本块

### block_p0110_b001

2026 年5 月3 日

### block_p0110_b002

"next_day_adjustment": [

### block_p0110_b003

{

### block_p0110_b004

"title": " 优先确认Decision 数据结构",

### block_p0110_b005

"reason": " 该事项影响Executive 决策链路和任务下发闭环。",

### block_p0110_b006

"target_user_ids": [10086, 20002],

### block_p0110_b007

"priority": "high",

### block_p0110_b008

"expected_output": " 形成decision_logs 是否建表的最终结论和字段草案。"

### block_p0110_b009

}

### block_p0110_b010

]

### block_p0110_b011

建议子字段包括：

### block_p0110_b012

子字段类型是否必填说明

### block_p0110_b013

titlestring是调整事项

### block_p0110_b014

reasonstring是调整原因

### block_p0110_b015

target_user_idsarray否涉及员工

### block_p0110_b016

prioritystring是优先级

### block_p0110_b017

expected_outputstring否预期产出

### block_p0110_b018

该字段可以作为次日任务生成的候选输入，但不建议所有调整建议都自动变成任务。是

### block_p0110_b019

否生成任务，应结合Manager 确认或后端规则决定。

### block_p0110_b020

6.3.17source_record_ids：引用的一线日报ID

### block_p0110_b021

source_record_ids 表示本次Manager 汇总引用了哪些Staff Work Record。

### block_p0110_b022

示例：

### block_p0110_b023

"source_record_ids": [301, 302, 303, 304]

### block_p0110_b024

这是Manager Schema 可追溯性的关键字段。Executive Agent 或审计人员后续可以根据

### block_p0110_b025

该字段追溯部门汇总的来源。

### block_p0110_b026

后端应校验这些记录是否都属于同一组织、同一部门，且当前Manager Agent 有读取权

### block_p0110_b027

限。

### block_p0110_b028

6.3.18signature：Manager 确认签名

### block_p0110_b029

signature 用于记录部门负责人是否确认了本次部门汇总。

### block_p0110_b030

示例：

### block_p0110_b031

"signature": {

### block_p0110_b032

"signature_required": true,

### block_p0110_b033

"signature_status": "signed",

### block_p0110_b034

"signed_by": 20001,

### block_p0110_b035

"signed_at": "2026-05-03T21:25:00+08:00",

### block_p0110_b036

"payload_hash": "sha256:manager_summary_example_hash",

### block_p0110_b037

"signature_source": "im"

### block_p0110_b038

}

### block_p0110_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0110_b040

AutoMage-2-MVP 架构设计文档·杨卓110

### block_p0110_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 110

## 表格

无。

## 备注

无。

<!-- 来自 page_0110.md 全文结束 -->

<!-- 来自 page_0111.md 全文开始 -->

# Page 0111

## 原始文本块

### block_p0111_b001

2026 年5 月3 日

### block_p0111_b002

MVP 阶段可以支持两种模式：

### block_p0111_b003

模式说明

### block_p0111_b004

人工确认模式Manager Agent 生成汇总后，由部门负责人确认

### block_p0111_b005

自动待确认模式到达截止时间未确认时，系统标记为pending_confirm，

### block_p0111_b006

但仍可供Executive Agent 参考

### block_p0111_b007

如果Manager Schema 中存在高风险事项或需上推老板事项，建议必须由部门负责人确

### block_p0111_b008

认后再进入Executive 正式决策流程。

### block_p0111_b009

6.4Manager Schema JSON 示例

### block_p0111_b010

下面是一个完整Manager Schema 示例，可作为Agent 输出和后端联调参考。

### block_p0111_b011

{

### block_p0111_b012

"schema_id": "schema_v1_manager",

### block_p0111_b013

"schema_version": "1.0.0",

### block_p0111_b014

"timestamp": "2026-05-03T21:10:00+08:00",

### block_p0111_b015

"org_id": 1,

### block_p0111_b016

"dept_id": 12,

### block_p0111_b017

"manager_user_id": 20001,

### block_p0111_b018

"manager_node_id": "manager_node_dept_12",

### block_p0111_b019

"summary_date": "2026-05-03",

### block_p0111_b020

"staff_report_count": 8,

### block_p0111_b021

"missing_report_count": 2,

### block_p0111_b022

"missing_staff_ids": [10012, 10017],

### block_p0111_b023

"overall_health": "yellow",

### block_p0111_b024

"aggregated_summary": "今日架构组主要完成了Staff Schema 字段定义、数据库映射梳理和部分

### block_p0111_b025

Agent Mock Flow 对齐。整体进展正常，但Decision 相关表结构尚未最终确定，

### block_p0111_b026

可能影响老板决策链路和任务下发联调。",

### block_p0111_b027

,→

### block_p0111_b028

,→

### block_p0111_b029

"top_3_risks": [

### block_p0111_b030

{

### block_p0111_b031

"title": "Decision 表结构未确认",

### block_p0111_b032

"description": "Agent mock 代码中已有decision_logs 概念，但当前DDL 中未单独建表，

### block_p0111_b033

可能影响Executive 决策记录和任务生成。",,→

### block_p0111_b034

"severity": "high",

### block_p0111_b035

"source_record_ids": [301, 302],

### block_p0111_b036

"suggested_action": " 建议后端与架构负责人确认是否新增独立决策表。"

### block_p0111_b037

},

### block_p0111_b038

{

### block_p0111_b039

"title": " 部分员工日报缺失",

### block_p0111_b040

"description": " 本部门应提交10 份日报，当前仅收到8 份，部门汇总存在数据不完整风险。",

### block_p0111_b041

"severity": "medium",

### block_p0111_b042

"source_record_ids": [],

### block_p0111_b043

"suggested_action": " 建议Staff Agent 对缺失员工进行二次催填。"

### block_p0111_b044

}

### block_p0111_b045

],

### block_p0111_b046

"workforce_efficiency": {

### block_p0111_b047 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0111_b048

AutoMage-2-MVP 架构设计文档·杨卓111

### block_p0111_b049 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 111

## 表格

无。

## 备注

无。

<!-- 来自 page_0111.md 全文结束 -->

<!-- 来自 page_0112.md 全文开始 -->

# Page 0112

## 原始文本块

### block_p0112_b001

2026 年5 月3 日

### block_p0112_b002

"score": 78,

### block_p0112_b003

"level": "medium",

### block_p0112_b004

"basis": "8 名员工提交日报，6 名员工完成主要任务，2 个事项仍处于阻塞状态，

### block_p0112_b005

整体产出符合预期但存在结构设计等待确认。",→

### block_p0112_b006

},

### block_p0112_b007

"pending_approvals": 1,

### block_p0112_b008

"highlight_staff": [

### block_p0112_b009

{

### block_p0112_b010

"user_id": 10086,

### block_p0112_b011

"display_name": " 杨卓",

### block_p0112_b012

"reason": " 完成Staff Schema 字段定义，并主动梳理与数据库表的映射关系。",

### block_p0112_b013

"source_record_ids": [301]

### block_p0112_b014

}

### block_p0112_b015

],

### block_p0112_b016

"blocked_items": [

### block_p0112_b017

{

### block_p0112_b018

"title": " 决策记录表结构未定",

### block_p0112_b019

"description": "当前Agent 侧和数据库侧对decision_logs 的承载方式不一致，影响后续

### block_p0112_b020

Executive 决策确认和任务生成链路。",,→

### block_p0112_b021

"owner_user_id": 20002,

### block_p0112_b022

"severity": "high",

### block_p0112_b023

"need_support": true,

### block_p0112_b024

"suggested_next_step": " 召开一次后端与架构对齐会，确认是否新增decision_logs 表。"

### block_p0112_b025

}

### block_p0112_b026

],

### block_p0112_b027

"manager_decisions": [

### block_p0112_b028

{

### block_p0112_b029

"decision_title": " 将Manager Schema 字段设计任务优先级调高",

### block_p0112_b030

"decision_reason": " 该任务影响Executive Agent 的输入结构，应优先完成。",

### block_p0112_b031

"action_taken": " 已将任务优先级调整为high，并安排明日上午完成初稿。",

### block_p0112_b032

"related_task_ids": [401],

### block_p0112_b033

"confirmed_by": 20001

### block_p0112_b034

}

### block_p0112_b035

],

### block_p0112_b036

"need_executive_decision": [

### block_p0112_b037

{

### block_p0112_b038

"decision_title": " 是否新增独立decision_logs 表",

### block_p0112_b039

"context": "当前Agent mock 流程中存在decision_logs，但现有DDL 未单独建表。若不新增，

### block_p0112_b040

短期可复用audit_logs，但后续老板决策追踪和任务来源会不够清晰。",,→

### block_p0112_b041

"options": [

### block_p0112_b042

{

### block_p0112_b043

"option_id": "A",

### block_p0112_b044

"title": " 新增独立decision_logs 表",

### block_p0112_b045

"pros": [" 审计清晰", " 便于追踪决策与任务关系", " 后续扩展空间大"],

### block_p0112_b046

"cons": [" 需要增加后端开发工作量"]

### block_p0112_b047

},

### block_p0112_b048

{

### block_p0112_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0112_b050

AutoMage-2-MVP 架构设计文档·杨卓112

### block_p0112_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 112

## 表格

无。

## 备注

无。

<!-- 来自 page_0112.md 全文结束 -->

<!-- 来自 page_0113.md 全文开始 -->

# Page 0113

## 原始文本块

### block_p0113_b001

2026 年5 月3 日

### block_p0113_b002

"option_id": "B",

### block_p0113_b003

"title": " 暂时复用audit_logs 和tasks",

### block_p0113_b004

"pros": [" 短期实现更快"],

### block_p0113_b005

"cons": [" 决策对象不够独立", " 后续复盘和统计不方便"]

### block_p0113_b006

}

### block_p0113_b007

],

### block_p0113_b008

"recommended_option": "A",

### block_p0113_b009

"reason": "AutoMage-2 的核心价值在于决策可追溯，独立决策表更符合长期架构。",

### block_p0113_b010

"source_record_ids": [301, 302],

### block_p0113_b011

"urgency": "high"

### block_p0113_b012

}

### block_p0113_b013

],

### block_p0113_b014

"next_day_adjustment": [

### block_p0113_b015

{

### block_p0113_b016

"title": " 优先确认Decision 数据结构",

### block_p0113_b017

"reason": " 该事项影响Executive 决策链路和任务下发闭环。",

### block_p0113_b018

"target_user_ids": [10086, 20002],

### block_p0113_b019

"priority": "high",

### block_p0113_b020

"expected_output": " 形成decision_logs 是否建表的最终结论和字段草案。"

### block_p0113_b021

}

### block_p0113_b022

],

### block_p0113_b023

"source_record_ids": [301, 302, 303, 304, 305, 306, 307, 308],

### block_p0113_b024

"related_task_ids": [401, 402],

### block_p0113_b025

"related_incident_ids": [501],

### block_p0113_b026

"signature": {

### block_p0113_b027

"signature_required": true,

### block_p0113_b028

"signature_status": "signed",

### block_p0113_b029

"signed_by": 20001,

### block_p0113_b030

"signed_at": "2026-05-03T21:25:00+08:00",

### block_p0113_b031

"payload_hash": "sha256:manager_summary_example_hash",

### block_p0113_b032

"signature_source": "im"

### block_p0113_b033

},

### block_p0113_b034

"meta": {

### block_p0113_b035

"input_channel": "scheduled_job",

### block_p0113_b036

"agent_template_version": "manager_agent_v0.1",

### block_p0113_b037

"staff_total_count": 10,

### block_p0113_b038

"summary_window": "daily"

### block_p0113_b039

}

### block_p0113_b040

}

### block_p0113_b041

6.5Manager Schema 聚合逻辑

### block_p0113_b042

Manager Schema 的生成过程应分为“读取、过滤、归类、提炼、判断、输出”六步。

### block_p0113_b043

读取Staff Schema

### block_p0113_b044

↓

### block_p0113_b045 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0113_b046

AutoMage-2-MVP 架构设计文档·杨卓113

### block_p0113_b047 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 113

## 表格

无。

## 备注

无。

<!-- 来自 page_0113.md 全文结束 -->

<!-- 来自 page_0114.md 全文开始 -->

# Page 0114

## 原始文本块

### block_p0114_b001

2026 年5 月3 日

### block_p0114_b002

过滤无效数据

### block_p0114_b003

↓

### block_p0114_b004

按事项归类

### block_p0114_b005

↓

### block_p0114_b006

提炼部门进展

### block_p0114_b007

↓

### block_p0114_b008

判断风险和权限边界

### block_p0114_b009

↓

### block_p0114_b010

输出Manager Schema

### block_p0114_b011

6.5.1读取Staff Schema

### block_p0114_b012

Manager Agent 只读取本部门、指定日期、已提交或已确认的Staff Schema。

### block_p0114_b013

推荐读取条件：

### block_p0114_b014

org_id = 当前组织

### block_p0114_b015

department_id = 当前部门

### block_p0114_b016

record_date = 汇总日期

### block_p0114_b017

status = 已提交/ 已确认

### block_p0114_b018

deleted_at is null

### block_p0114_b019

不应读取：

### block_p0114_b020

1. 草稿日报。

### block_p0114_b021

2. 校验失败日报。

### block_p0114_b022

3. 未签名且需要签名的日报。

### block_p0114_b023

4. 其他部门日报。

### block_p0114_b024

5. 已删除或无效记录。

### block_p0114_b025

6.5.2过滤无效数据

### block_p0114_b026

读取后，Manager Agent 需要过滤不适合进入正式汇总的数据。

### block_p0114_b027

需要过滤的数据包括：

### block_p0114_b028

1. 空日报。

### block_p0114_b029

2. 未确认日报。

### block_p0114_b030

3. 重复提交但已被新版本覆盖的日报。

### block_p0114_b031

4. 字段明显不完整的日报。

### block_p0114_b032

5. 当前Manager 无权限读取的数据。

### block_p0114_b033

过滤结果应影响staff_report_count 和missing_report_count，并在必要时进入风险

### block_p0114_b034

提示。

### block_p0114_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0114_b036

AutoMage-2-MVP 架构设计文档·杨卓114

### block_p0114_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 114

## 表格

无。

## 备注

无。

<!-- 来自 page_0114.md 全文结束 -->

<!-- 来自 page_0115.md 全文开始 -->

# Page 0115

## 原始文本块

### block_p0115_b001

2026 年5 月3 日

### block_p0115_b002

6.5.3按事项归类

### block_p0115_b003

Manager Agent 应将Staff Schema 中的信息归类为以下几类：

### block_p0115_b004

类别来源字段

### block_p0115_b005

已完成事项work_progress.status = completed

### block_p0115_b006

进行中事项work_progress.status = in_progress

### block_p0115_b007

阻塞事项work_progress.status = blocked、issues_faced

### block_p0115_b008

支持需求need_support = true、support_detail

### block_p0115_b009

明日计划next_day_plan

### block_p0115_b010

产出物artifacts

### block_p0115_b011

风险risk_level、issues_faced.severity

### block_p0115_b012

关联任务related_task_ids

### block_p0115_b013

归类后再进行汇总，避免生成一段没有结构的流水账。

### block_p0115_b014

6.5.4提炼部门进展

### block_p0115_b015

部门进展应从多个员工日报中提炼出来，不能逐条堆叠。

### block_p0115_b016

提炼时应优先关注：

### block_p0115_b017

1. 与部门目标相关的事项。

### block_p0115_b018

2. 已完成的关键任务。

### block_p0115_b019

3. 影响后续链路的关键产出。

### block_p0115_b020

4. 多名员工共同推进的事项。

### block_p0115_b021

5. 进度明显变化的事项。

### block_p0115_b022

示例：

### block_p0115_b023

不推荐：

### block_p0115_b024

张三完成接口文档，李四做了数据库，王五修改了Prompt，赵六整理了会议纪要。

### block_p0115_b025

推荐：

### block_p0115_b026

今日架构组主要推进了Schema 契约、数据库映射和Agent Mock Flow 三条线，其中Staff Schema

### block_p0115_b027

已完成初稿，数据库映射进入对齐阶段，Agent Mock Flow 已具备基本闭环。,→

### block_p0115_b028

6.5.5判断风险和权限边界

### block_p0115_b029

Manager Agent 需要判断每个问题属于哪一类：

### block_p0115_b030

类型处理方式

### block_p0115_b031

员工个人可解决记录即可，不生成上推

### block_p0115_b032

部门内可解决进入manager_decisions 或部门任务

### block_p0115_b033

需要跨部门支持进入blocked_items，必要时上推

### block_p0115_b034

超出Manager 权限进入need_executive_decision

### block_p0115_b035

影响关键交付进入top_3_risks

### block_p0115_b036

数据不足进入风险提示或缺失日报提示

### block_p0115_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0115_b038

AutoMage-2-MVP 架构设计文档·杨卓115

### block_p0115_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 115

## 表格

无。

## 备注

无。

<!-- 来自 page_0115.md 全文结束 -->

<!-- 来自 page_0116.md 全文开始 -->

# Page 0116

## 原始文本块

### block_p0116_b001

2026 年5 月3 日

### block_p0116_b002

权限边界的判断应保守。凡是涉及预算、战略方向、跨部门资源、重大延期、重大客户、

### block_p0116_b003

组织结构调整等事项，应优先进入need_executive_decision。

### block_p0116_b004

6.5.6输出Manager Schema

### block_p0116_b005

输出Manager Schema 前，Agent 应检查：

### block_p0116_b006

1. aggregated_summary 是否清楚。

### block_p0116_b007

2. top_3_risks 是否只保留重要风险。

### block_p0116_b008

3. pending_approvals 是否与need_executive_decision 数量一致。

### block_p0116_b009

4. source_record_ids 是否完整。

### block_p0116_b010

5. overall_health 是否与风险情况一致。

### block_p0116_b011

6. 是否存在需要部门负责人确认的事项。

### block_p0116_b012

7. 是否存在未处理的高风险阻塞。

### block_p0116_b013

输出后，应交由部门负责人确认或进入待确认状态。

### block_p0116_b014

6.6Manager Schema 生成Prompt 约束

### block_p0116_b015

Manager Agent 生成Manager Schema 时，应遵守以下约束。

### block_p0116_b016

6.6.1不复制员工日报

### block_p0116_b017

Manager Agent 不应简单拼接员工日报。它需要完成提炼、归类和判断。

### block_p0116_b018

错误方式：

### block_p0116_b019

张三今天做了A，李四今天做了B，王五今天做了C……

### block_p0116_b020

正确方式：

### block_p0116_b021

今日部门主要推进了A、B、C 三类工作，其中A 已完成，B 仍在进行，C 受外部依赖影响存在延期风险。

### block_p0116_b022

6.6.2不编造未出现的信息

### block_p0116_b023

Staff Schema 中没有出现的信息，Manager Agent 不得自行补充。

### block_p0116_b024

如果员工没有提交产出物，Manager Agent 不能写“已完成文档产出”。如果没有明确风

### block_p0116_b025

险来源，不能随意生成严重风险。

### block_p0116_b026

所有关键判断都应尽量关联source_record_ids。

### block_p0116_b027 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0116_b028

AutoMage-2-MVP 架构设计文档·杨卓116

### block_p0116_b029 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 116

## 表格

无。

## 备注

无。

<!-- 来自 page_0116.md 全文结束 -->

<!-- 来自 page_0117.md 全文开始 -->

# Page 0117

## 原始文本块

### block_p0117_b001

2026 年5 月3 日

### block_p0117_b002

6.6.3明确区分事实和判断

### block_p0117_b003

Manager Schema 中应区分事实信息和Agent 判断。

### block_p0117_b004

事实包括：

### block_p0117_b005

1. 已提交日报数量。

### block_p0117_b006

2. 缺失日报数量。

### block_p0117_b007

3. 员工填写的完成事项。

### block_p0117_b008

4. 已存在任务状态。

### block_p0117_b009

5. 已上报异常。

### block_p0117_b010

判断包括：

### block_p0117_b011

1. 部门健康度。

### block_p0117_b012

2. 风险等级。

### block_p0117_b013

3. 效能评分。

### block_p0117_b014

4. 是否需要上推。

### block_p0117_b015

5. 次日调整建议。

### block_p0117_b016

判断字段必须尽量给出依据，不要只给结论。

### block_p0117_b017

6.6.4高风险必须说明来源

### block_p0117_b018

如果overall_health = red，或某风险severity = high / critical，必须说明来源。

### block_p0117_b019

至少应提供：

### block_p0117_b020

1. 关联Staff 日报ID。

### block_p0117_b021

2. 关联任务ID 或异常ID。

### block_p0117_b022

3. 风险产生原因。

### block_p0117_b023

4. 建议下一步动作。

### block_p0117_b024

没有来源的高风险判断不应进入正式汇总。

### block_p0117_b025

6.6.5上推事项必须整理成决策题

### block_p0117_b026

如果事项进入need_executive_decision，不能只写“需要老板处理”。

### block_p0117_b027

应尽量整理为以下结构：

### block_p0117_b028

1. 决策标题。

### block_p0117_b029

2. 背景说明。

### block_p0117_b030

3. 至少两个可选方案。

### block_p0117_b031

4. 推荐方案。

### block_p0117_b032

5. 推荐理由。

### block_p0117_b033

6. 紧急程度。

### block_p0117_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0117_b035

AutoMage-2-MVP 架构设计文档·杨卓117

### block_p0117_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 117

## 表格

无。

## 备注

无。

<!-- 来自 page_0117.md 全文结束 -->

<!-- 来自 page_0118.md 全文开始 -->

# Page 0118

## 原始文本块

### block_p0118_b001

2026 年5 月3 日

### block_p0118_b002

7. 来源记录。

### block_p0118_b003

老板需要的是判断题或选择题，不是开放式问题。

### block_p0118_b004

6.6.6保留中层处理价值

### block_p0118_b005

Manager Agent 应记录部门内已经处理的问题，包括调整优先级、安排协作、催办缺失

### block_p0118_b006

日报、处理轻中度异常等。

### block_p0118_b007

这些内容进入manager_decisions，用于体现中层管理者的实际价值。

### block_p0118_b008

系统不应只记录“上推给老板”的事项，否则会让中层看起来没有贡献。

### block_p0118_b009

6.7Manager Schema 风险识别规则

### block_p0118_b010

Manager Agent 的风险识别应遵循明确规则，避免凭空判断。

### block_p0118_b011

6.7.1风险来源

### block_p0118_b012

风险主要来自以下字段或对象：

### block_p0118_b013

来源说明

### block_p0118_b014

Staff Schema.risk_level员工自报风险

### block_p0118_b015

Staff Schema.issues_faced员工遇到的问题

### block_p0118_b016

Staff Schema.need_support员工请求支持

### block_p0118_b017

work_progress.status = blocked工作事项阻塞

### block_p0118_b018

缺失日报数据不完整风险

### block_p0118_b019

逾期任务执行风险

### block_p0118_b020

未关闭异常管理风险

### block_p0118_b021

重复出现的问题结构性风险

### block_p0118_b022

6.7.2风险等级判断

### block_p0118_b023

建议Manager Agent 按以下规则判断风险等级：

### block_p0118_b024

风险等级判断标准

### block_p0118_b025

low问题轻微，不影响部门计划

### block_p0118_b026

medium需要部门负责人关注，但部门内可处理

### block_p0118_b027

high可能影响关键任务、交付或跨部门协作

### block_p0118_b028

critical已经影响关键交付、客户、预算或老板目标

### block_p0118_b029

示例：

### block_p0118_b030

情况建议等级

### block_p0118_b031

单个员工日报缺少产出物low

### block_p0118_b032

两名员工任务轻微延期medium

### block_p0118_b033

关键表结构未确认，影响联调high

### block_p0118_b034

客户交付延期或重大事故critical

### block_p0118_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0118_b036

AutoMage-2-MVP 架构设计文档·杨卓118

### block_p0118_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 118

## 表格

无。

## 备注

无。

<!-- 来自 page_0118.md 全文结束 -->

<!-- 来自 page_0119.md 全文开始 -->

# Page 0119

## 原始文本块

### block_p0119_b001

2026 年5 月3 日

### block_p0119_b002

6.7.3风险进入top_3_risks 的条件

### block_p0119_b003

不是所有风险都进入top_3_risks。

### block_p0119_b004

进入条件建议为：

### block_p0119_b005

1. 风险等级为high 或critical。

### block_p0119_b006

2. 影响多个员工或多个任务。

### block_p0119_b007

3. 影响MVP 主链路。

### block_p0119_b008

4. 需要跨部门协调。

### block_p0119_b009

5. 需要老板或高管决策。

### block_p0119_b010

6. 重复出现且长期未解决。

### block_p0119_b011

普通问题可以进入blocked_items，不必进入Top 风险。

### block_p0119_b012

6.7.4缺失日报风险

### block_p0119_b013

如果缺失日报比例较高，Manager Agent 应提示数据完整性风险。

### block_p0119_b014

建议规则：

### block_p0119_b015

缺失比例处理方式

### block_p0119_b016

0%正常

### block_p0119_b017

1%-20%轻微提示

### block_p0119_b018

20%-40%标记为medium 风险

### block_p0119_b019

40% 以上部门健康度建议为yellow 或gray

### block_p0119_b020

缺失日报不应直接等同于员工未工作，但会影响部门汇总可信度。

### block_p0119_b021

6.7.5风险与异常的转换

### block_p0119_b022

如果风险已经影响任务执行，或需要明确负责人处理，应转为Incident 或Task。

### block_p0119_b023

转换建议：

### block_p0119_b024

情况转换对象

### block_p0119_b025

风险仅需关注留在top_3_risks

### block_p0119_b026

风险需要处理人跟进生成incidents

### block_p0119_b027

风险已有明确行动生成tasks

### block_p0119_b028

风险超出部门权限生成need_executive_decision

### block_p0119_b029

MVP 阶段可以先不自动创建全部Incident，但必须在Schema 中保留清晰的风险和来源

### block_p0119_b030

信息。

### block_p0119_b031

6.8Manager Schema 与Staff Schema 的关系

### block_p0119_b032

Manager Schema 是由多个Staff Schema 聚合生成的上层结构。

### block_p0119_b033

二者关系如下：

### block_p0119_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0119_b035

AutoMage-2-MVP 架构设计文档·杨卓119

### block_p0119_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 119

## 表格

无。

## 备注

无。

<!-- 来自 page_0119.md 全文结束 -->

<!-- 来自 page_0120.md 全文开始 -->

# Page 0120

## 原始文本块

### block_p0120_b001

2026 年5 月3 日

### block_p0120_b002

多个Staff Schema

### block_p0120_b003

↓

### block_p0120_b004

读取、过滤、归类、提炼

### block_p0120_b005

↓

### block_p0120_b006

一个Manager Schema

### block_p0120_b007

6.8.1字段对应关系

### block_p0120_b008

Staff Schema 字段Manager Schema 字段说明

### block_p0120_b009

work_progressaggregated_summary提炼部门整体进展

### block_p0120_b010

issues_facedtop_3_risks / blocked_items提取风险和阻塞

### block_p0120_b011

solution_attemptblocked_items.suggested_next_step 判断是否仍需支持

### block_p0120_b012

need_supportblocked_items/

### block_p0120_b013

need_executive_decision

### block_p0120_b014

判断是否需要上级处理

### block_p0120_b015

support_detailblocked_items.description形成阻塞说明

### block_p0120_b016

next_day_plannext_day_adjustment提炼次日部门安排

### block_p0120_b017

artifactshighlight_staff/

### block_p0120_b018

aggregated_summary

### block_p0120_b019

标记关键产出

### block_p0120_b020

related_task_idsrelated_task_ids关联任务

### block_p0120_b021

risk_leveloverall_health / top_3_risks影响部门风险判断

### block_p0120_b022

signature过滤条件未确认数据不进入正式汇总

### block_p0120_b023

6.8.2一对多与多对一关系

### block_p0120_b024

一个Staff Schema 通常只属于一个员工、一个日期、一个部门。

### block_p0120_b025

一个Manager Schema 通常引用多个Staff Schema。

### block_p0120_b026

Staff Schema 1

### block_p0120_b027

Staff Schema 2

### block_p0120_b028

Staff Schema 3

### block_p0120_b029

↓

### block_p0120_b030

Manager Schema

### block_p0120_b031

因此，Manager Schema 必须保留source_record_ids，否则后续无法追溯部门汇总来源。

### block_p0120_b032

6.8.3Staff 数据不完整时的处理

### block_p0120_b033

如果部分员工未提交日报，Manager Schema 仍然可以生成，但必须标记数据不完整。

### block_p0120_b034

处理方式：

### block_p0120_b035

1. missing_report_count 记录缺失数量。

### block_p0120_b036

2. missing_staff_ids 记录缺失员工。

### block_p0120_b037

3. overall_health 可根据缺失比例调整为yellow 或gray。

### block_p0120_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0120_b039

AutoMage-2-MVP 架构设计文档·杨卓120

### block_p0120_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 120

## 表格

无。

## 备注

无。

<!-- 来自 page_0120.md 全文结束 -->

<!-- 来自 page_0121.md 全文开始 -->

# Page 0121

## 原始文本块

### block_p0121_b001

2026 年5 月3 日

### block_p0121_b002

4. aggregated_summary 中说明数据不完整。

### block_p0121_b003

5. 必要时生成催填任务或提醒。

### block_p0121_b004

不建议因为少量日报缺失就阻塞整个部门汇总。但如果缺失比例过高，Executive Agent

### block_p0121_b005

应看到该风险。

### block_p0121_b006

6.8.4Staff 原始数据不得被覆盖

### block_p0121_b007

Manager Agent 可以引用、汇总和判断Staff Schema，但不能直接覆盖Staff 原始日报。

### block_p0121_b008

如果发现Staff Schema 有明显错误，应通过以下方式处理：

### block_p0121_b009

1. 标记为数据异常。

### block_p0121_b010

2. 通知Staff Agent 或员工修改。

### block_p0121_b011

3. 生成审计日志。

### block_p0121_b012

4. 等员工重新确认后再进入正式汇总。

### block_p0121_b013

Manager Agent 不应直接替员工改日报。

### block_p0121_b014

6.9Manager Schema 与数据库字段映射

### block_p0121_b015

Manager Schema 主要映射到summaries 和summary_source_links，部分字段可关联

### block_p0121_b016

tasks、incidents、audit_logs。

### block_p0121_b017

6.9.1映射到summaries

### block_p0121_b018

summaries 存储部门汇总主记录。

### block_p0121_b019

Manager Schema 字段数据库字段说明

### block_p0121_b020

org_idsummaries.org_id组织ID

### block_p0121_b021

dept_idsummaries.department_id部门ID

### block_p0121_b022

manager_user_idsummaries.user_id或

### block_p0121_b023

meta.manager_user_id

### block_p0121_b024

中层负责人

### block_p0121_b025

summary_datesummaries.summary_date汇总日期

### block_p0121_b026

schema_id / schema_versionsummaries.metaSchema 标识和版本

### block_p0121_b027

aggregated_summarysummaries.content汇总正文

### block_p0121_b028

部门汇总标题summaries.title可自动生成

### block_p0121_b029

summary_typesummaries.summary_type部门日报类型

### block_p0121_b030

scope_typesummaries.scope_type部门级汇总

### block_p0121_b031

staff_report_countsummaries.source_count来源数量

### block_p0121_b032

overall_healthsummaries.meta部门健康度

### block_p0121_b033

top_3_riskssummaries.meta风险列表

### block_p0121_b034

signaturesummaries.meta签名信息

### block_p0121_b035

标题可以由系统生成，例如：

### block_p0121_b036

2026-05-03 架构组部门日报

### block_p0121_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0121_b038

AutoMage-2-MVP 架构设计文档·杨卓121

### block_p0121_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 121

## 表格

无。

## 备注

无。

<!-- 来自 page_0121.md 全文结束 -->

<!-- 来自 page_0122.md 全文开始 -->

# Page 0122

## 原始文本块

### block_p0122_b001

2026 年5 月3 日

### block_p0122_b002

如果summaries 当前字段无法承载所有结构化内容，可将完整Manager Schema 存入

### block_p0122_b003

meta，同时将摘要正文存入content。后续高频查询字段再逐步实体化。

### block_p0122_b004

6.9.2映射到summary_source_links

### block_p0122_b005

summary_source_links 用于记录Manager Schema 引用了哪些Staff Work Record。

### block_p0122_b006

Manager Schema 字段数据库字段说明

### block_p0122_b007

source_record_ids[]summary_source_links.source_id来源Staff 日报ID

### block_p0122_b008

固定值summary_source_links.source_type来源类型，如work_record

### block_p0122_b009

当前summary IDsummary_source_links.summary_id当前部门汇总ID

### block_p0122_b010

org_idsummary_source_links.org_id组织ID

### block_p0122_b011

该映射非常重要，决定了部门汇总能否追溯到原始员工日报。

### block_p0122_b012

6.9.3映射到tasks

### block_p0122_b013

如果Manager Schema 中存在次日调整建议或部门内处理事项，可以生成任务。

### block_p0122_b014

Manager Schema 字段数据库字段说明

### block_p0122_b015

next_day_adjustment[].title tasks.title任务标题

### block_p0122_b016

next_day_adjustment[].expected_outputtasks.description任务说明

### block_p0122_b017

dept_idtasks.department_id所属部门

### block_p0122_b018

target_user_ids[]task_assignments.user_id执行人

### block_p0122_b019

prioritytasks.priority优先级

### block_p0122_b020

当前summary IDtasks.meta.source_summary_id来源部门汇总

### block_p0122_b021

MVP 阶段建议任务生成需要Manager 确认，不要把所有建议自动变成任务。

### block_p0122_b022

6.9.4映射到incidents

### block_p0122_b023

如果Manager Schema 中存在严重阻塞事项，可以生成或更新异常。

### block_p0122_b024

Manager Schema 字段数据库字段说明

### block_p0122_b025

blocked_items[].titleincidents.title异常标题

### block_p0122_b026

blocked_items[].description incidents.description异常说明

### block_p0122_b027

blocked_items[].severityincidents.severity严重程度

### block_p0122_b028

dept_idincidents.department_id所属部门

### block_p0122_b029

owner_user_idincidents.reporter_user_id或

### block_p0122_b030

meta.owner_user_id

### block_p0122_b031

当前负责人

### block_p0122_b032

当前summary IDincidents.meta.source_summary_id来源部门汇总

### block_p0122_b033

如果阻塞事项已经由Staff Schema 生成过Incident，Manager Schema 应关联已有

### block_p0122_b034

related_incident_ids，不应重复创建。

### block_p0122_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0122_b036

AutoMage-2-MVP 架构设计文档·杨卓122

### block_p0122_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 122

## 表格

无。

## 备注

无。

<!-- 来自 page_0122.md 全文结束 -->

<!-- 来自 page_0123.md 全文开始 -->

# Page 0123

## 原始文本块

### block_p0123_b001

2026 年5 月3 日

### block_p0123_b002

6.9.5映射到决策记录

### block_p0123_b003

need_executive_decision 建议映射到独立Decision 表。若MVP 阶段暂未建表，可以

### block_p0123_b004

先存入summaries.meta.need_executive_decision，并写入audit_logs。

### block_p0123_b005

建议后续新增决策对象时，映射如下：

### block_p0123_b006

Manager Schema 字段决策对象字段说明

### block_p0123_b007

decision_titledecision.title决策标题

### block_p0123_b008

contextdecision.context决策背景

### block_p0123_b009

optionsdecision.options候选方案

### block_p0123_b010

recommended_optiondecision.recommended_option推荐方案

### block_p0123_b011

reasondecision.reason推荐理由

### block_p0123_b012

urgencydecision.priority紧急程度

### block_p0123_b013

当前summary IDdecision.source_summary_id来源部门汇总

### block_p0123_b014

该部分是当前数据库设计需要重点补齐的地方。

### block_p0123_b015

6.9.6映射到audit_logs

### block_p0123_b016

Manager Schema 的关键操作应写入审计日志。

### block_p0123_b017

建议记录以下动作：

### block_p0123_b018

动作说明

### block_p0123_b019

manager_schema_generatedManager Agent 生成部门汇总

### block_p0123_b020

manager_schema_confirmed部门负责人确认汇总

### block_p0123_b021

manager_schema_submitted汇总写入后端

### block_p0123_b022

manager_schema_validation_failed汇总校验失败

### block_p0123_b023

manager_schema_read_by_executiveExecutive Agent 读取部门汇总

### block_p0123_b024

manager_decision_createdManager 生成权限内决策

### block_p0123_b025

executive_decision_requested生成上推老板事项

### block_p0123_b026

审计日志应记录操作人、Agent 节点、对象ID、操作时间和必要的payload 摘要。

### block_p0123_b027

6.10Manager Agent 读取权限规则

### block_p0123_b028

Manager Agent 的读取权限必须由后端控制，不能只依赖Prompt。

### block_p0123_b029

6.10.1基础读取范围

### block_p0123_b030

Manager Agent 只能读取：

### block_p0123_b031

1. 当前组织内数据。

### block_p0123_b032

2. 当前绑定部门的数据。

### block_p0123_b033

3. 本部门员工已提交、已确认的Staff Schema。

### block_p0123_b034

4. 本部门任务。

### block_p0123_b035

5. 本部门异常。

### block_p0123_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0123_b037

AutoMage-2-MVP 架构设计文档·杨卓123

### block_p0123_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 123

## 表格

无。

## 备注

无。

<!-- 来自 page_0123.md 全文结束 -->

<!-- 来自 page_0124.md 全文开始 -->

# Page 0124

## 原始文本块

### block_p0124_b001

2026 年5 月3 日

### block_p0124_b002

6. 本部门历史汇总。

### block_p0124_b003

7. 与本部门相关的上级决策和任务。

### block_p0124_b004

Manager Agent 不应读取：

### block_p0124_b005

1. 其他组织数据。

### block_p0124_b006

2. 其他部门员工明细。

### block_p0124_b007

3. 老板未授权的组织级敏感数据。

### block_p0124_b008

4. 员工未确认草稿。

### block_p0124_b009

5. 已删除或无效记录。

### block_p0124_b010

6. 无关部门的任务和异常。

### block_p0124_b011

6.10.2读取Staff Schema 的条件

### block_p0124_b012

读取Staff Schema 时，后端应校验：

### block_p0124_b013

条件说明

### block_p0124_b014

org_id 一致防止跨组织读取

### block_p0124_b015

department_id 在权限范围内防止跨部门读取

### block_p0124_b016

Staff 记录状态有效只读取正式记录

### block_p0124_b017

Staff 签名状态有效未确认数据不进入正式汇总

### block_p0124_b018

当前Manager Agent 绑定有效防止伪造节点

### block_p0124_b019

请求时间和汇总日期合法防止异常范围查询

### block_p0124_b020

推荐查询条件：

### block_p0124_b021

org_id = 当前组织

### block_p0124_b022

department_id = 当前Manager 部门

### block_p0124_b023

record_date = 指定日期

### block_p0124_b024

status in 已提交/ 已确认

### block_p0124_b025

deleted_at is null

### block_p0124_b026

6.10.3跨部门事项处理

### block_p0124_b027

如果某个阻塞事项涉及其他部门，Manager Agent 不能直接读取对方部门明细。

### block_p0124_b028

正确方式是：

### block_p0124_b029

1. 在blocked_items 中标记跨部门依赖。

### block_p0124_b030

2. 生成跨部门协作请求。

### block_p0124_b031

3. 由后端或Executive Agent 判断是否授权。

### block_p0124_b032

4. 必要时上推老板或更高层确认。

### block_p0124_b033

5. 授权后再读取必要的摘要级数据。

### block_p0124_b034

MVP 阶段可以先不做复杂跨部门授权，但必须避免Manager Agent 默认拥有全公司读

### block_p0124_b035

取权限。

### block_p0124_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0124_b037

AutoMage-2-MVP 架构设计文档·杨卓124

### block_p0124_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 124

## 表格

无。

## 备注

无。

<!-- 来自 page_0124.md 全文结束 -->

<!-- 来自 page_0125.md 全文开始 -->

# Page 0125

## 原始文本块

### block_p0125_b001

2026 年5 月3 日

### block_p0125_b002

6.10.4数据下钻权限

### block_p0125_b003

老板或Executive Agent 可以从部门汇总下钻到来源Staff 记录，但Manager Agent 不应

### block_p0125_b004

跨部门下钻。

### block_p0125_b005

Manager Agent 的下钻范围：

### block_p0125_b006

本部门Manager Summary

### block_p0125_b007

↓

### block_p0125_b008

本部门Staff Work Records

### block_p0125_b009

↓

### block_p0125_b010

本部门Staff Work Record Items

### block_p0125_b011

禁止范围：

### block_p0125_b012

其他部门Manager Summary

### block_p0125_b013

其他部门Staff Work Records

### block_p0125_b014

组织级老板决策明细

### block_p0125_b015

其他部门员工个人日报

### block_p0125_b016

6.10.5权限失败处理

### block_p0125_b017

如果Manager Agent 发起越权读取，后端应返回明确错误。

### block_p0125_b018

常见错误包括：

### block_p0125_b019

错误类型建议处理

### block_p0125_b020

401 未鉴权要求重新初始化或登录

### block_p0125_b021

403 无权限拒绝读取，并记录审计

### block_p0125_b022

404 数据不存在返回空结果，不暴露其他部门存在性

### block_p0125_b023

422 参数错误提示Agent 修正请求参数

### block_p0125_b024

Agent 收到权限错误后，不应反复重试，也不应尝试改写部门ID 继续请求。

### block_p0125_b025

6.10.6Manager 汇总的写入权限

### block_p0125_b026

Manager Agent 只能写入自己负责部门的Manager Schema。

### block_p0125_b027

写入时后端应校验：

### block_p0125_b028

1. manager_user_id 是否为该部门负责人或授权管理者。

### block_p0125_b029

2. manager_node_id 是否绑定该部门。

### block_p0125_b030

3. dept_id 是否属于当前组织。

### block_p0125_b031

4. source_record_ids 是否全部来自该部门。

### block_p0125_b032

5. 是否存在未授权来源数据。

### block_p0125_b033

6. 签名人是否具备确认权限。

### block_p0125_b034

如果source_record_ids 中出现其他部门记录，应拒绝写入。

### block_p0125_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0125_b036

AutoMage-2-MVP 架构设计文档·杨卓125

### block_p0125_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 125

## 表格

无。

## 备注

无。

<!-- 来自 page_0125.md 全文结束 -->

<!-- 来自 page_0126.md 全文开始 -->

# Page 0126

## 原始文本块

### block_p0126_b001

2026 年5 月3 日

### block_p0126_b002

6.10.7审计要求

### block_p0126_b003

Manager Agent 的读取和写入都应保留审计记录，尤其是以下行为：

### block_p0126_b004

1. 读取本部门Staff 数据。

### block_p0126_b005

2. 生成部门汇总。

### block_p0126_b006

3. 修改部门汇总。

### block_p0126_b007

4. 确认部门汇总。

### block_p0126_b008

5. 创建部门任务。

### block_p0126_b009

6. 创建上推老板事项。

### block_p0126_b010

7. 读取历史汇总。

### block_p0126_b011

8. 权限失败请求。

### block_p0126_b012

Manager 层是组织数据从一线流向老板的关键中转点，必须保证可追溯。否则老板看到

### block_p0126_b013

的摘要无法说明来源，员工也无法确认自己的原始信息是否被正确使用。

### block_p0126_b014

6.11本章小结

### block_p0126_b015

Manager Schema 是AutoMage-2 MVP 中承上启下的核心结构。

### block_p0126_b016

它向下读取Staff Schema，向上提供Executive Agent 可理解的部门态势。它既不能只是

### block_p0126_b017

员工日报拼接，也不能变成没有来源的主观判断。一个合格的Manager Schema 应该同时满

### block_p0126_b018

足四个要求：

### block_p0126_b019

1. 能说明部门今天整体推进了什么。

### block_p0126_b020

2. 能指出当前最重要的风险和阻塞。

### block_p0126_b021

3. 能记录中层已经处理了哪些权限内事项。

### block_p0126_b022

4. 能把超权限问题整理成老板可判断的决策项。

### block_p0126_b023

MVP 阶段只要Manager Schema 能稳定完成“读取员工日报→生成部门汇总→标记

### block_p0126_b024

风险→上推决策→写入数据库”这一过程，就可以支撑Executive Agent 继续生成老板侧

### block_p0126_b025

摘要和任务下发闭环。

### block_p0126_b026 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0126_b027

AutoMage-2-MVP 架构设计文档·杨卓126

### block_p0126_b028 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 126

## 表格

无。

## 备注

无。

<!-- 来自 page_0126.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

