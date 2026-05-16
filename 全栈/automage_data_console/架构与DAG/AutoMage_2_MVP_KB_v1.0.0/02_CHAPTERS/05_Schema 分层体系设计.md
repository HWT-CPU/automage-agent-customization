# Schema 分层体系设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P070-P082
> 对应页面文件：`01_PAGES/page_0070.md` — `01_PAGES/page_0082.md`

## 原文整理

<!-- 来自 page_0070.md 全文开始 -->

# Page 0070

## 原始文本块

### block_p0070_b001

2026 年5 月3 日

### block_p0070_b002

4Schema 分层体系设计

### block_p0070_b003

4.1Schema 分层总览

### block_p0070_b004

AutoMage-2 MVP 阶段的Schema 采用分层设计，不把所有数据都塞进一个统一大表单，

### block_p0070_b005

而是按照组织运行过程拆成不同层级、不同用途的数据结构。

### block_p0070_b006

这样设计的原因很简单：一线员工每天产生的是「执行数据」，中层需要的是「部门态

### block_p0070_b007

势」，老板需要的是「决策依据」。如果三类角色都使用同一种数据结构，字段会变得非常臃

### block_p0070_b008

肿，Agent 也很难稳定生成和解析。

### block_p0070_b009

MVP 阶段建议将Schema 分为七类：

### block_p0070_b010

Schema 类型所属层级主要用途主要生成方主要读取方

### block_p0070_b011

Staff Schema一线员工层记录员工每日工作、问题、

### block_p0070_b012

计划和资源消耗

### block_p0070_b013

Staff AgentManager Agent、员工本人

### block_p0070_b014

Manager

### block_p0070_b015

Schema

### block_p0070_b016

部门管理层汇总部门进展、风险、阻

### block_p0070_b017

塞和待决策事项

### block_p0070_b018

Manager AgentExecutive Agent、部门负责人

### block_p0070_b019

Executive

### block_p0070_b020

Schema

### block_p0070_b021

公司决策层生成老板侧摘要、决策项

### block_p0070_b022

和方案建议

### block_p0070_b023

Executive Agent老板/高管

### block_p0070_b024

Task Schema执行闭环层承载决策拆解后的具体

### block_p0070_b025

任务

### block_p0070_b026

Manager Agent / Executive Agent

### block_p0070_b027

/ 系统

### block_p0070_b028

Staff Agent、Manager Agent

### block_p0070_b029

Incident

### block_p0070_b030

Schema

### block_p0070_b031

异常处理层记录风险、阻塞、异常和

### block_p0070_b032

处理过程

### block_p0070_b033

Staff Agent / Manager AgentManager Agent、Executive Agent

### block_p0070_b034

Decision

### block_p0070_b035

Schema

### block_p0070_b036

决策记录层记录决策项、候选方案、

### block_p0070_b037

确认状态和执行结果

### block_p0070_b038

Manager Agent / Executive Agent 老板、审计、任务系统

### block_p0070_b039

Summary

### block_p0070_b040

Schema

### block_p0070_b041

汇总沉淀层记录周期性汇总、日报、

### block_p0070_b042

周报、部门总结和组织级

### block_p0070_b043

总结

### block_p0070_b044

Manager Agent / Executive Agent

### block_p0070_b045

/ Dream

### block_p0070_b046

上级节点、看板、审计

### block_p0070_b047

这七类Schema 共同构成MVP 阶段的组织数据骨架：

### block_p0070_b048

Staff Schema

### block_p0070_b049

↓

### block_p0070_b050

Manager Schema

### block_p0070_b051

↓

### block_p0070_b052

Executive Schema

### block_p0070_b053

↓

### block_p0070_b054

Decision Schema

### block_p0070_b055

↓

### block_p0070_b056

Task Schema

### block_p0070_b057

↓

### block_p0070_b058

Staff 执行

### block_p0070_b059

↓

### block_p0070_b060

新的Staff Schema

### block_p0070_b061

Incident Schema 和Summary Schema 贯穿整个链路，用于处理异常和沉淀周期性结果。

### block_p0070_b062

MVP 阶段不要求一次性把每类Schema 都做得非常复杂，但必须先明确它们之间的边

### block_p0070_b063

界。只有边界清楚，后端、Agent、数据库和产品交互才能稳定协作。

### block_p0070_b064 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0070_b065

AutoMage-2-MVP 架构设计文档·杨卓70

### block_p0070_b066 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 70

## 表格

无。

## 备注

无。

<!-- 来自 page_0070.md 全文结束 -->

<!-- 来自 page_0071.md 全文开始 -->

# Page 0071

## 原始文本块

### block_p0071_b001

2026 年5 月3 日

