# Executive 决策 Schema 设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P127-P149
> 对应页面文件：`01_PAGES/page_0127.md` — `01_PAGES/page_0149.md`

## 原文整理

<!-- 来自 page_0127.md 全文开始 -->

# Page 0127

## 原始文本块

### block_p0127_b001

2026 年5 月3 日

### block_p0127_b002

7Executive 决策Schema 设计

### block_p0127_b003

7.1Schema 基本信息

### block_p0127_b004

Executive 决策Schema 是AutoMage-2 MVP 阶段的老板侧数据契约，用于承接各部门

### block_p0127_b005

Manager Schema，并将部门汇总、关键风险、上推事项和历史任务状态整理为老板可以直接

### block_p0127_b006

判断的决策卡片。

### block_p0127_b007

Executive Schema 的核心价值不是生成一篇“公司日报”，而是把老板真正需要处理的事

### block_p0127_b008

情压缩成少量高价值决策项。它要解决的问题是：老板每天不需要看所有一线数据，也不需

### block_p0127_b009

要逐条读部门日报，而是直接看到“今天公司哪里有风险、什么事情需要我拍板、有哪些方

### block_p0127_b010

案、确认后会下发什么任务”。

### block_p0127_b011

字段内容

### block_p0127_b012

Schema 名称Executive 决策Schema

### block_p0127_b013

Schema IDschema_v1_executive

### block_p0127_b014

当前版本1.0.0

### block_p0127_b015

使用节点Executive Agent

### block_p0127_b016

数据生成方Executive Agent / Dream 机制

### block_p0127_b017

数据确认人老板/ 高管/ 指定决策人

### block_p0127_b018

主要触发方式每日早间/ 定时Dream / Manager 上推

### block_p0127_b019

数据来源Manager Schema、历史决策、任务状态、异常记录、外

### block_p0127_b020

部变量

### block_p0127_b021

输出对象老板决策卡片、任务拆解草案、组织级摘要

### block_p0127_b022

主要写入对象决策记录表、summaries、tasks、audit_logs

### block_p0127_b023

主要读取对象老板、高管、任务系统、审计系统

### block_p0127_b024

核心目标将部门汇总转化为老板可确认的决策项，并在确认后生

### block_p0127_b025

成任务闭环

### block_p0127_b026

Executive Schema 的典型流程如下：

### block_p0127_b027

Executive Agent 定时触发

### block_p0127_b028

↓

### block_p0127_b029

读取各部门Manager Schema

### block_p0127_b030

↓

### block_p0127_b031

结合历史任务、异常和决策记录

### block_p0127_b032

↓

### block_p0127_b033

生成组织级业务摘要

### block_p0127_b034

↓

### block_p0127_b035

提取关键风险和待决策事项

### block_p0127_b036

↓

### block_p0127_b037

生成schema_v1_executive

### block_p0127_b038

↓

### block_p0127_b039

推送老板决策卡片

### block_p0127_b040

↓

### block_p0127_b041

老板确认方案

### block_p0127_b042

↓

### block_p0127_b043

系统生成任务并下发

### block_p0127_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0127_b045

AutoMage-2-MVP 架构设计文档·杨卓127

### block_p0127_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 127

## 表格

无。

## 备注

无。

<!-- 来自 page_0127.md 全文结束 -->

<!-- 来自 page_0128.md 全文开始 -->

# Page 0128

## 原始文本块

### block_p0128_b001

2026 年5 月3 日

### block_p0128_b002

↓

### block_p0128_b003

记录决策与执行状态

### block_p0128_b004

MVP 阶段建议Executive Schema 每天至少生成一次，优先在早会前推送。例如Manager

### block_p0128_b005

Agent 在前一天晚上生成部门汇总，Executive Agent 在第二天早上8:00 前生成老板侧决策卡

### block_p0128_b006

片。

### block_p0128_b007

7.1.1Schema ID：schema_v1_executive

### block_p0128_b008

Executive 决策Schema 固定使用：

### block_p0128_b009

"schema_id": "schema_v1_executive"

### block_p0128_b010

该字段用于标识当前数据属于老板侧决策结构。后端、Agent 和前端应根据该字段选择

### block_p0128_b011

对应的校验、展示和存储规则。

### block_p0128_b012

7.1.2使用节点：Executive Agent

### block_p0128_b013

Executive Schema 由Executive Agent 生成。

### block_p0128_b014

Executive Agent 一般绑定老板、高管或公司级管理节点。它可以读取组织级汇总数据、

### block_p0128_b015

部门级Manager Schema、关键任务和异常记录，但不能随意读取不相关的个人隐私数据。

### block_p0128_b016

Executive Agent 的主要工作不是替老板做决定，而是把需要老板判断的事项整理清楚，

### block_p0128_b017

并在老板确认后推动系统生成任务。

### block_p0128_b018

7.1.3触发方式：每日早间/ 定时Dream

### block_p0128_b019

Executive Schema 可以由两类触发方式生成。

### block_p0128_b020

触发方式说明

### block_p0128_b021

每日早间触发在早会前生成老板侧摘要和决策卡片

### block_p0128_b022

定时Dream 触发系统按固定时间读取部门汇总，生成组织级判断

### block_p0128_b023

Manager 上推触发部门存在超权限事项时，立即生成待决策项

### block_p0128_b024

老板主动查询触发老板主动询问某部门、某任务或某风险时生成局部摘要

### block_p0128_b025

MVP 阶段优先支持“每日早间触发”和“Manager 上推触发”。这样既能保证每天有固

### block_p0128_b026

定汇总，也能处理临时关键事项。

### block_p0128_b027

7.1.4数据来源：Manager Schema、历史决策、外部变量

### block_p0128_b028

Executive Schema 的主要数据来源是各部门的Manager Schema。

### block_p0128_b029

除Manager Schema 外，Executive Agent 还可以读取以下数据作为辅助：

### block_p0128_b030

1. 历史老板决策。

### block_p0128_b031

2. 未完成关键任务。

### block_p0128_b032

3. 逾期任务。

### block_p0128_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0128_b034

AutoMage-2-MVP 架构设计文档·杨卓128

### block_p0128_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 128

## 表格

无。

## 备注

无。

<!-- 来自 page_0128.md 全文结束 -->

<!-- 来自 page_0129.md 全文开始 -->

# Page 0129

## 原始文本块

### block_p0129_b001

2026 年5 月3 日

### block_p0129_b002

4. 未关闭异常。

### block_p0129_b003

5. 前一日或前一周组织级Summary。

### block_p0129_b004

6. Manager 上推的待决策事项。

### block_p0129_b005

7. 老板近期目标或临时指令。

### block_p0129_b006

8. 外部变量，例如客户反馈、市场变化、预算限制等。

### block_p0129_b007

MVP 阶段不建议引入过多外部数据。优先保证从Manager Schema 到老板决策项的链路

### block_p0129_b008

稳定，再逐步扩展外部变量。

### block_p0129_b009

7.1.5输出对象：老板决策卡片、任务拆解

### block_p0129_b010

Executive Schema 的输出主要有两类：

### block_p0129_b011

输出对象说明

### block_p0129_b012

老板决策卡片面向老板展示的摘要、风险、决策项和方案

### block_p0129_b013

任务拆解草案老板确认后可生成的执行任务

### block_p0129_b014

决策卡片解决“老板怎么快速判断”的问题。任务拆解解决“老板确认后怎么落地”的

### block_p0129_b015

问题。

### block_p0129_b016

Executive Schema 必须同时考虑这两件事。只有摘要没有任务，系统会停留在报告层；只

### block_p0129_b017

有任务没有决策依据，后续无法审计和复盘。

### block_p0129_b018

7.2Executive Schema 字段总览

### block_p0129_b019

Executive Schema 字段分为六类：基础身份字段、组织摘要字段、风险字段、决策字段、

### block_p0129_b020

