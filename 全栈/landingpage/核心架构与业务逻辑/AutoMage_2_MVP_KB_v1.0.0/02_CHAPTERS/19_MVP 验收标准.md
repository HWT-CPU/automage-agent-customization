# MVP 验收标准

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P386-P402
> 对应页面文件：`01_PAGES/page_0386.md` — `01_PAGES/page_0402.md`

## 原文整理

<!-- 来自 page_0386.md 全文开始 -->

# Page 0386

## 原始文本块

### block_p0386_b001

2026 年5 月3 日

### block_p0386_b002

18MVP 验收标准

### block_p0386_b003

18.1Schema 验收标准

### block_p0386_b004

Schema 是AutoMage-2 MVP 的数据契约。只要Schema 不稳定，Agent、API、数据库、

### block_p0386_b005

前端和IM 都会被迫各自理解一套字段，后续联调会非常痛苦。

### block_p0386_b006

MVP 阶段至少需要完成以下Schema：

### block_p0386_b007

Schema用途验收要求

### block_p0386_b008

schema_v1_staff员工日报可表达员工工作进展、问题、支持

### block_p0386_b009

需求、明日计划、签名

### block_p0386_b010

schema_v1_manager部门汇总可表达部门摘要、风险、阻塞、待

### block_p0386_b011

上推事项、来源记录

### block_p0386_b012

schema_v1_executive老板决策可表达组织摘要、关键风险、A/B

### block_p0386_b013

决策项、任务草案、确认状态

### block_p0386_b014

schema_v1_task任务可表达任务来源、负责人、状态、

### block_p0386_b015

优先级、截止时间、结果

### block_p0386_b016

schema_v1_incident异常可表达异常来源、等级、处理状态、

### block_p0386_b017

负责人、上推关系

### block_p0386_b018

Schema 验收标准如下：

### block_p0386_b019

验收项通过标准

### block_p0386_b020

Schema ID 清晰每类Schema 有固定schema_id，不能混用

### block_p0386_b021

版本可识别每类Schema 包含schema_version

### block_p0386_b022

必填字段明确每个Schema 有明确必填字段清单

### block_p0386_b023

字段类型稳定string、number、boolean、array、object 不混用

### block_p0386_b024

枚举值统一风险、状态、优先级等字段使用统一枚举

### block_p0386_b025

来源可追溯Staff、Manager、Executive、Task、Incident 都能保留来

### block_p0386_b026

源ID

### block_p0386_b027

签名字段统一涉及确认的数据有统一signature 结构

### block_p0386_b028

可被后端校验后端能根据Schema 规则返回明确422 错误

### block_p0386_b029

可被数据库承载每个核心字段能映射到表字段或meta

### block_p0386_b030

可被Agent 稳定生成Agent 连续生成多次，结构不应大幅漂移

### block_p0386_b031

不通过情况包括：

### block_p0386_b032

1. 同一个字段在不同示例中类型不一致。

### block_p0386_b033

2. 同一个状态出现多套写法，例如high、高、严重混用。

### block_p0386_b034

3. Staff Schema 不能追溯到员工和日期。

### block_p0386_b035

4. Manager Schema 不能追溯到来源Staff 记录。

### block_p0386_b036

5. Executive Schema 不能追溯到来源Manager Summary。

### block_p0386_b037

6. Task 没有来源对象。

### block_p0386_b038

7. Incident 不能关联任务或来源数据。

### block_p0386_b039

8. 签名字段只是文案，没有签名状态、确认人和时间。

### block_p0386_b040

Schema 最小验收结论应为：

### block_p0386_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0386_b042

AutoMage-2-MVP 架构设计文档·杨卓386

### block_p0386_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 386

## 表格

无。

## 备注

无。

<!-- 来自 page_0386.md 全文结束 -->

<!-- 来自 page_0387.md 全文开始 -->

# Page 0387

## 原始文本块

### block_p0387_b001

2026 年5 月3 日

### block_p0387_b002

Staff、Manager、Executive、Task、Incident 五类Schema 均已定义；

### block_p0387_b003

字段结构稳定；

### block_p0387_b004

能通过后端校验；

### block_p0387_b005

能落到现有数据库或明确的新增表；

### block_p0387_b006

能支撑Demo 主链路。

### block_p0387_b007

18.2Agent 验收标准

### block_p0387_b008

Agent 是AutoMage-2 MVP 的执行入口。MVP 阶段不要求Agent 拥有完整长期记忆和

### block_p0387_b009

复杂自主规划能力，但必须能在各自边界内稳定完成结构化、汇总、决策整理和任务读取。

### block_p0387_b010

需要验收的Agent 包括：

### block_p0387_b011

Agent核心职责

### block_p0387_b012

Staff Agent整理员工日报、提醒补全、提交Staff Schema、读取个

### block_p0387_b013

人任务

### block_p0387_b014

Manager Agent读取本部门日报、生成部门汇总、识别风险、上推老板

### block_p0387_b015

事项

### block_p0387_b016

Executive Agent读取部门汇总、生成老板决策卡片、处理确认结果

### block_p0387_b017

Dream定时生成组织摘要、风险、决策项和任务草案

### block_p0387_b018

18.2.1Staff Agent 验收标准

### block_p0387_b019

验收项通过标准

### block_p0387_b020

初始化能通过/api/v1/agent/init 获取用户、部门、节点和