### block_p0071_b002

4.2Staff Schema：一线执行数据

### block_p0071_b003

Staff Schema 是AutoMage-2 中最底层、也是最重要的数据来源。它记录一线员工在一个

### block_p0071_b004

工作周期内完成了什么、遇到了什么问题、是否需要支持、明天准备做什么，以及产生了哪

### block_p0071_b005

些可追溯的工作产物。

### block_p0071_b006

MVP 阶段Staff Schema 的核心目标不是做绩效考核，而是把原本分散在聊天、文档、会

### block_p0071_b007

议和个人脑子里的工作过程，转化为系统可以读取的结构化记录。

### block_p0071_b008

Staff Schema 主要回答以下问题：

### block_p0071_b009

1. 这个员工今天做了什么？

### block_p0071_b010

2. 做这些事情对应什么业务目标或任务？

### block_p0071_b011

3. 哪些事情已经完成，哪些还在推进？

### block_p0071_b012

4. 遇到了什么问题？

### block_p0071_b013

5. 员工自己尝试过什么解决办法？

### block_p0071_b014

6. 是否需要上级、其他部门或老板介入？

### block_p0071_b015

7. 明天计划继续做什么？

### block_p0071_b016

8. 是否产生了文档、代码、表格、链接、图片等产出物？

### block_p0071_b017

9. 是否存在风险、延期或资源不足？

### block_p0071_b018

Staff Schema 的数据来源主要包括：

### block_p0071_b019

数据来源MVP 阶段处理方式

### block_p0071_b020

员工主动填写通过IM 表单或Agent 问答收集

### block_p0071_b021

Agent 辅助整理将员工自然语言整理为标准字段

### block_p0071_b022

工作产出物由员工上传链接、文档、代码或附件

### block_p0071_b023

自动采集数据MVP 阶段可暂缓，后续接入屏幕记忆或办公软件插件

### block_p0071_b024

Staff Schema 生成后，后端应将其写入工作记录相关数据表。对于固定字段，例如用户、

### block_p0071_b025

部门、日期、标题、状态等，应进入显式列。对于工作进展、问题、计划、资源消耗等弹性内

### block_p0071_b026

容，可以进入字段明细或JSON 结构。

### block_p0071_b027

Staff Schema 是后续Manager 汇总、风险识别、任务生成和绩效分析的基础。如果Staff

### block_p0071_b028

Schema 不稳定，上层所有汇总都会失真。因此MVP 阶段要优先保证Staff Schema 的字段稳

### block_p0071_b029

定性和可校验性。

### block_p0071_b030

4.3Manager Schema：部门汇总数据

### block_p0071_b031

Manager Schema 是部门管理层的数据结构，由Manager Agent 基于本部门下属员工的

### block_p0071_b032

Staff Schema 聚合生成。

### block_p0071_b033

它不是简单地把员工日报拼接起来，而是要从多个一线记录中提炼出部门级信息。Man-

### block_p0071_b034

ager Schema 应该让部门负责人和老板快速知道：部门今天整体推进得怎么样，哪里有风险，

### block_p0071_b035

谁需要支持，哪些事情需要上推决策。

### block_p0071_b036

Manager Schema 主要回答以下问题：

### block_p0071_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0071_b038

AutoMage-2-MVP 架构设计文档·杨卓71

### block_p0071_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 71

## 表格

无。

## 备注

无。

<!-- 来自 page_0071.md 全文结束 -->

<!-- 来自 page_0072.md 全文开始 -->

# Page 0072

## 原始文本块

### block_p0072_b001

2026 年5 月3 日

### block_p0072_b002

1. 今天部门整体进展如何？

### block_p0072_b003

2. 哪些事项按计划推进？

### block_p0072_b004

3. 哪些事项出现阻塞？

### block_p0072_b005

4. 哪些风险需要重点关注？

### block_p0072_b006

5. 哪些员工表现突出？

### block_p0072_b007

6. 哪些员工或事项需要跟进？

### block_p0072_b008

7. 有多少事项需要部门负责人处理？

### block_p0072_b009

8. 有哪些事项超出部门权限，需要上推老板？

### block_p0072_b010

9. 明天部门工作重点应如何调整？

### block_p0072_b011

Manager Schema 的输入主要包括：

### block_p0072_b012

输入数据说明

### block_p0072_b013

本部门Staff Schema部门下属员工当日工作记录

### block_p0072_b014

未完成任务本部门仍在执行中的任务

### block_p0072_b015

异常记录员工上报或系统识别的风险与阻塞

### block_p0072_b016

历史部门汇总用于判断趋势变化

### block_p0072_b017

老板历史决策用于判断当前工作是否符合上级目标