任务字段、确认与审计字段。

### block_p0129_b021 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0129_b022

AutoMage-2-MVP 架构设计文档·杨卓129

### block_p0129_b023 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 129

## 表格

无。

## 备注

无。

<!-- 来自 page_0129.md 全文结束 -->

<!-- 来自 page_0130.md 全文开始 -->

# Page 0130

## 原始文本块

### block_p0130_b001

2026 年5 月3 日

### block_p0130_b002

字段名类型是否必填说明

### block_p0130_b003

schema_idstring是Schema标识，固定为

### block_p0130_b004

schema_v1_executive

### block_p0130_b005

schema_versionstring是Schema 版本，MVP 阶段默认

### block_p0130_b006

1.0.0

### block_p0130_b007

timestampstring是生成时间

### block_p0130_b008

org_idstring / number是组织ID

### block_p0130_b009

executive_user_idstring / number是老板或高管用户ID

### block_p0130_b010

executive_node_idstring是Executive Agent 节点ID

### block_p0130_b011

summary_datestring是摘要对应日期

### block_p0130_b012

business_summarystring是公司级业务摘要

### block_p0130_b013

key_risksarray是关键风险

### block_p0130_b014

decision_requiredboolean是是否需要老板决策

### block_p0130_b015

decision_itemsarray否待决策事项列表

### block_p0130_b016

option_aobject条件必填单决策项场景下的方案A

### block_p0130_b017

option_bobject条件必填单决策项场景下的方案B

### block_p0130_b018

recommended_optionstring否Agent 推荐方案

### block_p0130_b019

reasoning_summarystring否推荐理由摘要

### block_p0130_b020

expected_impactobject否预期影响

### block_p0130_b021

generated_tasksarray否老板确认后可下发任务

### block_p0130_b022

source_summary_idsarray是引用的部门汇总ID

### block_p0130_b023

source_decision_idsarray否引用的历史决策ID

### block_p0130_b024

source_incident_idsarray否引用的异常ID

### block_p0130_b025

human_confirm_status string是人工确认状态

### block_p0130_b026

confirmed_bystring / number否确认人

### block_p0130_b027

confirmed_atstring否确认时间

### block_p0130_b028

confirmed_optionstring否最终确认方案

### block_p0130_b029

signatureobject否老板确认签名

### block_p0130_b030

metaobject否扩展字段

### block_p0130_b031

MVP 阶段建议以decision_items 作为主要结构，option_a、option_b 可以作为单决

### block_p0130_b032

策项场景下的快捷字段。后续如果一个Executive Schema 中包含多个决策项，每个决策项内

### block_p0130_b033

部应各自包含自己的方案列表。

### block_p0130_b034

7.3字段定义明细

### block_p0130_b035

7.3.1timestamp：生成时间

### block_p0130_b036

timestamp 表示Executive Schema 被生成的时间，使用ISO8601 格式。

### block_p0130_b037

示例：

### block_p0130_b038

"timestamp": "2026-05-04T08:00:00+08:00"

### block_p0130_b039

该字段用于判断老板侧摘要是否按时生成，也用于后续审计和任务追踪。

### block_p0130_b040

需要注意，timestamp 是生成时间，summary_date 是摘要覆盖的业务日期。比如5 月4

### block_p0130_b041

日早上生成的摘要，可能覆盖的是5 月3 日的业务数据。

### block_p0130_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0130_b043

AutoMage-2-MVP 架构设计文档·杨卓130

### block_p0130_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 130

## 表格

无。

## 备注

无。

<!-- 来自 page_0130.md 全文结束 -->

<!-- 来自 page_0131.md 全文开始 -->

# Page 0131

## 原始文本块

### block_p0131_b001

2026 年5 月3 日

### block_p0131_b002

7.3.2executive_user_id：老板/高管用户ID

### block_p0131_b003

executive_user_id 表示该决策卡片面向的老板或高管用户。

### block_p0131_b004

示例：

### block_p0131_b005

"executive_user_id": 30001

### block_p0131_b006

该字段用于确认谁有权查看和确认该决策。后端应校验当前确认人是否与

### block_p0131_b007

executive_user_id 一致，或是否具备代确认权限。

### block_p0131_b008

如果一个决策需要多名高管确认，MVP 阶段可先由一个主确认人处理，后续再扩展多签

### block_p0131_b009

机制。

### block_p0131_b010

7.3.3executive_node_id：老板Agent 节点ID

### block_p0131_b011

executive_node_id 表示生成该Executive Schema 的老板侧Agent 节点。

### block_p0131_b012

示例：

### block_p0131_b013

"executive_node_id": "executive_node_org_1"

### block_p0131_b014

该字段用于追踪决策项由哪个Executive Agent 生成。后续如果不同老板或不同业务线

### block_p0131_b015

使用不同Executive Agent，该字段可以帮助区分来源。

### block_p0131_b016

7.3.4org_id：组织ID

### block_p0131_b017

org_id 表示该Executive Schema 所属组织。

### block_p0131_b018

示例：

### block_p0131_b019

"org_id": 1

### block_p0131_b020

Executive Schema 属于组织级数据，必须绑定组织ID。Executive Agent 不能跨组织读

### block_p0131_b021

取或生成决策数据。

### block_p0131_b022

7.3.5business_summary：公司级业务摘要

### block_p0131_b023

business_summary 是面向老板的整体业务摘要，用于说明当前组织运行状态。

### block_p0131_b024

示例：

### block_p0131_b025

"business_summary": "昨日各部门整体推进正常，架构组完成Staff Schema 与Manager Schema

### block_p0131_b026

的主要字段设计，后端完成部分业务表结构落地，Agent 客制化已跑通Mock Flow。

### block_p0131_b027

当前主要风险集中在决策记录表结构尚未统一，可能影响Executive 决策确认和任务下发联调。"

### block_p0131_b028

,→

### block_p0131_b029

,→

### block_p0131_b030

该字段应满足以下要求：

### block_p0131_b031

1. 不写流水账。

### block_p0131_b032

2. 不堆砌各部门所有细节。

### block_p0131_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0131_b034

AutoMage-2-MVP 架构设计文档·杨卓131

### block_p0131_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 131

## 表格

无。

## 备注

无。

<!-- 来自 page_0131.md 全文结束 -->

<!-- 来自 page_0132.md 全文开始 -->

# Page 0132

## 原始文本块

### block_p0132_b001

2026 年5 月3 日

### block_p0132_b002

3. 只保留老板需要知道的关键信息。

### block_p0132_b003

4. 明确整体状态、主要进展和关键问题。

### block_p0132_b004

5. 能在30 秒内读完。

### block_p0132_b005

建议控制在150 到400 字之间。MVP 阶段老板侧摘要宁可短一些，也不要让老板重新

### block_p0132_b006

陷入信息过载。

### block_p0132_b007

7.3.6key_risks：关键风险

### block_p0132_b008

key_risks 用于记录组织层面最重要的风险。

### block_p0132_b009

示例：

### block_p0132_b010

"key_risks": [

### block_p0132_b011

{

### block_p0132_b012

"title": " 决策记录结构未统一",

### block_p0132_b013

"description": "Agent mock 流程中已存在decision_logs 概念，但当前数据库DDL

### block_p0132_b014

尚未建立独立决策表，可能影响老板确认、任务来源追踪和后续复盘。",,→

### block_p0132_b015

"severity": "high",

### block_p0132_b016

"affected_departments": [12, 15],

### block_p0132_b017

"source_summary_ids": [801, 802],

### block_p0132_b018

"suggested_action": " 建议尽快确认Decision Schema 与数据库承载方式。"

### block_p0132_b019

}

### block_p0132_b020

]

### block_p0132_b021

建议每个风险项包含：

### block_p0132_b022

子字段类型是否必填说明

### block_p0132_b023

titlestring是风险标题

### block_p0132_b024

