# Dream 机制设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P175-P200
> 对应页面文件：`01_PAGES/page_0175.md` — `01_PAGES/page_0200.md`

## 原文整理

<!-- 来自 page_0175.md 全文开始 -->

# Page 0175

## 原始文本块

### block_p0175_b001

2026 年5 月3 日

### block_p0175_b002

9Dream 机制设计

### block_p0175_b003

9.1Dream 的定义

### block_p0175_b004

Dream 是AutoMage-2 中用于周期性整理组织运行数据、生成风险判断、形成老板决策

### block_p0175_b005

项和次日任务建议的智能分析机制。

### block_p0175_b006

它可以理解为系统每天固定时间做的一次“组织级复盘和预推演”。Staff Agent 负责记

### block_p0175_b007

录一线员工当天做了什么，Manager Agent 负责汇总部门发生了什么，而Dream 负责站在组

### block_p0175_b008

织层面判断：这些信息加在一起意味着什么，明天哪些事情最重要，哪些风险需要提前处理，

### block_p0175_b009

哪些事项需要老板确认。

### block_p0175_b010

Dream 不是普通日报生成器，也不是简单的总结Prompt。它的输入来自系统中已经结构

### block_p0175_b011

化的数据，包括Staff Schema、Manager Schema、历史Summary、历史Decision、未完成任

### block_p0175_b012

务、异常记录和外部业务目标。它的输出也必须是结构化结果，包括老板决策项、风险预警、

### block_p0175_b013

任务拆解、次日重点和部门调整建议。

### block_p0175_b014

MVP 阶段的Dream 不需要实现完整的长期记忆和复杂战略推演，但至少要完成以下能

### block_p0175_b015

力：

### block_p0175_b016

1. 定时读取已确认的部门汇总数据。

### block_p0175_b017

2. 识别组织层面的关键风险。

### block_p0175_b018

3. 将上推事项整理成老板可确认的决策项。

### block_p0175_b019

4. 为每个决策项生成可选方案和推荐理由。

### block_p0175_b020

5. 根据确认结果生成任务草案。

### block_p0175_b021

6. 将结果写入Executive Schema 或相关Summary。

### block_p0175_b022

简单来说，Dream 是AutoMage-2 从“数据汇总”走向“决策驱动”的中间层。

### block_p0175_b023

9.2Dream 在AutoMage-2 中的作用

### block_p0175_b024

Dream 在AutoMage-2 中承担五个作用。

### block_p0175_b025

第一，它负责把多部门汇总变成老板能看懂的组织摘要。Manager Schema 中包含大量部

### block_p0175_b026

门级信息，如果全部推给老板，老板仍然需要自己筛选。Dream 需要把这些信息进一步压缩

### block_p0175_b027

成公司级摘要，只保留关键进展、关键风险和关键决策点。

### block_p0175_b028

第二，它负责识别跨部门风险。单个Manager Agent 只能看到本部门数据，但很多风险

### block_p0175_b029

不是在单个部门内暴露出来的。例如后端表结构未确认，可能同时影响Agent 客制化、前端

### block_p0175_b030

联调和老板侧决策卡片。Dream 需要从多个部门汇总中识别这种共同风险。

### block_p0175_b031

第三，它负责生成老板决策项。老板不需要看到“有问题，请处理”这种开放式描述，而

### block_p0175_b032

是需要看到背景、方案、推荐理由和确认动作。Dream 要把模糊问题整理成可选择、可确认、

### block_p0175_b033

可追踪的决策项。

### block_p0175_b034

第四，它负责生成任务拆解草案。决策如果不能落到任务，就无法形成闭环。Dream 需

### block_p0175_b035

要在决策项中预先生成任务草案，等老板确认后由后端创建正式任务。

### block_p0175_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0175_b037

AutoMage-2-MVP 架构设计文档·杨卓175

### block_p0175_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 175

## 表格

无。

## 备注

无。

<!-- 来自 page_0175.md 全文结束 -->

<!-- 来自 page_0176.md 全文开始 -->

# Page 0176

## 原始文本块

### block_p0176_b001

2026 年5 月3 日

### block_p0176_b002

第五，它负责形成次日组织运行重点。Dream 应根据当天数据和历史状态，给出第二天

### block_p0176_b003

的重点事项、部门调整建议和需要关注的风险，为第二天的Staff Agent 和Manager Agent 提

### block_p0176_b004

供输入。

### block_p0176_b005

Dream 在系统中的位置如下：

### block_p0176_b006

Staff Schema

### block_p0176_b007

↓

### block_p0176_b008

Manager Schema

### block_p0176_b009

↓

### block_p0176_b010

Dream

### block_p0176_b011

↓

### block_p0176_b012

Executive Schema

### block_p0176_b013

↓

### block_p0176_b014

老板确认

### block_p0176_b015

↓

### block_p0176_b016

Task Schema

### block_p0176_b017

↓

### block_p0176_b018

Staff / Manager 执行

### block_p0176_b019

没有Dream，Executive Agent 容易退化成一个部门日报转发器；有了Dream，系统才开

### block_p0176_b020

始具备组织级判断和主动推进能力。

### block_p0176_b021

9.3Dream 的每日运行时间

### block_p0176_b022

MVP 阶段建议Dream 采用定时运行机制，不依赖实时长连接，也不要求全天候频繁推

### block_p0176_b023

理。

### block_p0176_b024

推荐每日运行节奏如下：

### block_p0176_b025

时间动作

### block_p0176_b026

18:00Staff Agent 提醒员工填写日报

### block_p0176_b027

20:00Staff Agent 二次催填缺失日报

### block_p0176_b028

21:00Manager Agent 读取Staff Schema，生成部门汇总

### block_p0176_b029

21:30部门负责人确认或标记部门汇总

### block_p0176_b030

22:00Dream 读取Manager Schema，生成夜间组织摘要草稿

### block_p0176_b031

次日08:00 前Dream 生成老板决策卡片和次日重点

### block_p0176_b032

次日08:30 前老板确认后，任务下发到Manager / Staff

### block_p0176_b033

MVP 阶段可以先采用一个固定Dream 批处理任务，例如每天晚上22:00 或次日早上

### block_p0176_b034

08:00 运行。两种方式各有优劣：

### block_p0176_b035

运行时间优点缺点

### block_p0176_b036

前一晚运行第二天早上可直接推送老板决策卡片部分部门汇总可能尚未确认

### block_p0176_b037

次日早上运行数据更完整，更适合早会前推送对运行稳定性和时间要求更高

### block_p0176_b038

晚上初稿+ 早上复核兼顾完整性和及时性实现稍复杂

### block_p0176_b039

推荐MVP 阶段先采用：

### block_p0176_b040

晚上生成草稿，早上生成正式老板卡片。

### block_p0176_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0176_b042

AutoMage-2-MVP 架构设计文档·杨卓176

### block_p0176_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 176

## 表格

无。

## 备注

无。

<!-- 来自 page_0176.md 全文结束 -->

<!-- 来自 page_0177.md 全文开始 -->

# Page 0177

## 原始文本块

### block_p0177_b001

2026 年5 月3 日

### block_p0177_b002

如果开发时间有限，也可以先只做早上定时运行。关键是保证Dream 的输入数据已经完

### block_p0177_b003

成后端校验和权限确认，不要读取员工未确认草稿作为老板决策依据。

### block_p0177_b004

9.4Dream 输入数据

### block_p0177_b005

Dream 的输入必须来自系统事实源。IM 聊天记录、Agent 临时上下文、未确认草稿都不

### block_p0177_b006

能作为正式输入。

### block_p0177_b007

MVP 阶段Dream 主要读取以下六类数据：

### block_p0177_b008

1. Staff Schema。

### block_p0177_b009

2. Manager Schema。

### block_p0177_b010

3. 历史Summary。

### block_p0177_b011

4. 历史Decision。

### block_p0177_b012

5. 未完成任务。

### block_p0177_b013

6. 外部业务目标。

### block_p0177_b014

其中，Manager Schema 是Dream 的主输入，其他数据用于补充上下文和判断趋势。

### block_p0177_b015

9.4.1Staff Schema

### block_p0177_b016

Staff Schema 是一线执行数据，记录员工当天完成事项、遇到问题、支持需求、明日计划

### block_p0177_b017

和产出物。

### block_p0177_b018

Dream 一般不直接读取全部Staff Schema 明细，而是通过Manager Schema 间接获取一