### block_p0072_b018

Manager Schema 的输出主要包括：

### block_p0072_b019

输出内容说明

### block_p0072_b020

部门综合摘要对部门当天整体进展的简要总结

### block_p0072_b021

部门健康度用green / yellow / red 或评分表示

### block_p0072_b022

Top 风险提炼最重要的几个风险

### block_p0072_b023

阻塞事项需要协调或上推的问题

### block_p0072_b024

突出员工有明显贡献或关键产出的员工

### block_p0072_b025

待审批事项需要部门负责人或老板确认的事项

### block_p0072_b026

次日调整建议对部门明天工作的建议

### block_p0072_b027

来源记录本次汇总引用的Staff 记录ID

### block_p0072_b028

Manager Schema 的关键在于「提炼」和「分流」。能在部门内解决的事项，应由Manager

### block_p0072_b029

Agent 生成部门任务或提醒负责人处理；超出权限的事项，应进入Executive 层的决策输入。

### block_p0072_b030

MVP 阶段不要求Manager Agent 做复杂绩效判断，但至少要完成三件事：

### block_p0072_b031

1. 把部门Staff 数据汇总成一段可读摘要。

### block_p0072_b032

2. 提取风险、阻塞和需要支持的事项。

### block_p0072_b033

3. 区分「部门内可处理」和「需要老板决策」的事项。

### block_p0072_b034

4.4Executive Schema：老板决策数据

### block_p0072_b035

Executive Schema 是老板/高管层使用的数据结构，由Executive Agent 基于多个部门的

### block_p0072_b036

Manager Schema 聚合生成。

### block_p0072_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0072_b038

AutoMage-2-MVP 架构设计文档·杨卓72

### block_p0072_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 72

## 表格

无。

## 备注

无。

<!-- 来自 page_0072.md 全文结束 -->

<!-- 来自 page_0073.md 全文开始 -->

# Page 0073

## 原始文本块

### block_p0073_b001

2026 年5 月3 日

### block_p0073_b002

它面向的对象不是普通员工，也不是部门负责人，而是老板。因此Executive Schema 不

### block_p0073_b003

能只是长篇总结，而应该直接服务于决策。老板看到的内容应该是：现在公司发生了什么、哪

### block_p0073_b004

些风险最重要、需要我决定什么、有哪些方案、每个方案的影响是什么。

### block_p0073_b005

Executive Schema 主要回答以下问题：

### block_p0073_b006

1. 公司今天整体运行状态如何？

### block_p0073_b007

2. 哪些部门表现正常，哪些部门出现风险？

### block_p0073_b008

3. 哪些事项需要老板介入？

### block_p0073_b009

4. 每个待决策事项的背景是什么？

### block_p0073_b010

5. Agent 推荐哪些可选方案？

### block_p0073_b011

6. 各方案的影响、风险和资源消耗是什么？

### block_p0073_b012

7. 老板确认后应生成哪些任务？

### block_p0073_b013

8. 决策结果应下发给哪些部门或员工？

### block_p0073_b014

Executive Schema 的输入包括：

### block_p0073_b015

输入数据说明

### block_p0073_b016

Manager Schema各部门每日汇总

### block_p0073_b017

部门风险与异常需要跨部门或老板处理的问题

### block_p0073_b018

历史决策记录用于判断决策连续性

### block_p0073_b019

未完成关键任务用于判断执行风险

### block_p0073_b020

组织目标如ROI、交付周期、销售目标等

### block_p0073_b021

外部变量MVP 阶段可选，例如市场信息、客户反馈等

### block_p0073_b022

Executive Schema 的输出包括：

### block_p0073_b023

输出内容说明

### block_p0073_b024

组织级业务摘要面向老板的整体情况说明

### block_p0073_b025

关键风险当前最需要老板关注的问题

### block_p0073_b026

决策项列表需要老板确认的事项

### block_p0073_b027

候选方案每个决策项对应的A/B 或多方案

### block_p0073_b028

推荐方案Agent 给出的建议选项

### block_p0073_b029

推荐理由简短说明为什么推荐该方案

### block_p0073_b030

预期影响对成本、进度、资源、风险的影响

### block_p0073_b031

任务拆解草案老板确认后可生成的任务

### block_p0073_b032

来源汇总引用的Manager Summary ID

### block_p0073_b033

Executive Schema 的核心不是「替老板做决策」，而是「把老板需要判断的事项整理成选

### block_p0073_b034

择题」。在MVP 阶段，重大决策必须由老板确认，Executive Agent 只负责生成结构化建议和

### block_p0073_b035

可执行的任务草案。

### block_p0073_b036

4.5Task Schema：任务下发数据

