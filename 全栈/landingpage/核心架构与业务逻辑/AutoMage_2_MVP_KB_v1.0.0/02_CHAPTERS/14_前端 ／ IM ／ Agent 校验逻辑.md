# 前端 / IM / Agent 校验逻辑

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P270-P288
> 对应页面文件：`01_PAGES/page_0270.md` — `01_PAGES/page_0288.md`

## 原文整理

<!-- 来自 page_0270.md 全文开始 -->

# Page 0270

## 原始文本块

### block_p0270_b001

2026 年5 月3 日

### block_p0270_b002

13前端/ IM / Agent 校验逻辑

### block_p0270_b003

13.1校验逻辑总览

### block_p0270_b004

AutoMage-2 MVP 中，数据从用户输入到最终写入数据库，至少会经过四层校验：

### block_p0270_b005

前端/ IM 校验

### block_p0270_b006

↓

### block_p0270_b007

Agent 生成前校验

### block_p0270_b008

↓

### block_p0270_b009

Agent 生成后校验

### block_p0270_b010

↓

### block_p0270_b011

后端Schema / 权限/ 签名校验

### block_p0270_b012

↓

### block_p0270_b013

写入数据库

### block_p0270_b014

这四层校验的职责不同。

### block_p0270_b015

前端和IM 校验主要负责提升用户体验，尽早发现明显缺失和格式错误；Agent 校验主要

### block_p0270_b016

负责保证生成内容符合业务语义和Schema 结构；后端校验负责最终兜底，决定数据是否可

### block_p0270_b017

以进入正式业务流程。

### block_p0270_b018

需要明确一点：前端、IM 和Agent 的校验都不能代替后端校验。

### block_p0270_b019

原因很简单。前端可能被绕过，IM 消息可能不完整，Agent 输出可能不稳定。最终能否

### block_p0270_b020

写入数据库、能否进入Manager 汇总、能否生成老板决策和任务，必须由后端统一判断。

### block_p0270_b021

整体校验职责建议如下：

### block_p0270_b022

校验层主要职责是否最终可信

### block_p0270_b023

前端表单校验检查用户输入是否完整、格式是否明

### block_p0270_b024

显错误

### block_p0270_b025

否

### block_p0270_b026

IM 交互校验引导用户补全关键信息，避免空输入否

### block_p0270_b027

Agent 生成前校验判断输入是否足够生成Schema否

### block_p0270_b028

Agent 生成后校验检查输出是否符合Schema 结构否

### block_p0270_b029

后端Schema 校验校验字段、类型、枚举、权限、签名、

### block_p0270_b030

状态

### block_p0270_b031

是

### block_p0270_b032

数据库约束保证唯一性、外键、状态一致性是

### block_p0270_b033

MVP 阶段建议采用“前面尽量拦，后端必须拦”的策略。前面拦是为了减少用户反复提

### block_p0270_b034

交失败；后端拦是为了保证系统数据可信。

### block_p0270_b035

13.2前端表单校验

### block_p0270_b036

前端表单校验适用于Web、App、小程序或IM 表单场景。它的目标是让用户在提交前

### block_p0270_b037

就知道哪些信息缺失，避免把明显错误的数据交给Agent 或后端。

### block_p0270_b038

前端表单校验主要包括：

### block_p0270_b039

1. 必填字段是否为空。

### block_p0270_b040

2. 字段长度是否超过限制。

### block_p0270_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0270_b042

AutoMage-2-MVP 架构设计文档·杨卓270

### block_p0270_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 270

## 表格

无。

## 备注

无。

<!-- 来自 page_0270.md 全文结束 -->

<!-- 来自 page_0271.md 全文开始 -->

# Page 0271

## 原始文本块

### block_p0271_b001

2026 年5 月3 日

### block_p0271_b002

3. 数字、日期、布尔值格式是否正确。

### block_p0271_b003

4. 枚举选项是否在允许范围内。

### block_p0271_b004

5. 条件必填字段是否已填写。

### block_p0271_b005

6. 文件、链接、附件格式是否合理。

### block_p0271_b006

7. 用户是否进行了确认动作。

### block_p0271_b007

以前端Staff 日报表单为例，至少应校验：

### block_p0271_b008

字段前端校验规则

### block_p0271_b009

今日完成事项至少填写一项

### block_p0271_b010

明日计划至少填写一项

### block_p0271_b011

是否需要支持必须选择是或否

### block_p0271_b012

支持详情当选择“需要支持”时必填

### block_p0271_b013

风险等级必须从枚举中选择

### block_p0271_b014

产出物链接如果填写，必须是合法URL

### block_p0271_b015

确认提交必须由员工主动点击确认

### block_p0271_b016

前端展示文案可以面向用户优化，但提交字段必须与Schema 保持一致。

### block_p0271_b017

例如，页面上可以展示为：

### block_p0271_b018

今日完成事项

### block_p0271_b019

但提交给后端时应使用：

### block_p0271_b020

{

### block_p0271_b021

"work_progress": []

### block_p0271_b022

}

### block_p0271_b023

前端校验不应做过重的业务判断。例如，前端不需要判断某个风险是否应该上推老板，也

### block_p0271_b024

不需要判断Manager 是否有权读取某部门数据。这些应交给Agent 和后端处理。

### block_p0271_b025

前端校验失败时，应提示用户具体字段，而不是只提示“提交失败”。

### block_p0271_b026

不推荐：

### block_p0271_b027

提交失败，请检查。

### block_p0271_b028

推荐：

### block_p0271_b029

请补充“需要支持的具体内容”。你已选择需要上级支持，但尚未说明需要谁支持、支持什么事项。

### block_p0271_b030

13.3Agent 生成前校验

### block_p0271_b031

Agent 生成前校验发生在Agent 准备把用户输入转成Schema 之前。