### block_p0177_b019

线情况。只有在以下场景下，Dream 才需要向下追溯Staff Schema：

### block_p0177_b020

1. 某个老板决策项需要核对来源。

### block_p0177_b021

2. Manager Schema 中的风险判断依据不足。

### block_p0177_b022

3. 某个员工产出物是关键决策依据。

### block_p0177_b023

4. 老板主动要求查看某个事项来源。

### block_p0177_b024

5. 系统需要判断某个问题是否多次出现。

### block_p0177_b025

读取Staff Schema 时必须遵守权限规则。Dream 可以追溯来源，但不应默认把所有员工

### block_p0177_b026

明细展示给老板。

### block_p0177_b027

推荐读取字段包括：

### block_p0177_b028

字段用途

### block_p0177_b029

work_progress判断实际完成事项

### block_p0177_b030

issues_faced识别一线问题

### block_p0177_b031

need_support识别需要上级介入的事项

### block_p0177_b032

support_detail理解支持需求

### block_p0177_b033

next_day_plan判断次日计划

### block_p0177_b034

risk_level判断风险等级

### block_p0177_b035

artifacts查看关键产出物

### block_p0177_b036

signature判断数据是否已确认

### block_p0177_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0177_b038

AutoMage-2-MVP 架构设计文档·杨卓177

### block_p0177_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 177

## 表格

无。

## 备注

无。

<!-- 来自 page_0177.md 全文结束 -->

<!-- 来自 page_0178.md 全文开始 -->

# Page 0178

## 原始文本块

### block_p0178_b001

2026 年5 月3 日

### block_p0178_b002

未签名、未确认、校验失败的Staff Schema 不应进入Dream 正式判断。

### block_p0178_b003

9.4.2Manager Schema

### block_p0178_b004

Manager Schema 是Dream 的核心输入。

### block_p0178_b005

Dream 主要读取各部门Manager Schema，并基于这些汇总生成组织级摘要、关键风险和

### block_p0178_b006

老板决策项。

### block_p0178_b007

推荐读取字段包括：

### block_p0178_b008

Manager Schema 字段Dream 使用方式

### block_p0178_b009

aggregated_summary生成公司级业务摘要

### block_p0178_b010

overall_health判断部门状态

### block_p0178_b011

top_3_risks提炼组织级风险

### block_p0178_b012

blocked_items识别阻塞事项

### block_p0178_b013

need_executive_decision生成老板决策项

### block_p0178_b014

manager_decisions判断部门内已处理事项

### block_p0178_b015

next_day_adjustment生成次日重点

### block_p0178_b016

staff_report_count判断数据覆盖情况

### block_p0178_b017

missing_report_count判断数据完整性风险

### block_p0178_b018

source_record_ids追溯来源

### block_p0178_b019

signature判断是否已由Manager 确认

### block_p0178_b020

Manager Schema 进入Dream 前，应满足以下条件：

### block_p0178_b021

1. 属于当前组织。

### block_p0178_b022

2. 汇总日期在本次运行窗口内。

### block_p0178_b023

3. 状态有效。

### block_p0178_b024

4. 数据来源可追溯。

### block_p0178_b025

5. 必要时已由部门负责人确认。

### block_p0178_b026

6. 当前Executive Agent 有读取权限。

### block_p0178_b027

如果某个部门没有提交Manager Schema，Dream 应在结果中标记数据缺失，而不是假装

### block_p0178_b028

该部门正常。

### block_p0178_b029

9.4.3历史Summary

### block_p0178_b030

历史Summary 用于让Dream 判断趋势，而不是只看当天快照。

### block_p0178_b031

例如，某个部门今天出现一个中风险问题，如果昨天、前天也出现类似问题，那么它可

### block_p0178_b032

能不是偶发问题，而是结构性风险。没有历史Summary，Dream 很难判断“今天的问题是否

### block_p0178_b033

正在变严重”。

### block_p0178_b034

推荐读取的历史Summary 包括：

### block_p0178_b035

1. 前一日组织级Summary。

### block_p0178_b036

2. 前一周部门Summary。

### block_p0178_b037

3. 最近几天的风险摘要。

### block_p0178_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0178_b039

AutoMage-2-MVP 架构设计文档·杨卓178

### block_p0178_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 178

## 表格

无。

## 备注

无。

<!-- 来自 page_0178.md 全文结束 -->

<!-- 来自 page_0179.md 全文开始 -->

# Page 0179

## 原始文本块

### block_p0179_b001

2026 年5 月3 日

### block_p0179_b002

4. 最近几天的任务完成摘要。

### block_p0179_b003

5. 历史Dream 输出结果。

### block_p0179_b004

6. 关键项目或部门的周期性汇总。

### block_p0179_b005

历史Summary 的用途包括：

### block_p0179_b006

用途示例

### block_p0179_b007

趋势判断某个风险连续三天出现

### block_p0179_b008

复盘对比昨日决策是否改善了今日情况

### block_p0179_b009

避免重复提醒昨天已提醒老板，今天只更新状态

### block_p0179_b010

识别长期阻塞同一问题多日未解决

### block_p0179_b011

生成次日重点根据历史未完成事项排序

### block_p0179_b012

MVP 阶段可以先读取最近3-7 天的Summary，不需要做长期全量扫描。

### block_p0179_b013

9.4.4历史Decision

### block_p0179_b014

历史Decision 用于判断当前决策是否与过去老板确认过的方向一致。

### block_p0179_b015

如果系统每天都生成新的决策项，但不记得昨天老板已经选过什么，就会反复打扰老板，

### block_p0179_b016

甚至生成相互冲突的任务。

### block_p0179_b017

Dream 应读取以下历史决策信息：

### block_p0179_b018

1. 最近已确认的老板决策。

### block_p0179_b019

2. 尚未完成的决策。

### block_p0179_b020

3. 已驳回的决策。

### block_p0179_b021

4. 要求补充信息的决策。

### block_p0179_b022

5. 已生成任务的决策。

### block_p0179_b023

6. 已撤回或取消的决策。

### block_p0179_b024

推荐读取字段包括：

### block_p0179_b025

字段用途

### block_p0179_b026

decision_title判断是否重复

### block_p0179_b027

decision_context理解决策背景

### block_p0179_b028

confirmed_option判断老板已选择方向

### block_p0179_b029

confirmed_at判断决策时间

### block_p0179_b030

generated_task_ids追踪执行结果

### block_p0179_b031

status判断是否完成

### block_p0179_b032

source_summary_ids判断来源关系

### block_p0179_b033

expected_impact判断后续影响

### block_p0179_b034

历史Decision 的作用主要有三点：

### block_p0179_b035

1. 避免重复生成相同决策。

### block_p0179_b036

2. 判断新决策是否与旧决策冲突。

### block_p0179_b037

3. 跟踪老板决策是否真正产生执行结果。

### block_p0179_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0179_b039

AutoMage-2-MVP 架构设计文档·杨卓179

### block_p0179_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 179

## 表格

无。

## 备注

无。

<!-- 来自 page_0179.md 全文结束 -->

<!-- 来自 page_0180.md 全文开始 -->

# Page 0180

## 原始文本块

### block_p0180_b001

2026 年5 月3 日

### block_p0180_b002

MVP 阶段如果独立Decision 表尚未建立，也应至少从audit_logs、summaries.meta 或

### block_p0180_b003

tasks.meta 中读取相关记录。后续建议将Decision 做成独立对象。

### block_p0180_b004

9.4.5未完成任务

### block_p0180_b005

未完成任务是Dream 判断执行风险的重要输入。

### block_p0180_b006

老板已经确认过的决策，如果没有对应任务推进，或者任务长期停留在阻塞状态，Dream

### block_p0180_b007

应主动提示。

### block_p0180_b008

推荐读取任务范围包括：

### block_p0180_b009

1. 高优先级未完成任务。

### block_p0180_b010

2. 已逾期任务。

### block_p0180_b011

3. 与老板决策相关的任务。

### block_p0180_b012

4. 与当前风险相关的任务。

### block_p0180_b013

5. 被多次更新为阻塞的任务。

### block_p0180_b014

6. 即将到期的重要任务。

### block_p0180_b015

推荐读取字段包括：

### block_p0180_b016

字段用途

### block_p0180_b017

title任务名称

### block_p0180_b018

status当前状态

### block_p0180_b019

priority优先级

