# MVP 系统总架构

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P040-P056
> 对应页面文件：`01_PAGES/page_0040.md` — `01_PAGES/page_0056.md`

## 原文整理

<!-- 来自 page_0040.md 全文开始 -->

# Page 0040

## 原始文本块

### block_p0040_b001

2026 年5 月3 日

### block_p0040_b002

2MVP 系统总架构

### block_p0040_b003

AutoMage-2 MVP 采用「三级Agent + Schema 契约+ 数据库中转+ 人工确认」的系

### block_p0040_b004

统架构。整体设计目标不是一次性替代企业现有所有管理系统，而是先跑通一条最小但完整

### block_p0040_b005

的组织数据闭环：一线员工提交工作数据，部门节点汇总判断，老板节点接收决策项，决策确

### block_p0040_b006

认后反向生成任务并下发到执行层。

### block_p0040_b007

MVP 阶段的系统重点不在于界面完整度，而在于验证以下几个关键问题：

### block_p0040_b008

1. 一线员工的日常工作能否被稳定转化为结构化Schema。

### block_p0040_b009

2. 中层节点能否基于下属数据形成部门级汇总和风险判断。

### block_p0040_b010

3. 老板节点能否收到真正需要决策的事项，而不是大量原始信息。

### block_p0040_b011

4. 老板确认后的结果能否被拆解为任务并下发到具体执行人。

### block_p0040_b012

5. 全链路数据能否被记录、校验、追踪和复盘。

### block_p0040_b013

因此，本章主要定义AutoMage-2 MVP 的总体架构、数据流转、模块边界、角色交互关

### block_p0040_b014

系和推荐技术路径。

### block_p0040_b015

2.1三层Agent 架构总览

### block_p0040_b016

AutoMage-2 MVP 的核心架构是三级Agent：

### block_p0040_b017

Executive Agent

### block_p0040_b018

老板决策与战略拆解节点

### block_p0040_b019

↑

### block_p0040_b020

￿读取部门汇总、生成决策项、下发任务

### block_p0040_b021

￿

### block_p0040_b022

Manager Agent

### block_p0040_b023

部门汇总与边界决策节点

### block_p0040_b024

↑

### block_p0040_b025

￿读取员工日报、生成部门态势、处理异常

### block_p0040_b026

￿

### block_p0040_b027

Staff Agent

### block_p0040_b028

岗位执行节点

### block_p0040_b029

这三级Agent 分别对应企业组织中的三个关键层级：

### block_p0040_b030

层级Agent 类型对应组织角色主要职责

### block_p0040_b031

L1Staff Agent一线员工记录工作、提交日报、接收任务、反馈执行结果

### block_p0040_b032

L2Manager Agent部门负责人/ 中层管理

### block_p0040_b033

者

### block_p0040_b034

汇总部门数据、识别风险、处理边界事项、上推决

### block_p0040_b035

策

### block_p0040_b036

L3Executive Agent老板/ 高管获取组织态势、确认关键决策、拆解战略任务

### block_p0040_b037

这套架构与传统「一个AI 中枢统一处理所有信息」的方式不同。AutoMage-2 不要求单

### block_p0040_b038

个中心模型直接读取和理解所有企业数据，而是让不同层级的Agent 在各自权限范围内处理

### block_p0040_b039

对应层级的数据。下级节点负责产出结构化数据，上级节点负责读取、汇总和判断。

### block_p0040_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0040_b041

AutoMage-2-MVP 架构设计文档·杨卓40

### block_p0040_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 40

## 表格

无。

## 备注

无。

<!-- 来自 page_0040.md 全文结束 -->

<!-- 来自 page_0041.md 全文开始 -->

# Page 0041

## 原始文本块

### block_p0041_b001

2026 年5 月3 日

### block_p0041_b002

这样做有三个好处：

### block_p0041_b003

第一，降低系统复杂度。基层数据先在基层节点被整理，部门数据先在部门节点被汇总，

### block_p0041_b004

老板侧只接收经过筛选的关键事项。

### block_p0041_b005

第二，降低组织阻力。中层管理者不是被系统直接替代，而是从「传话者」转为「异常处

### block_p0041_b006

理者」和「部门决策节点」。

### block_p0041_b007

第三，降低信任风险。关键决策不由AI 自动拍板，而是由Agent 生成选项和建议，再交

### block_p0041_b008

给人类确认。

### block_p0041_b009

2.1.1Staff Agent：岗位执行节点

### block_p0041_b010

Staff Agent 是一线员工对应的岗位级Agent。它的定位是员工的「工作记录助手」和「任

### block_p0041_b011

务接收助手」，负责把员工每天的工作过程转化为标准Staff Schema。

### block_p0041_b012

Staff Agent 的主要职责包括：

### block_p0041_b013

1. 通过IM 或其他入口提醒员工填写每日工作记录。

### block_p0041_b014

2. 引导员工补充今日完成事项、遇到的问题、解决尝试、明日计划和产出物。

### block_p0041_b015

3. 将员工输入的自然语言内容整理成标准Staff Schema。

### block_p0041_b016

4. 在提交前向员工展示结构化结果，并要求员工确认。

### block_p0041_b017

5. 调用后端接口提交日报数据。

### block_p0041_b018

6. 查询上级下发给该员工的任务。

### block_p0041_b019

7. 当员工遇到阻塞时，生成异常或支持请求。

### block_p0041_b020

8. 将任务执行结果继续沉淀为新的工作记录。

### block_p0041_b021

Staff Agent 的权限边界必须严格控制：

### block_p0041_b022

可做不可做

### block_p0041_b023

提交本人日报读取他人日报

### block_p0041_b024

查询本人任务查询部门整体数据

### block_p0041_b025

上报本人问题代表其他员工提交数据

### block_p0041_b026

接收上级任务自动做出部门级或老板级决策

### block_p0041_b027

辅助整理员工输入编造员工未确认的工作内容

### block_p0041_b028

Staff Agent 的核心价值不是「帮员工写好看日报」，而是把员工真实工作过程转化为系统