### block_p0387_b021

权限

### block_p0387_b022

日报整理能把员工自然语言整理为schema_v1_staff

### block_p0387_b023

缺失追问必填字段缺失时能精准追问

### block_p0387_b024

员工确认提交前必须让员工确认

### block_p0387_b025

权限边界只能读取和提交本人数据

### block_p0387_b026

任务读取能读取并展示分配给员工自己的任务

### block_p0387_b027

状态更新能将任务更新为进行中、阻塞、已完成

### block_p0387_b028

异常上报能识别need_support 和blocked 并上报

### block_p0387_b029

不通过情况包括：

### block_p0387_b030

1. 员工未确认就提交日报。

### block_p0387_b031

2. Staff Agent 替员工编造日报内容。

### block_p0387_b032

3. Staff Agent 读取其他员工日报。

### block_p0387_b033

4. need_support = true 但不追问支持详情。

### block_p0387_b034

5. 任务来源、截止时间、优先级展示不清楚。

### block_p0387_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0387_b036

AutoMage-2-MVP 架构设计文档·杨卓387

### block_p0387_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 387

## 表格

无。

## 备注

无。

<!-- 来自 page_0387.md 全文结束 -->

<!-- 来自 page_0388.md 全文开始 -->

# Page 0388

## 原始文本块

### block_p0388_b001

2026 年5 月3 日

### block_p0388_b002

18.2.2Manager Agent 验收标准

### block_p0388_b003

验收项通过标准

### block_p0388_b004

部门读取能读取本部门已提交Staff Schema

### block_p0388_b005

数据过滤不读取未确认、已删除或无权限数据

### block_p0388_b006

部门汇总能生成schema_v1_manager

### block_p0388_b007

风险识别能从Staff 记录中识别部门风险

### block_p0388_b008

缺失统计能统计日报数量和缺失数量

### block_p0388_b009

来源引用source_record_ids 准确

### block_p0388_b010

上推事项能生成need_executive_decision

### block_p0388_b011

权限边界不能读取其他部门员工明细

### block_p0388_b012

不通过情况包括：

### block_p0388_b013

1. Manager Schema 没有来源Staff 记录。

### block_p0388_b014

2. 部门风险只是空泛总结，没有证据。

### block_p0388_b015

3. 直接把所有员工日报原文拼接给老板。

### block_p0388_b016

4. 把部门内可解决事项全部上推老板。

### block_p0388_b017

5. 读取其他部门员工明细。

### block_p0388_b018

18.2.3Executive Agent 验收标准

### block_p0388_b019

验收项通过标准

### block_p0388_b020

汇总读取能读取组织内Manager Summary

### block_p0388_b021

决策生成能生成老板可判断的决策项

### block_p0388_b022

方案表达每个关键决策至少有A/B 方案

### block_p0388_b023

推荐理由推荐方案必须有简明理由

### block_p0388_b024

任务草案确认后可生成任务草案

### block_p0388_b025

卡片展示能生成IM 决策卡片

### block_p0388_b026

确认处理老板确认后调用决策提交接口

### block_p0388_b027

权限边界不能绕过老板确认生成重大任务

### block_p0388_b028

不通过情况包括：

### block_p0388_b029

1. 只生成一段普通日报，没有决策项。

### block_p0388_b030

2. 决策项没有方案。

### block_p0388_b031

3. 推荐方案没有理由。

### block_p0388_b032

4. 老板未确认就创建正式任务。

### block_p0388_b033

5. 无法追溯决策来源。

### block_p0388_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0388_b035

AutoMage-2-MVP 架构设计文档·杨卓388

### block_p0388_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 388

## 表格

无。

## 备注

无。

<!-- 来自 page_0388.md 全文结束 -->

<!-- 来自 page_0389.md 全文开始 -->

# Page 0389

## 原始文本块

### block_p0389_b001

2026 年5 月3 日

### block_p0389_b002

18.2.4Dream 验收标准

### block_p0389_b003

验收项通过标准

### block_p0389_b004

定时运行能按指定时间或手动触发运行

### block_p0389_b005

输入读取能读取Manager Schema、历史Summary、任务和决策

### block_p0389_b006

风险归并能合并同类风险，避免重复推送

### block_p0389_b007

输出结构输出能映射到Executive Schema

### block_p0389_b008

降级处理输入不足或运行失败时能生成简版摘要或失败记录

### block_p0389_b009

幂等处理同一日期重复运行不生成重复决策

### block_p0389_b010

审计记录每次运行有运行记录或审计日志

### block_p0389_b011

不通过情况包括：

### block_p0389_b012

1. Dream 输出自由文本，无法写库。

### block_p0389_b013

2. 重复生成同一老板决策项。

### block_p0389_b014

3. 不引用来源Summary。

### block_p0389_b015

4. 模型失败后没有记录。

### block_p0389_b016

5. 低风险事项大量推给老板。

### block_p0389_b017

18.3API 验收标准

### block_p0389_b018

API 是Agent、IM、前端和数据库之间的正式契约。MVP 阶段至少要保证主链路API

### block_p0389_b019

可用、可校验、可幂等、可追踪。

### block_p0389_b020

必须验收的接口如下：

### block_p0389_b021

接口用途

### block_p0389_b022

POST /api/v1/agent/initAgent 初始化

### block_p0389_b023

POST /api/v1/report/staffStaff 日报提交