### block_p0180_b020

due_at截止时间

### block_p0180_b021

department_id所属部门

### block_p0180_b022

assignee_user_id执行人

### block_p0180_b023

source_record_id来源日报

### block_p0180_b024

source_decision_id来源决策

### block_p0180_b025

result_summary任务结果

### block_p0180_b026

task_updates判断推进过程

### block_p0180_b027

未完成任务进入Dream 后，可以产生三种结果：

### block_p0180_b028

1. 生成风险预警。

### block_p0180_b029

2. 生成老板决策项。

### block_p0180_b030

3. 生成次日重点或部门调整建议。

### block_p0180_b031

9.4.6外部业务目标

### block_p0180_b032

外部业务目标指老板或企业给系统输入的阶段性目标、经营指标、项目目标或临时要求。

### block_p0180_b033

例如：

### block_p0180_b034

1. 本周必须完成MVP 联调。

### block_p0180_b035

2. 两周内跑通三级Agent 闭环。

### block_p0180_b036

3. 优先保证老板侧决策卡片可演示。

### block_p0180_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0180_b038

AutoMage-2-MVP 架构设计文档·杨卓180

### block_p0180_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 180

## 表格

无。

## 备注

无。

<!-- 来自 page_0180.md 全文结束 -->

<!-- 来自 page_0181.md 全文开始 -->

# Page 0181

## 原始文本块

### block_p0181_b001

2026 年5 月3 日

### block_p0181_b002

4. 本月重点是媒体演示和试点客户。

### block_p0181_b003

5. 某个客户项目必须优先交付。

### block_p0181_b004

6. 某项预算不能超过上限。

### block_p0181_b005

这些目标不一定来自Staff 或Manager Schema，但会影响Dream 对风险和任务优先级

### block_p0181_b006

的判断。

### block_p0181_b007

MVP 阶段可以先用简单配置方式输入外部目标，例如：

### block_p0181_b008

{

### block_p0181_b009

"business_goals": [

### block_p0181_b010

{

### block_p0181_b011

"goal_id": "goal_mvp_001",

### block_p0181_b012

"title": " 两周内跑通AutoMage-2 MVP 三级数据闭环",

### block_p0181_b013

"priority": "high",

### block_p0181_b014

"deadline": "2026-05-15",

### block_p0181_b015

"owner": "project_team"

### block_p0181_b016

}

### block_p0181_b017

]

### block_p0181_b018

}

### block_p0181_b019

Dream 生成决策和任务时，应参考这些目标。例如，如果MVP 主链路是最高优先级，那

### block_p0181_b020

么影响主链路的表结构、API、Schema 和Agent 联调问题，应优先进入老板侧摘要。

### block_p0181_b021

9.5Dream 输出数据

### block_p0181_b022

Dream 的输出不是一段普通总结，而是一组可被Executive Agent、老板、任务系统和审

### block_p0181_b023

计系统继续使用的结构化结果。

### block_p0181_b024

MVP 阶段Dream 主要输出五类数据：

### block_p0181_b025

1. 老板决策项。

### block_p0181_b026

2. 风险预警。

### block_p0181_b027

3. 任务拆解。

### block_p0181_b028

4. 次日重点。

### block_p0181_b029

5. 部门调整建议。

### block_p0181_b030

这些输出最终会进入Executive Schema、Summary、Decision 或Task。

### block_p0181_b031

9.5.1老板决策项

### block_p0181_b032

老板决策项是Dream 最重要的输出。

### block_p0181_b033

一个合格的老板决策项应包含：

### block_p0181_b034

1. 决策标题。

### block_p0181_b035

2. 背景说明。

### block_p0181_b036

3. 影响范围。

### block_p0181_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0181_b038

AutoMage-2-MVP 架构设计文档·杨卓181

### block_p0181_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 181

## 表格

无。

## 备注

无。

<!-- 来自 page_0181.md 全文结束 -->

<!-- 来自 page_0182.md 全文开始 -->

# Page 0182

## 原始文本块

### block_p0182_b001

2026 年5 月3 日

### block_p0182_b002

4. 决策等级。

### block_p0182_b003

5. 候选方案。

### block_p0182_b004

6. 推荐方案。

### block_p0182_b005

7. 推荐理由。

### block_p0182_b006

8. 预期影响。

### block_p0182_b007

9. 来源数据。

### block_p0182_b008

10. 确认后可生成的任务。

### block_p0182_b009

示例：

### block_p0182_b010

{

### block_p0182_b011

"decision_title": " 是否新增独立decision_logs 表",

### block_p0182_b012

"context": "当前Agent mock 流程中已有decision_logs 概念，但正式DDL 尚未建立独立决策表。

### block_p0182_b013

如果不新增，短期可以复用audit_logs，但后续老板决策追踪和任务来源会不清晰。",,→

### block_p0182_b014

"decision_level": "L3",

### block_p0182_b015

"options": [

### block_p0182_b016

{

### block_p0182_b017

"option_id": "A",

### block_p0182_b018

"title": " 新增独立decision_logs 表",

### block_p0182_b019

"pros": [" 决策对象清晰", " 方便审计", " 便于后续看板和复盘"],

### block_p0182_b020

"cons": [" 需要增加后端开发工作量"]

### block_p0182_b021

},

### block_p0182_b022

{

### block_p0182_b023

"option_id": "B",

### block_p0182_b024

"title": " 暂时复用audit_logs 和tasks",

### block_p0182_b025

"pros": [" 短期实现更快"],

### block_p0182_b026

"cons": [" 长期追踪不清晰", " 后续可能需要迁移"]

### block_p0182_b027

}

### block_p0182_b028

],

### block_p0182_b029

"recommended_option": "A",

### block_p0182_b030

"reasoning_summary": "AutoMage-2 的核心价值在于决策可追溯，独立决策对象更符合长期架构。",

### block_p0182_b031

"source_summary_ids": [801, 802]

### block_p0182_b032

}

### block_p0182_b033

老板决策项不应过多。MVP 阶段建议每天只推送1-3 个真正重要的决策事项，避免老板

### block_p0182_b034

侧再次信息过载。

### block_p0182_b035

9.5.2风险预警

### block_p0182_b036

风险预警用于提醒老板或Manager 当前最需要关注的问题。

### block_p0182_b037

Dream 的风险预警应与普通部门风险不同。部门风险可以很多，但组织级风险必须经过

### block_p0182_b038

筛选，只保留影响较大、跨部门、影响主链路或需要高层干预的事项。

### block_p0182_b039

风险预警建议包含：

### block_p0182_b040

1. 风险标题。

### block_p0182_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0182_b042

AutoMage-2-MVP 架构设计文档·杨卓182

### block_p0182_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 182

## 表格

无。

## 备注

无。

<!-- 来自 page_0182.md 全文结束 -->

<!-- 来自 page_0183.md 全文开始 -->

# Page 0183

## 原始文本块

### block_p0183_b001

2026 年5 月3 日

### block_p0183_b002

2. 风险说明。

### block_p0183_b003

3. 风险等级。

### block_p0183_b004

4. 影响范围。

### block_p0183_b005

5. 来源部门。

### block_p0183_b006

6. 来源Summary。

### block_p0183_b007

7. 建议动作。

### block_p0183_b008

8. 是否需要决策。

### block_p0183_b009

示例：

### block_p0183_b010

{

### block_p0183_b011

"risk_title": "MVP 主链路存在决策对象缺口",

### block_p0183_b012

"description": "Staff、Manager、Executive 三层Schema 已初步定义，但正式DDL 中尚未建立独立

### block_p0183_b013

Decision 表，可能影响老板确认、任务来源追踪和审计闭环。",,→

### block_p0183_b014

"severity": "high",

### block_p0183_b015

"affected_modules": ["database", "backend", "executive_agent"],

### block_p0183_b016

"source_summary_ids": [801],

### block_p0183_b017

"suggested_action": " 建议将Decision 表是否新增作为老板决策项处理。",

### block_p0183_b018

"decision_required": true

### block_p0183_b019

}

### block_p0183_b020

风险预警的目标不是制造焦虑，而是帮助上级提前看到会影响闭环的关键问题。

### block_p0183_b021

9.5.3任务拆解

### block_p0183_b022

任务拆解是Dream 将决策落地的关键输出。

### block_p0183_b023

Dream 不直接创建正式任务，而是生成任务草案。老板确认方案后，后端再根据任务草