descriptionstring是风险说明

### block_p0132_b025

severitystring是风险等级

### block_p0132_b026

affected_departments array否受影响部门

### block_p0132_b027

source_summary_idsarray否来源部门汇总

### block_p0132_b028

suggested_actionstring否建议处理方式

### block_p0132_b029

风险等级建议使用：

### block_p0132_b030

值含义

### block_p0132_b031

low轻微风险

### block_p0132_b032

medium需要关注

### block_p0132_b033

high可能影响关键链路

### block_p0132_b034

critical需要立即决策或干预

### block_p0132_b035

Executive Agent 只应保留组织级关键风险，不应把所有部门风险原样复制上来。

### block_p0132_b036

7.3.7decision_required：是否需要老板决策

### block_p0132_b037

decision_required 表示当前Executive Schema 是否包含需要老板确认的事项。

### block_p0132_b038

示例：

### block_p0132_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0132_b040

AutoMage-2-MVP 架构设计文档·杨卓132

### block_p0132_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 132

## 表格

无。

## 备注

无。

<!-- 来自 page_0132.md 全文结束 -->

<!-- 来自 page_0133.md 全文开始 -->

# Page 0133

## 原始文本块

### block_p0133_b001

2026 年5 月3 日

### block_p0133_b002

"decision_required": true

### block_p0133_b003

如果decision_required = true，则decision_items 必须至少包含一项。

### block_p0133_b004

如果decision_required = false，说明当前只是组织级摘要和风险提示，不需要老板

### block_p0133_b005

立即确认。此时也可以推送给老板，但不应生成任务确认流程。

### block_p0133_b006

7.3.8decision_items：待决策事项列表

### block_p0133_b007

decision_items 是Executive Schema 的核心字段，用于承载老板需要确认的事项。

### block_p0133_b008

示例：

### block_p0133_b009

"decision_items": [

### block_p0133_b010

{

### block_p0133_b011

"decision_id": "decision_tmp_001",

### block_p0133_b012

"title": " 是否新增独立decision_logs 表",

### block_p0133_b013

"context": "当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL

### block_p0133_b014

尚未建立独立决策表。如果不新增，短期可用audit_logs 和tasks 承载，

### block_p0133_b015

但后续老板决策追踪和复盘会不够清晰。",

### block_p0133_b016

,→

### block_p0133_b017

,→

### block_p0133_b018

"decision_level": "L3",

### block_p0133_b019

"urgency": "high",

### block_p0133_b020

"option_a": {

### block_p0133_b021

"option_id": "A",

### block_p0133_b022

"title": " 新增独立decision_logs 表",

### block_p0133_b023

"description": " 为老板决策、候选方案、确认结果和任务来源建立独立数据表。",

### block_p0133_b024

"pros": [" 审计清晰", " 便于复盘", " 后续扩展空间大"],

### block_p0133_b025

"cons": [" 需要增加后端开发工作量"]

### block_p0133_b026

},

### block_p0133_b027

"option_b": {

### block_p0133_b028

"option_id": "B",

### block_p0133_b029

"title": " 暂时复用audit_logs 和tasks",

### block_p0133_b030

"description": " 短期不新增表，先通过审计日志和任务表承载决策结果。",

### block_p0133_b031

"pros": [" 开发更快", "MVP 改动较少"],

### block_p0133_b032

"cons": [" 决策对象不独立", " 后续统计和追踪不方便"]

### block_p0133_b033

},

### block_p0133_b034

"recommended_option": "A",

### block_p0133_b035

"reasoning_summary": "AutoMage-2 的核心价值在于决策可追溯，独立决策对象有利于后续任务生成、

### block_p0133_b036

复盘和老板侧看板。",,→

### block_p0133_b037

"expected_impact": {

### block_p0133_b038

"cost": "medium",

### block_p0133_b039

"timeline": " 短期增加0.5-1 天后端工作量",

### block_p0133_b040

"risk": " 降低后续决策追踪混乱风险",

### block_p0133_b041

"affected_modules": ["backend", "agent", "database"]

### block_p0133_b042

},

### block_p0133_b043

"generated_tasks": [

### block_p0133_b044

{

### block_p0133_b045

"task_title": " 补充decision_logs 表结构草案",

### block_p0133_b046 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0133_b047

AutoMage-2-MVP 架构设计文档·杨卓133

### block_p0133_b048 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 133

## 表格

无。

## 备注

无。

<!-- 来自 page_0133.md 全文结束 -->

<!-- 来自 page_0134.md 全文开始 -->

# Page 0134

## 原始文本块

### block_p0134_b001

2026 年5 月3 日

### block_p0134_b002

"assignee_role": "backend",

### block_p0134_b003

"priority": "high",

### block_p0134_b004

"due_at": "2026-05-04T18:00:00+08:00"

### block_p0134_b005

}

### block_p0134_b006

],

### block_p0134_b007

"source_summary_ids": [801, 802]

### block_p0134_b008

}

### block_p0134_b009

]

### block_p0134_b010

每个决策项应尽量包含背景、方案、推荐理由、影响和可生成任务。老板看到后应该可

### block_p0134_b011

以直接选择，而不是还要再问“具体怎么做”。

### block_p0134_b012

7.3.9option_a：方案A

### block_p0134_b013

option_a 表示某个决策项下的第一个候选方案。

### block_p0134_b014

在单决策项场景下，option_a 可以放在Executive Schema 顶层；在多决策项场景下，建

### block_p0134_b015

议放在decision_items[] 内部。

### block_p0134_b016

示例：

### block_p0134_b017

"option_a": {

### block_p0134_b018

"option_id": "A",

### block_p0134_b019

"title": " 新增独立decision_logs 表",

### block_p0134_b020

"description": " 建立独立表记录老板决策项、候选方案、确认结果和后续任务。",

### block_p0134_b021

"pros": [" 结构清晰", " 便于审计", " 方便后续扩展"],

### block_p0134_b022

"cons": [" 需要增加开发工作量"]

### block_p0134_b023

}

### block_p0134_b024

方案A 不一定代表推荐方案，只是候选方案之一。

### block_p0134_b025

7.3.10option_b：方案B

### block_p0134_b026

option_b 表示某个决策项下的第二个候选方案。

### block_p0134_b027

示例：

### block_p0134_b028

"option_b": {

### block_p0134_b029

"option_id": "B",

### block_p0134_b030

"title": " 暂时复用audit_logs 和tasks",

### block_p0134_b031

"description": "MVP 阶段先不新增决策表，通过审计日志记录确认动作，通过任务表记录执行结果。",

### block_p0134_b032

"pros": [" 实现更快", " 减少短期表结构变更"],

### block_p0134_b033

"cons": [" 长期追踪不清晰", " 后续可能需要迁移数据"]

### block_p0134_b034

}

### block_p0134_b035

MVP 阶段建议每个老板决策项至少提供A/B 两个方案。后续可以扩展为多方案列表。

### block_p0134_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0134_b037

AutoMage-2-MVP 架构设计文档·杨卓134

### block_p0134_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 134

## 表格

无。

## 备注

无。

<!-- 来自 page_0134.md 全文结束 -->

<!-- 来自 page_0135.md 全文开始 -->

# Page 0135

## 原始文本块

### block_p0135_b001

2026 年5 月3 日

### block_p0135_b002

7.3.11recommended_option：Agent 推荐方案

### block_p0135_b003

recommended_option 表示Executive Agent 推荐老板选择的方案。

### block_p0135_b004

示例：

### block_p0135_b005

"recommended_option": "A"

### block_p0135_b006

推荐方案必须有理由，不能只给结论。推荐理由应写入reasoning_summary。

### block_p0135_b007

如果Agent 无法明确推荐，应允许该字段为空，并在决策卡片中标注“暂无明确推荐，需

### block_p0135_b008

要老板判断”。

### block_p0135_b009

