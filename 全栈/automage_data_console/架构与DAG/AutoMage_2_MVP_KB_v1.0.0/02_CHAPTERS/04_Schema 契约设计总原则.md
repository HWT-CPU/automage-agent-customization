# Schema 契约设计总原则

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P057-P069
> 对应页面文件：`01_PAGES/page_0057.md` — `01_PAGES/page_0069.md`

## 原文整理

<!-- 来自 page_0057.md 全文开始 -->

# Page 0057

## 原始文本块

### block_p0057_b001

2026 年5 月3 日

### block_p0057_b002

3Schema 契约设计总原则

### block_p0057_b003

3.1Schema 的定义

### block_p0057_b004

在AutoMage-2 中，Schema 指系统中用于描述和约束数据结构的标准格式。它规定了

### block_p0057_b005

Agent 生成的数据必须包含哪些字段、字段类型是什么、哪些字段必填、哪些字段可选、字段

### block_p0057_b006

之间是否存在逻辑关系，以及后端应如何校验、解析、存储和使用这些数据。

### block_p0057_b007

Schema 的本质不是普通表单，也不是简单的JSON 示例，而是AutoMage-2 三级Agent

### block_p0057_b008

之间进行数据传递的统一语言。Staff Agent、Manager Agent、Executive Agent 都必须按照

### block_p0057_b009

各自层级的Schema 生成结构化数据，避免不同Agent 输出格式不一致，导致后端无法解析、

### block_p0057_b010

数据库无法存储、上级节点无法汇总。

### block_p0057_b011

MVP 阶段所有核心业务数据都应优先通过Schema 表达，包括员工日报、部门汇总、老

### block_p0057_b012

板决策项、任务下发、异常上报和周期性总结。任何进入后端存储、跨节点读取、决策生成或

### block_p0057_b013

审计追踪的数据，都必须有明确的Schema 定义。

### block_p0057_b014

3.2为什么AutoMage-2 必须使用Schema 契约

### block_p0057_b015

AutoMage-2 的核心不是让Agent 输出一段自然语言总结，而是让Agent 参与企业组织

### block_p0057_b016

运行。组织运行要求数据稳定、可校验、可追溯、可聚合、可审计。自然语言文本无法直接满

### block_p0057_b017

足这些要求，因此必须引入Schema 契约。

### block_p0057_b018

使用Schema 契约主要解决以下问题：

### block_p0057_b019

1. 解决Agent 输出不稳定的问题

### block_p0057_b020

大模型天然容易输出格式不一致的内容。如果没有Schema 约束，同一个日报可能今天

### block_p0057_b021

输出成段落，明天输出成列表，后端无法稳定解析。

### block_p0057_b022

2. 解决前后端协作不一致的问题

### block_p0057_b023

前端、IM 表单、Agent、后端和数据库如果没有统一字段约定，联调阶段会出现大量字

### block_p0057_b024

段名、字段类型、必填项不一致的问题。

### block_p0057_b025

3. 解决多级节点汇总困难的问题

### block_p0057_b026

Manager Agent 需要读取多个Staff Schema，Executive Agent 需要读取多个Manager

### block_p0057_b027

Schema。只有下级数据结构稳定，上级节点才能自动聚合。

### block_p0057_b028

4. 解决决策依据不可追溯的问题

### block_p0057_b029

老板看到的决策建议必须能够追溯到具体部门汇总、员工日报和任务记录。Schema 可以

### block_p0057_b030

记录来源字段和引用关系。

### block_p0057_b031

5. 解决权限控制模糊的问题

### block_p0057_b032

不同层级Agent 能读取哪些字段、写入哪些字段、修改哪些字段，必须基于Schema 和

### block_p0057_b033

节点权限共同约束。

### block_p0057_b034

6. 解决数据长期沉淀的问题

### block_p0057_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0057_b036

AutoMage-2-MVP 架构设计文档·杨卓57

### block_p0057_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 57

## 表格

无。

## 备注

无。

<!-- 来自 page_0057.md 全文结束 -->

<!-- 来自 page_0058.md 全文开始 -->

# Page 0058

## 原始文本块

### block_p0058_b001

2026 年5 月3 日

### block_p0058_b002

AutoMage-2 的目标是沉淀组织运行数据。只有结构化数据才能被后续用于搜索、统计、

### block_p0058_b003

分析、绩效评估、组织诊断和Dream 决策。

### block_p0058_b004

7. 解决产品从通用型走向行业化的问题

### block_p0058_b005

MVP 阶段可以先使用通用Schema，后续可以扩展制造业、销售、研发、客服等行业模