### block_p0183_b024

案创建正式任务。

### block_p0183_b025

任务拆解建议包含：

### block_p0183_b026

1. 任务标题。

### block_p0183_b027

2. 任务说明。

### block_p0183_b028

3. 来源决策。

### block_p0183_b029

4. 执行人或执行角色。

### block_p0183_b030

5. 所属部门。

### block_p0183_b031

6. 优先级。

### block_p0183_b032

7. 截止时间。

### block_p0183_b033

8. 预期产出。

### block_p0183_b034

9. 依赖关系。

### block_p0183_b035

10. 是否需要Manager 二次拆解。

### block_p0183_b036

示例：

### block_p0183_b037 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0183_b038

AutoMage-2-MVP 架构设计文档·杨卓183

### block_p0183_b039 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 183

## 表格

无。

## 备注

无。

<!-- 来自 page_0183.md 全文结束 -->

<!-- 来自 page_0184.md 全文开始 -->

# Page 0184

## 原始文本块

### block_p0184_b001

2026 年5 月3 日

### block_p0184_b002

{

### block_p0184_b003

"task_title": " 补充decision_logs 表结构草案",

### block_p0184_b004

"task_description": "根据Executive 决策链路设计decision_logs 表，字段需覆盖决策标题、背景、

### block_p0184_b005

候选方案、推荐方案、确认人、确认时间和生成任务。",,→

### block_p0184_b006

"assignee_role": "backend",

### block_p0184_b007

"department_id": 12,

### block_p0184_b008

"priority": "high",

### block_p0184_b009

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0184_b010

"expected_output": " 提交decision_logs 表DDL 草案及与Executive Schema 的映射说明",

### block_p0184_b011

"source_decision_id": "decision_tmp_001"

### block_p0184_b012

}

### block_p0184_b013

任务草案要尽量具体，避免出现“推进项目”“完善系统”这类无法执行、无法验收的描

### block_p0184_b014

述。

### block_p0184_b015

9.5.4次日重点

### block_p0184_b016

次日重点用于指导第二天Staff Agent 和Manager Agent 的工作提醒。

### block_p0184_b017

它不是正式任务列表，而是组织或部门层面的重点方向。部分次日重点可以在Manager

### block_p0184_b018

或老板确认后转成任务。

### block_p0184_b019

次日重点建议包含：

### block_p0184_b020

1. 重点事项。

### block_p0184_b021

2. 所属部门。

### block_p0184_b022

3. 相关负责人。

### block_p0184_b023

4. 优先级。

### block_p0184_b024

5. 预期产出。

### block_p0184_b025

6. 来源原因。

### block_p0184_b026

7. 是否建议转任务。

### block_p0184_b027

示例：

### block_p0184_b028

{

### block_p0184_b029

"next_day_focus": [

### block_p0184_b030

{

### block_p0184_b031

"title": " 优先完成Decision Schema 与数据库映射",

### block_p0184_b032

"department_id": 12,

### block_p0184_b033

"priority": "high",

### block_p0184_b034

"reason": " 该事项影响Executive 决策卡片和任务下发闭环。",

### block_p0184_b035

"expected_output": " 形成Decision 字段定义和落表建议",

### block_p0184_b036

"suggest_task_creation": true

### block_p0184_b037

},

### block_p0184_b038

{

### block_p0184_b039

"title": " 补齐缺失日报",

### block_p0184_b040

"department_id": 15,

### block_p0184_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0184_b042

AutoMage-2-MVP 架构设计文档·杨卓184

### block_p0184_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 184

## 表格

无。

## 备注

无。

<!-- 来自 page_0184.md 全文结束 -->

<!-- 来自 page_0185.md 全文开始 -->

# Page 0185

## 原始文本块

### block_p0185_b001

2026 年5 月3 日

### block_p0185_b002

"priority": "medium",

### block_p0185_b003

"reason": " 该部门昨日缺失3 份Staff 日报，影响部门汇总可信度。",

### block_p0185_b004

"expected_output": " 完成缺失日报补交或说明",

### block_p0185_b005

"suggest_task_creation": false

### block_p0185_b006

}

### block_p0185_b007

]

### block_p0185_b008

}

### block_p0185_b009

次日重点可以用于第二天早上推送给Manager，也可以作为Staff Agent 任务提醒的输

### block_p0185_b010

入。

### block_p0185_b011

9.5.5部门调整建议

### block_p0185_b012

部门调整建议面向Manager 或老板，用于提示某个部门第二天或下一周期需要调整的方

### block_p0185_b013

向。

### block_p0185_b014

它和次日重点的区别是：次日重点偏具体事项，部门调整建议偏管理动作。

### block_p0185_b015

部门调整建议可以包括：

### block_p0185_b016

1. 任务优先级调整。

### block_p0185_b017

2. 人员协作调整。

### block_p0185_b018

3. 风险处理建议。

### block_p0185_b019

4. 缺失日报催办。

### block_p0185_b020

5. 跨部门协作建议。

### block_p0185_b021

6. 资源支持建议。

### block_p0185_b022

7. 阻塞事项处理建议。

### block_p0185_b023

示例：

### block_p0185_b024

{

### block_p0185_b025

"department_adjustments": [

### block_p0185_b026

{

### block_p0185_b027

"department_id": 12,

### block_p0185_b028

"department_name": " 架构组",

### block_p0185_b029

"adjustment_title": " 将决策表结构确认提升为最高优先级",

### block_p0185_b030

"reason": " 该事项影响后端、Agent 和老板侧卡片联调，是当前MVP 主链路阻塞点。",

### block_p0185_b031

"suggested_action": " 由后端负责人在今日内给出是否新增decision_logs 表的最终方案。",

### block_p0185_b032

"priority": "high",

### block_p0185_b033

"need_manager_confirm": true

### block_p0185_b034

}

### block_p0185_b035

]

### block_p0185_b036

}

### block_p0185_b037

部门调整建议不一定直接上推老板。Manager 权限内能处理的，应优先交给Manager 处

### block_p0185_b038

理；超出权限的，再进入Executive 决策项。

### block_p0185_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0185_b040

AutoMage-2-MVP 架构设计文档·杨卓185

### block_p0185_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 185

## 表格

无。

## 备注

无。

<!-- 来自 page_0185.md 全文结束 -->

<!-- 来自 page_0186.md 全文开始 -->

# Page 0186

## 原始文本块

### block_p0186_b001

2026 年5 月3 日

### block_p0186_b002

9.6Dream 运行流程

### block_p0186_b003

Dream 的运行流程建议分为九步：

### block_p0186_b004

触发运行

### block_p0186_b005

↓

### block_p0186_b006

读取数据

### block_p0186_b007

↓

### block_p0186_b008

过滤无效数据

### block_p0186_b009

↓

### block_p0186_b010

归并同类事项

### block_p0186_b011

↓

### block_p0186_b012

识别风险

### block_p0186_b013

↓

### block_p0186_b014

生成决策项

### block_p0186_b015

↓

### block_p0186_b016

生成任务草案

### block_p0186_b017

↓

### block_p0186_b018

写入Executive Schema / Summary

### block_p0186_b019

↓

### block_p0186_b020

推送老板或Manager

### block_p0186_b021

9.6.1触发运行

### block_p0186_b022

Dream 可以由定时任务、Manager 上推或老板主动查询触发。

### block_p0186_b023

MVP 阶段优先支持定时任务：

### block_p0186_b024

每天08:00 生成老板决策卡片

### block_p0186_b025

如果存在critical 风险，也可以支持即时触发：

### block_p0186_b026

Manager Agent 上推critical 事项

### block_p0186_b027

→立即触发Dream 局部分析

### block_p0186_b028

→生成临时老板决策卡片

### block_p0186_b029

9.6.2读取数据

### block_p0186_b030

Dream 根据运行窗口读取数据。

### block_p0186_b031

常见窗口包括：

### block_p0186_b032

1. 昨日所有Manager Schema。

### block_p0186_b033

2. 最近3 天未关闭风险。

### block_p0186_b034

3. 最近7 天未完成任务。

### block_p0186_b035

4. 最近7 天历史决策。

### block_p0186_b036

5. 当前有效外部目标。

### block_p0186_b037

读取时必须通过后端API，不允许直接绕过权限访问数据库。

### block_p0186_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0186_b039

AutoMage-2-MVP 架构设计文档·杨卓186

### block_p0186_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 186