7.3.12reasoning_summary：推荐理由摘要

### block_p0135_b010

reasoning_summary 用于说明为什么推荐某个方案。

### block_p0135_b011

示例：

### block_p0135_b012

"reasoning_summary": "方案A 虽然会增加少量后端开发工作量，但能让老板决策、

### block_p0135_b013

任务来源和后续复盘形成独立闭环，更符合AutoMage-2 长期架构。",→

### block_p0135_b014

该字段不是完整推理过程，也不需要写得很长。老板需要的是清楚的依据，而不是冗长

### block_p0135_b015

分析。

### block_p0135_b016

推荐理由应尽量包含：

### block_p0135_b017

1. 与当前目标的关系。

### block_p0135_b018

2. 对进度的影响。

### block_p0135_b019

3. 对风险的影响。

### block_p0135_b020

4. 对后续扩展的影响。

### block_p0135_b021

5. 为什么优于其他方案。

### block_p0135_b022

7.3.13expected_impact：预期影响

### block_p0135_b023

expected_impact 用于说明某个决策被确认后可能产生的影响。

### block_p0135_b024

示例：

### block_p0135_b025

"expected_impact": {

### block_p0135_b026

"cost": "medium",

### block_p0135_b027

"timeline": " 短期增加0.5-1 天后端工作量",

### block_p0135_b028

"risk": " 降低后续决策追踪混乱风险",

### block_p0135_b029

"affected_modules": ["backend", "agent", "database"],

### block_p0135_b030

"business_value": " 提升老板决策可追溯性和后续复盘能力"

### block_p0135_b031

}

### block_p0135_b032

建议子字段包括：

### block_p0135_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0135_b034

AutoMage-2-MVP 架构设计文档·杨卓135

### block_p0135_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 135

## 表格

无。

## 备注

无。

<!-- 来自 page_0135.md 全文结束 -->

<!-- 来自 page_0136.md 全文开始 -->

# Page 0136

## 原始文本块

### block_p0136_b001

2026 年5 月3 日

### block_p0136_b002

子字段类型是否必填说明

### block_p0136_b003

coststring否成本影响

### block_p0136_b004

timelinestring否时间影响

### block_p0136_b005

riskstring否风险变化

### block_p0136_b006

affected_modulesarray否受影响模块

### block_p0136_b007

business_valuestring否业务价值

### block_p0136_b008

MVP 阶段不要求非常精确的量化评估，但必须让老板知道选择不同方案会带来什么后

### block_p0136_b009

果。

### block_p0136_b010

7.3.14generated_tasks：可下发任务

### block_p0136_b011

generated_tasks 表示老板确认后可以自动生成的任务草案。

### block_p0136_b012

示例：

### block_p0136_b013

"generated_tasks": [

### block_p0136_b014

{

### block_p0136_b015

"task_title": " 补充decision_logs 表结构草案",

### block_p0136_b016

"task_description": "根据Executive 决策链路设计decision_logs 表，字段需覆盖决策标题、

### block_p0136_b017

背景、候选方案、推荐方案、确认人、确认时间和生成任务。",,→

### block_p0136_b018

"assignee_user_id": 20002,

### block_p0136_b019

"assignee_role": "backend",

### block_p0136_b020

"department_id": 12,

### block_p0136_b021

"priority": "high",

### block_p0136_b022

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0136_b023

"source_decision_id": "decision_tmp_001"

### block_p0136_b024

}

### block_p0136_b025

]

### block_p0136_b026

该字段在老板确认前只是草案，不应直接写入正式任务表。老板确认后，后端再根据确

### block_p0136_b027

认方案生成正式tasks 和task_assignments。

### block_p0136_b028

7.3.15source_summary_ids：引用的部门汇总ID

### block_p0136_b029

source_summary_ids 表示当前Executive Schema 引用了哪些Manager Summary。

### block_p0136_b030

示例：

### block_p0136_b031

"source_summary_ids": [801, 802, 803]

### block_p0136_b032

这是Executive Schema 可追溯性的关键字段。老板看到的摘要和决策项必须能追溯到具

### block_p0136_b033

体部门汇总，再继续追溯到Staff Work Records。

### block_p0136_b034

后端应校验这些Summary 是否属于同一组织，且Executive Agent 有读取权限。

### block_p0136_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0136_b036

AutoMage-2-MVP 架构设计文档·杨卓136

### block_p0136_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 136

## 表格

无。

## 备注

无。

<!-- 来自 page_0136.md 全文结束 -->

<!-- 来自 page_0137.md 全文开始 -->

# Page 0137

## 原始文本块

### block_p0137_b001

2026 年5 月3 日

### block_p0137_b002

7.3.16human_confirm_status：人工确认状态

### block_p0137_b003

human_confirm_status 表示当前Executive Schema 或其中决策项的人工确认状态。

### block_p0137_b004

示例：

### block_p0137_b005

"human_confirm_status": "pending"

### block_p0137_b006

建议枚举值如下：

### block_p0137_b007

值含义

### block_p0137_b008

draft草稿，尚未推送老板

### block_p0137_b009

pending已推送，等待老板确认

### block_p0137_b010

confirmed已确认

### block_p0137_b011

rejected已驳回

### block_p0137_b012

need_more_info需要补充信息

### block_p0137_b013

expired超时未确认

### block_p0137_b014

cancelled已取消

### block_p0137_b015

MVP 阶段，涉及任务生成的决策必须在confirmed 后才能继续执行。

### block_p0137_b016

7.3.17confirmed_by：确认人

### block_p0137_b017

confirmed_by 表示最终确认该决策的人。

### block_p0137_b018

示例：

### block_p0137_b019

"confirmed_by": 30001

### block_p0137_b020

该字段在human_confirm_status = confirmed 时必填。

### block_p0137_b021

如果老板未确认，该字段应为空。Agent 不能代替老板填写确认人。

### block_p0137_b022

7.3.18confirmed_at：确认时间

### block_p0137_b023

confirmed_at 表示老板确认决策的时间。

### block_p0137_b024

示例：

### block_p0137_b025

"confirmed_at": "2026-05-04T08:16:30+08:00"

### block_p0137_b026

该字段用于审计和任务生成。后端应以服务器确认时间为准，同时保留IM 或前端传入

### block_p0137_b027

的确认来源。

### block_p0137_b028 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0137_b029

AutoMage-2-MVP 架构设计文档·杨卓137

### block_p0137_b030 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 137

## 表格

无。

## 备注

无。

<!-- 来自 page_0137.md 全文结束 -->

<!-- 来自 page_0138.md 全文开始 -->

# Page 0138

## 原始文本块

### block_p0138_b001

2026 年5 月3 日

### block_p0138_b002

7.4Executive Schema JSON 示例

### block_p0138_b003

下面是一个完整Executive Schema 示例，可作为Agent 输出、老板决策卡片和后端联调

### block_p0138_b004

参考。

### block_p0138_b005