### block_p0058_b006

板。Schema 是行业化扩展的基础。

### block_p0058_b007

因此，Schema 契约是AutoMage-2 的系统底座。没有Schema，系统只能停留在「AI 总

### block_p0058_b008

结工具」；有了Schema，系统才能进入「AI 组织操作系统」的阶段。

### block_p0058_b009

3.3Schema 在系统中的位置

### block_p0058_b010

Schema 位于Agent、IM、后端API、数据库和Dream 决策机制之间，是各模块协同的

### block_p0058_b011

中心契约。

### block_p0058_b012

在MVP 阶段，Schema 的位置如下：

### block_p0058_b013

1. IM 侧

### block_p0058_b014

IM 负责触发员工填报、推送提醒、展示决策卡片和任务通知。IM 收集到的内容需要被

### block_p0058_b015

Agent 整理成Schema。

### block_p0058_b016

2. Agent 侧

### block_p0058_b017

Agent 负责理解用户输入、补全字段、整理结构、生成符合Schema 的JSON 数据。Agent

### block_p0058_b018

不能随意输出不受约束的结构。

### block_p0058_b019

3. 前端侧

### block_p0058_b020

如果存在老板侧看板或员工侧表单，前端表单字段应直接来源于Schema 定义，避免前

### block_p0058_b021

端另起一套字段体系。

### block_p0058_b022

4. 后端API 侧

### block_p0058_b023

后端负责接收Schema 数据，并进行字段校验、类型校验、权限校验、签名校验和幂等处

### block_p0058_b024

理。

### block_p0058_b025

5. 数据库侧

### block_p0058_b026

数据库负责将Schema 中的核心字段实体化存储，将弹性字段存入JSONB 或扩展字段，

### block_p0058_b027

并建立可查询、可聚合的索引。

### block_p0058_b028

6. Dream 机制侧

### block_p0058_b029

Dream 机制读取Staff Schema、Manager Schema、历史任务和历史决策，生成组织级总

### block_p0058_b030

结、风险判断和老板决策项。

### block_p0058_b031

7. 审计侧

### block_p0058_b032

审计日志需要记录Schema 的提交人、提交时间、来源节点、校验结果、签名状态和后续

### block_p0058_b033

影响对象。

### block_p0058_b034

可以理解为：IM 是入口，Agent 是生成器，Schema 是契约，API 是网关，数据库是

### block_p0058_b035

事实源，Dream 是推理层，任务是执行结果。

### block_p0058_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0058_b037

AutoMage-2-MVP 架构设计文档·杨卓58

### block_p0058_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 58

## 表格

无。

## 备注

无。

<!-- 来自 page_0058.md 全文结束 -->

<!-- 来自 page_0059.md 全文开始 -->

# Page 0059

## 原始文本块

### block_p0059_b001

2026 年5 月3 日

### block_p0059_b002

3.4Schema 与普通日报的区别

### block_p0059_b003

AutoMage-2 中的Staff Schema 不是传统意义上的日报。传统日报通常是一段自然语言

### block_p0059_b004

描述，主要用于人工阅读；Schema 则是一种可以被机器稳定读取、处理和聚合的数据契约。

### block_p0059_b005

二者区别如下：

### block_p0059_b006

对比项普通日报AutoMage-2 Schema

### block_p0059_b007

数据形态自然语言文本标准JSON 结构

### block_p0059_b008

主要读者人Agent、后端、数据库、人

### block_p0059_b009

字段约束弱约束或无约束强字段、强类型、强校验

### block_p0059_b010

可聚合性差，需要人工整理强，可自动汇总

### block_p0059_b011

可追溯性弱，难定位来源强，可关联用户、部门、任务和时间

### block_p0059_b012

可审计性弱强，可记录签名、来源和变更

### block_p0059_b013

决策支持依赖人工判断可作为Dream 和上级Agent 的输入

### block_p0059_b014

后续利用难以复用可用于统计、任务生成、风险识别和组织分析

### block_p0059_b015

普通日报解决的是「让上级知道我今天做了什么」。AutoMage-2 Schema 解决的是「让系

### block_p0059_b016

统能够理解、存储、汇总、判断和驱动下一步行动」。

### block_p0059_b017

因此，MVP 阶段即使从员工填报日报开始，也不能把日报当成普通文本处理，而必须把

### block_p0059_b018

它设计成标准化Work Record Schema。

### block_p0059_b019

3.5Schema 与数据库表的关系

### block_p0059_b020

Schema 是数据进入系统前的契约，数据库表是数据进入系统后的事实存储。二者不是完

