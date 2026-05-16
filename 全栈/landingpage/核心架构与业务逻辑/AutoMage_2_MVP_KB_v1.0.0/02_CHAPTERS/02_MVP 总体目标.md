# MVP 总体目标

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P035-P039
> 对应页面文件：`01_PAGES/page_0035.md` — `01_PAGES/page_0039.md`

## 原文整理

<!-- 来自 page_0035.md 全文开始 -->

# Page 0035

## 原始文本块

### block_p0035_b001

2026 年5 月3 日

### block_p0035_b002

1MVP 总体目标

### block_p0035_b003

1.1AutoMage-2 的核心目标

### block_p0035_b004

AutoMage-2 的核心目标是构建一套面向企业组织运行的三级AI Agent 数据闭环系统，

### block_p0035_b005

将传统企业中依赖人工汇报、人工传话、人工汇总和经验判断的管理流程，转化为由结构化

### block_p0035_b006

数据驱动、由Agent 辅助执行、由人类保留关键决策权的新型组织运行机制。

### block_p0035_b007

在AutoMage-2 中，系统不再把AI 仅作为单点工具使用，而是将AI Agent 嵌入组织结

### block_p0035_b008

构本身。每一线员工对应Staff Agent，每个部门或中层管理者对应Manager Agent，公司老

### block_p0035_b009

板或高管对应Executive Agent。不同层级的Agent 按照明确的Schema 契约生成、读取、汇

### block_p0035_b010

总和传递数据，从而形成「员工执行数据→部门汇总分析→老板决策建议→任务反向下

### block_p0035_b011

发→执行结果继续沉淀」的闭环。

### block_p0035_b012

MVP 阶段的核心目标不是一次性实现完整的企业AI 操作系统，而是先验证以下关键假

### block_p0035_b013

设：

### block_p0035_b014

1. 一线员工的日常工作可以被结构化为标准Staff Schema。

### block_p0035_b015

2. 中层节点可以基于本部门Staff Schema 自动生成Manager 汇总。

### block_p0035_b016

3. 老板节点可以基于Manager 汇总生成可确认的决策项。

### block_p0035_b017

4. 老板确认后的决策可以自动拆解为任务，并下发到对应执行节点。

### block_p0035_b018

5. 整个过程可以通过数据库、API、Agent 和IM 交互形成可运行闭环。

### block_p0035_b019

因此，AutoMage-2 MVP 的核心目标可以概括为：用最小系统跑通三级Agent 的组织

### block_p0035_b020

数据闭环，证明企业内部工作流可以被Schema 化、节点化、决策化和任务化。

### block_p0035_b021

1.2MVP 阶段的最小可验证闭环

### block_p0035_b022

MVP 阶段必须优先跑通一个最小可验证闭环，而不是堆叠过多功能。该闭环应覆盖Staff、

### block_p0035_b023

Manager、Executive 三个层级，并能够完整证明系统的数据流、决策流和任务流可以贯通。

### block_p0035_b024

最小可验证闭环如下：

### block_p0035_b025

1. Staff Agent 在每日固定时间通过IM 触发员工填写日报。

### block_p0035_b026

2. 员工提交今日工作进展、问题、解决尝试、明日计划和是否需要支持等信息。

### block_p0035_b027

3. Staff Agent 将员工输入整理为标准Staff Schema。

### block_p0035_b028

4. 后端对Staff Schema 进行字段、类型、权限和签名校验。

### block_p0035_b029

5. 校验通过后，数据写入数据库，形成Work Record。

### block_p0035_b030

6. Manager Agent 定时读取本部门下属员工的Work Record。

### block_p0035_b031

7. Manager Agent 聚合生成部门级Manager Schema，包括部门进展、风险、阻塞、突出员

### block_p0035_b032

工和待决策事项。

### block_p0035_b033

8. Executive Agent 读取各部门Manager Schema，生成老板侧业务摘要和决策选项。

### block_p0035_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0035_b035

AutoMage-2-MVP 架构设计文档·杨卓35

### block_p0035_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 35

## 表格

无。

## 备注

无。

<!-- 来自 page_0035.md 全文结束 -->

<!-- 来自 page_0036.md 全文开始 -->

# Page 0036

## 原始文本块

### block_p0036_b001

2026 年5 月3 日

### block_p0036_b002

9. 老板通过IM 或前端确认决策方案。