### block_p0389_b024

POST /api/v1/report/managerManager 汇总提交

### block_p0389_b025

POST /api/v1/decision/commit老板决策确认

### block_p0389_b026

GET /api/v1/tasks任务获取

### block_p0389_b027

GET /api/v1/summaries汇总读取

### block_p0389_b028

POST /api/v1/incidents异常上报

### block_p0389_b029

GET /api/v1/audit-logs审计日志读取

### block_p0389_b030

API 验收标准如下：

### block_p0389_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0389_b032

AutoMage-2-MVP 架构设计文档·杨卓389

### block_p0389_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 389

## 表格

无。

## 备注

无。

<!-- 来自 page_0389.md 全文结束 -->

<!-- 来自 page_0390.md 全文开始 -->

# Page 0390

## 原始文本块

### block_p0390_b001

2026 年5 月3 日

### block_p0390_b002

验收项通过标准

### block_p0390_b003

统一响应格式所有接口返回success/code/message/data/request_id

### block_p0390_b004

统一错误格式失败时返回明确错误码和字段级错误

### block_p0390_b005

鉴权可用未登录或Token 无效返回401

### block_p0390_b006

权限可用越权访问返回403 或404

### block_p0390_b007

Schema 校验字段缺失、类型错误、枚举错误返回422

### block_p0390_b008

幂等支持关键写入接口支持Idempotency-Key

### block_p0390_b009

审计写入关键操作写入audit_logs

### block_p0390_b010

错误可修复Agent 能根据错误信息追问用户或重试

### block_p0390_b011

状态可控非法状态流转会被拒绝

### block_p0390_b012

数据可追踪返回结果中包含写入对象ID

### block_p0390_b013

关键接口验收重点如下：

### block_p0390_b014

18.3.1Agent 初始化接口

### block_p0390_b015

必须返回：

### block_p0390_b016

1. 当前用户。

### block_p0390_b017

2. 当前组织。

### block_p0390_b018

3. 当前部门。

### block_p0390_b019

4. Agent 节点ID。

### block_p0390_b020

5. Agent 类型。

### block_p0390_b021

6. 权限范围。

### block_p0390_b022

7. 支持的Schema 版本。

### block_p0390_b023

18.3.2Staff 日报提交接口

### block_p0390_b024

必须支持：

### block_p0390_b025

1. Staff Schema 校验。

### block_p0390_b026

2. 员工本人权限校验。

### block_p0390_b027

3. 员工签名校验。

### block_p0390_b028

4. 幂等提交。

### block_p0390_b029

5. 写入work_records 和work_record_items。

### block_p0390_b030

18.3.3Manager 汇总提交接口

### block_p0390_b031

必须支持：

### block_p0390_b032

1. Manager Schema 校验。

### block_p0390_b033

2. 本部门权限校验。

### block_p0390_b034

3. 来源Staff 记录校验。

### block_p0390_b035

4. 写入summaries。

### block_p0390_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0390_b037

AutoMage-2-MVP 架构设计文档·杨卓390

### block_p0390_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 390

## 表格

无。

## 备注

无。

<!-- 来自 page_0390.md 全文结束 -->

<!-- 来自 page_0391.md 全文开始 -->

# Page 0391

## 原始文本块

### block_p0391_b001

2026 年5 月3 日

### block_p0391_b002

5. 写入summary_source_links。

### block_p0391_b003

18.3.4决策确认接口

### block_p0391_b004

必须支持：

### block_p0391_b005

1. 决策存在性校验。

### block_p0391_b006

2. 老板确认权限校验。

### block_p0391_b007

3. 确认方案校验。

### block_p0391_b008

4. 签名生成。

### block_p0391_b009

5. 任务生成。

### block_p0391_b010

6. 幂等防重复任务。

### block_p0391_b011

API 不通过情况包括：

### block_p0391_b012

1. 错误只返回“系统错误”。

### block_p0391_b013

2. Staff 能替别人提交日报。

### block_p0391_b014

3. Manager 能读取其他部门明细。

### block_p0391_b015

4. 老板重复确认生成多组任务。

### block_p0391_b016

5. 422 错误没有字段级提示。

### block_p0391_b017

6. 关键写入成功但没有审计日志。

### block_p0391_b018

18.4数据库验收标准

### block_p0391_b019

数据库是AutoMage-2 的事实源。MVP 验收时，不能只看Agent 是否生成了文字，还要

### block_p0391_b020

检查数据是否真实落表、关系是否完整、来源是否可追溯。

### block_p0391_b021

数据库验收分为两类：

### block_p0391_b022

1. 当前已有表是否能支撑主链路。

### block_p0391_b023

2. 关键缺口是否有明确补齐方案。

### block_p0391_b024 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0391_b025

AutoMage-2-MVP 架构设计文档·杨卓391

### block_p0391_b026 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 391

## 表格

无。

## 备注

无。

<!-- 来自 page_0391.md 全文结束 -->

<!-- 来自 page_0392.md 全文开始 -->

# Page 0392

## 原始文本块

### block_p0392_b001

2026 年5 月3 日

### block_p0392_b002

18.4.1主链路落表验收

### block_p0392_b003

数据对象目标表通过标准

### block_p0392_b004

Staff 日报主记录work_records能写入员工、日期、部门、状态、

### block_p0392_b005

模板

### block_p0392_b006