### block_p0059_b021

全等同关系。

### block_p0059_b022

一个Schema 可以映射到一张主表，也可以拆分映射到多张表。例如Staff Schema 中的

### block_p0059_b023

基础信息可以写入work_records，具体字段明细可以写入work_record_items，相关文件可

### block_p0059_b024

以写入artifacts，需要支持的事项可以进一步生成incidents 或tasks。

### block_p0059_b025

MVP 阶段建议采用以下映射原则：

### block_p0059_b026

Schema 类型主要数据库对象说明

### block_p0059_b027

Staff Schemawork_records、work_record_items存储员工每日工作记录和

### block_p0059_b028

字段明细

### block_p0059_b029

Manager Schemasummaries、summary_source_links存储部门级汇总及其来源

### block_p0059_b030

记录

### block_p0059_b031

Executive Schema决策记录表/ audit_logs / tasks存储老板决策项、确认结果

### block_p0059_b032

和生成任务

### block_p0059_b033

Task Schematasks、task_assignments、task_updates存储任务主体、负责人和任

### block_p0059_b034

务动态

### block_p0059_b035

Incident Schemaincidents、incident_updates存储异常、风险和处理过程

### block_p0059_b036

Artifact Schemaartifacts、artifact_links存储工作产出物、附件和外

### block_p0059_b037

部链接

### block_p0059_b038

Schema 与数据库的关系应遵循以下原则：

### block_p0059_b039

1. 高频查询字段必须实体化为数据库列。

### block_p0059_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0059_b041

AutoMage-2-MVP 架构设计文档·杨卓59

### block_p0059_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 59

## 表格

无。

## 备注

无。

<!-- 来自 page_0059.md 全文结束 -->

<!-- 来自 page_0060.md 全文开始 -->

# Page 0060

## 原始文本块

### block_p0060_b001

2026 年5 月3 日

### block_p0060_b002

2. 弹性扩展字段可以进入meta、payload 或value_json。

### block_p0060_b003

3. 关键业务对象必须有独立ID，方便追踪和引用。

### block_p0060_b004

4. 所有跨节点读取的数据必须带org_id、必要时带department_id。

### block_p0060_b005

5. 所有可审计对象必须记录创建人、创建时间、来源对象和状态。

### block_p0060_b006

6. 不允许长期依赖JSONB 中的字段完成高频过滤、排序和权限判断。

### block_p0060_b007

Schema 是「输入结构」，数据库是「事实沉淀」。系统设计时不能只看Schema，也不能

### block_p0060_b008

只看数据库表，必须保证二者可映射、可追溯、可演进。

### block_p0060_b009

3.6Schema 与Agent Prompt 的关系

### block_p0060_b010

Agent Prompt 负责告诉Agent 应该如何理解角色、如何处理输入、如何生成输出；Schema

### block_p0060_b011

负责约束Agent 最终输出的数据结构。

### block_p0060_b012

Prompt 与Schema 的关系如下：

### block_p0060_b013

1. Prompt 定义Agent 的行为边界。

### block_p0060_b014

2. Schema 定义Agent 的输出格式。

### block_p0060_b015

3. Prompt 不能代替Schema 校验。

### block_p0060_b016

4. Schema 不能代替Prompt 中的业务判断。

### block_p0060_b017

5. Agent 生成数据时必须同时遵守Prompt 和Schema。

### block_p0060_b018

例如Staff Agent 的Prompt 可以要求：

### block_p0060_b019

• 你是员工的岗位执行官。

### block_p0060_b020

• 你需要引导员工填写今日工作。

### block_p0060_b021

• 你不能编造员工未提供的信息。

### block_p0060_b022

• 你必须将员工输入整理为schema_v1_staff。

### block_p0060_b023

• 如果必填字段缺失，你必须追问员工。

### block_p0060_b024

• 如果员工提交内容不完整，你不能直接写入数据库。

### block_p0060_b025

但真正判断数据是否合格的，不应该只依赖Prompt，而应该由Schema 校验和后端校验

### block_p0060_b026

共同完成。

### block_p0060_b027

MVP 阶段必须避免以下错误：

### block_p0060_b028

1. 只在Prompt 中写「请输出JSON」，但没有定义字段结构。

### block_p0060_b029

2. 只让Agent 自己判断字段是否完整，后端不校验。

### block_p0060_b030

3. Agent 输出格式不稳定，但后端强行兼容。

### block_p0060_b031

4. Prompt 与后端字段命名不一致。

### block_p0060_b032