### block_p0073_b037

Task Schema 是AutoMage-2 中连接「决策」和「执行」的关键结构。

### block_p0073_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0073_b039

AutoMage-2-MVP 架构设计文档·杨卓73

### block_p0073_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 73

## 表格

无。

## 备注

无。

<!-- 来自 page_0073.md 全文结束 -->

<!-- 来自 page_0074.md 全文开始 -->

# Page 0074

## 原始文本块

### block_p0074_b001

2026 年5 月3 日

### block_p0074_b002

如果系统只做日报和总结，最多只能算一个信息汇总工具。只有当老板或Manager 的决

### block_p0074_b003

策可以被拆解成任务，并下发到具体执行人，AutoMage-2 才真正形成组织运行闭环。

### block_p0074_b004

Task Schema 主要回答以下问题：

### block_p0074_b005

1. 这是什么任务？

### block_p0074_b006

2. 为什么生成这个任务？

### block_p0074_b007

3. 任务来源于哪个日报、汇总、异常或决策？

### block_p0074_b008

4. 谁负责执行？

### block_p0074_b009

5. 谁负责确认？

### block_p0074_b010

6. 优先级是什么？

### block_p0074_b011

7. 截止时间是什么？

### block_p0074_b012

8. 当前状态是什么？

### block_p0074_b013

9. 如果阻塞，应向谁上报？

### block_p0074_b014

10. 任务完成后如何记录结果？

### block_p0074_b015

Task Schema 的来源主要有四类：

### block_p0074_b016

来源示例

### block_p0074_b017

Staff Schema员工日报中提出需要支持，生成跟进任务

### block_p0074_b018

Manager Schema部门汇总中发现阻塞，生成协调任务

### block_p0074_b019

Executive Schema老板确认决策后，生成执行任务

### block_p0074_b020

Incident Schema异常处理过程中拆解出的补救任务

### block_p0074_b021

Task Schema 的最小字段建议包括：

### block_p0074_b022

字段说明

### block_p0074_b023

task_title任务标题

### block_p0074_b024

task_description任务说明

### block_p0074_b025

source_type来源类型，如staff_report、manager_summary、decision、incident

### block_p0074_b026

source_id来源对象ID

### block_p0074_b027

assignee_user_id执行人

### block_p0074_b028

department_id所属部门

### block_p0074_b029

priority优先级

### block_p0074_b030

due_at截止时间

### block_p0074_b031

status任务状态

### block_p0074_b032

created_by_node_id创建任务的节点

### block_p0074_b033

confirm_required是否需要人工确认

### block_p0074_b034

result_summary完成后的结果摘要

### block_p0074_b035

Task Schema 的状态流转建议如下：

### block_p0074_b036

待领取/ 待执行

### block_p0074_b037

↓

### block_p0074_b038

进行中

### block_p0074_b039

↓

### block_p0074_b040

已完成

### block_p0074_b041

↓

### block_p0074_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0074_b043

AutoMage-2-MVP 架构设计文档·杨卓74

### block_p0074_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 74

## 表格

无。

## 备注

无。

<!-- 来自 page_0074.md 全文结束 -->

<!-- 来自 page_0075.md 全文开始 -->

# Page 0075

## 原始文本块

### block_p0075_b001

2026 年5 月3 日

### block_p0075_b002

已确认关闭

### block_p0075_b003

如果任务出现问题，则进入：

### block_p0075_b004

进行中

### block_p0075_b005

↓

### block_p0075_b006

阻塞

### block_p0075_b007

↓

### block_p0075_b008

异常处理/ 上推决策

### block_p0075_b009

MVP 阶段的Task Schema 不需要覆盖复杂项目管理功能，但必须能完成最基础的任务

### block_p0075_b010

生成、分配、查询和状态更新。

### block_p0075_b011

4.6Incident Schema：异常上报数据

### block_p0075_b012

Incident Schema 用于记录风险、阻塞、异常和需要上级介入的问题。

### block_p0075_b013

在组织运行中，真正需要管理者处理的往往不是正常流程，而是异常情况。AutoMage-2

### block_p0075_b014

需要让异常从一线被及时记录、分类、上推和追踪，而不是埋在聊天记录或口头汇报里。

### block_p0075_b015

Incident Schema 主要回答以下问题：

### block_p0075_b016

1. 发生了什么异常？

### block_p0075_b017

2. 异常来自哪个员工、任务或部门？

### block_p0075_b018

3. 异常严重程度如何？

### block_p0075_b019

4. 当前是否影响交付、客户、成本或安全？

### block_p0075_b020

5. 员工是否已经尝试解决？

### block_p0075_b021

6. 需要谁介入？