Staff 字段明细work_record_items能保存工作进展、问题、支持需求、

### block_p0392_b007

明日计划

### block_p0392_b008

Manager 汇总summaries能保存部门摘要、风险、健康度

### block_p0392_b009

Summary 来源summary_source_links能追溯到Staff 日报

### block_p0392_b010

任务主记录tasks能保存任务标题、描述、状态、优

### block_p0392_b011

先级、截止时间

### block_p0392_b012

任务分配task_assignments能关联任务和执行人

### block_p0392_b013

任务动态task_updates能记录状态变化

### block_p0392_b014

异常主记录incidents能保存异常标题、等级、状态

### block_p0392_b015

异常动态incident_updates能记录异常处理过程

### block_p0392_b016

产出物artifacts能关联日报、任务或异常

### block_p0392_b017

审计日志audit_logs能记录关键动作

### block_p0392_b018

18.4.2数据追溯验收

### block_p0392_b019

MVP 必须能追溯以下链路：

### block_p0392_b020

task_id

### block_p0392_b021

→source_decision_id

### block_p0392_b022

→source_summary_ids

### block_p0392_b023

→source_record_ids

### block_p0392_b024

→staff user_id

### block_p0392_b025

如果还没有独立Decision表，至少要能通过tasks.meta.source_decision_id、

### block_p0392_b026

summaries.meta.decision_items、summary_source_links 追溯。

### block_p0392_b027

最低通过标准：

### block_p0392_b028

任务可以追溯到老板决策；

### block_p0392_b029

老板决策可以追溯到Manager Summary；

### block_p0392_b030

Manager Summary 可以追溯到Staff Work Record；

### block_p0392_b031

Staff Work Record 可以追溯到员工本人确认。

### block_p0392_b032

18.4.3数据库缺口验收

### block_p0392_b033

当前DDL 中建议补齐的对象包括：

### block_p0392_b034

缺口MVP 验收要求

### block_p0392_b035

Agent 节点表至少有Mock 配置或agent_nodes 表方案

### block_p0392_b036

Decision 表至少有临时承载方式，最好新增decisions

### block_p0392_b037

Digital Signature至少能在meta.signature 中保存签名字段

### block_p0392_b038

Dream Run 表至少有运行日志或审计记录

### block_p0392_b039

Schema Contract至少有文档化Schema 和后端校验规则

### block_p0392_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0392_b041

AutoMage-2-MVP 架构设计文档·杨卓392

### block_p0392_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 392

## 表格

无。

## 备注

无。

<!-- 来自 page_0392.md 全文结束 -->

<!-- 来自 page_0393.md 全文开始 -->

# Page 0393

## 原始文本块

### block_p0393_b001

2026 年5 月3 日

### block_p0393_b002

不通过情况包括：

### block_p0393_b003

1. 只有IM 消息，没有数据库记录。

### block_p0393_b004

2. Manager 汇总无法追溯来源日报。

### block_p0393_b005

3. 老板决策无法追溯来源Summary。

### block_p0393_b006

4. 任务不知道由哪个决策产生。

### block_p0393_b007

5. 审计日志无法说明关键状态变化。

### block_p0393_b008

6. 签名信息完全没有落库。

### block_p0393_b009

18.5权限验收标准

### block_p0393_b010

权限验收的重点是证明系统不会因为引入Agent 而破坏组织、部门和用户边界。

### block_p0393_b011

权限验收至少覆盖四层：

### block_p0393_b012

组织级隔离

### block_p0393_b013

部门级隔离

### block_p0393_b014

用户级隔离

### block_p0393_b015

Agent 节点级隔离

### block_p0393_b016

18.5.1组织级权限

### block_p0393_b017

验收项通过标准

### block_p0393_b018

org_id 校验所有核心查询和写入都校验org_id

### block_p0393_b019

跨组织读取用户不能读取其他组织数据

### block_p0393_b020

跨组织写入用户不能向其他组织写数据

### block_p0393_b021

审计记录跨组织越权尝试有审计日志

### block_p0393_b022

18.5.2用户级权限

### block_p0393_b023

验收项通过标准

### block_p0393_b024

本人日报Staff 只能提交本人日报

### block_p0393_b025

本人任务Staff 只能查询分配给自己的任务

### block_p0393_b026

本人签名Staff 日报签名人必须是本人

### block_p0393_b027

他人数据Staff 不能读取其他员工日报

### block_p0393_b028

18.5.3部门级权限

### block_p0393_b029

验收项通过标准

### block_p0393_b030

本部门读取Manager 可读取本部门Staff 数据

### block_p0393_b031

跨部门限制Manager 默认不能读取其他部门员工明细

### block_p0393_b032

部门汇总Manager 只能提交本部门汇总

### block_p0393_b033

部门任务Manager 只能下发或管理本部门任务

### block_p0393_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0393_b035

AutoMage-2-MVP 架构设计文档·杨卓393

### block_p0393_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 393

## 表格

无。

## 备注

无。

<!-- 来自 page_0393.md 全文结束 -->

<!-- 来自 page_0394.md 全文开始 -->

# Page 0394

## 原始文本块

### block_p0394_b001

2026 年5 月3 日

### block_p0394_b002

18.5.4Executive 权限

### block_p0394_b003

验收项通过标准

### block_p0394_b004

组织汇总Executive 可读取组织级和部门级汇总

### block_p0394_b005