5. Prompt 更新后没有同步更新Schema 版本。

### block_p0060_b033

正确做法是：Prompt 引导Agent 生成Schema，Schema 约束Agent 输出，后端负

### block_p0060_b034

责最终校验。

### block_p0060_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0060_b036

AutoMage-2-MVP 架构设计文档·杨卓60

### block_p0060_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 60

## 表格

无。

## 备注

无。

<!-- 来自 page_0060.md 全文结束 -->

<!-- 来自 page_0061.md 全文开始 -->

# Page 0061

## 原始文本块

### block_p0061_b001

2026 年5 月3 日

### block_p0061_b002

3.7Schema 与前端表单的关系

### block_p0061_b003

MVP 阶段可能优先通过IM 表单完成员工填报和老板确认，也可能后续增加Web、小程

### block_p0061_b004

序或App 页面。不论交互形态如何，前端表单字段都应尽量与Schema 保持一致。

### block_p0061_b005

前端表单与Schema 的关系如下：

### block_p0061_b006

1. 前端表单字段应来源于Schema 字段定义。

### block_p0061_b007

2. 前端表单的必填项应与Schema 必填项一致。

### block_p0061_b008

3. 前端表单的枚举选项应与Schema 枚举值一致。

### block_p0061_b009

4. 前端表单的字段类型应与Schema 类型一致。

### block_p0061_b010

5. 前端校验只能作为第一层校验，后端仍需进行最终校验。

### block_p0061_b011

6. 表单展示文案可以面向用户优化，但字段key 不应随意变化。

### block_p0061_b012

例如，前端可以把work_progress 展示为「今日完成事项」，把issues_faced 展示为

### block_p0061_b013

「遇到的问题」，把need_support 展示为「是否需要上级支持」。但提交给后端时，字段key

### block_p0061_b014

必须保持Schema 定义中的标准命名。

### block_p0061_b015

这样做的好处是：

### block_p0061_b016

1. 前端、Agent、后端使用同一套字段。

### block_p0061_b017

2. 后续可以根据Schema 自动生成表单。

### block_p0061_b018

3. 表单改动可以被版本管理。

### block_p0061_b019

4. 不同企业或行业可以替换Schema 模板，而不必重写整套前端逻辑。

### block_p0061_b020

5. Agent 和前端可以共享同一套校验规则。

### block_p0061_b021

因此，Schema 不只是Agent 输出格式，也是前端表单设计的源头。

### block_p0061_b022

3.8Schema 与权限控制的关系

### block_p0061_b023

Schema 不仅定义数据结构，也会影响权限控制。不同层级的Agent 可以读取、生成、修

### block_p0061_b024

改的Schema 范围必须不同。

### block_p0061_b025

MVP 阶段的基本权限原则如下：

### block_p0061_b026

节点类型可写入Schema可读取Schema禁止行为

### block_p0061_b027

Staff Agent自己的Staff Schema、个人任务更

### block_p0061_b028

新、个人异常上报

### block_p0061_b029

自己的任务、自己的历史记录读取他人日报、读取部门汇总、越级查

### block_p0061_b030

看老板决策

### block_p0061_b031

Manager Agent本部门Manager Schema、部门任

### block_p0061_b032

务、部门异常处理

### block_p0061_b033

本部门Staff Schema、本部门任务

### block_p0061_b034

和异常

### block_p0061_b035

读取其他部门明细、直接执行老板级决

### block_p0061_b036

策

### block_p0061_b037

Executive AgentExecutive Schema、组织级决策、任

### block_p0061_b038

务拆解

### block_p0061_b039

组织级Manager Schema、关键汇

### block_p0061_b040

总、风险和任务

### block_p0061_b041

绕过人工确认自动执行重大决策

### block_p0061_b042

系统后台审计日志、Schema 校验结果、任务

### block_p0061_b043

状态

### block_p0061_b044

按权限读取所有相关数据无审计修改核心数据

### block_p0061_b045

Schema 权限控制需要包含以下维度：

### block_p0061_b046

1. 组织维度：所有业务数据必须绑定org_id。

### block_p0061_b047

2. 部门维度：部门级数据必须绑定department_id。

### block_p0061_b048 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0061_b049

AutoMage-2-MVP 架构设计文档·杨卓61

### block_p0061_b050 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 61

## 表格

无。

## 备注

无。

<!-- 来自 page_0061.md 全文结束 -->

<!-- 来自 page_0062.md 全文开始 -->

# Page 0062

## 原始文本块

### block_p0062_b001

2026 年5 月3 日

### block_p0062_b002