### block_p0075_b022

7. 是否已经生成处理任务？

### block_p0075_b023

8. 当前处理状态是什么？

### block_p0075_b024

9. 最终如何关闭？

### block_p0075_b025

Incident Schema 的来源包括：

### block_p0075_b026

来源示例

### block_p0075_b027

Staff Schema员工日报中标记need_support = true

### block_p0075_b028

Task Schema任务执行中被标记为阻塞

### block_p0075_b029

Manager Schema部门汇总中发现风险

### block_p0075_b030

Executive Schema老板决策中要求重点跟进

### block_p0075_b031

系统规则长时间未提交日报、任务逾期、重复失败等

### block_p0075_b032

Incident Schema 的最小字段建议包括：

### block_p0075_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0075_b034

AutoMage-2-MVP 架构设计文档·杨卓75

### block_p0075_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 75

## 表格

无。

## 备注

无。

<!-- 来自 page_0075.md 全文结束 -->

<!-- 来自 page_0076.md 全文开始 -->

# Page 0076

## 原始文本块

### block_p0076_b001

2026 年5 月3 日

### block_p0076_b002

字段说明

### block_p0076_b003

incident_title异常标题

### block_p0076_b004

description异常说明

### block_p0076_b005

source_type来源类型

### block_p0076_b006

source_id来源对象ID

### block_p0076_b007

reporter_user_id上报人

### block_p0076_b008

department_id所属部门

### block_p0076_b009

severity严重程度

### block_p0076_b010

status当前状态

### block_p0076_b011

related_task_id关联任务

### block_p0076_b012

need_escalation是否需要上推

### block_p0076_b013

suggested_actionAgent 建议处理方式

### block_p0076_b014

resolved_at解决时间

### block_p0076_b015

Incident Schema 的严重程度建议先采用简单分级：

### block_p0076_b016

等级含义

### block_p0076_b017

low轻微问题，不影响整体进度

### block_p0076_b018

medium需要部门负责人关注

### block_p0076_b019

high影响关键任务，需要上推

### block_p0076_b020

critical影响交付、客户或经营，需要老板决策

### block_p0076_b021

MVP 阶段Incident Schema 不需要覆盖复杂风控体系，但至少要能把「问题」从普通日

### block_p0076_b022

报中提取出来，进入可追踪对象。

### block_p0076_b023

4.7Decision Schema：决策记录数据

### block_p0076_b024

Decision Schema 用于记录系统中所有需要被确认、选择或执行的决策事项。

### block_p0076_b025

AutoMage-2 的关键不是让Agent 只做总结，而是让Agent 把复杂情况整理成可决策项。

### block_p0076_b026

Decision Schema 就是这个过程的结构化载体。

### block_p0076_b027

Decision Schema 主要回答以下问题：

### block_p0076_b028

1. 需要决策的事项是什么？

### block_p0076_b029

2. 决策事项来自哪里？

### block_p0076_b030

3. 为什么需要决策？

### block_p0076_b031

4. 有哪些可选方案？

### block_p0076_b032

5. Agent 推荐哪个方案？

### block_p0076_b033

6. 推荐理由是什么？

### block_p0076_b034

7. 谁有权限确认？

### block_p0076_b035

8. 最终选择了哪个方案？

### block_p0076_b036

9. 确认后生成了哪些任务？

### block_p0076_b037

10. 决策产生了什么结果？

### block_p0076_b038

Decision Schema 的来源包括：

### block_p0076_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0076_b040

AutoMage-2-MVP 架构设计文档·杨卓76

### block_p0076_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 76

## 表格

无。

## 备注

无。

<!-- 来自 page_0076.md 全文结束 -->

<!-- 来自 page_0077.md 全文开始 -->

# Page 0077

## 原始文本块

### block_p0077_b001

2026 年5 月3 日

### block_p0077_b002

来源示例

### block_p0077_b003

Manager Schema部门发现事项超出权限，需要老板判断

### block_p0077_b004

Executive SchemaDream 生成老板待决策项

### block_p0077_b005

Incident Schema异常严重，需要管理层确认处理方案

### block_p0077_b006

Task Schema任务执行出现冲突，需要重新分配资源

### block_p0077_b007

Decision Schema 的最小字段建议包括：

### block_p0077_b008

字段说明

### block_p0077_b009

decision_title决策标题

### block_p0077_b010

decision_context背景说明

### block_p0077_b011

source_type来源类型

### block_p0077_b012

source_id来源对象ID

### block_p0077_b013

decision_level决策等级

### block_p0077_b014

options候选方案列表

### block_p0077_b015

recommended_optionAgent 推荐方案

### block_p0077_b016

recommend_reason推荐理由