### block_p0041_b029

可读取、可汇总、可追踪的数据。

### block_p0041_b030

2.1.2Manager Agent：部门汇总与边界决策节点

### block_p0041_b031

Manager Agent 是部门负责人或中层管理者对应的管理级Agent。它的定位是部门数据

### block_p0041_b032

的汇总节点和边界决策节点。

### block_p0041_b033

Manager Agent 的主要职责包括：

### block_p0041_b034

1. 定时读取本部门员工提交的Staff Schema。

### block_p0041_b035

2. 汇总部门每日工作进展。

### block_p0041_b036

3. 识别部门风险、阻塞事项和资源缺口。

### block_p0041_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0041_b038

AutoMage-2-MVP 架构设计文档·杨卓41

### block_p0041_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 41

## 表格

无。

## 备注

无。

<!-- 来自 page_0041.md 全文结束 -->

<!-- 来自 page_0042.md 全文开始 -->

# Page 0042

## 原始文本块

### block_p0042_b001

2026 年5 月3 日

### block_p0042_b002

4. 标记表现突出员工、关键产出和异常事项。

### block_p0042_b003

5. 判断哪些问题可以在部门内解决。

### block_p0042_b004

6. 将超出权限的事项整理为待上推决策。

### block_p0042_b005

7. 接收老板确认后的任务，并拆解到具体员工或小组。

### block_p0042_b006

8. 生成部门级Manager Schema，供Executive Agent 读取。

### block_p0042_b007

Manager Agent 的权限边界如下：

### block_p0042_b008

可做不可做

### block_p0042_b009

读取本部门Staff Schema读取其他部门员工明细

### block_p0042_b010

生成本部门汇总直接修改员工原始日报

### block_p0042_b011

处理部门权限内异常绕过老板处理重大事项

### block_p0042_b012

下发部门级任务伪造员工确认

### block_p0042_b013

上推超权限决策越权查看组织级敏感数据

### block_p0042_b014

Manager Agent 的核心价值在于把中层从「信息中转站」转为「异常处理者」。它不只是

### block_p0042_b015

把员工日报复制给老板，而是要把零散的一线数据整理成部门态势：哪些事正常推进，哪些

### block_p0042_b016

事有风险，哪些人需要支持，哪些事项必须上推。

### block_p0042_b017

2.1.3Executive Agent：老板决策与战略拆解节点

### block_p0042_b018

Executive Agent 是老板或公司高管对应的决策级Agent。它的定位是老板的信息过滤器、

### block_p0042_b019

决策整理器和任务拆解器。

### block_p0042_b020

Executive Agent 的主要职责包括：

### block_p0042_b021

1. 定时读取各部门Manager Schema。

### block_p0042_b022

2. 生成组织级业务摘要。

### block_p0042_b023

3. 识别跨部门风险、资源冲突和关键阻塞。

### block_p0042_b024

4. 将复杂问题整理成老板可判断的决策项。

### block_p0042_b025

5. 为每个决策项生成候选方案、推荐方案和影响分析。

### block_p0042_b026

6. 通过IM 或老板侧前端推送决策卡片。

### block_p0042_b027

7. 接收老板确认结果。

### block_p0042_b028

8. 根据确认结果生成任务，并下发给Manager Agent 或Staff Agent。

### block_p0042_b029

9. 记录决策来源、确认人、确认时间和后续任务。

### block_p0042_b030

Executive Agent 的权限边界如下：

### block_p0042_b031

可做不可做

### block_p0042_b032

读取组织级汇总数据随意读取未授权隐私数据

### block_p0042_b033

生成老板决策项绕过老板执行重大决策

### block_p0042_b034

推荐A/B 方案自动批准重大资源调整

### block_p0042_b035

生成任务拆解草案删除原始业务记录

### block_p0042_b036

跟踪决策执行结果篡改历史决策依据

### block_p0042_b037

Executive Agent 的重点不是生成长篇报告，而是把老板真正需要处理的问题变成选择题。

### block_p0042_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0042_b039

AutoMage-2-MVP 架构设计文档·杨卓42

### block_p0042_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 42

## 表格

无。

## 备注

无。

<!-- 来自 page_0042.md 全文结束 -->

<!-- 来自 page_0043.md 全文开始 -->

# Page 0043

## 原始文本块

### block_p0043_b001

2026 年5 月3 日

### block_p0043_b002

老板不需要从大量日报里自己找问题，而是直接看到「需要我决定什么、有哪些方案、推荐

### block_p0043_b003

哪个、确认后会产生哪些任务」。

### block_p0043_b004

2.2数据流转总览

### block_p0043_b005

AutoMage-2 MVP 的数据流转分为两条主线：

### block_p0043_b006

第一条是自下而上的数据汇总链路，用于让老板看到真实的一线情况。

### block_p0043_b007

第二条是自上而下的任务下发链路，用于让老板确认后的决策回到具体执行人。

### block_p0043_b008

完整链路如下：

### block_p0043_b009

一线员工

### block_p0043_b010

↓

### block_p0043_b011

Staff Agent

### block_p0043_b012

↓

### block_p0043_b013

Staff Schema

### block_p0043_b014

↓

### block_p0043_b015

数据库

### block_p0043_b016

↓

### block_p0043_b017

Manager Agent

### block_p0043_b018

↓

### block_p0043_b019

部门汇总Schema

### block_p0043_b020

↓

### block_p0043_b021

Executive Agent

### block_p0043_b022

↓

### block_p0043_b023

Dream 决策

### block_p0043_b024

↓

### block_p0043_b025

老板确认

### block_p0043_b026

↓

### block_p0043_b027

任务下发

### block_p0043_b028

↓

### block_p0043_b029

Staff Agent 获取每日任务

### block_p0043_b030

↓

### block_p0043_b031

员工执行并形成新的工作记录

### block_p0043_b032

这个流程中，数据库是核心中转层。Agent 之间不依赖长连接互相通信，也不把IM 聊天

### block_p0043_b033

记录作为事实源。所有关键业务数据必须经过后端校验后写入数据库，再由上级节点按权限