## 表格

无。

## 备注

无。

<!-- 来自 page_0186.md 全文结束 -->

<!-- 来自 page_0187.md 全文开始 -->

# Page 0187

## 原始文本块

### block_p0187_b001

2026 年5 月3 日

### block_p0187_b002

9.6.3过滤无效数据

### block_p0187_b003

Dream 应过滤以下数据：

### block_p0187_b004

1. 草稿状态Summary。

### block_p0187_b005

2. 未确认且需要确认的高风险汇总。

### block_p0187_b006

3. 已删除数据。

### block_p0187_b007

4. 权限不匹配数据。

### block_p0187_b008

5. 重复数据。

### block_p0187_b009

6. 明显校验失败数据。

### block_p0187_b010

7. 已关闭且无复盘价值的低风险事项。

### block_p0187_b011

如果某部门数据缺失，Dream 应在结果中说明，而不是默认该部门没有问题。

### block_p0187_b012

9.6.4归并同类事项

### block_p0187_b013

多个部门可能上报同类问题，Dream 应进行归并。

### block_p0187_b014

例如：

### block_p0187_b015

1. 后端说Decision 表未确认。

### block_p0187_b016

2. Agent 客制化说decision_logs 接口未定。

### block_p0187_b017

3. Executive Schema 说决策确认无法落表。

### block_p0187_b018

这三条可能本质上是同一个问题：决策对象缺口。

### block_p0187_b019

归并后，Dream 应生成一个组织级风险或老板决策项，而不是重复推送三个相似问题。

### block_p0187_b020

9.6.5识别风险

### block_p0187_b021

Dream 根据Manager Schema、历史任务和历史决策识别风险。

### block_p0187_b022

风险判断应优先关注：

### block_p0187_b023

1. 是否影响MVP 主链路。

### block_p0187_b024

2. 是否跨部门。

### block_p0187_b025

3. 是否多日未解决。

### block_p0187_b026

4. 是否影响老板决策。

### block_p0187_b027

5. 是否影响任务下发。

### block_p0187_b028

6. 是否影响客户或交付。

### block_p0187_b029

7. 是否需要高层资源。

### block_p0187_b030

低风险事项不应进入老板决策卡片，避免打扰。

### block_p0187_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0187_b032

AutoMage-2-MVP 架构设计文档·杨卓187

### block_p0187_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 187

## 表格

无。

## 备注

无。

<!-- 来自 page_0187.md 全文结束 -->

<!-- 来自 page_0188.md 全文开始 -->

# Page 0188

## 原始文本块

### block_p0188_b001

2026 年5 月3 日

### block_p0188_b002

9.6.6生成决策项

### block_p0188_b003

对于需要老板确认的事项，Dream 应生成结构化决策项。

### block_p0188_b004

每个决策项至少包含：

### block_p0188_b005

1. 标题。

### block_p0188_b006

2. 背景。

### block_p0188_b007

3. 影响。

### block_p0188_b008

4. 方案A。

### block_p0188_b009

5. 方案B。

### block_p0188_b010

6. 推荐方案。

### block_p0188_b011

7. 推荐理由。

### block_p0188_b012

8. 来源Summary。

### block_p0188_b013

9. 确认后任务草案。

### block_p0188_b014

如果信息不足，Dream 不应硬生成决策项，而应生成“需要补充信息”的请求。

### block_p0188_b015

9.6.7生成任务草案

### block_p0188_b016

Dream 为每个推荐方案生成任务草案。

### block_p0188_b017

任务草案不能直接写入正式任务表，除非对应决策不需要人工确认，或者老板已经确认。

### block_p0188_b018

任务草案应随Executive Schema 一起展示，帮助老板理解“确认后会发生什么”。

### block_p0188_b019

9.6.8写入结果

### block_p0188_b020

Dream 输出应写入以下对象：

### block_p0188_b021

输出写入对象

### block_p0188_b022

组织级摘要summaries

### block_p0188_b023

老板决策项Decision 对象/ Executive Schema

### block_p0188_b024

风险预警summaries.meta / incidents

### block_p0188_b025

任务草案Executive Schema / Decision meta

### block_p0188_b026

审计记录audit_logs

### block_p0188_b027

MVP 阶段如果Decision 表尚未建立，可以先将决策项写入Executive Schema 的

### block_p0188_b028

decision_items 中，并在audit_logs 记录生成动作。

### block_p0188_b029

9.6.9推送结果

### block_p0188_b030

Dream 结果根据类型推送给不同对象：

### block_p0188_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0188_b032

AutoMage-2-MVP 架构设计文档·杨卓188

### block_p0188_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 188

## 表格

无。

## 备注

无。

<!-- 来自 page_0188.md 全文结束 -->

<!-- 来自 page_0189.md 全文开始 -->

# Page 0189

## 原始文本块

### block_p0189_b001

2026 年5 月3 日

### block_p0189_b002

结果类型推送对象

### block_p0189_b003

老板决策项老板/ Executive Agent

### block_p0189_b004

高风险预警老板+ 相关Manager

### block_p0189_b005

部门调整建议对应Manager

### block_p0189_b006

次日重点Manager / Staff Agent

### block_p0189_b007

任务草案暂不推员工，等待确认

### block_p0189_b008

老板侧推送应尽量少而精。Manager 侧可以更细一些，但也不能把所有明细原样推送。

### block_p0189_b009

9.7Dream Prompt 结构

### block_p0189_b010

Dream Prompt 需要保持稳定结构，避免每次输出格式不一致。MVP 阶段建议将Dream

### block_p0189_b011

Prompt 拆为六个部分。

### block_p0189_b012

9.7.1角色定义

### block_p0189_b013

明确Dream 当前扮演的角色。

### block_p0189_b014

示例：

### block_p0189_b015

你是AutoMage-2 的组织级Dream 分析节点。

### block_p0189_b016

你的任务不是写普通日报，而是基于各部门Manager Schema，生成老板侧摘要、关键风险、

### block_p0189_b017

待决策事项和任务草案。,→

### block_p0189_b018

你不能编造不存在的数据，所有关键判断必须引用来源Summary。

### block_p0189_b019

9.7.2输入说明

### block_p0189_b020

列出本次输入数据范围。

### block_p0189_b021

示例：

### block_p0189_b022

本次输入包括：

### block_p0189_b023

1. 2026-05-03 各部门Manager Schema。

### block_p0189_b024

2. 最近7 天未完成任务。

### block_p0189_b025

3. 最近7 天历史决策。

### block_p0189_b026

4. 当前MVP 业务目标。

### block_p0189_b027

这样可以减少Dream 混用上下文或引用无关历史信息。

### block_p0189_b028

9.7.3输出目标

### block_p0189_b029

明确本次Dream 需要输出什么。

### block_p0189_b030

示例：

### block_p0189_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0189_b032

AutoMage-2-MVP 架构设计文档·杨卓189

### block_p0189_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 189

## 表格

无。

## 备注

无。

<!-- 来自 page_0189.md 全文结束 -->

<!-- 来自 page_0190.md 全文开始 -->

# Page 0190

## 原始文本块

### block_p0190_b001

2026 年5 月3 日

### block_p0190_b002

请输出以下内容：

### block_p0190_b003

1. 公司级业务摘要。

### block_p0190_b004

2. 关键风险列表。

### block_p0190_b005

3. 老板待决策事项。

### block_p0190_b006

4. 每个决策项的A/B 方案。

### block_p0190_b007

5. 推荐方案和理由。

### block_p0190_b008

6. 老板确认后可生成的任务草案。

### block_p0190_b009

7. 次日重点和部门调整建议。

### block_p0190_b010

9.7.4约束规则

### block_p0190_b011

Dream 必须遵守约束规则。

### block_p0190_b012

建议约束包括：

### block_p0190_b013

1. 不得编造输入中不存在的事实。

### block_p0190_b014

2. 不得把未确认草稿作为正式依据。

### block_p0190_b015

3. 不得生成没有来源的高风险判断。

### block_p0190_b016

4. 不得直接执行重大决策。

### block_p0190_b017

5. 不得把低价值事项推给老板。

### block_p0190_b018

6. 每个决策项必须有来源Summary。

### block_p0190_b019

7. 每个任务草案必须有来源决策。

### block_p0190_b020

8. 不确定时应标记需要补充信息。

### block_p0190_b021

9.7.5输出格式

### block_p0190_b022