### block_p0077_b017

expected_impact预期影响

### block_p0077_b018

confirm_required是否需要人工确认

### block_p0077_b019

confirmed_by确认人

### block_p0077_b020

confirmed_at确认时间

### block_p0077_b021

confirmed_option最终确认方案

### block_p0077_b022

generated_task_ids决策后生成的任务ID

### block_p0077_b023

status决策状态

### block_p0077_b024

Decision Schema 的状态建议包括：

### block_p0077_b025

待生成

### block_p0077_b026

↓

### block_p0077_b027

待确认

### block_p0077_b028

↓

### block_p0077_b029

已确认

### block_p0077_b030

↓

### block_p0077_b031

已生成任务

### block_p0077_b032

↓

### block_p0077_b033

执行中

### block_p0077_b034

↓

### block_p0077_b035

已完成/ 已关闭

### block_p0077_b036

如果老板拒绝或要求修改，则进入：

### block_p0077_b037

待确认

### block_p0077_b038

↓

### block_p0077_b039

已驳回/ 需补充信息

### block_p0077_b040

MVP 阶段要特别注意：Decision Schema 不等于Agent 的自由发挥。每个决策项都必须

### block_p0077_b041

有来源、有选项、有推荐理由、有确认状态，不能只是一段泛泛的建议。

### block_p0077_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0077_b043

AutoMage-2-MVP 架构设计文档·杨卓77

### block_p0077_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 77

## 表格

无。

## 备注

无。

<!-- 来自 page_0077.md 全文结束 -->

<!-- 来自 page_0078.md 全文开始 -->

# Page 0078

## 原始文本块

### block_p0078_b001

2026 年5 月3 日

### block_p0078_b002

4.8Summary Schema：周期性汇总数据

### block_p0078_b003

Summary Schema 用于沉淀一段时间内的汇总结果，例如员工日总结、部门日报、组织

### block_p0078_b004

日报、周报、月报和Dream 结果摘要。

### block_p0078_b005

在AutoMage-2 中，不是每次查看数据都应该重新扫描所有明细记录。对于部门汇总、老

### block_p0078_b006

板日报和周期性复盘，应通过Summary Schema 固化结果，既方便读取，也方便后续追溯。

### block_p0078_b007

Summary Schema 主要回答以下问题：

### block_p0078_b008

1. 汇总对象是谁？

### block_p0078_b009

2. 汇总周期是什么？

### block_p0078_b010

3. 汇总范围是个人、部门还是组织？

### block_p0078_b011

4. 本周期内完成了什么？

### block_p0078_b012

5. 主要风险是什么？

### block_p0078_b013

6. 有哪些未完成事项？

### block_p0078_b014

7. 有哪些待决策事项？

### block_p0078_b015

8. 引用了哪些原始记录？

### block_p0078_b016

9. 由哪个Agent 生成？

### block_p0078_b017

10. 是否经过人工确认？

### block_p0078_b018

Summary Schema 的类型可以包括：

### block_p0078_b019

类型说明

### block_p0078_b020

staff_daily_summary员工日总结

### block_p0078_b021

department_daily_summary部门日总结

### block_p0078_b022

organization_daily_summary组织日总结

### block_p0078_b023

department_weekly_summary部门周总结

### block_p0078_b024

dream_summaryDream 运行后的组织级摘要

### block_p0078_b025

decision_summary决策执行结果摘要

### block_p0078_b026

Summary Schema 的最小字段建议包括：

### block_p0078_b027

字段说明

### block_p0078_b028

summary_type汇总类型

### block_p0078_b029

scope_type汇总范围，如user、department、organization

### block_p0078_b030

scope_id对应用户、部门或组织ID

### block_p0078_b031

summary_date汇总日期

### block_p0078_b032

title汇总标题

### block_p0078_b033

content汇总正文

### block_p0078_b034

key_points关键事项

### block_p0078_b035

risks风险列表

### block_p0078_b036

pending_items待处理事项

### block_p0078_b037

source_count引用记录数量

### block_p0078_b038

source_record_ids来源工作记录

### block_p0078_b039

source_summary_ids来源汇总

### block_p0078_b040

generated_by_node_id生成节点

### block_p0078_b041

status状态

### block_p0078_b042

Summary Schema 的价值在于减少重复计算，并为老板看板、日报推送、组织复盘和后

### block_p0078_b043 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0078_b044

AutoMage-2-MVP 架构设计文档·杨卓78

### block_p0078_b045 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 78

## 表格

无。

## 备注

无。

<!-- 来自 page_0078.md 全文结束 -->

<!-- 来自 page_0079.md 全文开始 -->

# Page 0079

## 原始文本块