### block_p0271_b032

它的目标是判断当前输入是否足够生成结构化数据。如果信息明显不足，Agent 应先追

### block_p0271_b033

问，而不是强行生成一个看似完整但实际编造的Schema。

### block_p0271_b034

以Staff Agent 为例，员工可能只输入：

### block_p0271_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0271_b036

AutoMage-2-MVP 架构设计文档·杨卓271

### block_p0271_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 271

## 表格

无。

## 备注

无。

<!-- 来自 page_0271.md 全文结束 -->

<!-- 来自 page_0272.md 全文开始 -->

# Page 0272

## 原始文本块

### block_p0272_b001

2026 年5 月3 日

### block_p0272_b002

今天正常推进，明天继续。

### block_p0272_b003

这类输入不足以生成正式Staff Schema。Agent 应追问：

### block_p0272_b004

请补充至少一项今日完成事项，并说明当前状态是已完成、进行中还是阻塞。

### block_p0272_b005

Agent 生成前需要检查：

### block_p0272_b006

检查项说明

### block_p0272_b007

输入是否为空空消息不能生成Schema

### block_p0272_b008

是否包含核心业务内容不能只有“正常”“继续”“OK”

### block_p0272_b009

是否缺少必填字段缺字段先追问

### block_p0272_b010

是否存在明显矛盾例如说无问题，但又说需要支持

### block_p0272_b011

是否缺少确认动作生成前可整理，提交前必须确认

### block_p0272_b012

是否越权请求用户要求查看无权数据时拒绝

### block_p0272_b013

是否需要更多上下文缺少来源任务、部门、日期时补问

### block_p0272_b014

不同Agent 的生成前校验重点不同。

### block_p0272_b015

Staff Agent 重点检查员工输入是否足够生成日报。Manager Agent 重点检查是否已经读

### block_p0272_b016

取到足够的Staff Schema。Executive Agent 重点检查是否有可用的Manager Schema 和来源

### block_p0272_b017

数据。Dream 重点检查输入窗口内的数据是否完整、是否已确认、是否可用于老板决策。

### block_p0272_b018

Agent 生成前校验的原则是：不够就问，不清楚就标记，不编造。

### block_p0272_b019

13.4Agent 生成后校验

### block_p0272_b020

Agent 生成后校验发生在Agent 已经输出Schema，但尚未调用后端接口之前。

### block_p0272_b021

这个阶段主要检查Agent 输出是否符合预期结构，减少后端422 错误。

### block_p0272_b022

Agent 生成后至少需要校验：

### block_p0272_b023

1. 是否为合法JSON。

### block_p0272_b024

2. 是否包含schema_id。

### block_p0272_b025

3. 是否包含schema_version。

### block_p0272_b026

4. 必填字段是否存在。

### block_p0272_b027

5. 字段类型是否正确。

### block_p0272_b028

6. 枚举值是否在允许范围内。

### block_p0272_b029

7. 条件必填字段是否满足。

### block_p0272_b030

8. 来源ID 是否存在。

### block_p0272_b031

9. 签名状态是否合理。

### block_p0272_b032

10. 是否存在多余且危险的字段。

### block_p0272_b033

例如Staff Schema 生成后，Agent 应检查：

### block_p0272_b034

need_support = true 时，support_detail 是否填写

### block_p0272_b035

work_progress 是否为数组

### block_p0272_b036

risk_level 是否属于low / medium / high / critical

### block_p0272_b037

signature 是否为pending 或signed

### block_p0272_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0272_b039

AutoMage-2-MVP 架构设计文档·杨卓272

### block_p0272_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 272

## 表格

无。

## 备注

无。

<!-- 来自 page_0272.md 全文结束 -->

<!-- 来自 page_0273.md 全文开始 -->

# Page 0273

## 原始文本块

### block_p0273_b001

2026 年5 月3 日

### block_p0273_b002

如果Agent 生成后发现错误，应优先在本地修正或追问用户，而不是直接提交后端。

### block_p0273_b003

示例：

### block_p0273_b004

我整理出的日报中缺少“明日计划”。请补充至少一项明天准备完成的事项。

### block_p0273_b005

Agent 生成后校验还应防止自由文本污染正式JSON。正式提交给后端的数据不能夹杂

### block_p0273_b006

解释性文字。

### block_p0273_b007

不推荐提交：

### block_p0273_b008

下面是整理好的JSON：

### block_p0273_b009

{

### block_p0273_b010

...

### block_p0273_b011

}

### block_p0273_b012

请查收。

### block_p0273_b013

推荐提交：

### block_p0273_b014

{

### block_p0273_b015

"schema_id": "schema_v1_staff",

### block_p0273_b016

"schema_version": "1.0.0"

### block_p0273_b017

}

### block_p0273_b018

Agent 可以在聊天里展示摘要，但调用API 时必须只传结构化JSON。

### block_p0273_b019

13.5后端Schema 校验

### block_p0273_b020

后端Schema 校验是最终校验层。所有正式进入数据库、参与上级汇总、生成决策和任务

### block_p0273_b021

的数据，都必须通过后端校验。

### block_p0273_b022

后端校验至少包括：

### block_p0273_b023

1. Schema ID 是否存在。

### block_p0273_b024

2. Schema 版本是否支持。

### block_p0273_b025

3. 必填字段是否完整。

### block_p0273_b026

4. 字段类型是否正确。

### block_p0273_b027

5. 枚举值是否合法。

### block_p0273_b028

6. 条件必填是否满足。

### block_p0273_b029

7. 字段长度是否超限。

### block_p0273_b030

8. 来源对象是否存在。

### block_p0273_b031

9. 当前用户是否有权限。

### block_p0273_b032

10. 当前Agent 是否有权限。

### block_p0273_b033

11. 签名状态是否满足要求。

### block_p0273_b034