Dream 输出必须符合结构化格式，建议直接输出Executive Schema 所需字段。

### block_p0190_b023

推荐输出结构：

### block_p0190_b024

{

### block_p0190_b025

"business_summary": "...",

### block_p0190_b026

"key_risks": [],

### block_p0190_b027

"decision_required": true,

### block_p0190_b028

"decision_items": [],

### block_p0190_b029

"next_day_focus": [],

### block_p0190_b030

"department_adjustments": [],

### block_p0190_b031

"source_summary_ids": []

### block_p0190_b032

}

### block_p0190_b033

不要输出大段无法解析的Markdown 作为正式结果。Markdown 可以用于IM 展示，但

### block_p0190_b034

系统保存应使用结构化JSON。

### block_p0190_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0190_b036

AutoMage-2-MVP 架构设计文档·杨卓190

### block_p0190_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 190

## 表格

无。

## 备注

无。

<!-- 来自 page_0190.md 全文结束 -->

<!-- 来自 page_0191.md 全文开始 -->

# Page 0191

## 原始文本块

### block_p0191_b001

2026 年5 月3 日

### block_p0191_b002

9.7.6自检要求

### block_p0191_b003

Dream 输出前应进行自检。

### block_p0191_b004

自检问题包括：

### block_p0191_b005

1. 是否引用了来源Summary？

### block_p0191_b006

2. 是否把低风险问题错误上推给老板？

### block_p0191_b007

3. 是否有决策项缺少方案？

### block_p0191_b008

4. 是否有推荐方案但没有理由？

### block_p0191_b009

5. 是否生成了没有来源的任务草案？

### block_p0191_b010

6. 是否把未确认数据当作事实？

### block_p0191_b011

7. 是否存在和历史决策冲突的内容？

### block_p0191_b012

自检不需要展示给老板，但可以作为Agent 内部校验步骤。

### block_p0191_b013

9.8Dream 结果校验

### block_p0191_b014

Dream 结果必须经过校验后才能进入正式流程。校验分为结构校验、来源校验、权限校

### block_p0191_b015

验、业务校验和人工确认校验。

### block_p0191_b016

9.8.1结构校验

### block_p0191_b017

结构校验检查Dream 输出是否符合Executive Schema 或指定输出Schema。

### block_p0191_b018

校验项包括：

### block_p0191_b019

1. 必填字段是否存在。

### block_p0191_b020

2. 字段类型是否正确。

### block_p0191_b021

3. 枚举值是否合法。

### block_p0191_b022

4. decision_required = true 时，decision_items 是否非空。

### block_p0191_b023

5. 每个决策项是否包含候选方案。

### block_p0191_b024

6. 每个任务草案是否包含标题、负责人或角色、优先级和来源。

### block_p0191_b025

7. source_summary_ids 是否存在。

### block_p0191_b026

结构校验失败时，不应推送老板，应返回Dream 重新生成或进入人工检查。

### block_p0191_b027

9.8.2来源校验

### block_p0191_b028

来源校验检查Dream 判断是否有数据依据。

### block_p0191_b029

校验项包括：

### block_p0191_b030

1. source_summary_ids 是否真实存在。

### block_p0191_b031

2. 引用Summary 是否属于当前组织。

### block_p0191_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0191_b033

AutoMage-2-MVP 架构设计文档·杨卓191

### block_p0191_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 191

## 表格

无。

## 备注

无。

<!-- 来自 page_0191.md 全文结束 -->

<!-- 来自 page_0192.md 全文开始 -->

# Page 0192

## 原始文本块

### block_p0192_b001

2026 年5 月3 日

### block_p0192_b002

3. 引用Summary 是否在当前时间窗口内。

### block_p0192_b003

4. 引用Summary 是否状态有效。

### block_p0192_b004

5. 高风险判断是否能追溯到Manager Schema。

### block_p0192_b005

6. 决策项是否来自Manager 上推或风险识别。

### block_p0192_b006

没有来源的决策项不应进入老板卡片。

### block_p0192_b007

9.8.3权限校验

### block_p0192_b008

权限校验检查当前Dream / Executive Agent 是否有权读取输入数据和生成输出结果。

### block_p0192_b009

校验项包括：

### block_p0192_b010

1. 当前Agent 是否属于该组织。

### block_p0192_b011

2. 当前Agent 是否具备Executive 权限。

### block_p0192_b012

3. 引用的Manager Summary 是否在授权范围内。

### block_p0192_b013

4. 是否读取了未经授权的员工明细。

### block_p0192_b014

5. 是否试图生成超权限执行任务。

### block_p0192_b015

权限失败时，应拒绝生成正式结果，并写入审计日志。

### block_p0192_b016

9.8.4业务校验

### block_p0192_b017

业务校验检查Dream 输出是否符合业务规则。

### block_p0192_b018

重点校验：

### block_p0192_b019

1. 高风险事项是否错误降级。

### block_p0192_b020

2. 低风险事项是否过度上推。

### block_p0192_b021

3. 决策项是否缺少明确问题。

### block_p0192_b022

4. 任务草案是否过于空泛。

### block_p0192_b023

5. 任务截止时间是否合理。

### block_p0192_b024

6. 决策项是否和历史已确认决策冲突。

### block_p0192_b025

7. 是否重复生成已有未完成决策。

### block_p0192_b026

8. 是否将任务草案当作正式任务。

### block_p0192_b027

业务校验可以先由规则+ 人工抽查完成，后续再逐步自动化。

### block_p0192_b028

9.8.5人工确认校验

### block_p0192_b029

涉及老板级决策或重大任务下发时，必须校验人工确认状态。

### block_p0192_b030

规则如下：

### block_p0192_b031

1. human_confirm_status != confirmed 时，不创建正式任务。

### block_p0192_b032

2. confirmed_by 为空时，不视为已确认。

### block_p0192_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0192_b034

AutoMage-2-MVP 架构设计文档·杨卓192

### block_p0192_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 192

## 表格

无。

## 备注

无。

<!-- 来自 page_0192.md 全文结束 -->

<!-- 来自 page_0193.md 全文开始 -->

# Page 0193

## 原始文本块

### block_p0193_b001

2026 年5 月3 日

### block_p0193_b002

3. confirmed_at 为空时，不视为已确认。

### block_p0193_b003

4. 确认人无权限时，确认无效。

### block_p0193_b004

5. 确认后任务生成必须写入审计日志。

### block_p0193_b005

Dream 可以生成建议，但不能替代老板确认。

### block_p0193_b006

9.9Dream 与Executive Schema 的关系

### block_p0193_b007

Dream 是Executive Schema 的生成逻辑，Executive Schema 是Dream 的结构化输出。

### block_p0193_b008

二者关系如下：

### block_p0193_b009

Dream 读取输入数据

### block_p0193_b010

↓

### block_p0193_b011

Dream 生成组织级分析

### block_p0193_b012

↓

### block_p0193_b013

输出schema_v1_executive

### block_p0193_b014

↓

### block_p0193_b015

Executive Agent 推送老板决策卡片

### block_p0193_b016

Dream 输出与Executive Schema 字段的映射如下：

### block_p0193_b017

Dream 输出Executive Schema 字段

### block_p0193_b018

组织级摘要business_summary

### block_p0193_b019

关键风险key_risks

### block_p0193_b020

是否需要老板确认decision_required

### block_p0193_b021

老板决策项decision_items

### block_p0193_b022

推荐方案recommended_option

### block_p0193_b023

推荐理由reasoning_summary

### block_p0193_b024

预期影响expected_impact

### block_p0193_b025

任务草案generated_tasks

### block_p0193_b026

来源部门汇总source_summary_ids

### block_p0193_b027

人工确认状态human_confirm_status

### block_p0193_b028

Dream 不应绕开Executive Schema 直接给老板发一段自由文本。老板侧展示可以是卡片

### block_p0193_b029

或自然语言，但底层数据必须先进入Executive Schema，这样后续才能确认、写库、生成任

### block_p0193_b030

务和审计。

### block_p0193_b031

MVP 阶段建议将Dream 的正式输出统一设为：

### block_p0193_b032

schema_v1_executive

### block_p0193_b033

如果后续需要更复杂的Dream 运行记录，可以新增dream_runs 表记录输入、输出、状

### block_p0193_b034

态和错误信息。

### block_p0193_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0193_b036

AutoMage-2-MVP 架构设计文档·杨卓193