### block_p0079_b001

2026 年5 月3 日

### block_p0079_b002

续Dream 分析提供稳定输入。

### block_p0079_b003

MVP 阶段可以先实现日级Summary，后续再扩展周报、月报和长期趋势分析。

### block_p0079_b004

4.9不同Schema 之间的转换关系

### block_p0079_b005

AutoMage-2 的Schema 不是孤立存在的。系统真正的价值来自不同Schema 之间的逐级

### block_p0079_b006

转换。

### block_p0079_b007

MVP 阶段建议按照以下转换关系设计：

### block_p0079_b008

Staff Schema

### block_p0079_b009

→Work Record

### block_p0079_b010

→Manager Schema

### block_p0079_b011

→Department Summary

### block_p0079_b012

→Executive Schema

### block_p0079_b013

→Decision Schema

### block_p0079_b014

→Task Schema

### block_p0079_b015

→Staff 执行

### block_p0079_b016

→新的Staff Schema

### block_p0079_b017

同时，异常链路如下：

### block_p0079_b018

Staff Schema / Task Schema

### block_p0079_b019

→Incident Schema

### block_p0079_b020

→Manager 处理

### block_p0079_b021

→Decision Schema

### block_p0079_b022

→Task Schema

### block_p0079_b023

→Incident 关闭

### block_p0079_b024

汇总链路如下：

### block_p0079_b025

多个Staff Schema

### block_p0079_b026

→Manager Schema

### block_p0079_b027

→Summary Schema

### block_p0079_b028

多个Manager Schema

### block_p0079_b029

→Executive Schema

### block_p0079_b030

→Summary Schema / Decision Schema

### block_p0079_b031

各类转换关系说明如下：

### block_p0079_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0079_b033

AutoMage-2-MVP 架构设计文档·杨卓79

### block_p0079_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 79

## 表格

无。

## 备注

无。

<!-- 来自 page_0079.md 全文结束 -->

<!-- 来自 page_0080.md 全文开始 -->

# Page 0080

## 原始文本块

### block_p0080_b001

2026 年5 月3 日

### block_p0080_b002

来源Schema目标Schema触发条件说明

### block_p0080_b003

Staff SchemaManager Schema每日定时汇总Manager 读取本部门员工日报

### block_p0080_b004

Staff SchemaIncident Schemaneed_support = true 或风险较高员工问题进入异常处理

### block_p0080_b005

Staff SchemaTask Schema员工提出明确后续事项生成个人或部门任务

### block_p0080_b006

Manager SchemaExecutive Schema每日老板侧汇总Executive 读取各部门数据

### block_p0080_b007

Manager SchemaDecision Schema出现超权限事项生成待老板确认决策

### block_p0080_b008

Executive SchemaDecision SchemaDream 生成决策项老板侧选择题

### block_p0080_b009

Decision SchemaTask Schema决策确认后自动拆解执行任务

### block_p0080_b010

Task SchemaIncident Schema任务阻塞或逾期进入异常处理

### block_p0080_b011

Task SchemaStaff Schema员工执行后反馈形成新的工作记录

### block_p0080_b012

Summary SchemaExecutive Schema周期复盘或Dream 运行支持更高层判断

### block_p0080_b013

设计时需要注意三点：

### block_p0080_b014

第一，每次转换都要记录来源对象，不能只保留转换后的结果。第二，转换后的Schema

### block_p0080_b015

不能覆盖原始Schema，原始数据应保持可追溯。第三，Agent 可以负责生成转换结果，但后

### block_p0080_b016

端需要负责校验、写入和状态更新。

### block_p0080_b017

4.10Schema 生命周期

### block_p0080_b018

每条Schema 数据从生成到归档，应具备完整生命周期。生命周期设计的目的，是让系统

### block_p0080_b019

知道一条数据当前处于什么状态、是否可信、是否已经被上级读取、是否已经产生后续任务

### block_p0080_b020

或决策。

### block_p0080_b021

MVP 阶段建议将Schema 生命周期分为十个阶段：

### block_p0080_b022

生成

### block_p0080_b023

↓

### block_p0080_b024

校验

### block_p0080_b025

↓

### block_p0080_b026

补全

### block_p0080_b027

↓

### block_p0080_b028

确认

### block_p0080_b029

↓

### block_p0080_b030

签名

### block_p0080_b031

↓

### block_p0080_b032

写入

### block_p0080_b033

↓

### block_p0080_b034

读取

### block_p0080_b035

↓

### block_p0080_b036

聚合

### block_p0080_b037

↓

### block_p0080_b038

决策/ 任务生成

### block_p0080_b039

↓

### block_p0080_b040

归档

### block_p0080_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0080_b042