3. 用户维度：个人数据必须绑定user_id。

### block_p0062_b003

4. 节点维度：Agent 操作必须绑定node_id 或等价身份。

### block_p0062_b004

5. 角色维度：不同角色拥有不同读取和写入范围。

### block_p0062_b005

6. 动作维度：读取、创建、修改、确认、删除、下发任务应分别授权。

### block_p0062_b006

7. 字段维度：某些字段可以展示，某些字段只能用于系统内部处理。

### block_p0062_b007

权限不能只写在Prompt 中，必须由后端强制执行。Agent 即使生成了越权请求，后端也

### block_p0062_b008

必须拒绝。

### block_p0062_b009

3.9Schema 与数字签名的关系

### block_p0062_b010

数字签名用于解决Schema 数据的责任归属和完整性问题。

### block_p0062_b011

在AutoMage-2 中，Agent 可以辅助整理数据，但关键数据需要有人或指定节点确认。尤

### block_p0062_b012

其是Staff 日报、Manager 汇总、Executive 决策和任务确认，都需要记录提交主体、确认主

### block_p0062_b013

体和提交内容的哈希信息。

### block_p0062_b014

MVP 阶段可以采用简化签名机制，不要求立即实现复杂的密码学签名，但至少应具备以

### block_p0062_b015

下能力：

### block_p0062_b016

1. 记录是谁提交了Schema。

### block_p0062_b017

2. 记录提交时间。

### block_p0062_b018

3. 记录提交时的Schema 内容摘要。

### block_p0062_b019

4. 记录提交来源Agent。

### block_p0062_b020

5. 记录是否经过人类确认。

### block_p0062_b021

6. 记录确认人和确认时间。

### block_p0062_b022

7. 记录后续是否被修改。

### block_p0062_b023

8. 记录校验是否通过。

### block_p0062_b024

建议签名相关字段包括：

### block_p0062_b025

字段含义

### block_p0062_b026

signature_required是否需要签名

### block_p0062_b027

signature_status签名状态

### block_p0062_b028

signed_by签名人用户ID

### block_p0062_b029

signed_at签名时间

### block_p0062_b030

payload_hashSchema 内容哈希

### block_p0062_b031

signature_type签名类型

### block_p0062_b032

signature_source签名来源，如IM、Web、Agent

### block_p0062_b033

verify_status后端验签状态

### block_p0062_b034

数字签名与Schema 的关系可以理解为：

### block_p0062_b035

• Schema 规定「数据长什么样」。

### block_p0062_b036

• 数字签名证明「这份数据是谁确认的」。

### block_p0062_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0062_b038

AutoMage-2-MVP 架构设计文档·杨卓62

### block_p0062_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 62

## 表格

无。

## 备注

无。

<!-- 来自 page_0062.md 全文结束 -->

<!-- 来自 page_0063.md 全文开始 -->

# Page 0063

## 原始文本块

### block_p0063_b001

2026 年5 月3 日

### block_p0063_b002

• 审计日志记录「这份数据后来产生了什么影响」。

### block_p0063_b003

没有签名，Schema 只能说明数据格式正确；有了签名，Schema 才能进入组织责任体系。

### block_p0063_b004

3.10Schema 设计原则

### block_p0063_b005

MVP 阶段所有Schema 设计必须遵守以下原则。

### block_p0063_b006

3.10.1字段稳定

### block_p0063_b007

Schema 字段一旦进入前后端联调，不应频繁变更。字段名称、字段类型、必填规则和枚

### block_p0063_b008

举值必须经过确认后再使用。

### block_p0063_b009

如果确实需要变更，应通过Schema 版本管理解决，而不是直接修改旧字段含义。

### block_p0063_b010

错误示例：

### block_p0063_b011

{

### block_p0063_b012

"today_work": "完成客户沟通"

### block_p0063_b013

}

### block_p0063_b014

下一版又改为：

### block_p0063_b015

{

### block_p0063_b016

"work_progress": "完成客户沟通"

### block_p0063_b017

}

### block_p0063_b018

如果没有版本管理，会导致后端解析混乱。

### block_p0063_b019

正确做法是保持字段稳定，并通过版本号区分：

### block_p0063_b020

{

### block_p0063_b021

"schema_id": "schema_v1_staff",

### block_p0063_b022

"work_progress": "完成客户沟通"

### block_p0063_b023

}

### block_p0063_b024

3.10.2类型明确

### block_p0063_b025

每个字段必须有明确类型，不能让同一字段有时是字符串，有时是数组，有时是对象。

### block_p0063_b026

例如：

### block_p0063_b027