### block_p0193_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 193

## 表格

无。

## 备注

无。

<!-- 来自 page_0193.md 全文结束 -->

<!-- 来自 page_0194.md 全文开始 -->

# Page 0194

## 原始文本块

### block_p0194_b001

2026 年5 月3 日

### block_p0194_b002

9.10Dream 与任务生成的关系

### block_p0194_b003

Dream 可以生成任务草案，但不能直接生成正式任务，除非该任务属于低风险自动处理

### block_p0194_b004

范围。

### block_p0194_b005

MVP 阶段的原则是：

### block_p0194_b006

Dream 生成任务草案；

### block_p0194_b007

老板或Manager 确认后；

### block_p0194_b008

后端创建正式任务。

### block_p0194_b009

9.10.1任务草案生成

### block_p0194_b010

Dream 在以下情况下可以生成任务草案：

### block_p0194_b011

1. 老板决策项确认后必然需要执行。

### block_p0194_b012

2. 某个风险需要明确负责人处理。

### block_p0194_b013

3. 某个部门需要调整次日重点。

### block_p0194_b014

4. 某个历史任务长期阻塞，需要补救任务。

### block_p0194_b015

5. 某个缺失数据需要催办。

### block_p0194_b016

任务草案应包含：

### block_p0194_b017

1. 标题。

### block_p0194_b018

2. 描述。

### block_p0194_b019

3. 所属部门。

### block_p0194_b020

4. 负责人或负责人角色。

### block_p0194_b021

5. 优先级。

### block_p0194_b022

6. 截止时间。

### block_p0194_b023

7. 来源决策或来源风险。

### block_p0194_b024

8. 预期产出。

### block_p0194_b025

9.10.2正式任务生成

### block_p0194_b026

正式任务只能由后端在确认后创建。

### block_p0194_b027

创建条件包括：

### block_p0194_b028

1. 决策状态为confirmed。

### block_p0194_b029

2. 确认人具备权限。

### block_p0194_b030

3. 任务草案通过校验。

### block_p0194_b031

4. 任务来源明确。

### block_p0194_b032

5. 没有重复任务。

### block_p0194_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0194_b034

AutoMage-2-MVP 架构设计文档·杨卓194

### block_p0194_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 194

## 表格

无。

## 备注

无。

<!-- 来自 page_0194.md 全文结束 -->

<!-- 来自 page_0195.md 全文开始 -->

# Page 0195

## 原始文本块

### block_p0195_b001

2026 年5 月3 日

### block_p0195_b002

6. 任务负责人或负责人角色明确。

### block_p0195_b003

创建后应写入：

### block_p0195_b004

1. tasks。

### block_p0195_b005

2. task_assignments。

### block_p0195_b006

3. task_updates。

### block_p0195_b007

4. audit_logs。

### block_p0195_b008

9.10.3任务分发

### block_p0195_b009

任务创建后，根据任务类型分发：

### block_p0195_b010

任务类型分发对象

### block_p0195_b011

具体执行任务Staff Agent

### block_p0195_b012

部门拆解任务Manager Agent

### block_p0195_b013

跨部门任务多个Manager Agent

### block_p0195_b014

老板追踪任务Executive Agent 保留跟踪

### block_p0195_b015

数据补全任务对应Staff / Manager Agent

### block_p0195_b016

任务分发不应只停留在IM 通知。正式任务状态必须保存在数据库中。

### block_p0195_b017

9.10.4任务结果回流

### block_p0195_b018

任务执行结果最终应回流到Staff Schema 或Manager Schema。

### block_p0195_b019

例如：

### block_p0195_b020

老板确认任务

### block_p0195_b021

↓

### block_p0195_b022

任务下发给员工

### block_p0195_b023

↓

### block_p0195_b024

员工执行

### block_p0195_b025

↓

### block_p0195_b026

Staff Agent 在日报中记录任务进展

### block_p0195_b027

↓

### block_p0195_b028

Manager Agent 汇总任务结果

### block_p0195_b029

↓

### block_p0195_b030

Dream 次日判断该决策是否有效

### block_p0195_b031

这一步是Dream 闭环的关键。否则Dream 只会不断生成新建议，却无法判断旧建议是

### block_p0195_b032

否被执行。

### block_p0195_b033

9.11Dream 失败时的降级策略

### block_p0195_b034

Dream 失败不能导致整个系统停止运行。MVP 阶段必须设计降级策略，保证即使Dream

### block_p0195_b035

没有成功生成，员工日报、部门汇总和任务系统仍然可以继续工作。

### block_p0195_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0195_b037

AutoMage-2-MVP 架构设计文档·杨卓195

### block_p0195_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 195

## 表格

无。

## 备注

无。

<!-- 来自 page_0195.md 全文结束 -->

<!-- 来自 page_0196.md 全文开始 -->

# Page 0196

## 原始文本块

### block_p0196_b001

2026 年5 月3 日

### block_p0196_b002

9.11.1常见失败类型

### block_p0196_b003

Dream 失败可能来自以下原因：

### block_p0196_b004

失败类型示例

### block_p0196_b005

输入缺失部门未生成Manager Schema

### block_p0196_b006

数据质量差大量员工日报缺失或未确认

### block_p0196_b007

Schema 校验失败Dream 输出不符合Executive Schema

### block_p0196_b008

模型调用失败LLM 超时或返回异常

### block_p0196_b009

权限失败Executive Agent 无权读取某些汇总

### block_p0196_b010

业务冲突生成的决策与历史决策冲突

### block_p0196_b011

任务草案不合格缺少负责人、截止时间或来源

### block_p0196_b012

推送失败IM 卡片发送失败

### block_p0196_b013

9.11.2降级策略一：生成简版摘要

### block_p0196_b014

如果完整Dream 失败，但Manager Schema 可读，系统可以生成简版摘要。

### block_p0196_b015

简版摘要只包含：

### block_p0196_b016

1. 各部门健康度。

### block_p0196_b017

2. 关键风险列表。

### block_p0196_b018

3. 缺失数据说明。

### block_p0196_b019

4. 暂无决策项提示。

### block_p0196_b020

示例：

### block_p0196_b021

今日Dream 完整分析未完成，已生成简版摘要：

### block_p0196_b022

架构组：yellow，主要风险为Decision 表结构未确认。

### block_p0196_b023

后端组：green，暂无高风险。

### block_p0196_b024

客制化组：yellow，存在接口契约待确认问题。

### block_p0196_b025

简版摘要不生成任务，只用于老板了解情况。

### block_p0196_b026

9.11.3降级策略二：只转发Manager 上推事项

### block_p0196_b027

如果Dream 无法完成综合分析，但Manager Schema 中已有need_executive_decision，

### block_p0196_b028

系统可以先将这些事项转成基础老板卡片。

### block_p0196_b029

此时不做复杂推荐，只展示：

### block_p0196_b030

1. 上推部门。

### block_p0196_b031

2. 决策标题。

### block_p0196_b032

3. 背景说明。

### block_p0196_b033

4. Manager 推荐方案。

### block_p0196_b034

5. 来源Summary。

### block_p0196_b035

这样可以保证紧急决策不被Dream 失败阻塞。

### block_p0196_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0196_b037

AutoMage-2-MVP 架构设计文档·杨卓196

### block_p0196_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 196

## 表格

无。

## 备注

无。

<!-- 来自 page_0196.md 全文结束 -->

<!-- 来自 page_0197.md 全文开始 -->

# Page 0197

## 原始文本块

### block_p0197_b001

2026 年5 月3 日

### block_p0197_b002

9.11.4降级策略三：延迟重试

### block_p0197_b003

如果失败原因是模型超时、接口异常或IM 推送失败，可以延迟重试。

### block_p0197_b004

建议重试策略：

### block_p0197_b005

次数间隔

### block_p0197_b006

第1 次1 分钟

### block_p0197_b007

第2 次5 分钟

### block_p0197_b008

第3 次15 分钟

### block_p0197_b009

第4 次通知管理员

### block_p0197_b010

重试时必须使用同一个运行ID 或幂等键，避免重复生成多个老板决策卡片。

### block_p0197_b011

9.11.5降级策略四：人工接管

### block_p0197_b012

如果Dream 连续失败，系统应通知项目管理员或相关负责人。

### block_p0197_b013

人工接管内容包括：

### block_p0197_b014

1. 查看失败原因。

### block_p0197_b015

2. 查看输入数据是否完整。