### block_p0043_b034

读取。

### block_p0043_b035

2.2.1一线员工→Staff Schema

### block_p0043_b036

数据流的第一步，是一线员工向Staff Agent 提供每日工作信息。

### block_p0043_b037

MVP 阶段推荐通过IM 触发日报填写。员工不需要打开复杂后台，只需要在IM 中回答

### block_p0043_b038

几个固定问题：

### block_p0043_b039

1. 今天完成了哪些事项？

### block_p0043_b040

2. 哪些事项还在进行中？

### block_p0043_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0043_b042

AutoMage-2-MVP 架构设计文档·杨卓43

### block_p0043_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 43

## 表格

无。

## 备注

无。

<!-- 来自 page_0043.md 全文结束 -->

<!-- 来自 page_0044.md 全文开始 -->

# Page 0044

## 原始文本块

### block_p0044_b001

2026 年5 月3 日

### block_p0044_b002

3. 遇到了什么问题？

### block_p0044_b003

4. 已经尝试过什么解决方式？

### block_p0044_b004

5. 是否需要上级支持？

### block_p0044_b005

6. 明天计划做什么？

### block_p0044_b006

7. 是否有文档、代码、链接或其他产出物？

### block_p0044_b007

Staff Agent 根据员工输入整理出Staff Schema。整理过程中，Staff Agent 需要做三件事：

### block_p0044_b008

第一，结构化。把自然语言拆成标准字段，例如work_progress、issues_faced、

### block_p0044_b009

next_day_plan。

### block_p0044_b010

第二，补全。发现必填字段缺失时，继续追问员工，而不是自行编造。

### block_p0044_b011

第三，确认。提交前必须把整理结果展示给员工，由员工确认后再写入系统。

### block_p0044_b012

该阶段的输出是：

### block_p0044_b013

schema_v1_staff

### block_p0044_b014

这条Staff Schema 是后续部门汇总的原始输入。它必须尽量稳定、清晰、可校验。

### block_p0044_b015

2.2.2Staff Schema →数据库

### block_p0044_b016

Staff Schema 生成后，不直接传给Manager Agent，而是先通过后端API 写入数据库。

### block_p0044_b017

这个环节的职责主要在后端。后端需要完成以下操作：

### block_p0044_b018

1. 校验用户身份。

### block_p0044_b019

2. 校验Agent 身份。

### block_p0044_b020

3. 校验Schema ID 和版本。

### block_p0044_b021

4. 校验必填字段。

### block_p0044_b022

5. 校验字段类型和枚举值。

### block_p0044_b023

6. 校验员工是否属于对应组织和部门。

### block_p0044_b024

7. 校验签名或确认状态。

### block_p0044_b025

8. 判断是否重复提交。

### block_p0044_b026

9. 写入工作记录主表和字段明细表。

### block_p0044_b027

10. 写入审计日志。

### block_p0044_b028

建议映射方式如下：

### block_p0044_b029

Staff Schema 内容数据库对象

### block_p0044_b030

日报主信息work_records

### block_p0044_b031

具体字段明细work_record_items

### block_p0044_b032

文档、代码、链接等产出物artifacts / artifact_links

### block_p0044_b033

需要支持或高风险问题incidents

### block_p0044_b034

可执行后续事项tasks

### block_p0044_b035

提交、确认、修改行为audit_logs

### block_p0044_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0044_b037

AutoMage-2-MVP 架构设计文档·杨卓44

### block_p0044_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 44

## 表格

无。

## 备注

无。

<!-- 来自 page_0044.md 全文结束 -->

<!-- 来自 page_0045.md 全文开始 -->

# Page 0045

## 原始文本块

### block_p0045_b001

2026 年5 月3 日

### block_p0045_b002

数据库写入成功后，Staff Schema 才算正式进入系统。后续Manager Agent 读取的是数

### block_p0045_b003

据库中的正式记录，而不是员工与Staff Agent 的聊天上下文。

### block_p0045_b004

2.2.3Manager Agent →部门汇总Schema

### block_p0045_b005

Manager Agent 定时读取本部门员工当天或指定周期内的Staff Schema，并生成部门汇

### block_p0045_b006

总Schema。

### block_p0045_b007

该环节的输入包括：

### block_p0045_b008

1. 本部门员工Staff Schema。

### block_p0045_b009

2. 本部门未完成任务。

### block_p0045_b010

3. 本部门异常记录。

### block_p0045_b011

4. 历史部门汇总。

### block_p0045_b012

5. 老板此前下发的任务或决策。

### block_p0045_b013

Manager Agent 不应该简单拼接员工日报，而要完成整理和判断：

### block_p0045_b014

处理动作说明

### block_p0045_b015

汇总进展提炼部门当天主要推进事项

### block_p0045_b016

识别风险从员工问题、阻塞、延期中提取关键风险

### block_p0045_b017

识别支持需求判断哪些员工或事项需要部门介入

### block_p0045_b018

识别突出产出标记有价值的工作成果

### block_p0045_b019

判断权限边界区分部门内可处理事项和需要上推事项

### block_p0045_b020

形成次日建议给出部门明日重点调整方向

### block_p0045_b021

该阶段输出的是：

### block_p0045_b022

schema_v1_manager

### block_p0045_b023

Manager Schema 应至少包含部门进展、健康度、风险、阻塞事项、突出员工、待处理事

### block_p0045_b024

项、待上推决策和来源记录。

### block_p0045_b025

Manager Schema 的作用是给Executive Agent 提供更高层级的输入，而不是让老板直接

### block_p0045_b026

读取所有员工日报。

### block_p0045_b027

2.2.4Executive Agent →Dream 决策

### block_p0045_b028

Executive Agent 读取各部门Manager Schema 后，进入Dream 决策流程。

### block_p0045_b029

这里的Dream 不一定在MVP 阶段实现复杂的长期记忆系统，但至少要完成一次组织级

### block_p0045_b030

的定时分析：读取部门汇总，提取关键问题，生成老板需要确认的决策项。