12. 是否重复提交。

### block_p0273_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0273_b036

AutoMage-2-MVP 架构设计文档·杨卓273

### block_p0273_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 273

## 表格

无。

## 备注

无。

<!-- 来自 page_0273.md 全文结束 -->

<!-- 来自 page_0274.md 全文开始 -->

# Page 0274

## 原始文本块

### block_p0274_b001

2026 年5 月3 日

### block_p0274_b002

13. 状态流转是否合法。

### block_p0274_b003

14. 幂等键是否重复。

### block_p0274_b004

后端收到数据后，不应因为Agent “看起来生成得对”就直接写库。

### block_p0274_b005

推荐校验流程如下：

### block_p0274_b006

接收请求

### block_p0274_b007

↓

### block_p0274_b008

鉴权

### block_p0274_b009

↓

### block_p0274_b010

识别schema_id / schema_version

### block_p0274_b011

↓

### block_p0274_b012

加载对应校验规则

### block_p0274_b013

↓

### block_p0274_b014

字段和类型校验

### block_p0274_b015

↓

### block_p0274_b016

业务规则校验

### block_p0274_b017

↓

### block_p0274_b018

权限校验

### block_p0274_b019

↓

### block_p0274_b020

签名校验

### block_p0274_b021

↓

### block_p0274_b022

幂等校验

### block_p0274_b023

↓

### block_p0274_b024

写入数据库

### block_p0274_b025

↓

### block_p0274_b026

写入审计日志

### block_p0274_b027

后端校验失败时，应返回明确错误结构，方便Agent 或前端修正。

### block_p0274_b028

推荐错误格式：

### block_p0274_b029

{

### block_p0274_b030

"code": "SCHEMA_VALIDATION_FAILED",

### block_p0274_b031

"message": "Schema 校验失败",

### block_p0274_b032

"errors": [

### block_p0274_b033

{

### block_p0274_b034

"field": "support_detail",

### block_p0274_b035

"reason": "need_support 为true 时，support_detail 必填"

### block_p0274_b036

}

### block_p0274_b037

]

### block_p0274_b038

}

### block_p0274_b039

这样Agent 可以准确追问用户，而不是让用户重新填写整份内容。

### block_p0274_b040

13.6字段类型校验

### block_p0274_b041

字段类型校验用于保证每个字段的数据类型稳定。类型不稳定会导致后端解析、数据库

### block_p0274_b042

存储、Agent 汇总和前端展示全部变复杂。

### block_p0274_b043 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0274_b044

AutoMage-2-MVP 架构设计文档·杨卓274

### block_p0274_b045 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 274

## 表格

无。

## 备注

无。

<!-- 来自 page_0274.md 全文结束 -->

<!-- 来自 page_0275.md 全文开始 -->

# Page 0275

## 原始文本块

### block_p0275_b001

2026 年5 月3 日

### block_p0275_b002

MVP 阶段常见字段类型包括：

### block_p0275_b003

类型示例

### block_p0275_b004

string"schema_v1_staff"

### block_p0275_b005

number10086

### block_p0275_b006

booleantrue

### block_p0275_b007

array[301, 302]

### block_p0275_b008

object{ "score": 78 }

### block_p0275_b009

datetime"2026-05-04T18:00:00+08:00"

### block_p0275_b010

date"2026-05-04"

### block_p0275_b011

类型校验要求如下：

### block_p0275_b012

13.6.1string 字段

### block_p0275_b013

字符串字段必须是字符串，不能传对象或数组。

### block_p0275_b014

示例：

### block_p0275_b015

{

### block_p0275_b016

"risk_level": "high"

### block_p0275_b017

}

### block_p0275_b018

不允许：

### block_p0275_b019

{

### block_p0275_b020

"risk_level": ["high"]

### block_p0275_b021

}

### block_p0275_b022

13.6.2boolean 字段

### block_p0275_b023

布尔字段必须是true 或false，不能用中文或数字代替。

### block_p0275_b024

正确：

### block_p0275_b025

{

### block_p0275_b026

"need_support": true

### block_p0275_b027

}

### block_p0275_b028

错误：

### block_p0275_b029

{

### block_p0275_b030

"need_support": " 需要"

### block_p0275_b031

}

### block_p0275_b032

13.6.3array 字段

### block_p0275_b033

数组字段必须是数组。即使只有一项，也应使用数组。

### block_p0275_b034

正确：

### block_p0275_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0275_b036

AutoMage-2-MVP 架构设计文档·杨卓275

### block_p0275_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 275

## 表格

无。

## 备注

无。

<!-- 来自 page_0275.md 全文结束 -->

<!-- 来自 page_0276.md 全文开始 -->

# Page 0276

## 原始文本块

### block_p0276_b001

2026 年5 月3 日

### block_p0276_b002

{

### block_p0276_b003

"source_record_ids": [301]

### block_p0276_b004

}

### block_p0276_b005

错误：

### block_p0276_b006

{

### block_p0276_b007

"source_record_ids": 301

### block_p0276_b008

}

### block_p0276_b009

13.6.4object 字段

### block_p0276_b010

对象字段必须是结构化对象，不能直接塞入长文本。

### block_p0276_b011

正确：

### block_p0276_b012

{

### block_p0276_b013

"signature": {

### block_p0276_b014

"signature_status": "signed",

### block_p0276_b015

"signed_by": 10086

### block_p0276_b016

}

### block_p0276_b017

}

### block_p0276_b018

错误：

### block_p0276_b019

{

### block_p0276_b020

"signature": " 员工已确认"

### block_p0276_b021

}

### block_p0276_b022

13.6.5datetime 字段

### block_p0276_b023

时间字段建议统一使用ISO8601 格式。

### block_p0276_b024

正确：

### block_p0276_b025