{

### block_p0138_b006

"schema_id": "schema_v1_executive",

### block_p0138_b007

"schema_version": "1.0.0",

### block_p0138_b008

"timestamp": "2026-05-04T08:00:00+08:00",

### block_p0138_b009

"org_id": 1,

### block_p0138_b010

"executive_user_id": 30001,

### block_p0138_b011

"executive_node_id": "executive_node_org_1",

### block_p0138_b012

"summary_date": "2026-05-03",

### block_p0138_b013

"business_summary": "昨日各部门整体推进正常，架构组完成Staff Schema 与Manager Schema

### block_p0138_b014

的主要字段设计，后端完成部分业务表结构落地，Agent 客制化已跑通Mock Flow。

### block_p0138_b015

当前主要风险集中在决策记录表结构尚未统一，可能影响Executive 决策确认和任务下发联调。",

### block_p0138_b016

,→

### block_p0138_b017

,→

### block_p0138_b018

"key_risks": [

### block_p0138_b019

{

### block_p0138_b020

"title": " 决策记录结构未统一",

### block_p0138_b021

"description": "Agent mock 流程中已存在decision_logs 概念，但当前数据库DDL

### block_p0138_b022

尚未建立独立决策表，可能影响老板确认、任务来源追踪和后续复盘。",,→

### block_p0138_b023

"severity": "high",

### block_p0138_b024

"affected_departments": [12, 15],

### block_p0138_b025

"source_summary_ids": [801, 802],

### block_p0138_b026

"suggested_action": " 建议尽快确认Decision Schema 与数据库承载方式。"

### block_p0138_b027

}

### block_p0138_b028

],

### block_p0138_b029

"decision_required": true,

### block_p0138_b030

"decision_items": [

### block_p0138_b031

{

### block_p0138_b032

"decision_id": "decision_tmp_001",

### block_p0138_b033

"title": " 是否新增独立decision_logs 表",

### block_p0138_b034

"context": "当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL

### block_p0138_b035

尚未建立独立决策表。如果不新增，短期可用audit_logs 和tasks 承载，

### block_p0138_b036

但后续老板决策追踪和复盘会不够清晰。",

### block_p0138_b037

,→

### block_p0138_b038

,→

### block_p0138_b039

"decision_level": "L3",

### block_p0138_b040

"urgency": "high",

### block_p0138_b041

"option_a": {

### block_p0138_b042

"option_id": "A",

### block_p0138_b043

"title": " 新增独立decision_logs 表",

### block_p0138_b044

"description": " 为老板决策、候选方案、确认结果和任务来源建立独立数据表。",

### block_p0138_b045

"pros": [" 审计清晰", " 便于复盘", " 后续扩展空间大"],

### block_p0138_b046

"cons": [" 需要增加后端开发工作量"]

### block_p0138_b047

},

### block_p0138_b048

"option_b": {

### block_p0138_b049

"option_id": "B",

### block_p0138_b050

"title": " 暂时复用audit_logs 和tasks",

### block_p0138_b051

"description": " 短期不新增表，先通过审计日志和任务表承载决策结果。",

### block_p0138_b052 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0138_b053

AutoMage-2-MVP 架构设计文档·杨卓138

### block_p0138_b054 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 138

## 表格

无。

## 备注

无。

<!-- 来自 page_0138.md 全文结束 -->

<!-- 来自 page_0139.md 全文开始 -->

# Page 0139

## 原始文本块

### block_p0139_b001

2026 年5 月3 日

### block_p0139_b002

"pros": [" 开发更快", "MVP 改动较少"],

### block_p0139_b003

"cons": [" 决策对象不独立", " 后续统计和追踪不方便"]

### block_p0139_b004

},

### block_p0139_b005

"recommended_option": "A",

### block_p0139_b006

"reasoning_summary": "AutoMage-2 的核心价值在于决策可追溯，

### block_p0139_b007

独立决策对象有利于后续任务生成、复盘和老板侧看板。",,→

### block_p0139_b008

"expected_impact": {

### block_p0139_b009

"cost": "medium",

### block_p0139_b010

"timeline": " 短期增加0.5-1 天后端工作量",

### block_p0139_b011

"risk": " 降低后续决策追踪混乱风险",

### block_p0139_b012

"affected_modules": ["backend", "agent", "database"],

### block_p0139_b013

"business_value": " 提升老板决策可追溯性和后续复盘能力"

### block_p0139_b014

},

### block_p0139_b015

"generated_tasks": [

### block_p0139_b016

{

### block_p0139_b017

"task_title": " 补充decision_logs 表结构草案",

### block_p0139_b018

"task_description": "根据Executive 决策链路设计decision_logs 表，

### block_p0139_b019

字段需覆盖决策标题、背景、候选方案、推荐方案、确认人、确认时间和生成任务。",,→

### block_p0139_b020

"assignee_user_id": 20002,

### block_p0139_b021

"assignee_role": "backend",

### block_p0139_b022

"department_id": 12,

### block_p0139_b023

"priority": "high",

### block_p0139_b024

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0139_b025

"source_decision_id": "decision_tmp_001"

### block_p0139_b026

}

### block_p0139_b027

],

### block_p0139_b028

"source_summary_ids": [801, 802]

### block_p0139_b029

}

### block_p0139_b030

],

### block_p0139_b031

"source_summary_ids": [801, 802, 803],

### block_p0139_b032

"source_decision_ids": [],

### block_p0139_b033

"source_incident_ids": [501],

### block_p0139_b034

"human_confirm_status": "pending",

### block_p0139_b035

"confirmed_by": null,

### block_p0139_b036

"confirmed_at": null,

### block_p0139_b037

"confirmed_option": null,

### block_p0139_b038

"signature": {

### block_p0139_b039

"signature_required": true,

### block_p0139_b040

"signature_status": "pending",

### block_p0139_b041

"signed_by": null,

### block_p0139_b042

"signed_at": null,

### block_p0139_b043

"payload_hash": "sha256:executive_decision_example_hash",

### block_p0139_b044

"signature_source": "im"

### block_p0139_b045

},

### block_p0139_b046

"meta": {

### block_p0139_b047

"input_channel": "scheduled_dream",

### block_p0139_b048

"agent_template_version": "executive_agent_v0.1",

### block_p0139_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0139_b050

AutoMage-2-MVP 架构设计文档·杨卓139

### block_p0139_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 139

## 表格

无。

## 备注

无。

<!-- 来自 page_0139.md 全文结束 -->

<!-- 来自 page_0140.md 全文开始 -->

# Page 0140

## 原始文本块

### block_p0140_b001

2026 年5 月3 日

### block_p0140_b002

"summary_window": "daily",

### block_p0140_b003

"push_channel": "feishu"

### block_p0140_b004

}

### block_p0140_b005

}

### block_p0140_b006

7.5Executive Schema 决策卡片格式

### block_p0140_b007

Executive Schema 最终需要以老板容易理解的形式展示出来。MVP 阶段建议优先使用

### block_p0140_b008

IM 决策卡片，后续再扩展老板侧App 或看板。

### block_p0140_b009

决策卡片不应展示完整JSON，而应展示经过整理的关键内容。

### block_p0140_b010

推荐格式如下：

### block_p0140_b011

【今日老板待决策】

### block_p0140_b012

日期：2026-05-04

### block_p0140_b013

状态：需要确认1 项决策

### block_p0140_b014

一、公司整体情况

### block_p0140_b015

昨日各部门整体推进正常，架构组完成Staff Schema 与Manager Schema 的主要字段设计，

### block_p0140_b016

后端完成部分业务表结构落地，Agent 客制化已跑通Mock Flow。

### block_p0140_b017

当前主要风险集中在决策记录表结构尚未统一。

### block_p0140_b018

,→

### block_p0140_b019

,→

### block_p0140_b020

二、关键风险

### block_p0140_b021

1. 决策记录结构未统一

### block_p0140_b022

影响：可能影响老板确认、任务来源追踪和后续复盘

### block_p0140_b023

风险等级：高

### block_p0140_b024

三、待决策事项

### block_p0140_b025

事项：是否新增独立decision_logs 表

### block_p0140_b026

背景：

### block_p0140_b027

当前Agent mock 流程中已经存在decision_logs 概念，但正式DDL 尚未建立独立决策表。

### block_p0140_b028

方案A：新增独立decision_logs 表

### block_p0140_b029

优点：审计清晰、便于复盘、后续扩展空间大

### block_p0140_b030

缺点：需要增加后端开发工作量

### block_p0140_b031

方案B：暂时复用audit_logs 和tasks

### block_p0140_b032

优点：开发更快、MVP 改动较少

### block_p0140_b033

缺点：决策对象不独立，后续统计和追踪不方便

### block_p0140_b034

推荐：方案A

### block_p0140_b035