### block_p0045_b031

Dream 决策的输入包括：

### block_p0045_b032

1. 各部门Manager Schema。

### block_p0045_b033

2. 部门风险和异常。

### block_p0045_b034

3. 未完成关键任务。

### block_p0045_b035

4. 历史决策记录。

### block_p0045_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0045_b037

AutoMage-2-MVP 架构设计文档·杨卓45

### block_p0045_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 45

## 表格

无。

## 备注

无。

<!-- 来自 page_0045.md 全文结束 -->

<!-- 来自 page_0046.md 全文开始 -->

# Page 0046

## 原始文本块

### block_p0046_b001

2026 年5 月3 日

### block_p0046_b002

5. 老板近期目标或策略。

### block_p0046_b003

6. 必要的外部输入。

### block_p0046_b004

Dream 决策的输出包括：

### block_p0046_b005

1. 今日组织级摘要。

### block_p0046_b006

2. 当前最重要的风险。

### block_p0046_b007

3. 需要老板确认的事项。

### block_p0046_b008

4. 每个事项的候选方案。

### block_p0046_b009

5. Agent 推荐方案。

### block_p0046_b010

6. 推荐理由。

### block_p0046_b011

7. 预期影响。

### block_p0046_b012

8. 确认后可生成的任务草案。

### block_p0046_b013

Executive Agent 在这个阶段要特别注意信息密度。老板侧不应收到大量无筛选内容，而

### block_p0046_b014

应收到少量高价值决策项。

### block_p0046_b015

示例输出形态：

### block_p0046_b016

今日需要确认1 项决策：

### block_p0046_b017

事项：是否新增独立decision_logs 表承载老板决策记录。

### block_p0046_b018

方案A：新增独立决策表，审计清晰，后续扩展方便。

### block_p0046_b019

方案B：暂时复用audit_logs + tasks，开发更快，但后续追踪不够清晰。

### block_p0046_b020

推荐：方案A。

### block_p0046_b021

原因：该系统后续核心价值在于决策可追溯，独立决策表更符合长期架构。

### block_p0046_b022

2.2.5老板确认→任务下发

### block_p0046_b023

老板看到Executive Agent 推送的决策项后，需要做确认动作。MVP 阶段可以先通过IM

### block_p0046_b024

按钮、文字回复或简单前端卡片完成确认。

### block_p0046_b025

确认结果通常有几种：

### block_p0046_b026

确认动作系统处理

### block_p0046_b027

选择方案A记录决策，生成对应任务

### block_p0046_b028

选择方案B记录决策，生成另一组任务

### block_p0046_b029

要求补充信息决策状态变为待补充

### block_p0046_b030

驳回决策关闭，不生成任务

### block_p0046_b031

改写方案记录人工修改内容，再生成任务

### block_p0046_b032

老板确认后，系统需要把决策转化为可执行任务。任务不应只停留在「老板已确认」状

### block_p0046_b033

态，而应进入任务系统，并明确：

### block_p0046_b034

1. 任务标题。

### block_p0046_b035

2. 任务说明。

### block_p0046_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0046_b037

AutoMage-2-MVP 架构设计文档·杨卓46

### block_p0046_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 46

## 表格

无。

## 备注

无。

<!-- 来自 page_0046.md 全文结束 -->

<!-- 来自 page_0047.md 全文开始 -->

# Page 0047

## 原始文本块

### block_p0047_b001

2026 年5 月3 日

### block_p0047_b002

3. 负责人。

### block_p0047_b003

4. 所属部门。

### block_p0047_b004

5. 优先级。

### block_p0047_b005

6. 截止时间。

### block_p0047_b006

7. 来源决策。

### block_p0047_b007

8. 确认人。

### block_p0047_b008

9. 当前状态。

### block_p0047_b009

任务可以下发给Manager Agent，也可以直接下发给Staff Agent。具体取决于任务粒度：

### block_p0047_b010

任务类型下发对象

### block_p0047_b011

部门级调整Manager Agent

### block_p0047_b012

具体执行事项Staff Agent

### block_p0047_b013

跨部门事项多个Manager Agent

### block_p0047_b014

需要继续拆解的事项Manager Agent 先接收，再拆给Staff

### block_p0047_b015

这个阶段是决策闭环的关键。没有任务下发，Executive Agent 生成的决策项只是一份报

### block_p0047_b016

告；有了任务下发，老板决策才进入执行链路。

### block_p0047_b017

2.2.6Staff Agent →获取每日任务

### block_p0047_b018

任务生成后，Staff Agent 需要在合适时间读取员工自己的待执行任务，并推送给员工。

### block_p0047_b019

典型触发时间包括：

### block_p0047_b020

1. 每天早上上班前。

### block_p0047_b021

2. 老板或Manager 下发任务后。

### block_p0047_b022

3. 任务截止前。

### block_p0047_b023

4. 任务状态发生变化时。

### block_p0047_b024

5. 员工主动查询时。

### block_p0047_b025

Staff Agent 获取任务时，只能读取当前员工相关任务，不能读取其他员工或整个部门任

### block_p0047_b026

务。

### block_p0047_b027

任务展示内容应简洁明确：

### block_p0047_b028

今日待执行任务：

### block_p0047_b029

1. 完成decision_logs 表结构设计初稿

### block_p0047_b030

优先级：高

### block_p0047_b031

截止时间：今日18:00

### block_p0047_b032

来源：老板确认的“决策记录表设计方案A”

### block_p0047_b033

2. 补充Manager Schema 与Summary 表映射说明

### block_p0047_b034

优先级：中

### block_p0047_b035

截止时间：明日12:00

### block_p0047_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0047_b037

AutoMage-2-MVP 架构设计文档·杨卓47

### block_p0047_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 47

## 表格

无。

## 备注

无。

<!-- 来自 page_0047.md 全文结束 -->

<!-- 来自 page_0048.md 全文开始 -->

# Page 0048

## 原始文本块

### block_p0048_b001

2026 年5 月3 日

### block_p0048_b002