### block_p0036_b003

10. 系统根据老板确认结果生成任务。

### block_p0036_b004

11. 任务下发到对应Manager Agent 或Staff Agent。

### block_p0036_b005

12. 员工在次日通过Staff Agent 获取自己的任务并继续执行。

### block_p0036_b006

这个闭环是MVP 阶段的核心验证对象。只要该闭环能够稳定跑通，就可以证明

### block_p0036_b007

AutoMage-2 的三级节点架构、Schema 契约机制、数据汇总机制和决策下发机制具备基础

### block_p0036_b008

可行性。

### block_p0036_b009

1.3MVP 不追求的能力边界

### block_p0036_b010

MVP 阶段不追求完整替代企业现有OA、ERP、CRM、飞书、企业微信、钉钉或项目管

### block_p0036_b011

理系统，也不追求一次性完成所有自动化能力。当前阶段的重点是验证架构闭环，而不是追

### block_p0036_b012

求功能完备。

### block_p0036_b013

MVP 阶段暂不追求以下能力：

### block_p0036_b014

1. 不追求完整的行业业务系统集成。

### block_p0036_b015

2. 不追求自动读取所有电脑屏幕、鼠标行为和软件操作记录。

### block_p0036_b016

3. 不追求完全自动判断员工真实工作量。

### block_p0036_b017

4. 不追求完整绩效考核、薪酬计算和组织优化模型。

### block_p0036_b018

5. 不追求复杂审批流、预算流、报销流和法务流的全量替代。

### block_p0036_b019

6. 不追求老板侧独立App 的完整产品体验。

### block_p0036_b020

7. 不追求多模型、多工具、多插件生态的完整开放能力。

### block_p0036_b021

8. 不追求复杂的长期记忆、跨周期战略推演和高级Dream 决策能力。

### block_p0036_b022

9. 不追求完全无人干预的AI 自动经营公司。

### block_p0036_b023

10. 不追求在MVP 阶段解决所有数据真实性和员工抵触问题。

### block_p0036_b024

MVP 阶段的实现策略是：先用通用日报Schema、IM 交互、数据库存储、Agent 汇总

### block_p0036_b025

和人工确认决策跑通闭环，再逐步扩展自动采集、行业模板、复杂权限和高级决策能力。

### block_p0036_b026

1.4本阶段的核心验收目标

### block_p0036_b027

MVP 阶段的核心验收目标是验证AutoMage-2 的三级Agent 架构是否能够稳定完成一

### block_p0036_b028

次完整的数据闭环和决策闭环。

### block_p0036_b029

本阶段验收目标包括：

### block_p0036_b030

1. Staff Agent 能够引导员工提交每日工作数据。

### block_p0036_b031

2. Staff Agent 能够生成符合schema_v1_staff 的结构化数据。

### block_p0036_b032

3. 后端能够对Staff Schema 进行校验、鉴权和写入。

### block_p0036_b033

4. 数据库能够保存员工每日工作记录，并支持按组织、部门、用户、日期查询。

### block_p0036_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0036_b035

AutoMage-2-MVP 架构设计文档·杨卓36

### block_p0036_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 36

## 表格

无。

## 备注

无。

<!-- 来自 page_0036.md 全文结束 -->

<!-- 来自 page_0037.md 全文开始 -->

# Page 0037

## 原始文本块

### block_p0037_b001

2026 年5 月3 日

### block_p0037_b002

5. Manager Agent 能够读取本部门员工数据。

### block_p0037_b003

6. Manager Agent 能够生成符合schema_v1_manager 的部门汇总数据。

### block_p0037_b004

7. Manager Schema 能够体现部门整体健康度、综合进展、风险、阻塞和待决策事项。

### block_p0037_b005

8. Executive Agent 能够读取部门汇总数据。

### block_p0037_b006

9. Executive Agent 能够生成老板可理解、可选择、可确认的决策项。

### block_p0037_b007

10. 老板确认决策后，系统能够生成对应任务。

### block_p0037_b008

11. 任务能够被分配到指定员工或部门。

### block_p0037_b009

12. Staff Agent 能够读取并展示员工待执行任务。

### block_p0037_b010

13. 整个流程中关键数据均有来源记录、状态记录和基础审计记录。

### block_p0037_b011

14. 异常输入、Schema 校验失败、权限不足和接口失败能够返回明确错误信息。