{

### block_p0276_b026

"timestamp": "2026-05-04T18:00:00+08:00"

### block_p0276_b027

}

### block_p0276_b028

错误：

### block_p0276_b029

{

### block_p0276_b030

"timestamp": " 今天下午六点"

### block_p0276_b031

}

### block_p0276_b032

类型校验失败应返回422，不应由后端自动猜测和转换。例如"true" 不应自动转成true，

### block_p0276_b033

否则容易隐藏前端或Agent 的问题。

### block_p0276_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0276_b035

AutoMage-2-MVP 架构设计文档·杨卓276

### block_p0276_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 276

## 表格

无。

## 备注

无。

<!-- 来自 page_0276.md 全文结束 -->

<!-- 来自 page_0277.md 全文开始 -->

# Page 0277

## 原始文本块

### block_p0277_b001

2026 年5 月3 日

### block_p0277_b002

13.7必填字段校验

### block_p0277_b003

必填字段校验用于保证每个Schema 具备最小可用数据。

### block_p0277_b004

不同Schema 的必填字段不同，但都应包含基础身份、来源、核心内容和状态信息。

### block_p0277_b005

13.7.1Staff Schema 必填字段

### block_p0277_b006

字段说明

### block_p0277_b007

schema_id标识Schema 类型

### block_p0277_b008

schema_version标识版本

### block_p0277_b009

timestamp提交时间

### block_p0277_b010

org_id组织ID

### block_p0277_b011

department_id部门ID

### block_p0277_b012

user_id员工ID

### block_p0277_b013

node_idStaff Agent 节点

### block_p0277_b014

record_date日报日期

### block_p0277_b015

work_progress今日完成事项

### block_p0277_b016

need_support是否需要支持

### block_p0277_b017

next_day_plan明日计划

### block_p0277_b018

risk_level风险等级

### block_p0277_b019

signature员工确认信息

### block_p0277_b020

13.7.2Manager Schema 必填字段

### block_p0277_b021

字段说明

### block_p0277_b022

schema_id标识Schema 类型

### block_p0277_b023

schema_version标识版本

### block_p0277_b024

timestamp汇总生成时间

### block_p0277_b025

org_id组织ID

### block_p0277_b026

dept_id部门ID

### block_p0277_b027

manager_user_id部门负责人

### block_p0277_b028

manager_node_idManager Agent 节点

### block_p0277_b029

summary_date汇总日期

### block_p0277_b030

staff_report_count读取日报数量

### block_p0277_b031

missing_report_count缺失日报数量

### block_p0277_b032

overall_health部门健康度

### block_p0277_b033

aggregated_summary部门摘要

### block_p0277_b034

top_3_risks主要风险

### block_p0277_b035

pending_approvals待上推事项数量

### block_p0277_b036

next_day_adjustment次日调整建议

### block_p0277_b037

source_record_ids来源日报

### block_p0277_b038

signatureManager 确认信息

### block_p0277_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0277_b040

AutoMage-2-MVP 架构设计文档·杨卓277

### block_p0277_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 277

## 表格

无。

## 备注

无。

<!-- 来自 page_0277.md 全文结束 -->

<!-- 来自 page_0278.md 全文开始 -->

# Page 0278

## 原始文本块

### block_p0278_b001

2026 年5 月3 日

### block_p0278_b002

13.7.3Executive Schema 必填字段

### block_p0278_b003

字段说明

### block_p0278_b004

schema_id标识Schema 类型

### block_p0278_b005

schema_version标识版本

### block_p0278_b006

timestamp生成时间

### block_p0278_b007

org_id组织ID

### block_p0278_b008

executive_user_id老板/ 高管ID

### block_p0278_b009

executive_node_idExecutive Agent 节点

### block_p0278_b010

summary_date摘要日期

### block_p0278_b011

business_summary组织级摘要

### block_p0278_b012

key_risks关键风险

### block_p0278_b013

decision_required是否需要老板确认

### block_p0278_b014

source_summary_ids来源部门汇总

### block_p0278_b015

human_confirm_status人工确认状态

### block_p0278_b016

必填字段缺失时，后端返回422。Agent 收到后应只追问缺失字段，不要要求用户重填全

### block_p0278_b017

部内容。

### block_p0278_b018

13.8枚举值校验

### block_p0278_b019

枚举值校验用于保证状态、等级、类型等字段使用统一值，避免同一个意思出现多种写

### block_p0278_b020

法。

### block_p0278_b021

例如风险等级应统一为：

### block_p0278_b022

low / medium / high / critical

### block_p0278_b023

不能出现：

### block_p0278_b024

低/ 中/ 高/ 严重/ 紧急/ 很危险

### block_p0278_b025

MVP 阶段建议统一以下枚举。

### block_p0278_b026

13.8.1风险等级

### block_p0278_b027

值含义

### block_p0278_b028

low低风险

### block_p0278_b029

medium中风险

### block_p0278_b030

high高风险

### block_p0278_b031

critical严重风险

### block_p0278_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0278_b033

AutoMage-2-MVP 架构设计文档·杨卓278

### block_p0278_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 278

## 表格

无。

## 备注

无。

<!-- 来自 page_0278.md 全文结束 -->

<!-- 来自 page_0279.md 全文开始 -->

# Page 0279

## 原始文本块

### block_p0279_b001

2026 年5 月3 日

### block_p0279_b002

13.8.2部门健康度

### block_p0279_b003

值含义

### block_p0279_b004

green正常

### block_p0279_b005

yellow有风险但可控

### block_p0279_b006

red高风险

### block_p0279_b007

gray数据不足

### block_p0279_b008

13.8.3任务优先级

### block_p0279_b009

值含义

### block_p0279_b010

——––

### block_p0279_b011

urgent紧急

### block_p0279_b012

high高

### block_p0279_b013

medium中

### block_p0279_b014

low低

### block_p0279_b015