老板确认只有老板或授权高管能确认L3 决策

### block_p0394_b006

下钻控制Executive 默认看汇总，必要时可追溯来源

### block_p0394_b007

任务生成未确认决策不能生成正式任务

### block_p0394_b008

18.5.5Agent 节点权限

### block_p0394_b009

验收项通过标准

### block_p0394_b010

节点绑定Staff / Manager / Executive Agent 有明确绑定对象

### block_p0394_b011

初始化权限/agent/init 返回准确权限

### block_p0394_b012

API 校验后端同时校验用户和Agent 节点

### block_p0394_b013

节点越权Agent 越权请求被拒绝

### block_p0394_b014

权限不通过情况包括：

### block_p0394_b015

1. Staff Agent 能查询其他员工日报。

### block_p0394_b016

2. Manager Agent 能读取其他部门明细。

### block_p0394_b017

3. 普通员工能确认老板决策。

### block_p0394_b018

4. 未初始化Agent 能调用核心写入接口。

### block_p0394_b019

5. Agent 修改org_id 或department_id 后能绕过权限。

### block_p0394_b020

6. 权限失败没有审计日志。

### block_p0394_b021

18.6决策机制验收标准

### block_p0394_b022

决策机制是AutoMage-2 区别于普通日报系统的核心。MVP 验收时，要重点检查决策是

### block_p0394_b023

否能从Staff 问题逐步上推到老板确认，并在确认后下发任务。

### block_p0394_b024

18.6.1决策分层验收

### block_p0394_b025

决策等级验收标准

### block_p0394_b026

L0Agent 可自动提醒和补全，不改变重大业务状态

### block_p0394_b027

L1员工确认后提交个人日报和任务状态

### block_p0394_b028

L2Manager 确认部门汇总、部门任务和部门异常

### block_p0394_b029

L3老板确认后才能执行组织级决策

### block_p0394_b030

L4高风险事项能标记为线下会议或人工审批

### block_p0394_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0394_b032

AutoMage-2-MVP 架构设计文档·杨卓394

### block_p0394_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 394

## 表格

无。

## 备注

无。

<!-- 来自 page_0394.md 全文结束 -->

<!-- 来自 page_0395.md 全文开始 -->

# Page 0395

## 原始文本块

### block_p0395_b001

2026 年5 月3 日

### block_p0395_b002

18.6.2上推机制验收

### block_p0395_b003

验收项通过标准

### block_p0395_b004

Staff 上推Staff 的阻塞和支持需求能进入Manager 视角

### block_p0395_b005

Manager 上推Manager 能生成need_executive_decision

### block_p0395_b006

来源完整上推事项包含来源记录

### block_p0395_b007

方案完整老板决策项包含A/B 方案

### block_p0395_b008

推荐明确Agent 推荐方案有理由

### block_p0395_b009

权限正确超权限事项不会被下级直接执行

### block_p0395_b010

18.6.3老板确认验收

### block_p0395_b011

验收项通过标准

### block_p0395_b012

决策卡片老板能看到背景、方案、推荐理由和任务草案

### block_p0395_b013

确认动作老板可选择方案A / B / 补充信息/ 驳回

### block_p0395_b014

签名记录确认动作记录确认人、时间、来源和hash

### block_p0395_b015

状态变化决策从pending 变为confirmed

### block_p0395_b016

审计记录决策确认写入审计日志

### block_p0395_b017

任务触发确认后生成正式任务

### block_p0395_b018

不通过情况包括：

### block_p0395_b019

1. Manager 直接执行老板级决策。

### block_p0395_b020

2. 老板卡片没有方案，只是“请老板处理”。

### block_p0395_b021

3. 老板未确认，系统已生成任务。

### block_p0395_b022

4. 决策没有来源Summary。

### block_p0395_b023

5. 决策确认后没有记录签名和审计。

### block_p0395_b024

6. 决策结果无法追溯到任务。

### block_p0395_b025

18.7Dream 机制验收标准

### block_p0395_b026

Dream 机制的验收重点，不是判断它是否“聪明”，而是判断它是否能稳定完成组织级摘

### block_p0395_b027

要、风险识别、决策生成和任务草案输出。

### block_p0395_b028

18.7.1Dream 输入验收

### block_p0395_b029

输入类型通过标准

### block_p0395_b030

Manager Schema能读取指定日期部门汇总

### block_p0395_b031

历史Summary能读取近几天相关摘要

### block_p0395_b032

历史Decision能判断是否重复决策

### block_p0395_b033

未完成任务能识别高优、逾期、阻塞任务

### block_p0395_b034

外部目标能参考当前MVP 目标或演示目标

### block_p0395_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0395_b036

AutoMage-2-MVP 架构设计文档·杨卓395

### block_p0395_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 395

## 表格

无。

## 备注

无。

<!-- 来自 page_0395.md 全文结束 -->

<!-- 来自 page_0396.md 全文开始 -->

# Page 0396

## 原始文本块

### block_p0396_b001

2026 年5 月3 日

### block_p0396_b002

MVP 最低要求是能读取Manager Schema。其他输入可以先作为增强项。

### block_p0396_b003

18.7.2Dream 输出验收

### block_p0396_b004

输出类型通过标准

### block_p0396_b005

组织摘要生成business_summary

### block_p0396_b006

关键风险生成key_risks，且有来源

### block_p0396_b007

决策项生成decision_items