员工执行后，Staff Agent 应在当天日报中引导员工反馈这些任务的完成情况。这样任务

### block_p0048_b003

执行结果会重新进入Staff Schema，形成新的数据输入。

### block_p0048_b004

2.3MVP 核心链路图

### block_p0048_b005

MVP 阶段只验证一条主链路：日报提交、部门汇总、老板决策、任务下发、员工执行反

### block_p0048_b006

馈。

### block_p0048_b007

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿1. 员工通过IM 填写日报￿

### block_p0048_b008

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b009

↓

### block_p0048_b010

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b011

￿2. Staff Agent 整理输入￿

### block_p0048_b012

￿生成Staff Schema￿

### block_p0048_b013

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b014

↓

### block_p0048_b015

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b016

￿3. 后端校验Schema￿

### block_p0048_b017

￿鉴权/ 签名/ 写库￿

### block_p0048_b018

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b019

↓

### block_p0048_b020

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b021

￿4. 数据库保存工作记录￿

### block_p0048_b022

￿Work Record￿

### block_p0048_b023

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b024

↓

### block_p0048_b025

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b026

￿5. Manager Agent 读取￿

### block_p0048_b027

￿本部门员工数据￿

### block_p0048_b028

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b029

↓

### block_p0048_b030

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b031

￿6. 生成部门汇总Schema ￿

### block_p0048_b032

￿进展/ 风险/ 待决策￿

### block_p0048_b033

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b034

↓

### block_p0048_b035

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b036

￿7. Executive Agent 读取￿

### block_p0048_b037

￿各部门汇总数据￿

### block_p0048_b038

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b039

↓

### block_p0048_b040

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b041

￿8. Dream 生成决策项￿

### block_p0048_b042

￿A/B 方案/ 推荐理由￿

### block_p0048_b043

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b044

↓

### block_p0048_b045

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b046

￿9. 老板确认方案￿

### block_p0048_b047

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b048

↓

### block_p0048_b049

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b050

￿10. 系统生成任务￿

### block_p0048_b051

￿分配到部门或员工￿

### block_p0048_b052

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b053

↓

### block_p0048_b054

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0048_b055 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0048_b056

AutoMage-2-MVP 架构设计文档·杨卓48

### block_p0048_b057 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 48

## 表格

无。

## 备注

无。

<!-- 来自 page_0048.md 全文结束 -->

<!-- 来自 page_0049.md 全文开始 -->

# Page 0049

## 原始文本块

### block_p0049_b001

2026 年5 月3 日

### block_p0049_b002

￿11. Staff Agent 获取任务￿

### block_p0049_b003

￿员工执行并反馈￿

### block_p0049_b004

￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿￿

### block_p0049_b005

该链路的验收重点如下：

### block_p0049_b006

1. Staff Schema 能否稳定生成。

### block_p0049_b007

2. 后端能否完成校验和写库。

### block_p0049_b008

3. Manager Agent 能否读取本部门数据。

### block_p0049_b009

4. Manager Agent 能否生成有效部门汇总。

### block_p0049_b010

5. Executive Agent 能否生成老板可确认的决策项。

### block_p0049_b011

6. 老板确认动作能否被记录。

### block_p0049_b012

7. 任务能否被生成并分配。

### block_p0049_b013

8. Staff Agent 能否读取员工任务。

### block_p0049_b014

9. 任务结果能否在下一次日报中继续沉淀。

### block_p0049_b015

MVP 阶段所有功能开发都应围绕这条链路展开。与该链路无关的复杂功能，可以暂缓。

### block_p0049_b016

2.4系统模块边界

### block_p0049_b017

AutoMage-2 MVP 主要由六个模块组成：

### block_p0049_b018

1. IM 交互层。

### block_p0049_b019

2. Agent 层。

### block_p0049_b020

3. API 层。

### block_p0049_b021

4. 数据库层。

### block_p0049_b022

5. Dream 决策层。

### block_p0049_b023

6. 管理展示层。

### block_p0049_b024

各模块边界如下：

### block_p0049_b025

模块主要职责不负责的内容

### block_p0049_b026

IM 交互层触发填报、展示消息、接收确认、推送任务不保存最终事实数据，不做复杂权限判

### block_p0049_b027

断

### block_p0049_b028

Agent 层理解输入、生成Schema、读取数据、汇总分

### block_p0049_b029

析、生成建议

### block_p0049_b030

不直接改数据库，不越权读写，不伪造人

### block_p0049_b031

工确认

### block_p0049_b032

API 层鉴权、Schema 校验、权限判断、写库、状态

### block_p0049_b033

流转、错误返回

### block_p0049_b034

不负责自然语言理解，不替代Agent 推

### block_p0049_b035

理

### block_p0049_b036

数据库层保存组织、用户、日报、任务、异常、汇总、

### block_p0049_b037

审计等事实数据

### block_p0049_b038

不生成业务判断，不做Agent 推理

### block_p0049_b039

Dream 决策层定时分析部门汇总，生成老板侧摘要和决策

### block_p0049_b040

项

### block_p0049_b041

不绕过老板自动执行重大决策

### block_p0049_b042

管理展示层展示老板决策、部门汇总、任务和风险MVP 阶段非强依赖，可先由IM 承载

### block_p0049_b043

需要强调的是，Agent 不是事实源，IM 也不是事实源。员工在IM 中说过的话，只有经

### block_p0049_b044

过Agent 整理、员工确认、后端校验并写入数据库后，才成为正式业务数据。

### block_p0049_b045 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0049_b046

AutoMage-2-MVP 架构设计文档·杨卓49

### block_p0049_b047 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 49

## 表格

无。

## 备注

无。

<!-- 来自 page_0049.md 全文结束 -->

<!-- 来自 page_0050.md 全文开始 -->

# Page 0050

## 原始文本块

### block_p0050_b001

2026 年5 月3 日

### block_p0050_b002

系统边界可以概括为：

### block_p0050_b003

IM：负责交互

### block_p0050_b004

Agent：负责整理和生成

### block_p0050_b005

API：负责校验和控制

### block_p0050_b006