13.8.4任务状态

### block_p0279_b016

值含义

### block_p0279_b017

pending待处理

### block_p0279_b018

in_progress进行中

### block_p0279_b019

blocked阻塞

### block_p0279_b020

completed已完成

### block_p0279_b021

closed已关闭

### block_p0279_b022

cancelled已取消

### block_p0279_b023

13.8.5决策状态

### block_p0279_b024

值含义

### block_p0279_b025

draft草稿

### block_p0279_b026

pending待确认

### block_p0279_b027

confirmed已确认

### block_p0279_b028

rejected已驳回

### block_p0279_b029

need_more_info需要补充信息

### block_p0279_b030

task_generated已生成任务

### block_p0279_b031

expired已超时

### block_p0279_b032

closed已关闭

### block_p0279_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0279_b034

AutoMage-2-MVP 架构设计文档·杨卓279

### block_p0279_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 279

## 表格

无。

## 备注

无。

<!-- 来自 page_0279.md 全文结束 -->

<!-- 来自 page_0280.md 全文开始 -->

# Page 0280

## 原始文本块

### block_p0280_b001

2026 年5 月3 日

### block_p0280_b002

13.8.6签名状态

### block_p0280_b003

值含义

### block_p0280_b004

not_required不需要签名

### block_p0280_b005

pending等待签名

### block_p0280_b006

signed已签名

### block_p0280_b007

rejected拒绝签名

### block_p0280_b008

expired签名超时

### block_p0280_b009

invalid签名无效

### block_p0280_b010

revoked签名撤回

### block_p0280_b011

枚举值校验失败时，后端不应自动转换。例如收到" 高"，应返回错误，让Agent 或前

### block_p0280_b012

端转换为"high" 后重新提交。

### block_p0280_b013

13.9权限校验

### block_p0280_b014

权限校验决定当前用户或Agent 是否有权读取、创建、修改、确认某个对象。

### block_p0280_b015

权限校验必须由后端执行，不能只依赖前端隐藏按钮，也不能只依赖Agent Prompt。

### block_p0280_b016

MVP 阶段权限校验至少覆盖四个维度：

### block_p0280_b017

1. 组织维度。

### block_p0280_b018

2. 部门维度。

### block_p0280_b019

3. 用户维度。

### block_p0280_b020

4. Agent 节点维度。

### block_p0280_b021

13.9.1Staff Agent 权限

### block_p0280_b022

Staff Agent 只能操作当前员工个人范围内的数据。

### block_p0280_b023

可操作：

### block_p0280_b024

1. 提交本人Staff Schema。

### block_p0280_b025

2. 查询本人任务。

### block_p0280_b026

3. 更新本人任务状态。

### block_p0280_b027

4. 上报本人异常。

### block_p0280_b028

5. 查看本人历史日报。

### block_p0280_b029

不可操作：

### block_p0280_b030

1. 读取其他员工日报。

### block_p0280_b031

2. 读取部门汇总。

### block_p0280_b032

3. 查看老板决策卡片。

### block_p0280_b033

4. 替其他员工确认日报。

### block_p0280_b034

5. 下发部门任务。

### block_p0280_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0280_b036

AutoMage-2-MVP 架构设计文档·杨卓280

### block_p0280_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 280

## 表格

无。

## 备注

无。

<!-- 来自 page_0280.md 全文结束 -->

<!-- 来自 page_0281.md 全文开始 -->

# Page 0281

## 原始文本块

### block_p0281_b001

2026 年5 月3 日

### block_p0281_b002

13.9.2Manager Agent 权限

### block_p0281_b003

Manager Agent 只能操作本部门范围内的数据。

### block_p0281_b004

可操作：

### block_p0281_b005

1. 读取本部门Staff Schema。

### block_p0281_b006

2. 生成本部门Manager Schema。

### block_p0281_b007

3. 创建本部门任务。

### block_p0281_b008

4. 处理本部门异常。

### block_p0281_b009

5. 上推需老板决策事项。

### block_p0281_b010

不可操作：

### block_p0281_b011

1. 读取其他部门员工明细。

### block_p0281_b012

2. 修改员工原始日报。

### block_p0281_b013

3. 确认老板决策。

### block_p0281_b014

4. 越权生成跨部门任务。

### block_p0281_b015

5. 删除历史审计记录。

### block_p0281_b016

13.9.3Executive Agent 权限

### block_p0281_b017

Executive Agent 可以读取组织级汇总和部门汇总。

### block_p0281_b018

可操作：

### block_p0281_b019

1. 读取Manager Schema。

### block_p0281_b020

2. 生成Executive Schema。

### block_p0281_b021

3. 生成老板决策卡片。

### block_p0281_b022

4. 根据老板确认生成任务。

### block_p0281_b023

5. 追踪组织级风险。

### block_p0281_b024

不可操作：

### block_p0281_b025

1. 绕过老板确认执行重大决策。

### block_p0281_b026

2. 随意读取无关个人隐私明细。

### block_p0281_b027

3. 修改员工原始日报。

### block_p0281_b028

4. 无审计删除决策或任务。

### block_p0281_b029

权限校验失败时：

### block_p0281_b030

错误码含义

### block_p0281_b031

401未认证或登录失效

### block_p0281_b032

403已认证但无权限

### block_p0281_b033

404数据不存在或不可见

### block_p0281_b034

422参数不合法

### block_p0281_b035

建议对于跨部门敏感数据，返回404 或脱敏结果，避免暴露其他部门数据是否存在。

### block_p0281_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0281_b037

AutoMage-2-MVP 架构设计文档·杨卓281

### block_p0281_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 281

## 表格

无。

## 备注

无。

<!-- 来自 page_0281.md 全文结束 -->

<!-- 来自 page_0282.md 全文开始 -->

# Page 0282

## 原始文本块