理由：AutoMage-2 的核心价值在于决策可追溯，独立决策对象更符合长期架构。

### block_p0140_b036

确认后生成任务：

### block_p0140_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0140_b038

AutoMage-2-MVP 架构设计文档·杨卓140

### block_p0140_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 140

## 表格

无。

## 备注

无。

<!-- 来自 page_0140.md 全文结束 -->

<!-- 来自 page_0141.md 全文开始 -->

# Page 0141

## 原始文本块

### block_p0141_b001

2026 年5 月3 日

### block_p0141_b002

1. 补充decision_logs 表结构草案

### block_p0141_b003

负责人：后端

### block_p0141_b004

截止时间：今日18:00

### block_p0141_b005

IM 卡片按钮建议包括：

### block_p0141_b006

按钮系统动作

### block_p0141_b007

选择方案A记录确认结果，生成A 对应任务

### block_p0141_b008

选择方案B记录确认结果，生成B 对应任务

### block_p0141_b009

需要补充信息状态改为need_more_info

### block_p0141_b010

暂不处理状态改为rejected 或cancelled

### block_p0141_b011

查看来源展示引用的部门汇总和来源记录

### block_p0141_b012

老板侧卡片的原则是：短、准、可操作。不建议让老板在卡片中阅读大量原始日报，也不

### block_p0141_b013

建议只给一段泛泛总结。

### block_p0141_b014

7.6Executive Schema 与Dream 机制关系

### block_p0141_b015

Dream 是Executive Schema 的主要生成机制之一。它负责在固定时间读取系统中的结构

### block_p0141_b016

化数据，生成组织级摘要、关键风险和老板决策项。

### block_p0141_b017

二者关系如下：

### block_p0141_b018

Manager Schema

### block_p0141_b019

↓

### block_p0141_b020

Dream 读取和分析

### block_p0141_b021

↓

### block_p0141_b022

Executive Schema

### block_p0141_b023

↓

### block_p0141_b024

老板决策卡片

### block_p0141_b025

↓

### block_p0141_b026

任务下发

### block_p0141_b027

Dream 的输入主要包括：

### block_p0141_b028

输入说明

### block_p0141_b029

Manager Schema各部门汇总

### block_p0141_b030

Summary Schema历史日报、周报、组织级摘要

### block_p0141_b031

Task Schema未完成任务、逾期任务、关键任务

### block_p0141_b032

Incident Schema未关闭异常、重大风险

### block_p0141_b033

Decision Schema历史老板决策和执行结果

### block_p0141_b034

老板目标临时目标、经营目标、战略重点

### block_p0141_b035

Dream 的输出主要包括：

### block_p0141_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0141_b037

AutoMage-2-MVP 架构设计文档·杨卓141

### block_p0141_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 141

## 表格

无。

## 备注

无。

<!-- 来自 page_0141.md 全文结束 -->

<!-- 来自 page_0142.md 全文开始 -->

# Page 0142

## 原始文本块

### block_p0142_b001

2026 年5 月3 日

### block_p0142_b002

输出对应Executive Schema 字段

### block_p0142_b003

组织级摘要business_summary

### block_p0142_b004

关键风险key_risks

### block_p0142_b005

待决策事项decision_items

### block_p0142_b006

推荐方案recommended_option

### block_p0142_b007

推荐理由reasoning_summary

### block_p0142_b008

任务草案generated_tasks

### block_p0142_b009

来源引用source_summary_ids

### block_p0142_b010

MVP 阶段Dream 不需要做得很复杂。只要能完成以下动作，就可以支撑主链路：

### block_p0142_b011

1. 定时读取部门汇总。

### block_p0142_b012

2. 提炼组织级摘要。

### block_p0142_b013

3. 识别最重要的风险。

### block_p0142_b014

4. 将上推事项整理为老板决策项。

### block_p0142_b015

5. 生成A/B 方案。

### block_p0142_b016

6. 在老板确认后生成任务草案。

### block_p0142_b017

后续版本可以再扩展长期记忆、跨周期趋势判断、组织效率分析和战略推演。

### block_p0142_b018

7.7Executive Schema 与任务下发关系

### block_p0142_b019

Executive Schema 不是任务表，但它是老板任务下发的来源。

### block_p0142_b020

任务下发必须发生在老板确认之后。确认前，generated_tasks 只是任务草案；确认后，

### block_p0142_b021

后端才根据确认结果创建正式任务。

### block_p0142_b022

推荐流程如下：

### block_p0142_b023

Executive Schema 生成

### block_p0142_b024

↓

### block_p0142_b025

老板查看决策卡片

### block_p0142_b026

↓

### block_p0142_b027

老板选择方案

### block_p0142_b028

↓

### block_p0142_b029

后端记录确认结果

### block_p0142_b030

↓

### block_p0142_b031

读取对应方案的generated_tasks

### block_p0142_b032

↓

### block_p0142_b033

创建tasks / task_assignments

### block_p0142_b034

↓

### block_p0142_b035

推送给Manager Agent 或Staff Agent

### block_p0142_b036

任务下发规则如下：

### block_p0142_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0142_b038

AutoMage-2-MVP 架构设计文档·杨卓142

### block_p0142_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 142

## 表格

无。

## 备注

无。

<!-- 来自 page_0142.md 全文结束 -->

<!-- 来自 page_0143.md 全文开始 -->

# Page 0143

## 原始文本块

### block_p0143_b001

2026 年5 月3 日

### block_p0143_b002

情况任务下发方式

### block_p0143_b003

任务需要部门拆解先下发给Manager Agent

### block_p0143_b004

任务已有明确执行人直接下发给Staff Agent

### block_p0143_b005

任务涉及多个部门分别下发给多个Manager Agent

### block_p0143_b006

任务需要老板再次确认保持待确认，不生成正式任务

### block_p0143_b007

老板选择“补充信息”不生成任务，回到信息补全状态

### block_p0143_b008

Executive Schema 中的generated_tasks 至少应包含：

### block_p0143_b009

1. 任务标题。

### block_p0143_b010

2. 任务说明。

### block_p0143_b011

3. 负责人或负责人角色。

### block_p0143_b012

4. 所属部门。

### block_p0143_b013

5. 优先级。

### block_p0143_b014

6. 截止时间。

### block_p0143_b015

7. 来源决策ID。

### block_p0143_b016

8. 触发方案。

### block_p0143_b017

任务一旦创建，必须与决策记录建立来源关系。否则后续无法回答“这个任务为什么产

### block_p0143_b018

生”。

### block_p0143_b019

7.8Executive Schema 与数据库字段映射

### block_p0143_b020

Executive Schema 需要映射到多个数据库对象。当前DDL 中已有summaries、tasks、

### block_p0143_b021

task_assignments、audit_logs 等表，但独立Decision 表仍建议补齐。

### block_p0143_b022

7.8.1映射到组织级summaries

### block_p0143_b023

Executive Schema 中的组织级摘要可以写入summaries。

### block_p0143_b024

Executive Schema 字段数据库字段说明

### block_p0143_b025

org_idsummaries.org_id组织ID

### block_p0143_b026

executive_user_idsummaries.user_id或

### block_p0143_b027

meta.executive_user_id

### block_p0143_b028

老板/高管ID

### block_p0143_b029

summary_datesummaries.summary_date摘要日期

### block_p0143_b030

business_summarysummaries.content组织级摘要正文

### block_p0143_b031

schema_id / schema_versionsummaries.metaSchema 标识和版本

### block_p0143_b032

key_riskssummaries.meta.key_risks关键风险

### block_p0143_b033

decision_requiredsummaries.meta.decision_required是否需要决策

### block_p0143_b034

source_summary_idssummary_source_links来源部门汇总

### block_p0143_b035

human_confirm_statussummaries.status 或meta确认状态

### block_p0143_b036

summaries.scope_type 应标记为组织级，表示该Summary 不属于某个单独部门或员工。