数据库：负责保存事实

### block_p0050_b007

Dream：负责分析和建议

### block_p0050_b008

管理展示层：负责呈现结果

### block_p0050_b009

2.5角色与系统交互关系

### block_p0050_b010

MVP 阶段主要涉及四类用户角色和两类系统角色。

### block_p0050_b011

角色入口主要动作主要看到的数据

### block_p0050_b012

一线员工IM / Staff Agent填写日报、确认提交、接收任

### block_p0050_b013

务、反馈问题

### block_p0050_b014

自己的日报、自己的任务

### block_p0050_b015

部门负责人IM / Manager Agent查看部门汇总、处理异常、上

### block_p0050_b016

推事项、拆解任务

### block_p0050_b017

本部门汇总、本部门风险、本部门任务

### block_p0050_b018

老板/ 高管IM / Executive Agent

### block_p0050_b019

/ 看板

### block_p0050_b020

查看组织摘要、确认决策、查

### block_p0050_b021

看执行结果

### block_p0050_b022

部门汇总、关键风险、决策项、任务结

### block_p0050_b023

果

### block_p0050_b024

管理员后台/ 配置系统配置组织、用户、部门、权限、

### block_p0050_b025

Agent 模板

### block_p0050_b026

组织结构、用户权限、系统运行状态

### block_p0050_b027

Agent 系统Agent Runtime生成Schema、汇总数据、调

### block_p0050_b028

用API、推送消息

### block_p0050_b029

权限范围内的结构化数据

### block_p0050_b030

后端系统API / DB鉴权、校验、写库、审计、状

### block_p0050_b031

态流转

### block_p0050_b032

全部授权业务数据

### block_p0050_b033

典型交互关系如下：

### block_p0050_b034

一线员工交互

### block_p0050_b035

Staff Agent：请填写今日工作记录。

### block_p0050_b036

员工：今天完成了Staff Schema，遇到Decision 表未确认的问题，明天继续补Manager Schema。

### block_p0050_b037

Staff Agent：我整理成以下日报，请确认。

### block_p0050_b038

员工：确认提交。

### block_p0050_b039

Staff Agent：已提交，进入部门汇总。

### block_p0050_b040

一线员工侧强调低成本填报，尽量不要求员工学习复杂系统。

### block_p0050_b041

部门负责人交互

### block_p0050_b042

Manager Agent：今日部门8 人提交日报，2 个事项存在阻塞，1 个事项建议上推。

### block_p0050_b043

部门负责人：查看上推事项。

### block_p0050_b044

Manager Agent：事项为“决策记录表结构未确认”，影响老板侧决策链路。

### block_p0050_b045

部门负责人：上推老板确认。

### block_p0050_b046

部门负责人侧强调风险和异常，不需要逐条阅读所有员工日报。

### block_p0050_b047 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0050_b048

AutoMage-2-MVP 架构设计文档·杨卓50

### block_p0050_b049 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 50

## 表格

无。

## 备注

无。

<!-- 来自 page_0050.md 全文结束 -->

<!-- 来自 page_0051.md 全文开始 -->

# Page 0051

## 原始文本块

### block_p0051_b001

2026 年5 月3 日

### block_p0051_b002

老板/ 高管交互

### block_p0051_b003

Executive Agent：今日有1 个关键决策需要确认。

### block_p0051_b004

事项：是否新增独立decision_logs 表。

### block_p0051_b005

方案A：新增独立表，审计清晰。

### block_p0051_b006

方案B：复用audit_logs，开发更快。

### block_p0051_b007

推荐：方案A。

### block_p0051_b008

老板：选择方案A。

### block_p0051_b009

Executive Agent：已确认，将生成任务并下发给后端负责人。

### block_p0051_b010

老板侧强调信息过滤和决策效率，不展示过多一线细节，除非老板主动下钻查看。

### block_p0051_b011

2.6IM、Agent、后端、数据库之间的职责划分

### block_p0051_b012

MVP 阶段必须明确IM、Agent、后端和数据库的职责，否则后续联调会出现数据重复、

### block_p0051_b013

状态不一致和权限失控。

### block_p0051_b014

总体职责划分如下：

### block_p0051_b015

IM 负责触发和展示；

### block_p0051_b016

Agent 负责理解和生成；

### block_p0051_b017

后端负责校验和控制；

### block_p0051_b018

数据库负责保存事实。

### block_p0051_b019

详细划分如下：

### block_p0051_b020

组件负责内容不负责内容

### block_p0051_b021

IM消息提醒、表单入口、按钮确认、任务推送不保存最终业务状态，不承担复杂权限，不

### block_p0051_b022

直接改库

### block_p0051_b023

Agent理解用户输入、整理Schema、生成汇总、提出

### block_p0051_b024

建议、调用API

### block_p0051_b025

不越权读取数据，不伪造确认，不绕过API

### block_p0051_b026

直连数据库

### block_p0051_b027

后端API鉴权、权限校验、Schema 校验、幂等控制、状

### block_p0051_b028

态流转、写库、错误码

### block_p0051_b029

不负责自然语言理解，不生成复杂业务判

### block_p0051_b030

断

### block_p0051_b031

数据库保存事实数据、支持查询、保留审计、记录任务

### block_p0051_b032

和决策状态

### block_p0051_b033

不负责Agent 推理，不直接决定业务动作

### block_p0051_b034

以员工提交日报为例：

### block_p0051_b035

员工在IM 中输入日报

### block_p0051_b036

↓

### block_p0051_b037

IM 将内容传给Staff Agent

### block_p0051_b038

↓

### block_p0051_b039

Staff Agent 整理成Staff Schema

### block_p0051_b040

↓

### block_p0051_b041

员工确认

### block_p0051_b042

↓

### block_p0051_b043

Agent 调用后端API

### block_p0051_b044

↓

### block_p0051_b045

后端校验身份、权限、Schema、签名

### block_p0051_b046

↓

### block_p0051_b047 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0051_b048

AutoMage-2-MVP 架构设计文档·杨卓51