### block_p0396_b008

A/B 方案每个关键决策至少两个方案

### block_p0396_b009

推荐理由reasoning_summary 不为空

### block_p0396_b010

任务草案generated_tasks 可转成正式任务

### block_p0396_b011

次日重点可生成next_day_focus 或部门调整建议

### block_p0396_b012

18.7.3Dream 运行验收

### block_p0396_b013

验收项通过标准

### block_p0396_b014

定时运行能按时间或手动触发

### block_p0396_b015

输出结构输出能映射到schema_v1_executive

### block_p0396_b016

来源引用每个高风险和决策项有来源Summary

### block_p0396_b017

幂等同一运行窗口不重复生成同一决策

### block_p0396_b018

失败记录运行失败有错误记录

### block_p0396_b019

降级策略失败时可生成简版摘要或转发上推事项

### block_p0396_b020

审计运行成功、失败、重试都有记录

### block_p0396_b021

不通过情况包括：

### block_p0396_b022

1. Dream 输出无法解析。

### block_p0396_b023

2. Dream 编造不存在的数据。

### block_p0396_b024

3. Dream 不引用来源Summary。

### block_p0396_b025

4. Dream 每次运行都生成重复决策。

### block_p0396_b026

5. Dream 失败没有记录。

### block_p0396_b027

6. Dream 直接绕过老板确认生成重大任务。

### block_p0396_b028

18.8任务闭环验收标准

### block_p0396_b029

任务闭环证明系统不只是汇总信息，而是能推动执行。

### block_p0396_b030

MVP 阶段必须跑通：

### block_p0396_b031

老板确认

### block_p0396_b032

→任务生成

### block_p0396_b033

→任务分配

### block_p0396_b034

→Staff Agent 展示

### block_p0396_b035

→员工更新状态

### block_p0396_b036

→任务结果回流

### block_p0396_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0396_b038

AutoMage-2-MVP 架构设计文档·杨卓396

### block_p0396_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 396

## 表格

无。

## 备注

无。

<!-- 来自 page_0396.md 全文结束 -->

<!-- 来自 page_0397.md 全文开始 -->

# Page 0397

## 原始文本块

### block_p0397_b001

2026 年5 月3 日

### block_p0397_b002

18.8.1任务生成验收

### block_p0397_b003

验收项通过标准

### block_p0397_b004

来源明确每个任务有source_type 和source_id

### block_p0397_b005

决策任务老板确认后才能创建

### block_p0397_b006

任务字段标题、描述、负责人、优先级、截止时间完整

### block_p0397_b007

任务写库写入tasks

### block_p0397_b008

任务分配写入task_assignments

### block_p0397_b009

任务动态创建时写入task_updates

### block_p0397_b010

幂等同一决策不重复生成任务

### block_p0397_b011

18.8.2任务分配验收

### block_p0397_b012

验收项通过标准

### block_p0397_b013

明确执行人有assignee_user_id 时直接分配

### block_p0397_b014

角色任务只有角色时先给Manager 分配

### block_p0397_b015

跨部门任务可由多个Manager 承接

### block_p0397_b016

权限校验不能把任务分配给无关组织或部门

### block_p0397_b017

分配失败任务进入待分配状态或返回明确错误

### block_p0397_b018

18.8.3任务状态验收

### block_p0397_b019

任务至少支持以下状态：

### block_p0397_b020

状态通过标准

### block_p0397_b021

pending任务已创建但未开始

### block_p0397_b022

in_progress员工开始处理

### block_p0397_b023

blocked员工说明阻塞原因

### block_p0397_b024

completed员工提交完成结果

### block_p0397_b025

closed确认方关闭任务

### block_p0397_b026

cancelled任务被取消并记录原因

### block_p0397_b027

状态变化必须写入task_updates，关键动作写入audit_logs。

### block_p0397_b028

18.8.4Staff Agent 任务交互验收

### block_p0397_b029

验收项通过标准

### block_p0397_b030

查询任务Staff Agent 能获取本人任务

### block_p0397_b031

展示任务展示标题、来源、优先级、截止时间

### block_p0397_b032

开始任务员工可将任务改为进行中

### block_p0397_b033

标记阻塞员工可说明阻塞原因

### block_p0397_b034

提交完成员工可提交结果摘要和产出物

### block_p0397_b035

回流日报当日任务状态可进入Staff Schema

### block_p0397_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0397_b037

AutoMage-2-MVP 架构设计文档·杨卓397

### block_p0397_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 397

## 表格

无。

## 备注

无。

<!-- 来自 page_0397.md 全文结束 -->

<!-- 来自 page_0398.md 全文开始 -->

# Page 0398

## 原始文本块

### block_p0398_b001

2026 年5 月3 日

### block_p0398_b002

不通过情况包括：

### block_p0398_b003

1. 任务没有来源。

### block_p0398_b004

2. 老板未确认就生成任务。

### block_p0398_b005

3. 员工看不到自己的任务。

### block_p0398_b006

4. 任务完成没有结果摘要。

### block_p0398_b007

5. 任务状态变化没有记录。

### block_p0398_b008

6. 重复点击老板确认生成重复任务。

### block_p0398_b009

18.9异常处理验收标准

### block_p0398_b010

异常处理机制用于证明系统能识别阻塞和风险，而不是只记录顺利完成的事项。

### block_p0398_b011