{

### block_p0063_b028

"need_support": true

### block_p0063_b029

}

### block_p0063_b030

不能写成：

### block_p0063_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0063_b032

AutoMage-2-MVP 架构设计文档·杨卓63

### block_p0063_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 63

## 表格

无。

## 备注

无。

<!-- 来自 page_0063.md 全文结束 -->

<!-- 来自 page_0064.md 全文开始 -->

# Page 0064

## 原始文本块

### block_p0064_b001

2026 年5 月3 日

### block_p0064_b002

{

### block_p0064_b003

"need_support": "需要"

### block_p0064_b004

}

### block_p0064_b005

字段类型不稳定会直接影响后端校验、数据库存储和上级Agent 聚合。

### block_p0064_b006

3.10.3必填项明确

### block_p0064_b007

每个Schema 必须区分必填字段和可选字段。

### block_p0064_b008

MVP 阶段Staff Schema 至少应包含：

### block_p0064_b009

1. 提交时间。

### block_p0064_b010

2. 用户ID。

### block_p0064_b011

3. 部门ID。

### block_p0064_b012

4. 今日完成事项。

### block_p0064_b013

5. 遇到的问题。

### block_p0064_b014

6. 是否需要支持。

### block_p0064_b015

7. 明日计划。

### block_p0064_b016

如果必填字段缺失，Agent 应优先追问用户，不能直接提交后端。后端收到缺失必填字段

### block_p0064_b017

的数据时，应返回明确错误。

### block_p0064_b018

3.10.4可校验

### block_p0064_b019

Schema 必须能被程序校验，不能只依赖人工阅读。

### block_p0064_b020

校验至少包括：

### block_p0064_b021

1. 字段是否存在。

### block_p0064_b022

2. 字段类型是否正确。

### block_p0064_b023

3. 枚举值是否合法。

### block_p0064_b024

4. 字符串长度是否超限。

### block_p0064_b025

5. 数组数量是否超限。

### block_p0064_b026

6. 对象结构是否符合要求。

### block_p0064_b027

7. 时间格式是否正确。

### block_p0064_b028

8. 当前用户是否有权限提交该数据。

### block_p0064_b029

9. 签名状态是否符合要求。

### block_p0064_b030

Agent 生成Schema 后，应先进行本地校验；后端收到Schema 后，应进行最终校验。

### block_p0064_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0064_b032

AutoMage-2-MVP 架构设计文档·杨卓64

### block_p0064_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 64

## 表格

无。

## 备注

无。

<!-- 来自 page_0064.md 全文结束 -->

<!-- 来自 page_0065.md 全文开始 -->

# Page 0065

## 原始文本块

### block_p0065_b001

2026 年5 月3 日

### block_p0065_b002

3.10.5可追溯

### block_p0065_b003

任何上级汇总、老板决策和任务下发，都必须能够追溯到原始来源。

### block_p0065_b004

例如Manager Schema 应记录其引用了哪些Staff Work Record。Executive Schema 应记

### block_p0065_b005

录其引用了哪些Manager Summary。任务应记录来源于哪个决策或异常。

### block_p0065_b006

建议所有汇总类Schema 都包含来源字段：

### block_p0065_b007

{

### block_p0065_b008

"source_record_ids": [1001, 1002, 1003],

### block_p0065_b009

"source_summary_ids": [2001, 2002]

### block_p0065_b010

}

### block_p0065_b011

可追溯是后续审计、复盘和责任划分的基础。

### block_p0065_b012

3.10.6可聚合

### block_p0065_b013

Schema 必须便于上级节点聚合。

### block_p0065_b014

Staff Schema 中的工作进展、问题、风险、资源使用和支持需求，应该能被Manager Agent

### block_p0065_b015

汇总成部门进展、Top 风险、阻塞事项和待决策事项。

### block_p0065_b016

Manager Schema 中的部门健康度、风险、待审批事项和效率评分，应该能被Executive

### block_p0065_b017

Agent 汇总成组织级业务摘要和老板决策项。

### block_p0065_b018

因此，Schema 不能只写大段文本，必须包含可聚合字段。例如：

### block_p0065_b019

{

### block_p0065_b020

"risk_level": "medium",

### block_p0065_b021

"need_support": true,

### block_p0065_b022

"resource_usage": {

### block_p0065_b023

"hours": 6,

### block_p0065_b024

"tools": ["CRM", "Feishu"]

### block_p0065_b025

}

### block_p0065_b026

}

### block_p0065_b027

这样的字段才能被系统用于统计、筛选和排序。

### block_p0065_b028