### block_p0282_b001

2026 年5 月3 日

### block_p0282_b002

13.10签名校验

### block_p0282_b003

签名校验用于判断某个对象是否已经被有权限的人确认，确认后内容是否发生变化。

### block_p0282_b004

签名校验至少包含：

### block_p0282_b005

1. 是否需要签名。

### block_p0282_b006

2. 签名状态是否为signed。

### block_p0282_b007

3. 签名人是否有权限。

### block_p0282_b008

4. 签名时间是否存在。

### block_p0282_b009

5. payload_hash 是否存在。

### block_p0282_b010

6. 当前内容重新计算hash 后是否一致。

### block_p0282_b011

7. 签名是否过期。

### block_p0282_b012

8. 签名后内容是否被修改。

### block_p0282_b013

不同对象的签名要求不同。

### block_p0282_b014

对象签名要求

### block_p0282_b015

Staff 日报员工确认后进入正式汇总

### block_p0282_b016

Manager 汇总高风险和上推事项必须Manager 确认

### block_p0282_b017

Executive 决策老板确认后才能生成任务

### block_p0282_b018

任务完成执行人提交，确认人关闭

### block_p0282_b019

异常关闭根据异常等级由对应权限人确认

### block_p0282_b020

签名校验失败时的处理：

### block_p0282_b021

失败原因处理

### block_p0282_b022

未签名保持待确认，不进入正式流程

### block_p0282_b023

签名人无权限拒绝操作，记录审计

### block_p0282_b024

内容被修改原签名失效，要求重新确认

### block_p0282_b025

签名超时状态置为expired，重新推送

### block_p0282_b026

hash 缺失拒绝进入正式流程

### block_p0282_b027

校验异常阻断关键流程，通知管理员

### block_p0282_b028

尤其需要注意：老板决策未签名，不能生成正式任务。

### block_p0282_b029

Executive Agent 可以生成任务草案，但后端只有在human_confirm_status = confirmed

### block_p0282_b030

且签名校验通过后，才能创建正式任务。

### block_p0282_b031

13.11重试机制

### block_p0282_b032

重试机制用于处理网络波动、模型超时、接口短暂失败等问题。

### block_p0282_b033

MVP 阶段需要区分“可以重试”和“不应该重试”的错误。

### block_p0282_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0282_b035

AutoMage-2-MVP 架构设计文档·杨卓282

### block_p0282_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 282

## 表格

无。

## 备注

无。

<!-- 来自 page_0282.md 全文结束 -->

<!-- 来自 page_0283.md 全文开始 -->

# Page 0283

## 原始文本块

### block_p0283_b001

2026 年5 月3 日

### block_p0283_b002

13.11.1可以重试的场景

### block_p0283_b003

场景处理

### block_p0283_b004

网络超时使用同一幂等键重试

### block_p0283_b005

后端5xx延迟重试

### block_p0283_b006

IM 推送失败重试推送

### block_p0283_b007

Agent 模型调用超时重新调用或降级

### block_p0283_b008

Dream 运行超时延迟重试或生成简版摘要

### block_p0283_b009

13.11.2不建议自动重试的场景

### block_p0283_b010

场景处理

### block_p0283_b011

401 未认证重新登录或初始化

### block_p0283_b012

403 无权限停止请求，记录审计

### block_p0283_b013

422 Schema 错误补充或修正字段后再提交

### block_p0283_b014

409 重复提交走更新或幂等返回

### block_p0283_b015

签名人无权限不重试

### block_p0283_b016

状态流转非法不重试，提示人工处理

### block_p0283_b017

重试必须配合幂等键，避免重复写入。

### block_p0283_b018

例如Staff 日报提交可以使用：

### block_p0283_b019

staff_report:{org_id}:{user_id}:{record_date}

### block_p0283_b020

任务生成可以使用：

### block_p0283_b021

task_from_decision:{decision_id}:{option_id}

### block_p0283_b022

Dream 运行可以使用：

### block_p0283_b023

dream_run:{org_id}:{summary_date}:{run_type}

### block_p0283_b024

推荐重试策略：

### block_p0283_b025

次数间隔

### block_p0283_b026

第1 次1 秒

### block_p0283_b027

第2 次3 秒

### block_p0283_b028

第3 次10 秒

### block_p0283_b029

第4 次30 秒

### block_p0283_b030

仍失败标记失败并通知管理员

### block_p0283_b031

重试过程中不应重复通知用户，避免用户收到多条相同消息。

### block_p0283_b032

13.12422 错误处理

### block_p0283_b033

422 表示请求格式或业务字段不符合Schema 要求。这是Agent 和前端最常遇到的错误。

### block_p0283_b034

常见422 场景包括：

### block_p0283_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0283_b036

AutoMage-2-MVP 架构设计文档·杨卓283

### block_p0283_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 283

## 表格

无。

## 备注

无。

<!-- 来自 page_0283.md 全文结束 -->

<!-- 来自 page_0284.md 全文开始 -->

# Page 0284

## 原始文本块

### block_p0284_b001

2026 年5 月3 日

### block_p0284_b002

1. 缺少必填字段。

### block_p0284_b003

2. 字段类型错误。

### block_p0284_b004

3. 枚举值非法。

### block_p0284_b005

4. 条件必填未满足。

### block_p0284_b006

5. 字符串长度超限。

### block_p0284_b007

6. 日期格式错误。

### block_p0284_b008

7. 来源对象不存在。

### block_p0284_b009

8. 状态流转不合法。

### block_p0284_b010

9. decision_required = true 但decision_items 为空。

### block_p0284_b011

10. need_support = true 但support_detail 为空。

### block_p0284_b012

后端返回422 时，应提供可机器读取的错误详情。

### block_p0284_b013

示例：

### block_p0284_b014