18.9.1异常识别验收

### block_p0398_b012

异常来源通过标准

### block_p0398_b013

Staff 日报能从need_support、blocked、高风险字段识别异常

### block_p0398_b014

Manager 汇总能合并多个Staff 异常

### block_p0398_b015

Task任务逾期或阻塞能生成异常

### block_p0398_b016

Dream组织级风险能生成异常或决策项

### block_p0398_b017

系统规则Schema 校验失败、推送失败、接口失败能记录异常

### block_p0398_b018

18.9.2异常字段验收

### block_p0398_b019

Incident 至少包含：

### block_p0398_b020

1. incident_title

### block_p0398_b021

2. description

### block_p0398_b022

3. incident_type

### block_p0398_b023

4. severity

### block_p0398_b024

5. status

### block_p0398_b025

6. source_type

### block_p0398_b026

7. source_id

### block_p0398_b027

8. reporter_user_id

### block_p0398_b028

9. owner_user_id

### block_p0398_b029

10. need_escalation

### block_p0398_b030 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0398_b031

AutoMage-2-MVP 架构设计文档·杨卓398

### block_p0398_b032 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 398

## 表格

无。

## 备注

无。

<!-- 来自 page_0398.md 全文结束 -->

<!-- 来自 page_0399.md 全文开始 -->

# Page 0399

## 原始文本块

### block_p0399_b001

2026 年5 月3 日

### block_p0399_b002

18.9.3异常流转验收

### block_p0399_b003

异常至少支持以下流转：

### block_p0399_b004

open

### block_p0399_b005

→assigned

### block_p0399_b006

→in_progress

### block_p0399_b007

→resolved

### block_p0399_b008

→closed

### block_p0399_b009

涉及老板决策的异常可进入：

### block_p0399_b010

waiting_decision

### block_p0399_b011

异常处理必须满足：

### block_p0399_b012

验收项通过标准

### block_p0399_b013

创建Staff / Manager / 系统规则能创建异常

### block_p0399_b014

分级异常有low / medium / high / critical

### block_p0399_b015

分配异常能指定负责人

### block_p0399_b016

上推high 或critical 可上推Executive

### block_p0399_b017

生成任务需要处理的异常可生成任务

### block_p0399_b018

关闭关闭必须有原因和确认人

### block_p0399_b019

重新打开问题复现时可reopened

### block_p0399_b020

审计状态变化写入审计

### block_p0399_b021

18.9.4异常与任务关系验收

### block_p0399_b022

验收项通过标准

### block_p0399_b023

异常生成任务一个异常可生成一个或多个任务

### block_p0399_b024

任务关联异常任务能追溯到异常

### block_p0399_b025

任务阻塞反向异常任务blocked 可生成或更新异常

### block_p0399_b026

异常关闭依赖任务关联任务未完成时，不应直接关闭异常

### block_p0399_b027

多来源合并多个Staff 问题可合并为一个部门异常

### block_p0399_b028

不通过情况包括：

### block_p0399_b029

1. 员工标记阻塞后Manager 看不到。

### block_p0399_b030

2. 异常没有来源。

### block_p0399_b031

3. 异常只创建不处理。

### block_p0399_b032

4. 异常生成任务后无法追踪。

### block_p0399_b033

5. 任务未完成但异常已关闭。

### block_p0399_b034

6. critical 异常没有上推和审计。

### block_p0399_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0399_b036

AutoMage-2-MVP 架构设计文档·杨卓399

### block_p0399_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 399

## 表格

无。

## 备注

无。

<!-- 来自 page_0399.md 全文结束 -->

<!-- 来自 page_0400.md 全文开始 -->

# Page 0400

## 原始文本块

### block_p0400_b001

2026 年5 月3 日

### block_p0400_b002

18.10演示验收标准

### block_p0400_b003

演示验收是最终验收。它不要求所有边缘能力完美，但必须证明主链路真实可用。

### block_p0400_b004

MVP Demo 必须完整跑通以下12 步：

### block_p0400_b005

Step 1：Staff Agent 初始化

### block_p0400_b006

Step 2：员工提交每日工作Schema

### block_p0400_b007

Step 3：Staff Schema 写入数据库

### block_p0400_b008

Step 4：Manager Agent 定时读取部门数据

### block_p0400_b009

Step 5：Manager 生成部门汇总Schema

### block_p0400_b010

Step 6：Executive Agent 读取部门汇总

### block_p0400_b011

Step 7：Dream 生成老板决策项

### block_p0400_b012

Step 8：IM 推送老板决策卡片

### block_p0400_b013

Step 9：老板选择方案

### block_p0400_b014

Step 10：系统自动生成任务

### block_p0400_b015

Step 11：任务下发到Staff Agent

### block_p0400_b016

Step 12：员工查询今日任务

### block_p0400_b017

18.10.1Demo 主链路验收

### block_p0400_b018

步骤成功标准

### block_p0400_b019

Staff 初始化返回用户、部门、Agent 节点和权限

### block_p0400_b020

员工填报自然语言被整理成Staff Schema

### block_p0400_b021

员工确认Staff 日报有签名信息

### block_p0400_b022

日报写库work_records 和work_record_items 有记录

### block_p0400_b023

Manager 读取能读取本部门Staff 数据

### block_p0400_b024

Manager 汇总summaries 有部门汇总

### block_p0400_b025

来源追溯summary_source_links 指向Staff 日报