### block_p0197_b016

3. 手动触发重新运行。

### block_p0197_b017

4. 手动生成老板摘要。

### block_p0197_b018

5. 暂停某些错误输出。

### block_p0197_b019

6. 标记本次Dream 失败原因。

### block_p0197_b020

MVP 阶段人工接管是可以接受的。优先保证主链路可演示，不要求所有异常完全自动化。

### block_p0197_b021

9.11.6失败记录

### block_p0197_b022

Dream 失败必须写入审计或运行日志。

### block_p0197_b023

建议记录：

### block_p0197_b024

1. 运行ID。

### block_p0197_b025

2. 运行时间。

### block_p0197_b026

3. 输入范围。

### block_p0197_b027

4. 失败阶段。

### block_p0197_b028

5. 失败原因。

### block_p0197_b029

6. 是否重试。

### block_p0197_b030

7. 是否降级。

### block_p0197_b031

8. 最终状态。

### block_p0197_b032

9. 错误摘要。

### block_p0197_b033

10. 相关Agent 节点。

### block_p0197_b034

后续优化Dream 机制时，这些失败记录非常重要。

### block_p0197_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0197_b036

AutoMage-2-MVP 架构设计文档·杨卓197

### block_p0197_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 197

## 表格

无。

## 备注

无。

<!-- 来自 page_0197.md 全文结束 -->

<!-- 来自 page_0198.md 全文开始 -->

# Page 0198

## 原始文本块

### block_p0198_b001

2026 年5 月3 日

### block_p0198_b002

9.12Dream 结果的人工确认机制

### block_p0198_b003

Dream 结果进入执行链路前，必须区分“可直接参考”和“需要人工确认”。

### block_p0198_b004

MVP 阶段建议采用以下原则：

### block_p0198_b005

摘要可以直接展示；

### block_p0198_b006

风险可以直接提醒；

### block_p0198_b007

决策必须人工确认；

### block_p0198_b008

任务下发必须基于确认状态。

### block_p0198_b009

9.12.1不同输出的确认要求

### block_p0198_b010

Dream 输出是否需要确认说明

### block_p0198_b011

公司级摘要不强制确认可直接展示给老板

### block_p0198_b012

风险预警不强制确认可直接提醒，但不自动执行

### block_p0198_b013

部门调整建议Manager 确认后执行影响部门任务时需确认

### block_p0198_b014

老板决策项必须老板确认确认后才可执行

### block_p0198_b015

任务草案必须基于确认生成草案不是正式任务

### block_p0198_b016

次日重点可由Manager 确认可作为提醒或任务来源

### block_p0198_b017

9.12.2老板确认

### block_p0198_b018

老板确认Dream 决策项时，应至少记录：

### block_p0198_b019

1. 确认人。

### block_p0198_b020

2. 确认时间。

### block_p0198_b021

3. 选择方案。

### block_p0198_b022

4. 是否修改方案。

### block_p0198_b023

5. 确认来源。

### block_p0198_b024

6. 决策内容哈希。

### block_p0198_b025

7. 生成任务列表。

### block_p0198_b026

确认后状态从：

### block_p0198_b027

pending

### block_p0198_b028

变为：

### block_p0198_b029

confirmed

### block_p0198_b030

随后后端才创建正式任务。

### block_p0198_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0198_b032

AutoMage-2-MVP 架构设计文档·杨卓198

### block_p0198_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 198

## 表格

无。

## 备注

无。

<!-- 来自 page_0198.md 全文结束 -->

<!-- 来自 page_0199.md 全文开始 -->

# Page 0199

## 原始文本块

### block_p0199_b001

2026 年5 月3 日

### block_p0199_b002

9.12.3Manager 确认

### block_p0199_b003

部门调整建议如果影响部门任务，应由Manager 确认。

### block_p0199_b004

例如Dream 建议“明天优先处理Decision 表结构”，这可以先推给Manager。Manager

### block_p0199_b005

确认后，再拆成Staff 任务。

### block_p0199_b006

Manager 确认内容包括：

### block_p0199_b007

1. 是否接受调整建议。

### block_p0199_b008

2. 是否生成任务。

### block_p0199_b009

3. 分配给谁。

### block_p0199_b010

4. 截止时间。

### block_p0199_b011

5. 优先级。

### block_p0199_b012

9.12.4修改确认

### block_p0199_b013

老板或Manager 可以不接受Dream 的原始建议，而是修改后确认。

### block_p0199_b014

系统应保留：

### block_p0199_b015

1. Dream 原始建议。

### block_p0199_b016

2. 人工修改内容。

### block_p0199_b017

3. 最终确认内容。

### block_p0199_b018

4. 修改人。

### block_p0199_b019

5. 修改时间。

### block_p0199_b020

6. 修改原因。

### block_p0199_b021

不要覆盖原始Dream 输出。这样后续才能复盘Dream 建议质量。

### block_p0199_b022

9.12.5驳回与补充信息

### block_p0199_b023

如果老板驳回Dream 决策项，应记录驳回原因，并通知相关Manager。

### block_p0199_b024

如果老板要求补充信息，系统应将该请求回传给对应Manager Agent 或Staff Agent。

### block_p0199_b025

流程如下：

### block_p0199_b026

老板要求补充信息

### block_p0199_b027

↓

### block_p0199_b028

Executive Agent 记录问题

### block_p0199_b029

↓

### block_p0199_b030

相关Manager Agent 补充来源数据

### block_p0199_b031

↓

### block_p0199_b032

Dream 局部重新生成

### block_p0199_b033

↓

### block_p0199_b034

再次推送老板确认

### block_p0199_b035

补充信息期间，不生成正式任务。

### block_p0199_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0199_b037

AutoMage-2-MVP 架构设计文档·杨卓199

### block_p0199_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 199

## 表格

无。

## 备注

无。

<!-- 来自 page_0199.md 全文结束 -->

<!-- 来自 page_0200.md 全文开始 -->

# Page 0200

## 原始文本块

### block_p0200_b001

2026 年5 月3 日

### block_p0200_b002

9.12.6人工确认后的审计

### block_p0200_b003

所有人工确认行为必须写入审计日志。

### block_p0200_b004

审计事件包括：

### block_p0200_b005

1. dream_result_generated

### block_p0200_b006

2. dream_result_pushed

### block_p0200_b007

3. dream_decision_confirmed

### block_p0200_b008

4. dream_decision_rejected

### block_p0200_b009

5. dream_decision_modified

### block_p0200_b010

6. dream_need_more_info

### block_p0200_b011

7. dream_task_generated

### block_p0200_b012

审计记录至少包含：

### block_p0200_b013

1. 操作人。

### block_p0200_b014

2. 操作时间。

### block_p0200_b015

3. 操作对象。

### block_p0200_b016

4. 原始Dream 输出。

### block_p0200_b017

5. 人工确认内容。

### block_p0200_b018

6. 生成任务。

### block_p0200_b019

7. 来源Summary。

### block_p0200_b020

8. 渠道信息。

### block_p0200_b021

9.13本章小结

### block_p0200_b022

Dream 是AutoMage-2 MVP 中负责组织级复盘、风险识别和老板决策生成的核心机制。

### block_p0200_b023

它向下读取Staff、Manager、Summary、Decision、Task 等结构化数据，向上输出老板决

### block_p0200_b024

策项、风险预警、任务拆解和次日重点。它不直接替老板拍板，也不直接绕过确认生成重大

### block_p0200_b025

任务，而是把复杂的组织信息整理成可判断、可确认、可执行的结构化结果。

### block_p0200_b026

MVP 阶段，Dream 只需要先跑通一条最小链路：

### block_p0200_b027

读取Manager Schema

### block_p0200_b028

→生成组织级摘要

### block_p0200_b029

→识别关键风险

### block_p0200_b030

→生成老板决策项

### block_p0200_b031

→老板确认

### block_p0200_b032

→生成任务草案并下发

### block_p0200_b033

只要这条链路稳定，AutoMage-2 就具备了每日自动复盘和次日任务驱动的基础能力。后

### block_p0200_b034

续再在此基础上扩展长期记忆、趋势分析、跨周期复盘、组织诊断和更复杂的战略推演。

### block_p0200_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0200_b036

AutoMage-2-MVP 架构设计文档·杨卓200

### block_p0200_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 200

## 表格

无。

## 备注

无。

<!-- 来自 page_0200.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