### block_p0143_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0143_b038

AutoMage-2-MVP 架构设计文档·杨卓143

### block_p0143_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 143

## 表格

无。

## 备注

无。

<!-- 来自 page_0143.md 全文结束 -->

<!-- 来自 page_0144.md 全文开始 -->

# Page 0144

## 原始文本块

### block_p0144_b001

2026 年5 月3 日

### block_p0144_b002

7.8.2映射到Decision 记录

### block_p0144_b003

建议新增独立Decision 表承载老板决策。若MVP 阶段暂未新增，可先使用audit_logs

### block_p0144_b004

+ summaries.meta 暂存，但这不是长期方案。

### block_p0144_b005

建议Decision 对象字段如下：

### block_p0144_b006

Executive Schema 字段Decision 字段说明

### block_p0144_b007

decision_items[].titletitle决策标题

### block_p0144_b008

decision_items[].contextcontext决策背景

### block_p0144_b009

decision_leveldecision_level决策等级

### block_p0144_b010

option_a / option_boptions候选方案

### block_p0144_b011

recommended_optionrecommended_option推荐方案

### block_p0144_b012

reasoning_summaryrecommend_reason推荐理由

### block_p0144_b013

expected_impactexpected_impact预期影响

### block_p0144_b014

human_confirm_statusstatus确认状态

### block_p0144_b015

confirmed_byconfirmed_by确认人

### block_p0144_b016

confirmed_atconfirmed_at确认时间

### block_p0144_b017

confirmed_optionconfirmed_option最终选择

### block_p0144_b018

source_summary_idssource_summary_ids来源部门汇总

### block_p0144_b019

generated_tasksmeta.generated_tasks任务草案

### block_p0144_b020

Decision 表是老板决策可追溯的核心。建议后端优先补齐该对象。

### block_p0144_b021

7.8.3映射到tasks

### block_p0144_b022

老板确认后，generated_tasks 应写入tasks 和task_assignments。

### block_p0144_b023

Executive Schema 字段数据库字段说明

### block_p0144_b024

generated_tasks[].task_titletasks.title任务标题

### block_p0144_b025

generated_tasks[].task_descriptiontasks.description任务说明

### block_p0144_b026

department_idtasks.department_id所属部门

### block_p0144_b027

prioritytasks.priority优先级

### block_p0144_b028

due_attasks.due_at截止时间

### block_p0144_b029

source_decision_idtasks.meta.source_decision_id来源决策

### block_p0144_b030

assignee_user_idtask_assignments.user_id执行人

### block_p0144_b031

assignee_roletasks.meta.assignee_role执行角色

### block_p0144_b032

如果任务只指定角色而未指定具体人，可以先下发给Manager Agent，由部门负责人再

### block_p0144_b033

拆解到具体员工。

### block_p0144_b034

7.8.4映射到audit_logs

### block_p0144_b035

Executive Schema 的关键动作必须写入审计日志。

### block_p0144_b036

建议记录以下动作：

### block_p0144_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0144_b038

AutoMage-2-MVP 架构设计文档·杨卓144

### block_p0144_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 144

## 表格

无。

## 备注

无。

<!-- 来自 page_0144.md 全文结束 -->

<!-- 来自 page_0145.md 全文开始 -->

# Page 0145

## 原始文本块

### block_p0145_b001

2026 年5 月3 日

### block_p0145_b002

动作说明

### block_p0145_b003

executive_schema_generatedExecutive Agent 生成老板侧摘要

### block_p0145_b004

executive_decision_pushed决策卡片推送给老板

### block_p0145_b005

executive_decision_confirmed老板确认方案

### block_p0145_b006

executive_decision_rejected老板驳回

### block_p0145_b007

executive_decision_need_more_info老板要求补充信息

### block_p0145_b008

executive_task_generated确认后生成任务

### block_p0145_b009

executive_schema_read_source读取部门汇总来源

### block_p0145_b010

executive_decision_expired决策超时未确认

### block_p0145_b011

审计日志应记录操作人、Agent 节点、决策对象、确认方案、确认时间和生成任务。

### block_p0145_b012

7.8.5映射到summary_source_links

### block_p0145_b013

Executive Schema 引用的部门汇总应写入summary_source_links。

### block_p0145_b014

Executive Schema 字段数据库字段说明

### block_p0145_b015

source_summary_ids[]summary_source_links.source_id来源部门Summary ID

### block_p0145_b016

当前组织级summary IDsummary_source_links.summary_id当前Executive Summary ID

### block_p0145_b017

固定来源类型summary_source_links.source_type来源类型，如manager_summary

### block_p0145_b018

org_idsummary_source_links.org_id组织ID

### block_p0145_b019

这样可以保证老板侧摘要可以向下追溯到部门汇总，再继续追溯到员工日报。

### block_p0145_b020

7.9老板确认后的状态变化

### block_p0145_b021

老板确认是Executive Schema 从“建议”变成“执行”的关键节点。

### block_p0145_b022

确认前，Executive Schema 只是决策草案。确认后，系统才可以记录正式决策，并生成

### block_p0145_b023

任务。

### block_p0145_b024

状态变化建议如下：

### block_p0145_b025

draft

### block_p0145_b026

↓

### block_p0145_b027

pending

### block_p0145_b028

↓

### block_p0145_b029

confirmed

### block_p0145_b030

↓

### block_p0145_b031

task_generated

### block_p0145_b032

↓

### block_p0145_b033

in_execution

### block_p0145_b034

↓

### block_p0145_b035

completed / closed

### block_p0145_b036

如果老板驳回或要求补充信息，则进入：

### block_p0145_b037

pending

### block_p0145_b038

↓

### block_p0145_b039

rejected / need_more_info

### block_p0145_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0145_b041

AutoMage-2-MVP 架构设计文档·杨卓145

### block_p0145_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 145

## 表格

无。

## 备注

无。

<!-- 来自 page_0145.md 全文结束 -->

<!-- 来自 page_0146.md 全文开始 -->

# Page 0146

## 原始文本块

### block_p0146_b001

2026 年5 月3 日

### block_p0146_b002

各状态说明如下：

### block_p0146_b003

状态含义系统动作

### block_p0146_b004

draft草稿，尚未推送老板不生成任务

### block_p0146_b005

pending已推送老板，等待确认允许提醒和查看来源

### block_p0146_b006

confirmed老板已选择方案记录确认人和确认时间

### block_p0146_b007

task_generated已生成任务写入任务表和分配表

### block_p0146_b008

in_execution任务执行中Staff / Manager Agent 跟进

### block_p0146_b009

completed任务已完成可进入复盘

### block_p0146_b010

closed决策闭环关闭保留审计记录

### block_p0146_b011

rejected老板驳回不生成任务

### block_p0146_b012

need_more_info老板要求补充信息回到Manager 或相关负责人补充

### block_p0146_b013

expired超时未确认按规则提醒或降级处理

### block_p0146_b014

老板确认后，后端必须执行以下动作：

### block_p0146_b015

1. 校验确认人权限。

### block_p0146_b016

2. 更新决策状态。

### block_p0146_b017

3. 记录confirmed_by。

### block_p0146_b018

4. 记录confirmed_at。

### block_p0146_b019

5. 记录confirmed_option。

### block_p0146_b020

6. 写入审计日志。

### block_p0146_b021

7. 根据确认方案生成任务。

### block_p0146_b022

8. 将任务下发给对应Manager 或Staff。

### block_p0146_b023

9. 通知相关人员。

### block_p0146_b024

10. 保留来源关系。

### block_p0146_b025

Agent 不能在没有后端确认状态的情况下自行声称“老板已确认”。

### block_p0146_b026

7.10未确认时的处理规则

### block_p0146_b027

并不是所有决策卡片都会立即被老板确认。MVP 阶段需要明确未确认时的处理规则，避

### block_p0146_b028

免系统卡死。