3.10.7可版本化

### block_p0065_b029

Schema 必须支持版本管理。

### block_p0065_b030

每条Schema 数据建议包含：

### block_p0065_b031

{

### block_p0065_b032

"schema_id": "schema_v1_staff",

### block_p0065_b033

"schema_version": "1.0.0"

### block_p0065_b034

}

### block_p0065_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0065_b036

AutoMage-2-MVP 架构设计文档·杨卓65

### block_p0065_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 65

## 表格

无。

## 备注

无。

<!-- 来自 page_0065.md 全文结束 -->

<!-- 来自 page_0066.md 全文开始 -->

# Page 0066

## 原始文本块

### block_p0066_b001

2026 年5 月3 日

### block_p0066_b002

版本管理用于解决以下问题：

### block_p0066_b003

1. 旧数据仍然可以解析。

### block_p0066_b004

2. 新字段可以逐步加入。

### block_p0066_b005

3. 不同企业可以使用不同模板。

### block_p0066_b006

4. 行业化Schema 可以从通用Schema 扩展。

### block_p0066_b007

5. 后端可以根据版本选择不同校验逻辑。

### block_p0066_b008

禁止在没有版本号的情况下直接改变字段含义。

### block_p0066_b009

3.10.8可审计

### block_p0066_b010

所有关键Schema 操作都应该写入审计日志，包括创建、修改、确认、驳回、上推、下发

### block_p0066_b011

任务和异常关闭。

### block_p0066_b012

审计信息至少包括：

### block_p0066_b013

1. 操作人。

### block_p0066_b014

2. 操作Agent。

### block_p0066_b015

3. 操作时间。

### block_p0066_b016

4. 操作对象。

### block_p0066_b017

5. 操作类型。

### block_p0066_b018

6. 操作前后状态。

### block_p0066_b019

7. 请求来源。

### block_p0066_b020

8. 校验结果。

### block_p0066_b021

可审计不是后期功能，而是组织级AI 系统的基础要求。没有审计，系统无法被企业信任。

### block_p0066_b022

3.10.9可被Agent 理解

### block_p0066_b023

Schema 不仅要方便后端处理，也要方便Agent 理解。

### block_p0066_b024

字段名称应尽量语义清晰，避免过度缩写。例如应使用work_progress，而不是wp；应

### block_p0066_b025

使用need_support，而不是ns。

### block_p0066_b026

字段说明中应明确告诉Agent：

### block_p0066_b027

1. 字段含义。

### block_p0066_b028

2. 填写方式。

### block_p0066_b029

3. 是否允许为空。

### block_p0066_b030

4. 示例值。

### block_p0066_b031

5. 错误示例。

### block_p0066_b032

6. 与其他字段的关系。

### block_p0066_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0066_b034

AutoMage-2-MVP 架构设计文档·杨卓66

### block_p0066_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 66

## 表格

无。

## 备注

无。

<!-- 来自 page_0066.md 全文结束 -->

<!-- 来自 page_0067.md 全文开始 -->

# Page 0067

## 原始文本块

### block_p0067_b001

2026 年5 月3 日

### block_p0067_b002

如果Schema 对Agent 不友好，Agent 生成数据时会频繁出错，后端校验失败率会升高，

### block_p0067_b003

用户体验会变差。

### block_p0067_b004

3.10.10人类最终确认

### block_p0067_b005

MVP 阶段必须坚持关键数据和关键决策的人类确认原则。

### block_p0067_b006

Agent 可以生成日报草稿、部门汇总、风险判断、老板决策建议和任务拆解，但以下行为

### block_p0067_b007

必须保留人类确认：

### block_p0067_b008

1. 员工日报最终提交。

### block_p0067_b009

2. Manager 部门汇总确认。

### block_p0067_b010

3. 超出权限的异常处理。

### block_p0067_b011

4. 老板级关键决策。

### block_p0067_b012

5. 重大任务下发。

### block_p0067_b013

6. 影响组织资源配置的操作。

### block_p0067_b014

这一原则用于降低黑盒AI 决策带来的信任风险，也有助于企业客户接受系统。

### block_p0067_b015

3.10.11MVP 优先通用，后续支持行业化

### block_p0067_b016

MVP 阶段Schema 应优先采用通用结构，覆盖大多数电脑办公场景。不要一开始就绑定

### block_p0067_b017

制造业、销售、客服、研发等特定行业流程。

### block_p0067_b018

通用Staff Schema 应优先回答以下问题：

### block_p0067_b019

1. 今天做了什么？

### block_p0067_b020