{

### block_p0284_b015

"code": "SCHEMA_VALIDATION_FAILED",

### block_p0284_b016

"message": " 提交内容不符合Staff Schema",

### block_p0284_b017

"errors": [

### block_p0284_b018

{

### block_p0284_b019

"field": "support_detail",

### block_p0284_b020

"reason": "need_support 为true 时，support_detail 必填",

### block_p0284_b021

"suggestion": " 请补充需要谁支持、支持什么事项"

### block_p0284_b022

}

### block_p0284_b023

]

### block_p0284_b024

}

### block_p0284_b025

Agent 收到422 后，应根据errors 精准追问。

### block_p0284_b026

示例：

### block_p0284_b027

日报暂未提交成功。你选择了“需要上级支持”，但没有填写具体支持内容。请补充需要谁支持、

### block_p0284_b028

支持什么事项。,→

### block_p0284_b029

不应让用户重新填写整份日报。

### block_p0284_b030

对于多字段错误，Agent 可以一次性列出需要补充的字段：

### block_p0284_b031

还需要补充2 项信息：

### block_p0284_b032

1. 明日计划。

### block_p0284_b033

2. 需要支持的具体内容。

### block_p0284_b034

422 不是系统故障，而是正常的数据修正流程。MVP 阶段要把422 处理好，否则用户会

### block_p0284_b035

觉得系统“不稳定”。

### block_p0284_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0284_b037

AutoMage-2-MVP 架构设计文档·杨卓284

### block_p0284_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 284

## 表格

无。

## 备注

无。

<!-- 来自 page_0284.md 全文结束 -->

<!-- 来自 page_0285.md 全文开始 -->

# Page 0285

## 原始文本块

### block_p0285_b001

2026 年5 月3 日

### block_p0285_b002

13.13401/403 权限错误处理

### block_p0285_b003

401 和403 都与权限相关，但含义不同。

### block_p0285_b004

错误码含义

### block_p0285_b005

401未认证、登录失效、Token 无效

### block_p0285_b006

403已认证，但无权访问或操作

### block_p0285_b007

13.13.1401 处理

### block_p0285_b008

401 常见场景：

### block_p0285_b009

1. 用户未登录。

### block_p0285_b010

2. Token 过期。

### block_p0285_b011

3. Agent 初始化失败。

### block_p0285_b012

4. IM 用户未绑定系统账号。

### block_p0285_b013

5. API 凭证错误。

### block_p0285_b014

处理方式：

### block_p0285_b015

1. 停止当前写入操作。

### block_p0285_b016

2. 提示用户重新登录或绑定账号。

### block_p0285_b017

3. 暂存当前草稿。

### block_p0285_b018

4. 不重复提交。

### block_p0285_b019

5. 记录错误日志。

### block_p0285_b020

提示示例：

### block_p0285_b021

当前账号状态已失效，日报暂未提交。我已保留本次填写内容，请重新登录后继续提交。

### block_p0285_b022

13.13.2403 处理

### block_p0285_b023

403 常见场景：

### block_p0285_b024

1. Staff Agent 读取他人日报。

### block_p0285_b025

2. Manager Agent 读取其他部门数据。

### block_p0285_b026

3. 普通员工确认老板决策。

### block_p0285_b027

4. 未授权用户关闭高风险异常。

### block_p0285_b028

5. Agent 尝试创建跨部门任务。

### block_p0285_b029

6. 用户提交不属于自己的日报。

### block_p0285_b030

处理方式：

### block_p0285_b031

1. 停止操作。

### block_p0285_b032

2. 不自动改写用户、部门或组织ID。

### block_p0285_b033

3. 提示无权限。

### block_p0285_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0285_b035

AutoMage-2-MVP 架构设计文档·杨卓285

### block_p0285_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 285

## 表格

无。

## 备注

无。

<!-- 来自 page_0285.md 全文结束 -->

<!-- 来自 page_0286.md 全文开始 -->

# Page 0286

## 原始文本块

### block_p0286_b001

2026 年5 月3 日

### block_p0286_b002

4. 写入审计日志。

### block_p0286_b003

5. 必要时通知管理员或上级。

### block_p0286_b004

提示示例：

### block_p0286_b005

当前账号没有权限确认该决策。该操作需要老板或授权高管确认。

### block_p0286_b006

403 不能通过重试解决。Agent 收到403 后，不应尝试换一个ID 或请求更大范围数据。

### block_p0286_b007

13.14超时与幂等处理

### block_p0286_b008

超时和重复请求是MVP 联调中非常常见的问题。尤其是IM、Agent、后端、数据库多

### block_p0286_b009

方协作时，一次操作可能因为网络、模型响应或接口延迟被重复触发。

### block_p0286_b010

因此，关键写入接口必须支持幂等。

### block_p0286_b011

13.14.1为什么需要幂等

### block_p0286_b012

没有幂等时，可能出现：

### block_p0286_b013

1. 员工一条日报被提交两次。

### block_p0286_b014

2. 老板确认一次，系统生成两组任务。

### block_p0286_b015

3. Dream 重试后生成多个重复决策卡片。

### block_p0286_b016

4. IM 推送失败重试后，用户收到多条相同消息。

### block_p0286_b017

5. 任务状态被重复更新。

### block_p0286_b018

6. 审计日志出现重复关键事件。

### block_p0286_b019

幂等的目标是：同一业务动作重复请求多次，最终只产生一次业务结果。

### block_p0286_b020

13.14.2推荐幂等键设计

### block_p0286_b021

不同场景建议使用不同幂等键。

### block_p0286_b022

场景幂等键

### block_p0286_b023

Staff 日报提交staff_report:{org_id}:{user_id}:{record_date}

### block_p0286_b024

Manager 汇总生成manager_summary:{org_id}:{dept_id}:{summary_date}

### block_p0286_b025