### block_p0051_b049 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 51

## 表格

无。

## 备注

无。

<!-- 来自 page_0051.md 全文结束 -->

<!-- 来自 page_0052.md 全文开始 -->

# Page 0052

## 原始文本块

### block_p0052_b001

2026 年5 月3 日

### block_p0052_b002

数据库写入Work Record

### block_p0052_b003

↓

### block_p0052_b004

审计日志记录提交行为

### block_p0052_b005

以老板确认决策为例：

### block_p0052_b006

Executive Agent 推送决策卡片

### block_p0052_b007

↓

### block_p0052_b008

老板在IM 中点击确认

### block_p0052_b009

↓

### block_p0052_b010

IM 将确认动作传给后端

### block_p0052_b011

↓

### block_p0052_b012

后端记录决策确认

### block_p0052_b013

↓

### block_p0052_b014

系统生成任务

### block_p0052_b015

↓

### block_p0052_b016

任务写入数据库

### block_p0052_b017

↓

### block_p0052_b018

Staff / Manager Agent 读取任务并推送执行人

### block_p0052_b019

这个职责划分需要在实现中保持一致。不能出现以下情况：

### block_p0052_b020

1. Agent 说已经提交，但后端没有记录。

### block_p0052_b021

2. IM 里有确认动作，但数据库没有决策状态。

### block_p0052_b022

3. Manager Agent 读取聊天记录做汇总，而不是读取正式数据库记录。

### block_p0052_b023

4. Staff Agent 能看到其他员工日报。

### block_p0052_b024

5. 老板确认后只生成一段文字，没有生成正式任务。

### block_p0052_b025

2.7MVP 阶段推荐技术路径

### block_p0052_b026

MVP 阶段的技术路径应以「尽快跑通闭环」为第一原则。复杂能力可以后置，先把关键

### block_p0052_b027

链路打通。

### block_p0052_b028

推荐路线如下：

### block_p0052_b029

先IM 表单

### block_p0052_b030

↓

### block_p0052_b031

后屏幕记忆/ 自动采集

### block_p0052_b032

先Mock

### block_p0052_b033

↓

### block_p0052_b034

后真实API

### block_p0052_b035

先通用Schema

### block_p0052_b036

↓

### block_p0052_b037

后行业模板Schema

### block_p0052_b038

这条路径的目标是降低早期开发不确定性。不要一开始就把屏幕自动采集、复杂行业模

### block_p0052_b039

板、老板App、长期记忆和完整权限系统全部放进MVP 主链路。

### block_p0052_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0052_b041

AutoMage-2-MVP 架构设计文档·杨卓52

### block_p0052_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 52

## 表格

无。

## 备注

无。

<!-- 来自 page_0052.md 全文结束 -->

<!-- 来自 page_0053.md 全文开始 -->

# Page 0053

## 原始文本块

### block_p0053_b001

2026 年5 月3 日

### block_p0053_b002

2.7.1先IM 表单

### block_p0053_b003

MVP 阶段建议优先使用IM 表单或IM 问答完成数据采集。

### block_p0053_b004

原因如下：

### block_p0053_b005

1. 开发成本低。

### block_p0053_b006

2. 员工学习成本低。

### block_p0053_b007

3. 字段可控。

### block_p0053_b008

4. 便于快速验证Schema 是否合理。

### block_p0053_b009

5. 不依赖复杂客户端权限。

### block_p0053_b010

6. 更适合两周内跑通MVP 闭环。

### block_p0053_b011

员工侧可以先通过固定问题填报：

### block_p0053_b012

1. 今天完成了什么？

### block_p0053_b013

2. 遇到了什么问题？

### block_p0053_b014

3. 是否需要支持？

### block_p0053_b015

4. 明天准备做什么？

### block_p0053_b016

5. 有什么产出物？

### block_p0053_b017

Staff Agent 再将这些回答整理为Staff Schema。

### block_p0053_b018

IM 表单不是最终产品形态，但它适合作为MVP 的第一交互入口。

### block_p0053_b019

2.7.2后屏幕记忆/自动采集

### block_p0053_b020

屏幕记忆、自动录屏、行为采集、办公软件插件等能力可以作为后续增强方向，但不建

### block_p0053_b021

议作为MVP 前置条件。

### block_p0053_b022

原因如下：

### block_p0053_b023

1. 自动采集涉及客户端权限和隐私问题。

### block_p0053_b024

2. 不同企业环境差异较大。

### block_p0053_b025

3. 开源项目集成成本不确定。

### block_p0053_b026

4. 自动采集结果仍然需要Schema 化和人工确认。

### block_p0053_b027

5. 如果一开始依赖自动采集，MVP 交付风险会明显增加。

### block_p0053_b028

推荐阶段划分：

### block_p0053_b029

阶段数据采集方式

### block_p0053_b030

MVP v0.1IM 表单手动填报

### block_p0053_b031

MVP v0.2Agent 追问和结构化整理

### block_p0053_b032

MVP v0.3支持上传文档、代码、链接作为产出物

### block_p0053_b033

后续版本接入屏幕记忆、办公插件、业务系统数据

### block_p0053_b034

后续即使接入自动采集，也不应绕过员工确认。自动采集只能作为草稿来源，最终进入

### block_p0053_b035

系统的数据仍应经过员工确认和后端校验。

### block_p0053_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0053_b037

AutoMage-2-MVP 架构设计文档·杨卓53

### block_p0053_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 53

## 表格

无。

## 备注

无。

<!-- 来自 page_0053.md 全文结束 -->

<!-- 来自 page_0054.md 全文开始 -->

# Page 0054

## 原始文本块

### block_p0054_b001

2026 年5 月3 日

### block_p0054_b002

2.7.3先Mock

### block_p0054_b003

在真实后端接口完成前，Agent 侧可以先使用Mock API 跑通流程。

### block_p0054_b004

Mock 阶段的目标不是模拟所有细节，而是先验证Agent 之间的主流程是否成立。

### block_p0054_b005

Mock 阶段至少要跑通：

### block_p0054_b006