### block_p0146_b029

7.10.1等待确认

### block_p0146_b030

当决策卡片已推送但老板未操作时，状态为：

### block_p0146_b031

"human_confirm_status": "pending"

### block_p0146_b032

在该状态下：

### block_p0146_b033

1. 不生成正式任务。

### block_p0146_b034

2. 不改变下级任务状态。

### block_p0146_b035

3. 可以提醒老板确认。

### block_p0146_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0146_b037

AutoMage-2-MVP 架构设计文档·杨卓146

### block_p0146_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 146

## 表格

无。

## 备注

无。

<!-- 来自 page_0146.md 全文结束 -->

<!-- 来自 page_0147.md 全文开始 -->

# Page 0147

## 原始文本块

### block_p0147_b001

2026 年5 月3 日

### block_p0147_b002

4. Manager Agent 可以看到该事项处于待确认。

### block_p0147_b003

5. 超过一定时间后进入超时规则。

### block_p0147_b004

7.10.2超时未确认

### block_p0147_b005

如果老板在设定时间内未确认，系统应按决策等级处理。

### block_p0147_b006

建议规则：

### block_p0147_b007

决策等级超时处理

### block_p0147_b008

低风险事项提醒一次后降级为Manager 处理

### block_p0147_b009

中风险事项持续提醒，并通知相关Manager

### block_p0147_b010

高风险事项提醒老板，并标记为高优先级待确认

### block_p0147_b011

重大事项不允许自动执行，必须等待人工确认

### block_p0147_b012

MVP 阶段建议高风险和重大事项都不自动执行。宁可延迟，也不要让系统绕过老板做关

### block_p0147_b013

键决策。

### block_p0147_b014

7.10.3老板要求补充信息

### block_p0147_b015

如果老板点击“需要补充信息”，状态应变为：

### block_p0147_b016

"human_confirm_status": "need_more_info"

### block_p0147_b017

系统应记录老板提出的问题，并将补充请求返回给相关Manager Agent。

### block_p0147_b018

流程如下：

### block_p0147_b019

老板要求补充信息

### block_p0147_b020

↓

### block_p0147_b021

Executive Agent 记录问题

### block_p0147_b022

↓

### block_p0147_b023

相关Manager Agent 收到补充请求

### block_p0147_b024

↓

### block_p0147_b025

Manager 补充说明或重新生成汇总

### block_p0147_b026

↓

### block_p0147_b027

Executive Agent 更新决策卡片

### block_p0147_b028

↓

### block_p0147_b029

再次推送老板确认

### block_p0147_b030

此时不应生成任务，除非老板明确要求先执行部分事项。

### block_p0147_b031

7.10.4老板驳回

### block_p0147_b032

如果老板驳回决策项，状态应变为：

### block_p0147_b033

"human_confirm_status": "rejected"

### block_p0147_b034

驳回后：

### block_p0147_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0147_b036

AutoMage-2-MVP 架构设计文档·杨卓147

### block_p0147_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 147

## 表格

无。

## 备注

无。

<!-- 来自 page_0147.md 全文结束 -->

<!-- 来自 page_0148.md 全文开始 -->

# Page 0148

## 原始文本块

### block_p0148_b001

2026 年5 月3 日

### block_p0148_b002

1. 不生成任务。

### block_p0148_b003

2. 记录驳回人和驳回时间。

### block_p0148_b004

3. 记录驳回原因。

### block_p0148_b005

4. 通知相关Manager Agent。

### block_p0148_b006

5. 保留审计日志。

### block_p0148_b007

6. 后续如需重新提交，应生成新版本决策项。

### block_p0148_b008

不建议直接覆盖原决策项，否则会丢失决策过程。

### block_p0148_b009

7.10.5决策卡片修改

### block_p0148_b010

老板可能不选择方案A 或B，而是提出新的方案。此时系统应记录为人工改写。

### block_p0148_b011

处理方式：

### block_p0148_b012

1. 保留原方案。

### block_p0148_b013

2. 记录老板修改内容。

### block_p0148_b014

3. 将confirmed_option 标记为custom。

### block_p0148_b015

4. 将老板输入写入confirmed_custom_plan 或meta。

### block_p0148_b016

5. 根据新方案生成任务。

### block_p0148_b017

6. 写入审计日志。

### block_p0148_b018

示例：

### block_p0148_b019

{

### block_p0148_b020

"confirmed_option": "custom",

### block_p0148_b021

"confirmed_custom_plan": "先新增轻量decision_logs 表，只保留决策标题、确认人、确认时间、来源

### block_p0148_b022

summary 和生成任务，复杂字段后续迭代。",→

### block_p0148_b023

}

### block_p0148_b024

这种能力对老板侧非常重要，因为真实决策往往不是简单二选一。

### block_p0148_b025

7.10.6未确认数据的可见范围

### block_p0148_b026

未确认的Executive Schema 可以被相关角色查看，但不能被当作最终决策执行。

### block_p0148_b027

角色可见内容

### block_p0148_b028

老板全部决策卡片

### block_p0148_b029

Executive Agent全部生成内容

### block_p0148_b030

相关Manager Agent与本部门相关的待确认事项

### block_p0148_b031

Staff Agent一般不可见，除非任务已正式下发

### block_p0148_b032

审计系统可见生成、推送和等待确认记录

### block_p0148_b033

未确认事项不应下发给一线员工，避免造成“老板还没拍板，下面已经开始执行”的混

### block_p0148_b034

乱。

### block_p0148_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0148_b036

AutoMage-2-MVP 架构设计文档·杨卓148

### block_p0148_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 148

## 表格

无。

## 备注

无。

<!-- 来自 page_0148.md 全文结束 -->

<!-- 来自 page_0149.md 全文开始 -->

# Page 0149

## 原始文本块

### block_p0149_b001

2026 年5 月3 日

### block_p0149_b002

7.10.7未确认事项的复盘

### block_p0149_b003

未确认事项也有复盘价值。系统应记录：

### block_p0149_b004

1. 什么时间生成。

### block_p0149_b005

2. 来自哪些部门汇总。

### block_p0149_b006

3. 为什么需要老板确认。

### block_p0149_b007

4. 是否被查看。

### block_p0149_b008

5. 是否超时。

### block_p0149_b009

6. 是否被驳回。

### block_p0149_b010

7. 是否被要求补充信息。

### block_p0149_b011

8. 最终是否再次提交。

### block_p0149_b012

这些数据后续可以帮助判断：哪些事项频繁卡在老板确认环节，哪些部门上推质量较低，

### block_p0149_b013

哪些决策类型需要调整权限边界。

### block_p0149_b014

7.11本章小结

### block_p0149_b015

Executive Schema 是AutoMage-2 MVP 中连接“部门汇总”和“老板决策”的关键结构。

### block_p0149_b016

它向下读取Manager Schema，向上生成老板可确认的决策卡片。一个合格的Executive

### block_p0149_b017

Schema 不应该只是公司日报，也不应该只是Agent 的主观建议，而应该同时满足四个要求：

### block_p0149_b018

1. 能让老板快速了解公司整体状态。

### block_p0149_b019

2. 能指出当前最重要的组织级风险。

### block_p0149_b020

3. 能把复杂问题整理成可选择、可确认的决策项。

### block_p0149_b021

4. 能在老板确认后生成可执行、可追踪的任务。

### block_p0149_b022

MVP 阶段只要Executive Schema 能稳定完成“读取部门汇总→生成老板摘要→生成

### block_p0149_b023

决策项→老板确认→任务下发”这一过程，就可以证明AutoMage-2 的三级Agent 决策闭

### block_p0149_b024

环具备基础可行性。

### block_p0149_b025 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0149_b026

AutoMage-2-MVP 架构设计文档·杨卓149

### block_p0149_b027 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 149

## 表格

无。

## 备注

无。

<!-- 来自 page_0149.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