Executive 摘要生成executive_summary:{org_id}:{summary_date}

### block_p0286_b026

老板确认决策decision_confirm:{decision_id}:{confirmed_by}

### block_p0286_b027

决策生成任务task_from_decision:{decision_id}:{confirmed_option}

### block_p0286_b028

异常生成任务task_from_incident:{incident_id}

### block_p0286_b029

Dream 运行dream_run:{org_id}:{summary_date}:{run_type}

### block_p0286_b030

IM 消息推送im_push:{target_type}:{target_id}:{event_type}

### block_p0286_b031

幂等键应由后端校验和保存，不能只在Agent 本地判断。

### block_p0286_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0286_b033

AutoMage-2-MVP 架构设计文档·杨卓286

### block_p0286_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 286

## 表格

无。

## 备注

无。

<!-- 来自 page_0286.md 全文结束 -->

<!-- 来自 page_0287.md 全文开始 -->

# Page 0287

## 原始文本块

### block_p0287_b001

2026 年5 月3 日

### block_p0287_b002

13.14.3超时处理

### block_p0287_b003

如果请求超时，调用方不能立即认为失败，也不能无脑生成新请求。

### block_p0287_b004

推荐流程：

### block_p0287_b005

请求超时

### block_p0287_b006

↓

### block_p0287_b007

使用同一幂等键查询结果

### block_p0287_b008

↓

### block_p0287_b009

如果已成功，返回成功结果

### block_p0287_b010

↓

### block_p0287_b011

如果未成功，使用同一幂等键重试

### block_p0287_b012

↓

### block_p0287_b013

多次失败后标记待处理

### block_p0287_b014

例如老板确认决策时，如果前端超时，但后端其实已经创建了任务，再次点击确认不应

### block_p0287_b015

重复生成任务。

### block_p0287_b016

13.14.4幂等返回

### block_p0287_b017

如果后端发现同一幂等键已经处理过，应返回原处理结果。

### block_p0287_b018

示例：

### block_p0287_b019

{

### block_p0287_b020

"code": "IDEMPOTENT_REPLAY",

### block_p0287_b021

"message": " 该请求已处理，返回原结果",

### block_p0287_b022

"data": {

### block_p0287_b023

"task_ids": [9001, 9002]

### block_p0287_b024

}

### block_p0287_b025

}

### block_p0287_b026

这样Agent 或前端可以继续展示正确结果，而不是提示用户失败。

### block_p0287_b027

13.14.5重复提交处理

### block_p0287_b028

重复提交不一定都是错误。系统应区分：

### block_p0287_b029

情况处理

### block_p0287_b030

同一请求重复发送幂等返回原结果

### block_p0287_b031

用户修改后重新提交创建新版本或更新原记录

### block_p0287_b032

老板重复点击同一确认按钮返回已确认结果

### block_p0287_b033

Dream 重复运行同一日期返回已有运行记录或生成新版本

### block_p0287_b034

任务重复生成合并或返回已有任务

### block_p0287_b035

对于Staff 日报，可以采用：

### block_p0287_b036

同一员工同一天一条主记录；

### block_p0287_b037

修改走update 或revision；

### block_p0287_b038

重复提交走幂等返回。

### block_p0287_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0287_b040

AutoMage-2-MVP 架构设计文档·杨卓287

### block_p0287_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 287

## 表格

无。

## 备注

无。

<!-- 来自 page_0287.md 全文结束 -->

<!-- 来自 page_0288.md 全文开始 -->

# Page 0288

## 原始文本块

### block_p0288_b001

2026 年5 月3 日

### block_p0288_b002

对于老板决策任务，必须防止重复生成任务：

### block_p0288_b003

同一decision_id + confirmed_option 只能生成一次正式任务集。

### block_p0288_b004

13.14.6超时后的用户提示

### block_p0288_b005

超时提示要谨慎，不要让用户以为数据一定丢了。

### block_p0288_b006

不推荐：

### block_p0288_b007

提交失败，请重新提交。

### block_p0288_b008

推荐：

### block_p0288_b009

提交结果暂时未确认，我会继续查询处理结果。请不要重复提交，避免产生重复记录。

### block_p0288_b010

如果最终确认失败，再提示用户重试或联系管理员。

### block_p0288_b011

13.15本章小结

### block_p0288_b012

前端、IM、Agent 和后端校验逻辑，是AutoMage-2 MVP 稳定运行的基础。

### block_p0288_b013

前端和IM 负责让用户少犯明显错误；Agent 负责把自然语言整理成合格的Schema；后

### block_p0288_b014

端负责最终校验字段、权限、签名、状态和幂等；数据库负责保证事实数据一致。任何一层缺

### block_p0288_b015

失，都会导致数据不可用、任务重复、权限失控或决策无法追溯。

### block_p0288_b016

MVP 阶段至少要先跑通以下校验闭环：

### block_p0288_b017

用户输入

### block_p0288_b018

↓

### block_p0288_b019

前端/ IM 基础校验

### block_p0288_b020

↓

### block_p0288_b021

Agent 追问和结构化

### block_p0288_b022

↓

### block_p0288_b023

Agent 本地Schema 校验

### block_p0288_b024

↓

### block_p0288_b025

后端字段/ 权限/ 签名校验

### block_p0288_b026

↓

### block_p0288_b027

幂等写库

### block_p0288_b028

↓

### block_p0288_b029

错误可追踪、可修正

### block_p0288_b030

只要这套校验链路稳定，Staff 日报、Manager 汇总、Executive 决策、任务下发和异常处

### block_p0288_b031

理才能真正进入可联调、可演示、可扩展的状态。

### block_p0288_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0288_b033

AutoMage-2-MVP 架构设计文档·杨卓288

### block_p0288_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 288

## 表格

无。

## 备注

无。

<!-- 来自 page_0288.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