### block_p0400_b026

Executive 读取能读取Manager Summary

### block_p0400_b027

Dream 输出能生成老板决策项

### block_p0400_b028

IM 卡片老板能看到A/B 方案

### block_p0400_b029

老板确认决策状态变为confirmed

### block_p0400_b030

任务生成tasks 和task_assignments 有记录

### block_p0400_b031

Staff 查询员工能看到下发任务

### block_p0400_b032

18.10.2Demo 数据追溯验收

### block_p0400_b033

Demo 最后必须能展示一条完整链路：

### block_p0400_b034

任务9001

### block_p0400_b035

→来源于老板决策decision_0001

### block_p0400_b036

→来源于Manager Summary 801

### block_p0400_b037

→来源于Staff Work Record 301

### block_p0400_b038

→来源于员工杨卓确认提交的Staff Schema

### block_p0400_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0400_b040

AutoMage-2-MVP 架构设计文档·杨卓400

### block_p0400_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 400

## 表格

无。

## 备注

无。

<!-- 来自 page_0400.md 全文结束 -->

<!-- 来自 page_0401.md 全文开始 -->

# Page 0401

## 原始文本块

### block_p0401_b001

2026 年5 月3 日

### block_p0401_b002

这条链路是MVP 的核心验收点。如果追溯链断了，说明系统只是“生成了内容”，还没

### block_p0401_b003

有形成可信组织数据闭环。

### block_p0401_b004

18.10.3Demo 签名与审计验收

### block_p0401_b005

至少要展示以下确认和审计：

### block_p0401_b006

动作验收标准

### block_p0401_b007

员工确认日报有signed_by、signed_at、payload_hash

### block_p0401_b008

Manager 确认汇总有确认状态或签名记录

### block_p0401_b009

老板确认决策有确认人、确认时间、确认方案

### block_p0401_b010

任务生成有审计日志

### block_p0401_b011

权限校验越权操作会被拒绝

### block_p0401_b012

幂等重放重复确认不会重复生成任务

### block_p0401_b013

18.10.4Demo 失败判定

### block_p0401_b014

出现以下任一情况，应判定Demo 未通过：

### block_p0401_b015

1. 员工日报没有真实写库。

### block_p0401_b016

2. Manager 汇总无法追溯Staff 日报。

### block_p0401_b017

3. 老板决策没有A/B 方案。

### block_p0401_b018

4. 老板未确认就生成正式任务。

### block_p0401_b019

5. 老板重复确认生成重复任务。

### block_p0401_b020

6. Staff Agent 看不到下发任务。

### block_p0401_b021

7. 关键动作没有审计记录。

### block_p0401_b022

8. Staff 能读取他人日报。

### block_p0401_b023

9. Manager 能越权读取其他部门明细。

### block_p0401_b024

10. 任务无法追溯来源决策。

### block_p0401_b025

18.10.5Demo 最终通过标准

### block_p0401_b026

MVP Demo 最终通过标准可以写成一句话：

### block_p0401_b027

系统能从员工确认的Staff 日报出发，经Manager 汇总、Dream 分析、老板确认，

### block_p0401_b028

生成正式任务并下发给执行人；同时全链路具备来源追溯、权限校验、签名确认、幂等控制和审计记录。,→

### block_p0401_b029

只要达到这个标准，AutoMage-2 MVP 就可以认为完成了第一阶段核心闭环。

### block_p0401_b030 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0401_b031

AutoMage-2-MVP 架构设计文档·杨卓401

### block_p0401_b032 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 401

## 表格

无。

## 备注

无。

<!-- 来自 page_0401.md 全文结束 -->

<!-- 来自 page_0402.md 全文开始 -->

# Page 0402

## 原始文本块

### block_p0402_b001

2026 年5 月3 日

### block_p0402_b002

18.11本章小结

### block_p0402_b003

MVP 验收不应只看“功能有没有页面”，而应看AutoMage-2 的组织闭环是否成立。

### block_p0402_b004

本阶段最重要的验收结果是：

### block_p0402_b005

Schema 能稳定表达业务；

### block_p0402_b006

Agent 能按边界生成和读取数据；

### block_p0402_b007

API 能校验、写库、返回错误；

### block_p0402_b008

数据库能支撑来源追溯；

### block_p0402_b009

权限能阻止越权访问；

### block_p0402_b010

决策能从下级上推到老板；

### block_p0402_b011

Dream 能生成老板可判断的决策项；

### block_p0402_b012

任务能在确认后下发并回流；

### block_p0402_b013

异常能被发现、处理和关闭；

### block_p0402_b014

Demo 能完整跑通主链路。

### block_p0402_b015

MVP 通过后，系统应具备一条最小但完整的运行链路：

### block_p0402_b016

员工事实

### block_p0402_b017

→部门判断

### block_p0402_b018

→老板决策

### block_p0402_b019

→任务执行

### block_p0402_b020

→异常处理

### block_p0402_b021

→审计复盘

### block_p0402_b022

这条链路跑通，才说明AutoMage-2 不只是一个日报生成器，而是具备了企业级AI 中枢

### block_p0402_b023

的基础形态。

### block_p0402_b024 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0402_b025

AutoMage-2-MVP 架构设计文档·杨卓402

### block_p0402_b026 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 402

## 表格

无。

## 备注

无。

<!-- 来自 page_0402.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