### block_p0037_b012

15. MVP Demo 能够完整演示「日报提交→部门汇总→老板决策→任务下发→员工接

### block_p0037_b013

收」的流程。

### block_p0037_b014

本阶段验收不以界面美观度、复杂功能数量或商业化完整度为主要标准，而以闭环是否

### block_p0037_b015

跑通、数据是否可解析、节点是否能协作、决策是否能落地为主要标准。

### block_p0037_b016

1.5MVP 成功标准

### block_p0037_b017

MVP 成功的判断标准不是系统功能有多少，而是是否证明AutoMage-2 的核心架构假设

### block_p0037_b018

成立。

### block_p0037_b019

MVP 成功标准如下：

### block_p0037_b020

1. 数据结构可用

### block_p0037_b021

Staff、Manager、Executive 三层Schema 字段清晰、类型明确、可被Agent 生成、可被

### block_p0037_b022

后端校验、可被数据库存储。

### block_p0037_b023

2. 数据链路可通

### block_p0037_b024

一线员工提交的数据能够经过Staff Agent 写入数据库，并被Manager Agent 正确读取

### block_p0037_b025

和汇总。

### block_p0037_b026

3. 汇总逻辑可跑

### block_p0037_b027

Manager Agent 能够基于多条Staff 数据生成部门级摘要、风险识别、阻塞事项和待上推

### block_p0037_b028

决策。

### block_p0037_b029

4. 决策项可生成

### block_p0037_b030

Executive Agent 能够基于Manager 汇总生成老板可确认的决策项，而不是只输出普通

### block_p0037_b031

文本总结。

### block_p0037_b032

5. 人工确认可介入

### block_p0037_b033

关键决策必须经过老板或指定负责人确认，系统不能在MVP 阶段绕过人类执行重大决

### block_p0037_b034

策。

### block_p0037_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0037_b036

AutoMage-2-MVP 架构设计文档·杨卓37

### block_p0037_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 37

## 表格

无。

## 备注

无。

<!-- 来自 page_0037.md 全文结束 -->

<!-- 来自 page_0038.md 全文开始 -->

# Page 0038

## 原始文本块

### block_p0038_b001

2026 年5 月3 日

### block_p0038_b002

6. 任务可以反向下发

### block_p0038_b003

老板确认后的决策能够被系统转化为具体任务，并分配到对应部门或员工。

### block_p0038_b004

7. 执行节点可接收任务

### block_p0038_b005

Staff Agent 能够读取员工自己的任务，并通过IM 或其他方式展示给员工。

### block_p0038_b006

8. 权限边界清晰

### block_p0038_b007

Staff Agent 只能访问个人相关数据，Manager Agent 只能访问本部门数据，Executive

### block_p0038_b008

Agent 才能访问组织级汇总数据。

### block_p0038_b009

9. 接口与数据库可联调

### block_p0038_b010

Agent、后端API、数据库之间能够基于统一契约完成联调，不依赖口头约定。

### block_p0038_b011

10. Demo 可稳定复现

### block_p0038_b012

系统能够在演示环境中稳定复现完整流程，且每一步都有可观察的数据输入、输出和状

### block_p0038_b013

态变化。

### block_p0038_b014

如果以上标准基本满足，即可认为AutoMage-2 MVP 阶段达成初步成功。

### block_p0038_b015

1.6与AutoMage-1 的区别

### block_p0038_b016

AutoMage-1 的核心思路是「AI 中枢总控台」，即由一个中心化AI 系统全面感知公司信

### block_p0038_b017

息、分配任务、监控进度、做出决策，并将少数关键事项推送给管理层确认。该方案的优势是

### block_p0038_b018

想象空间大、自动化程度高，但同时存在较高的信任风险、技术风险和组织变革阻力。

### block_p0038_b019

AutoMage-2 相比AutoMage-1，核心变化在于从「单一AI 中枢」转向「多级Agent 节

### block_p0038_b020

点架构」。

### block_p0038_b021

主要区别如下：

### block_p0038_b022

对比项AutoMage-1AutoMage-2 MVP

### block_p0038_b023

架构形态单一AI 中枢Staff / Manager / Executive 三级Agent

### block_p0038_b024

数据处理方式中枢集中处理全量数据分层处理、逐级汇总

### block_p0038_b025