AutoMage-2-MVP 架构设计文档·杨卓80

### block_p0080_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 80

## 表格

无。

## 备注

无。

<!-- 来自 page_0080.md 全文结束 -->

<!-- 来自 page_0081.md 全文开始 -->

# Page 0081

## 原始文本块

### block_p0081_b001

2026 年5 月3 日

### block_p0081_b002

各阶段说明如下：

### block_p0081_b003

阶段说明责任方

### block_p0081_b004

生成Agent 根据用户输入或下级数据生成Schema 草稿Agent

### block_p0081_b005

校验检查字段、类型、枚举、权限和格式Agent 本地校验+ 后端校验

### block_p0081_b006

补全必填信息缺失时，向用户或下级节点追问Agent / IM

### block_p0081_b007

确认关键数据由对应人员确认员工/ Manager / 老板

### block_p0081_b008

签名记录确认人、确认时间和内容哈希后端

### block_p0081_b009

写入将通过校验的数据写入数据库后端

### block_p0081_b010

读取上级节点按权限读取数据Manager Agent / Executive Agent

### block_p0081_b011

聚合将多条下级数据汇总为上级SchemaManager Agent / Executive Agent

### block_p0081_b012

决策/ 任务生成根据汇总结果生成决策项或任务Executive Agent / Manager Agent

### block_p0081_b013

归档周期结束后保留为历史记录，用于审计和复盘后端/ 数据库

### block_p0081_b014

不同Schema 的生命周期略有差异。

### block_p0081_b015

Staff Schema 的典型生命周期：

### block_p0081_b016

员工填写

### block_p0081_b017

→Staff Agent 整理

### block_p0081_b018

→员工确认

### block_p0081_b019

→后端校验

### block_p0081_b020

→写入Work Record

### block_p0081_b021

→Manager 读取

### block_p0081_b022

→参与部门汇总

### block_p0081_b023

Manager Schema 的典型生命周期：

### block_p0081_b024

Manager Agent 读取Staff 数据

### block_p0081_b025

→聚合部门汇总

### block_p0081_b026

→Manager 确认或系统标记

### block_p0081_b027

→写入Summary

### block_p0081_b028

→Executive 读取

### block_p0081_b029

→参与老板决策

### block_p0081_b030

Executive Schema 的典型生命周期：

### block_p0081_b031

Executive Agent 读取Manager 汇总

### block_p0081_b032

→生成老板摘要和决策项

### block_p0081_b033

→推送老板确认

### block_p0081_b034

→写入Decision

### block_p0081_b035

→生成Task

### block_p0081_b036

→下发执行

### block_p0081_b037

Task Schema 的典型生命周期：

### block_p0081_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0081_b039

AutoMage-2-MVP 架构设计文档·杨卓81

### block_p0081_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 81

## 表格

无。

## 备注

无。

<!-- 来自 page_0081.md 全文结束 -->

<!-- 来自 page_0082.md 全文开始 -->

# Page 0082

## 原始文本块

### block_p0082_b001

2026 年5 月3 日

### block_p0082_b002

由决策或异常生成

### block_p0082_b003

→分配执行人

### block_p0082_b004

→员工接收

### block_p0082_b005

→执行中更新

### block_p0082_b006

→完成

### block_p0082_b007

→确认关闭

### block_p0082_b008

Incident Schema 的典型生命周期：

### block_p0082_b009

发现异常

### block_p0082_b010

→上报

### block_p0082_b011

→分配处理人

### block_p0082_b012

→处理跟进

### block_p0082_b013

→必要时上推决策

### block_p0082_b014

→关闭

### block_p0082_b015

Schema 生命周期中有几个关键原则：

### block_p0082_b016

1. 草稿数据不能直接进入上级汇总。

### block_p0082_b017

2. 未通过校验的数据不能写入正式业务表。

### block_p0082_b018

3. 需要人类确认的数据，未确认前不能触发重大任务。

### block_p0082_b019

4. 被上级引用的数据不能随意修改，修改应产生新版本或变更记录。

### block_p0082_b020

5. 已经生成任务或决策的数据，必须保留来源关系。

### block_p0082_b021

6. 归档数据仍可被审计和复盘，但默认不进入高频查询路径。

### block_p0082_b022

通过生命周期管理，AutoMage-2 可以避免数据随意生成、随意修改、随意引用的问题，

### block_p0082_b023

让每一条进入系统的数据都有状态、有来源、有责任人、有后续影响。

### block_p0082_b024 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0082_b025

AutoMage-2-MVP 架构设计文档·杨卓82

### block_p0082_b026 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 82

## 表格

无。

## 备注

无。

<!-- 来自 page_0082.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