1. Staff Agent 提交日报。

### block_p0054_b007

2. Mock 后端保存Staff Schema。

### block_p0054_b008

3. Manager Agent 读取日报并生成汇总。

### block_p0054_b009

4. Executive Agent 读取汇总并生成决策项。

### block_p0054_b010

5. 老板确认方案。

### block_p0054_b011

6. 系统生成任务。

### block_p0054_b012

7. Staff Agent 查询任务。

### block_p0054_b013

Mock 阶段需要保持接口形式尽量接近真实接口，避免后续切换真实API 时大面积重写。

### block_p0054_b014

建议Mock 数据结构提前采用正式字段名，例如：

### block_p0054_b015

/api/v1/report/staff

### block_p0054_b016

/api/v1/report/manager

### block_p0054_b017

/api/v1/decision/commit

### block_p0054_b018

/api/v1/tasks

### block_p0054_b019

2.7.4后真实API

### block_p0054_b020

Mock 流程跑通后，再逐步切换真实后端API。

### block_p0054_b021

真实API 阶段重点补齐以下能力：

### block_p0054_b022

1. 用户鉴权。

### block_p0054_b023

2. Agent 鉴权。

### block_p0054_b024

3. Schema 校验。

### block_p0054_b025

4. 组织和部门权限校验。

### block_p0054_b026

5. 数据库写入。

### block_p0054_b027

6. 幂等控制。

### block_p0054_b028

7. 错误码返回。

### block_p0054_b029

8. 审计日志。

### block_p0054_b030

9. 任务状态流转。

### block_p0054_b031

10. 签名记录。

### block_p0054_b032

真实API 不应只是「能写入数据」，还要保证数据边界清楚。尤其是Staff、Manager、

### block_p0054_b033

Executive 三类节点的读取和写入权限必须在后端控制。

### block_p0054_b034

Agent 侧不得绕过API 直接连接数据库。数据库读写必须统一经过后端接口，便于权限

### block_p0054_b035

控制和审计追踪。

### block_p0054_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0054_b037

AutoMage-2-MVP 架构设计文档·杨卓54

### block_p0054_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 54

## 表格

无。

## 备注

无。

<!-- 来自 page_0054.md 全文结束 -->

<!-- 来自 page_0055.md 全文开始 -->

# Page 0055

## 原始文本块

### block_p0055_b001

2026 年5 月3 日

### block_p0055_b002

2.7.5先通用Schema

### block_p0055_b003

MVP 阶段建议先采用通用Schema，不绑定某个具体行业。

### block_p0055_b004

通用Staff Schema 重点覆盖：

### block_p0055_b005

1. 今日完成事项。

### block_p0055_b006

2. 遇到的问题。

### block_p0055_b007

3. 已尝试方案。

### block_p0055_b008

4. 是否需要支持。

### block_p0055_b009

5. 明日计划。

### block_p0055_b010

6. 资源消耗。

### block_p0055_b011

7. 工作产出物。

### block_p0055_b012

通用Manager Schema 重点覆盖：

### block_p0055_b013

1. 部门综合进展。

### block_p0055_b014

2. 部门健康度。

### block_p0055_b015

3. 风险和阻塞。

### block_p0055_b016

4. 突出员工和产出。

### block_p0055_b017

5. 待处理事项。

### block_p0055_b018

6. 待上推决策。

### block_p0055_b019

通用Executive Schema 重点覆盖：

### block_p0055_b020

1. 组织级摘要。

### block_p0055_b021

2. 关键风险。

### block_p0055_b022

3. 待老板确认事项。

### block_p0055_b023

4. 候选方案。

### block_p0055_b024

5. 推荐方案。

### block_p0055_b025

6. 预期影响。

### block_p0055_b026

7. 任务拆解草案。

### block_p0055_b027

先做通用Schema 的好处是可以快速验证组织数据闭环，而不用在早期陷入复杂行业细

### block_p0055_b028

节。

### block_p0055_b029

2.7.6后行业模板Schema

### block_p0055_b030

通用Schema 跑通后，再逐步扩展行业模板Schema。

### block_p0055_b031

行业模板不是重写整套系统，而是在通用Schema 基础上增加行业字段和业务规则。

### block_p0055_b032

示例：

### block_p0055_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0055_b034

AutoMage-2-MVP 架构设计文档·杨卓55

### block_p0055_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 55

## 表格

无。

## 备注

无。

<!-- 来自 page_0055.md 全文结束 -->

<!-- 来自 page_0056.md 全文开始 -->

# Page 0056

## 原始文本块

### block_p0056_b001

2026 年5 月3 日

### block_p0056_b002

行业/ 场景可扩展字段

### block_p0056_b003

销售客户名称、跟进阶段、成交概率、合同金额、下一步动作

### block_p0056_b004

研发需求ID、代码提交、Bug 编号、测试状态、发布计划

### block_p0056_b005

客服客户问题、处理结果、满意度、升级原因、响应时长

### block_p0056_b006

制造工序、产量、良率、设备状态、异常原因

### block_p0056_b007

市场活动名称、投放渠道、线索数量、ROI、转化率

### block_p0056_b008

项目管理里程碑、依赖项、交付物、风险、延期原因

### block_p0056_b009

行业模板Schema 的推进顺序建议如下：

### block_p0056_b010

通用Schema 跑通

### block_p0056_b011

↓

### block_p0056_b012

选择一个试点行业

### block_p0056_b013

↓

### block_p0056_b014

补充行业字段

### block_p0056_b015

↓

### block_p0056_b016

保留通用字段兼容

### block_p0056_b017

↓

### block_p0056_b018

形成行业模板

### block_p0056_b019

↓

### block_p0056_b020

复制到更多行业

### block_p0056_b021

这样既能保证MVP 阶段快速落地，也为后续商业化和行业化部署留下扩展空间。

### block_p0056_b022 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0056_b023

AutoMage-2-MVP 架构设计文档·杨卓56

### block_p0056_b024 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 56

## 表格

无。

## 备注

无。

<!-- 来自 page_0056.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