决策方式AI 做大量自动决策Agent 提供建议，人类确认关键决策

### block_p0038_b026

组织接受度冲击较大，容易引发抵触保留原有层级，但重塑中层职责

### block_p0038_b027

技术压力单点模型和系统压力较高多节点分担，数据库作为契约中转层

### block_p0038_b028

数据透明度中枢黑盒风险较高每级Schema 可追溯、可审计

### block_p0038_b029

中层角色可能被直接替代从传话者转为异常处理者和决策节点

### block_p0038_b030

MVP 落地难度较高更适合分阶段验证

### block_p0038_b031

AutoMage-2 并不是放弃AI 中枢的目标，而是采用更稳妥的落地路径：先让每一层组织

### block_p0038_b032

节点都具备数字分身，再通过标准Schema 让数据逐级汇总，最终形成更可信、更可控、更容

### block_p0038_b033

易被企业接受的AI 组织操作系统。

### block_p0038_b034

1.7与飞书/传统OA/项目管理工具的区别

### block_p0038_b035

AutoMage-2 MVP 与飞书、传统OA、项目管理工具存在本质区别。

### block_p0038_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0038_b037

AutoMage-2-MVP 架构设计文档·杨卓38

### block_p0038_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 38

## 表格

无。

## 备注

无。

<!-- 来自 page_0038.md 全文结束 -->

<!-- 来自 page_0039.md 全文开始 -->

# Page 0039

## 原始文本块

### block_p0039_b001

2026 年5 月3 日

### block_p0039_b002

飞书、企业微信、钉钉等工具主要解决的是沟通、协作、审批和信息承载问题。传统OA

### block_p0039_b003

主要解决流程流转和表单审批问题。项目管理工具主要解决任务分配、进度追踪和团队协作

### block_p0039_b004

问题。

### block_p0039_b005

AutoMage-2 的目标不是再做一个协作工具，而是构建一套由Agent 驱动的组织运行机

### block_p0039_b006

制。

### block_p0039_b007

主要区别如下：

### block_p0039_b008

对比项飞书/企业微信/钉钉传统OA项目管理工具AutoMage-2 MVP

### block_p0039_b009

核心定位沟通协作平台流程审批系统任务管理系统AI 组织运行系统

### block_p0039_b010

数据来源人主动发消息、开会、填

### block_p0039_b011

文档

### block_p0039_b012

人提交审批表单人创建和更新任务Agent 引导生成Schema

### block_p0039_b013

数据结构大量非结构化消息和文

### block_p0039_b014

档

### block_p0039_b015

固定审批表单任务字段为主Staff / Manager / Executive 多级Schema

### block_p0039_b016

AI 角色辅助总结、搜索、问答较弱辅助生成任务或总结作为组织节点参与数据汇总和决策建议

### block_p0039_b017

管理方式人看消息、人做判断人按流程审批人维护任务状态Agent 分层读取、聚合、上推和下发

### block_p0039_b018

老板视角需要自己查群、看文档、

### block_p0039_b019

问中层

### block_p0039_b020

主要看审批结果主要看项目进度直接接收关键摘要、风险和决策选项

### block_p0039_b021

中层角色仍以传话、协调、汇报为

### block_p0039_b022

主

### block_p0039_b023

仍以流程节点为主仍以任务推进为主转为异常处理、风险判断和部门决策节点

### block_p0039_b024

闭环能力沟通闭环为主审批闭环为主任务闭环为主数据→汇总→决策→任务→再数据的组

### block_p0039_b025

织闭环

### block_p0039_b026

AutoMage-2 可以接入飞书、企业微信或钉钉作为IM 入口，但它本身不是IM 工具。IM

### block_p0039_b027

在MVP 阶段只是触发器和交互入口，真正的核心在于后端数据库中的结构化工作记录、分

### block_p0039_b028

层汇总、决策日志和任务闭环。

### block_p0039_b029

因此，AutoMage-2 与传统工具的最大区别是：传统工具让人更方便地沟通和管理，

### block_p0039_b030

AutoMage-2 则尝试让组织运行过程本身变成可被Agent 理解、处理和优化的数据系统。

### block_p0039_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0039_b032

AutoMage-2-MVP 架构设计文档·杨卓39

### block_p0039_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 39

## 表格

无。

## 备注

无。

<!-- 来自 page_0039.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