2. 遇到了什么问题？

### block_p0067_b021

3. 如何尝试解决？

### block_p0067_b022

4. 是否需要支持？

### block_p0067_b023

5. 明天计划做什么？

### block_p0067_b024

6. 消耗了哪些资源？

### block_p0067_b025

7. 产生了哪些产出物？

### block_p0067_b026

后续行业化版本可以在通用Schema 基础上扩展行业字段。例如销售场景可以增加客户

### block_p0067_b027

名称、跟进阶段、成交概率；研发场景可以增加代码提交、Bug 编号、需求ID；制造业场景

### block_p0067_b028

可以增加工序、产量、良率、设备状态。

### block_p0067_b029

3.10.12后端校验优先于Agent 自觉

### block_p0067_b030

Agent 生成的数据不能直接被视为可信数据。即使Agent 已经按照Prompt 输出了JSON，

### block_p0067_b031

后端也必须进行严格校验。

### block_p0067_b032

后端至少需要校验：

### block_p0067_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0067_b034

AutoMage-2-MVP 架构设计文档·杨卓67

### block_p0067_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 67

## 表格

无。

## 备注

无。

<!-- 来自 page_0067.md 全文结束 -->

<!-- 来自 page_0068.md 全文开始 -->

# Page 0068

## 原始文本块

### block_p0068_b001

2026 年5 月3 日

### block_p0068_b002

1. Schema ID 是否存在。

### block_p0068_b003

2. Schema 版本是否支持。

### block_p0068_b004

3. 字段是否完整。

### block_p0068_b005

4. 类型是否正确。

### block_p0068_b006

5. 当前用户是否有权限。

### block_p0068_b007

6. 当前Agent 是否有权限。

### block_p0068_b008

7. 签名是否满足要求。

### block_p0068_b009

8. 是否存在重复提交。

### block_p0068_b010

9. 来源对象是否真实存在。

### block_p0068_b011

10. 数据是否符合业务状态流转。

### block_p0068_b012

系统不能依赖「Agent 应该不会错」来保证稳定性。Agent 可以辅助生成，但后端必须负

### block_p0068_b013

责兜底。

### block_p0068_b014

3.10.13数据库是事实源

### block_p0068_b015

MVP 阶段可以使用IM、Agent 记忆、缓存或临时文件作为交互辅助，但最终事实数据

### block_p0068_b016

必须写入数据库。

### block_p0068_b017

以下数据必须以数据库为准：

### block_p0068_b018

1. 员工工作记录。

### block_p0068_b019

2. 部门汇总。

### block_p0068_b020

3. 老板决策。

### block_p0068_b021

4. 任务状态。

### block_p0068_b022

5. 异常状态。

### block_p0068_b023

6. 审计日志。

### block_p0068_b024

7. 签名记录。

### block_p0068_b025

8. Schema 校验结果。

### block_p0068_b026

Agent 本地记忆、聊天上下文和IM 消息只能作为辅助，不应作为最终事实源。

### block_p0068_b027

3.10.14先闭环，后优化

### block_p0068_b028

MVP 阶段Schema 设计不追求一次性完美，而应优先服务于最小闭环。

### block_p0068_b029

当前阶段最重要的是让以下链路跑通：

### block_p0068_b030

Staff Schema

### block_p0068_b031

→Work Record

### block_p0068_b032

→Manager Schema

### block_p0068_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0068_b034

AutoMage-2-MVP 架构设计文档·杨卓68

### block_p0068_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 68

## 表格

无。

## 备注

无。

<!-- 来自 page_0068.md 全文结束 -->

<!-- 来自 page_0069.md 全文开始 -->

# Page 0069

## 原始文本块

### block_p0069_b001

2026 年5 月3 日

### block_p0069_b002

→Department Summary

### block_p0069_b003

→Executive Decision

### block_p0069_b004

→Human Confirmation

### block_p0069_b005

→Task

### block_p0069_b006

→Staff Execution

### block_p0069_b007

只要该链路能够跑通，后续可以继续优化字段、补充行业模板、增强自动采集、加入绩

### block_p0069_b008

效分析和复杂Dream 机制。

### block_p0069_b009

因此，Schema 设计应避免过度复杂化。字段要够用、稳定、可校验、可扩展，但不应在

### block_p0069_b010

MVP 阶段引入过多暂时无法实现的复杂结构。

### block_p0069_b011 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0069_b012

AutoMage-2-MVP 架构设计文档·杨卓69

### block_p0069_b013 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 69

## 表格

无。

## 备注

无。

<!-- 来自 page_0069.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

