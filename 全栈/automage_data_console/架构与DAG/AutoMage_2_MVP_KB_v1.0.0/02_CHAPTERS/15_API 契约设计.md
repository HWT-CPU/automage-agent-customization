# API 契约设计

> 来源 PDF：`00_SOURCE/AutoMage_2_MVP_架构设计文档v1.0.0.pdf`
> 来源页码：P289-P315
> 对应页面文件：`01_PAGES/page_0289.md` — `01_PAGES/page_0315.md`

## 原文整理

<!-- 来自 page_0289.md 全文开始 -->

# Page 0289

## 原始文本块

### block_p0289_b001

2026 年5 月3 日

### block_p0289_b002

14API 契约设计

### block_p0289_b003

14.1API 设计原则

### block_p0289_b004

AutoMage-2 MVP 的API 不是普通CRUD 接口，而是Agent、IM、前端、后端和数据

### block_p0289_b005

库之间的统一协作契约。

### block_p0289_b006

API 的核心作用有三个：

### block_p0289_b007

1. 接收Agent 生成的结构化Schema。

### block_p0289_b008

2. 对Schema 做鉴权、校验、签名、幂等和写库。

### block_p0289_b009

3. 为上级Agent 提供可追溯、可权限控制的数据读取能力。

### block_p0289_b010

MVP 阶段API 设计应遵守以下原则。

### block_p0289_b011

14.1.1Schema 优先

### block_p0289_b012

所有核心写入接口都应以Schema 为核心输入，而不是让每个接口自定义一套字段。

### block_p0289_b013

例如Staff 日报提交接口应接收schema_v1_staff，Manager 汇总提交接口应接收

### block_p0289_b014

schema_v1_manager，Executive 决策提交接口应接收schema_v1_executive。

### block_p0289_b015

这样做的好处是：

### block_p0289_b016

1. Agent 输出结构稳定。

### block_p0289_b017

2. 后端校验规则清晰。

### block_p0289_b018

3. 前后端字段一致。

### block_p0289_b019

4. 数据库映射可追踪。

### block_p0289_b020

5. 后续Schema 版本可以演进。

### block_p0289_b021

14.1.2后端最终校验

### block_p0289_b022

Agent 可以做本地校验，前端可以做表单校验，IM 可以做交互校验，但所有正式写入必

### block_p0289_b023

须经过后端校验。

### block_p0289_b024

后端至少负责：

### block_p0289_b025

1. 用户鉴权。

### block_p0289_b026

2. Agent 鉴权。

### block_p0289_b027

3. Schema 字段校验。

### block_p0289_b028

4. 字段类型校验。

### block_p0289_b029

5. 枚举值校验。

### block_p0289_b030

6. 权限校验。

### block_p0289_b031

7. 签名校验。

### block_p0289_b032

8. 幂等校验。

### block_p0289_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0289_b034

AutoMage-2-MVP 架构设计文档·杨卓289

### block_p0289_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 289

## 表格

无。

## 备注

无。

<!-- 来自 page_0289.md 全文结束 -->

<!-- 来自 page_0290.md 全文开始 -->

# Page 0290

## 原始文本块

### block_p0290_b001

2026 年5 月3 日

### block_p0290_b002

9. 状态流转校验。

### block_p0290_b003

10. 审计日志记录。

### block_p0290_b004

不允许Agent 直接写数据库，也不允许前端绕过API 写入正式业务表。

### block_p0290_b005

14.1.3数据库是事实源

### block_p0290_b006

API 写入成功后，数据库中的数据才是正式事实。

### block_p0290_b007

IM 聊天记录、Agent 上下文、前端临时状态都不能作为最终事实源。

### block_p0290_b008

例如：

### block_p0290_b009

员工在IM 中说“确认提交”

### block_p0290_b010

￿

### block_p0290_b011

日报已正式提交

### block_p0290_b012

只有当Staff Agent 调用/api/v1/report/staff 成功，后端完成校验、签名和写库后，

### block_p0290_b013

该日报才算正式进入系统。

### block_p0290_b014

14.1.4幂等优先

### block_p0290_b015

所有关键写入接口必须支持幂等，避免重复提交、重复任务、重复决策和重复审计。

### block_p0290_b016

需要支持幂等的典型接口包括：

### block_p0290_b017

1. Staff 日报提交。

### block_p0290_b018

2. Manager 汇总提交。

### block_p0290_b019

3. Executive 决策提交。

### block_p0290_b020

4. 老板确认决策。

### block_p0290_b021

5. 任务生成。

### block_p0290_b022

6. 异常上报。

### block_p0290_b023

7. Dream 运行结果写入。

### block_p0290_b024

建议统一使用请求头：

### block_p0290_b025

Idempotency-Key: staff_report:1:10086:2026-05-03

### block_p0290_b026

后端发现同一幂等键已处理时，应返回原结果，而不是重复写入。

### block_p0290_b027

14.1.5错误可被Agent 理解

### block_p0290_b028

API 错误不能只返回“失败”。错误必须明确到字段、原因和建议修正方式，这样Agent

### block_p0290_b029

才能继续追问用户或重新生成Schema。

### block_p0290_b030

推荐错误格式：

### block_p0290_b031 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0290_b032

AutoMage-2-MVP 架构设计文档·杨卓290

### block_p0290_b033 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 290

## 表格

无。

## 备注

无。

<!-- 来自 page_0290.md 全文结束 -->

<!-- 来自 page_0291.md 全文开始 -->

# Page 0291

## 原始文本块

### block_p0291_b001

2026 年5 月3 日

### block_p0291_b002

{

### block_p0291_b003

"success": false,

### block_p0291_b004

"code": "SCHEMA_VALIDATION_FAILED",

### block_p0291_b005

"message": "Schema 校验失败",

### block_p0291_b006

"errors": [

### block_p0291_b007

{

### block_p0291_b008

"field": "support_detail",

### block_p0291_b009

"reason": "need_support 为true 时，support_detail 必填",

### block_p0291_b010

"suggestion": " 请补充需要谁支持、支持什么事项"

### block_p0291_b011

}

### block_p0291_b012

],

### block_p0291_b013

"request_id": "req_01HXAMPLE"

### block_p0291_b014

}

### block_p0291_b015

14.1.6权限由后端强制执行

### block_p0291_b016

权限不能只写在Prompt 中。

### block_p0291_b017

即使Agent 请求越权数据，后端也必须拒绝。例如：

### block_p0291_b018

1. Staff Agent 不能读取其他员工日报。

### block_p0291_b019

2. Manager Agent 不能读取其他部门员工明细。

### block_p0291_b020

3. 普通员工不能确认老板决策。

### block_p0291_b021

4. 未授权Agent 不能创建跨部门任务。

### block_p0291_b022

5. 未签名老板决策不能生成正式任务。

### block_p0291_b023

14.1.7接口版本化

### block_p0291_b024

MVP 阶段统一使用：

### block_p0291_b025

/api/v1

### block_p0291_b026

后续如果Schema、权限或任务状态流转发生破坏性变化，应新增版本，而不是直接修改

### block_p0291_b027

旧接口含义。

### block_p0291_b028

14.2统一响应格式

### block_p0291_b029

所有API 建议使用统一响应结构，方便前端、IM 和Agent Runtime 统一处理。

### block_p0291_b030

14.2.1成功响应格式

### block_p0291_b031

{

### block_p0291_b032

"success": true,

### block_p0291_b033

"code": "OK",

### block_p0291_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0291_b035

AutoMage-2-MVP 架构设计文档·杨卓291

### block_p0291_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 291

## 表格

无。

## 备注

无。

<!-- 来自 page_0291.md 全文结束 -->

<!-- 来自 page_0292.md 全文开始 -->

# Page 0292

## 原始文本块

### block_p0292_b001

2026 年5 月3 日

### block_p0292_b002

"message": "success",

### block_p0292_b003

"data": {},

### block_p0292_b004

"request_id": "req_01HXAMPLE",

### block_p0292_b005

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0292_b006

}

### block_p0292_b007

字段说明：

### block_p0292_b008

字段类型说明

### block_p0292_b009

successboolean是否成功

### block_p0292_b010

codestring业务状态码

### block_p0292_b011

messagestring简短说明

### block_p0292_b012

dataobject业务数据

### block_p0292_b013

request_idstring请求ID，用于排查

### block_p0292_b014

server_timestring服务端时间

### block_p0292_b015

14.2.2失败响应格式

### block_p0292_b016

{

### block_p0292_b017

"success": false,

### block_p0292_b018

"code": "SCHEMA_VALIDATION_FAILED",

### block_p0292_b019

"message": " 提交内容不符合Staff Schema",

### block_p0292_b020

"errors": [

### block_p0292_b021

{

### block_p0292_b022

"field": "support_detail",

### block_p0292_b023

"reason": "need_support 为true 时，support_detail 必填",

### block_p0292_b024

"suggestion": " 请补充需要谁支持、支持什么事项"

### block_p0292_b025

}

### block_p0292_b026

],

### block_p0292_b027

"request_id": "req_01HXAMPLE",

### block_p0292_b028

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0292_b029

}

### block_p0292_b030

字段说明：

### block_p0292_b031

字段类型说明

### block_p0292_b032

successboolean固定为false

### block_p0292_b033

codestring错误码

### block_p0292_b034

messagestring错误摘要

### block_p0292_b035

errorsarray字段级错误列表

### block_p0292_b036

request_idstring请求ID

### block_p0292_b037

server_timestring服务端时间

### block_p0292_b038

14.2.3分页响应格式

### block_p0292_b039

读取列表类接口使用统一分页结构。

### block_p0292_b040 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0292_b041

AutoMage-2-MVP 架构设计文档·杨卓292

### block_p0292_b042 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 292

## 表格

无。

## 备注

无。

<!-- 来自 page_0292.md 全文结束 -->

<!-- 来自 page_0293.md 全文开始 -->

# Page 0293

## 原始文本块

### block_p0293_b001

2026 年5 月3 日

### block_p0293_b002

{

### block_p0293_b003

"success": true,

### block_p0293_b004

"code": "OK",

### block_p0293_b005

"message": "success",

### block_p0293_b006

"data": {

### block_p0293_b007

"items": [],

### block_p0293_b008

"pagination": {

### block_p0293_b009

"page": 1,

### block_p0293_b010

"page_size": 20,

### block_p0293_b011

"total": 128,

### block_p0293_b012

"has_more": true

### block_p0293_b013

}

### block_p0293_b014

},

### block_p0293_b015

"request_id": "req_01HXAMPLE",

### block_p0293_b016

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0293_b017

}

### block_p0293_b018

14.2.4幂等重放响应格式

### block_p0293_b019

如果请求已经处理过，后端应返回原结果，并明确标记为幂等重放。

### block_p0293_b020

{

### block_p0293_b021

"success": true,

### block_p0293_b022

"code": "IDEMPOTENT_REPLAY",

### block_p0293_b023

"message": " 该请求已处理，返回原结果",

### block_p0293_b024

"data": {

### block_p0293_b025

"work_record_id": 301

### block_p0293_b026

},

### block_p0293_b027

"request_id": "req_01HXAMPLE",

### block_p0293_b028

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0293_b029

}

### block_p0293_b030

14.3统一错误码

### block_p0293_b031

MVP 阶段建议先定义一组稳定错误码，供Agent、前端和后端联调使用。

### block_p0293_b032 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0293_b033

AutoMage-2-MVP 架构设计文档·杨卓293

### block_p0293_b034 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 293

## 表格

无。

## 备注

无。

<!-- 来自 page_0293.md 全文结束 -->

<!-- 来自 page_0294.md 全文开始 -->

# Page 0294

## 原始文本块

### block_p0294_b001

2026 年5 月3 日

### block_p0294_b002

HTTP 状态码错误码含义处理方式

### block_p0294_b003

200OK成功正常处理

### block_p0294_b004

200IDEMPOTENT_REPLAY幂等重放使用原结果

### block_p0294_b005

400BAD_REQUEST请求格式错误修正请求结构

### block_p0294_b006

401UNAUTHORIZED未认证或登录失效重新登录/ 重新初始化

### block_p0294_b007

403FORBIDDEN无权限停止操作，记录审计

### block_p0294_b008

404NOT_FOUND数据不存在或不可

### block_p0294_b009

见

### block_p0294_b010

返回空或提示无数据

### block_p0294_b011

409CONFLICT数据冲突或重复提

### block_p0294_b012

交

### block_p0294_b013

走幂等、更新或人工处理

### block_p0294_b014

422SCHEMA_VALIDATION_FAILED Schema 校验失败Agent 追问补全

### block_p0294_b015

422FIELD_TYPE_INVALID字段类型错误修正字段类型

### block_p0294_b016

422ENUM_VALUE_INVALID枚举值非法使用标准枚举

### block_p0294_b017

422REQUIRED_FIELD_MISSING缺少必填字段补充字段

### block_p0294_b018

422SIGNATURE_REQUIRED缺少签名请求确认

### block_p0294_b019

422SIGNATURE_INVALID签名无效重新签名

### block_p0294_b020

422STATE_TRANSITION_INVALID 状态流转非法人工检查

### block_p0294_b021

429RATE_LIMITED请求过快延迟重试

### block_p0294_b022

500INTERNAL_ERROR服务端异常重试或通知管理员

### block_p0294_b023

503SERVICE_UNAVAILABLE服务不可用延迟重试

### block_p0294_b024

Agent 处理错误时应遵守以下规则：

### block_p0294_b025

1. 422：根据字段错误追问用户。

### block_p0294_b026

2. 401：提示重新登录或重新绑定。

### block_p0294_b027

3. 403：停止请求，不要尝试绕过。

### block_p0294_b028

4. 409：查询已有结果或走更新流程。

### block_p0294_b029

5. 5xx：使用幂等键延迟重试。

### block_p0294_b030

14.4Agent 初始化接口

### block_p0294_b031

14.4.1POST /api/v1/agent/init

### block_p0294_b032

该接口用于初始化Agent 节点，获取当前用户、组织、部门、节点类型、权限范围和Schema

### block_p0294_b033

版本信息。

### block_p0294_b034

Staff Agent、Manager Agent、Executive Agent 启动时都应先调用该接口。

### block_p0294_b035

14.4.2请求参数

### block_p0294_b036

{

### block_p0294_b037

"org_id": 1,

### block_p0294_b038

"user_id": 10086,

### block_p0294_b039

"agent_type": "staff",

### block_p0294_b040

"client_type": "im",

### block_p0294_b041

"client_user_id": "feishu_open_id_xxx",

### block_p0294_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0294_b043

AutoMage-2-MVP 架构设计文档·杨卓294

### block_p0294_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 294

## 表格

无。

## 备注

无。

<!-- 来自 page_0294.md 全文结束 -->

<!-- 来自 page_0295.md 全文开始 -->

# Page 0295

## 原始文本块

### block_p0295_b001

2026 年5 月3 日

### block_p0295_b002

"agent_template_version": "staff_agent_v0.1"

### block_p0295_b003

}

### block_p0295_b004

字段说明：

### block_p0295_b005

字段类型是否必填说明

### block_p0295_b006

org_idnumber / string是组织ID

### block_p0295_b007

user_idnumber / string否系统用户ID

### block_p0295_b008

agent_typestring是Agent 类型

### block_p0295_b009

client_typestring是客户端类型，如im、web

### block_p0295_b010

client_user_idstring否IM 或外部系统用户ID

### block_p0295_b011

agent_template_versionstring否Agent 模板版本

### block_p0295_b012

agent_type 建议枚举：

### block_p0295_b013

值含义

### block_p0295_b014

staffStaff Agent

### block_p0295_b015

managerManager Agent

### block_p0295_b016

executiveExecutive Agent

### block_p0295_b017

dreamDream 运行节点

### block_p0295_b018

admin管理节点

### block_p0295_b019

14.4.3响应参数

### block_p0295_b020

{

### block_p0295_b021

"success": true,

### block_p0295_b022

"code": "OK",

### block_p0295_b023

"message": "success",

### block_p0295_b024

"data": {

### block_p0295_b025

"agent_session_id": "agent_sess_01HXAMPLE",

### block_p0295_b026

"node_id": "staff_node_10086",

### block_p0295_b027

"agent_type": "staff",

### block_p0295_b028

"org_id": 1,

### block_p0295_b029

"user_id": 10086,

### block_p0295_b030

"department_id": 12,

### block_p0295_b031

"role": "staff",

### block_p0295_b032

"permissions": {

### block_p0295_b033

"can_read_own_reports": true,

### block_p0295_b034

"can_submit_staff_report": true,

### block_p0295_b035

"can_read_department_reports": false,

### block_p0295_b036

"can_generate_manager_summary": false,

### block_p0295_b037

"can_generate_executive_decision": false

### block_p0295_b038

},

### block_p0295_b039

"supported_schemas": [

### block_p0295_b040

{

### block_p0295_b041

"schema_id": "schema_v1_staff",

### block_p0295_b042

"schema_version": "1.0.0"

### block_p0295_b043

}

### block_p0295_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0295_b045

AutoMage-2-MVP 架构设计文档·杨卓295

### block_p0295_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 295

## 表格

无。

## 备注

无。

<!-- 来自 page_0295.md 全文结束 -->

<!-- 来自 page_0296.md 全文开始 -->

# Page 0296

## 原始文本块

### block_p0296_b001

2026 年5 月3 日

### block_p0296_b002

],

### block_p0296_b003

"expires_at": "2026-05-04T23:59:59+08:00"

### block_p0296_b004

},

### block_p0296_b005

"request_id": "req_01HXAMPLE",

### block_p0296_b006

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0296_b007

}

### block_p0296_b008

14.4.4错误码

### block_p0296_b009

错误码场景

### block_p0296_b010

UNAUTHORIZED用户未登录或IM 账号未绑定

### block_p0296_b011

FORBIDDEN用户无权初始化该类型Agent

### block_p0296_b012

NOT_FOUND组织、用户或部门不存在

### block_p0296_b013

AGENT_TYPE_INVALIDAgent 类型非法

### block_p0296_b014

INTERNAL_ERROR初始化失败

### block_p0296_b015

14.5Staff 日报提交接口

### block_p0296_b016

14.5.1POST /api/v1/report/staff

### block_p0296_b017

该接口用于提交员工每日Staff Schema。

### block_p0296_b018

Staff Agent 在员工确认日报后调用该接口。后端完成Schema 校验、权限校验、签名校

### block_p0296_b019

验、幂等校验后，将数据写入work_records 和work_record_items。

### block_p0296_b020

14.5.2请求参数

### block_p0296_b021

请求头建议：

### block_p0296_b022

Authorization: Bearer <token>

### block_p0296_b023

Idempotency-Key: staff_report:1:10086:2026-05-03

### block_p0296_b024

Content-Type: application/json

### block_p0296_b025

请求体：

### block_p0296_b026

{

### block_p0296_b027

"schema": {

### block_p0296_b028

"schema_id": "schema_v1_staff",

### block_p0296_b029

"schema_version": "1.0.0",

### block_p0296_b030

"timestamp": "2026-05-03T18:12:30+08:00",

### block_p0296_b031

"org_id": 1,

### block_p0296_b032

"department_id": 12,

### block_p0296_b033

"user_id": 10086,

### block_p0296_b034

"node_id": "staff_node_10086",

### block_p0296_b035

"record_date": "2026-05-03",

### block_p0296_b036 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0296_b037

AutoMage-2-MVP 架构设计文档·杨卓296

### block_p0296_b038 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 296

## 表格

无。

## 备注

无。

<!-- 来自 page_0296.md 全文结束 -->

<!-- 来自 page_0297.md 全文开始 -->

# Page 0297

## 原始文本块

### block_p0297_b001

2026 年5 月3 日

### block_p0297_b002

"work_progress": [

### block_p0297_b003

{

### block_p0297_b004

"title": " 完成Staff 日报Schema 初稿",

### block_p0297_b005

"description": " 整理一线员工日报字段、签名字段和数据库映射关系。",

### block_p0297_b006

"status": "completed",

### block_p0297_b007

"related_task_id": 201

### block_p0297_b008

}

### block_p0297_b009

],

### block_p0297_b010

"issues_faced": [

### block_p0297_b011

{

### block_p0297_b012

"title": "Decision 表结构尚未最终确定",

### block_p0297_b013

"description": " 当前DDL 中没有独立decision_logs 表，需要后端确认承载方式。",

### block_p0297_b014

"severity": "medium"

### block_p0297_b015

}

### block_p0297_b016

],

### block_p0297_b017

"solution_attempt": [

### block_p0297_b018

{

### block_p0297_b019

"issue_title": "Decision 表结构尚未最终确定",

### block_p0297_b020

"attempt": " 先在文档中列出Decision Schema 最小字段。",

### block_p0297_b021

"result": " 待后端确认"

### block_p0297_b022

}

### block_p0297_b023

],

### block_p0297_b024

"need_support": true,

### block_p0297_b025

"support_detail": " 需要后端确认是否新增decision_logs 表。",

### block_p0297_b026

"next_day_plan": [

### block_p0297_b027

{

### block_p0297_b028

"title": " 完善Manager Schema 字段定义",

### block_p0297_b029

"priority": "high",

### block_p0297_b030

"expected_output": " 形成可提交后端联调的字段说明"

### block_p0297_b031

}

### block_p0297_b032

],

### block_p0297_b033

"resource_usage": {

### block_p0297_b034

"work_hours": 7.5,

### block_p0297_b035

"tools": ["ChatGPT", "PostgreSQL", "Markdown"]

### block_p0297_b036

},

### block_p0297_b037

"artifacts": [],

### block_p0297_b038

"related_task_ids": [201],

### block_p0297_b039

"risk_level": "medium",

### block_p0297_b040

"employee_comment": " 部分内容需要等后端确认后定稿。",

### block_p0297_b041

"signature": {

### block_p0297_b042

"signature_required": true,

### block_p0297_b043

"signature_status": "signed",

### block_p0297_b044

"signed_by": 10086,

### block_p0297_b045

"signed_at": "2026-05-03T18:13:00+08:00",

### block_p0297_b046

"payload_hash": "sha256:example_hash",

### block_p0297_b047

"signature_source": "im"

### block_p0297_b048

},

### block_p0297_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0297_b050

AutoMage-2-MVP 架构设计文档·杨卓297

### block_p0297_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 297

## 表格

无。

## 备注

无。

<!-- 来自 page_0297.md 全文结束 -->

<!-- 来自 page_0298.md 全文开始 -->

# Page 0298

## 原始文本块

### block_p0298_b001

2026 年5 月3 日

### block_p0298_b002

"meta": {

### block_p0298_b003

"input_channel": "feishu",

### block_p0298_b004

"agent_template_version": "staff_agent_v0.1"

### block_p0298_b005

}

### block_p0298_b006

}

### block_p0298_b007

}

### block_p0298_b008

14.5.3响应参数

### block_p0298_b009

{

### block_p0298_b010

"success": true,

### block_p0298_b011

"code": "OK",

### block_p0298_b012

"message": "Staff 日报提交成功",

### block_p0298_b013

"data": {

### block_p0298_b014

"work_record_id": 301,

### block_p0298_b015

"record_date": "2026-05-03",

### block_p0298_b016

"status": "submitted",

### block_p0298_b017

"created_incident_ids": [501],

### block_p0298_b018

"created_task_ids": [],

### block_p0298_b019

"audit_log_id": 7001

### block_p0298_b020

},

### block_p0298_b021

"request_id": "req_01HXAMPLE",

### block_p0298_b022

"server_time": "2026-05-03T18:13:05+08:00"

### block_p0298_b023

}

### block_p0298_b024

字段说明：

### block_p0298_b025

字段说明

### block_p0298_b026

work_record_id写入后的日报主记录ID

### block_p0298_b027

record_date日报日期

### block_p0298_b028

status写入状态

### block_p0298_b029

created_incident_ids因风险或支持需求生成的异常

### block_p0298_b030

created_task_ids因明确事项生成的任务

### block_p0298_b031

audit_log_id审计日志ID

### block_p0298_b032

14.5.4Schema 校验规则

### block_p0298_b033

后端至少校验：

### block_p0298_b034

1. schema_id = schema_v1_staff。

### block_p0298_b035

2. schema_version 为支持版本。

### block_p0298_b036

3. org_id、department_id、user_id 与当前身份匹配。

### block_p0298_b037

4. node_id 与当前Staff Agent 绑定。

### block_p0298_b038

5. work_progress 至少一项。

### block_p0298_b039 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0298_b040

AutoMage-2-MVP 架构设计文档·杨卓298

### block_p0298_b041 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 298

## 表格

无。

## 备注

无。

<!-- 来自 page_0298.md 全文结束 -->

<!-- 来自 page_0299.md 全文开始 -->

# Page 0299

## 原始文本块

### block_p0299_b001

2026 年5 月3 日

### block_p0299_b002

6. next_day_plan 至少一项。

### block_p0299_b003

7. need_support 必须是boolean。

### block_p0299_b004

8. need_support = true 时，support_detail 必填。

### block_p0299_b005

9. risk_level 必须属于low / medium / high / critical。

### block_p0299_b006

10. signature.signed_by 必须等于user_id。

### block_p0299_b007

11. 同一用户同一日期重复提交时走幂等或修订流程。

### block_p0299_b008

14.6Manager 汇总提交接口

### block_p0299_b009

14.6.1POST /api/v1/report/manager

### block_p0299_b010

该接口用于提交部门级Manager Schema。

### block_p0299_b011

Manager Agent 读取本部门Staff Schema 后，生成部门汇总，并在Manager 确认或系统

### block_p0299_b012

标记后调用该接口。

### block_p0299_b013

14.6.2请求参数

### block_p0299_b014

请求头：

### block_p0299_b015

Authorization: Bearer <token>

### block_p0299_b016

Idempotency-Key: manager_summary:1:12:2026-05-03

### block_p0299_b017

Content-Type: application/json

### block_p0299_b018

请求体：

### block_p0299_b019

{

### block_p0299_b020

"schema": {

### block_p0299_b021

"schema_id": "schema_v1_manager",

### block_p0299_b022

"schema_version": "1.0.0",

### block_p0299_b023

"timestamp": "2026-05-03T21:10:00+08:00",

### block_p0299_b024

"org_id": 1,

### block_p0299_b025

"dept_id": 12,

### block_p0299_b026

"manager_user_id": 20001,

### block_p0299_b027

"manager_node_id": "manager_node_dept_12",

### block_p0299_b028

"summary_date": "2026-05-03",

### block_p0299_b029

"staff_report_count": 8,

### block_p0299_b030

"missing_report_count": 2,

### block_p0299_b031

"missing_staff_ids": [10012, 10017],

### block_p0299_b032

"overall_health": "yellow",

### block_p0299_b033

"aggregated_summary": "今日架构组主要完成Staff Schema 字段定义和数据库映射梳理。Decision

### block_p0299_b034

相关表结构尚未最终确定，可能影响Executive 决策链路。",,→

### block_p0299_b035

"top_3_risks": [

### block_p0299_b036

{

### block_p0299_b037

"title": "Decision 表结构未确认",

### block_p0299_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0299_b039

AutoMage-2-MVP 架构设计文档·杨卓299

### block_p0299_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 299

## 表格

无。

## 备注

无。

<!-- 来自 page_0299.md 全文结束 -->

<!-- 来自 page_0300.md 全文开始 -->

# Page 0300

## 原始文本块

### block_p0300_b001

2026 年5 月3 日

### block_p0300_b002

"description": "当前DDL 中未单独建立decision_logs 表，可能影响老板决策记录和任务生成。

### block_p0300_b003

",,→

### block_p0300_b004

"severity": "high",

### block_p0300_b005

"source_record_ids": [301, 302],

### block_p0300_b006

"suggested_action": " 建议后端与架构负责人确认是否新增独立决策表。"

### block_p0300_b007

}

### block_p0300_b008

],

### block_p0300_b009

"workforce_efficiency": {

### block_p0300_b010

"score": 78,

### block_p0300_b011

"level": "medium",

### block_p0300_b012

"basis": "8 名员工提交日报，6 名员工完成主要任务，2 个事项仍处于阻塞状态。"

### block_p0300_b013

},

### block_p0300_b014

"pending_approvals": 1,

### block_p0300_b015

"highlight_staff": [

### block_p0300_b016

{

### block_p0300_b017

"user_id": 10086,

### block_p0300_b018

"display_name": " 杨卓",

### block_p0300_b019

"reason": " 完成Staff Schema 字段定义，并主动梳理数据库映射。",

### block_p0300_b020

"source_record_ids": [301]

### block_p0300_b021

}

### block_p0300_b022

],

### block_p0300_b023

"blocked_items": [],

### block_p0300_b024

"manager_decisions": [],

### block_p0300_b025

"need_executive_decision": [

### block_p0300_b026

{

### block_p0300_b027

"decision_title": " 是否新增独立decision_logs 表",

### block_p0300_b028

"context": " 当前Agent mock 流程中存在decision_logs，但正式DDL 尚未建表。",

### block_p0300_b029

"options": [

### block_p0300_b030

{

### block_p0300_b031

"option_id": "A",

### block_p0300_b032

"title": " 新增独立decision_logs 表"

### block_p0300_b033

},

### block_p0300_b034

{

### block_p0300_b035

"option_id": "B",

### block_p0300_b036

"title": " 暂时复用audit_logs 和tasks"

### block_p0300_b037

}

### block_p0300_b038

],

### block_p0300_b039

"recommended_option": "A",

### block_p0300_b040

"reason": " 独立决策表更利于审计和任务来源追踪。",

### block_p0300_b041

"source_record_ids": [301, 302],

### block_p0300_b042

"urgency": "high"

### block_p0300_b043

}

### block_p0300_b044

],

### block_p0300_b045

"next_day_adjustment": [

### block_p0300_b046

{

### block_p0300_b047

"title": " 优先确认Decision 数据结构",

### block_p0300_b048

"reason": " 该事项影响Executive 决策链路。",

### block_p0300_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0300_b050

AutoMage-2-MVP 架构设计文档·杨卓300

### block_p0300_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 300

## 表格

无。

## 备注

无。

<!-- 来自 page_0300.md 全文结束 -->

<!-- 来自 page_0301.md 全文开始 -->

# Page 0301

## 原始文本块

### block_p0301_b001

2026 年5 月3 日

### block_p0301_b002

"target_user_ids": [10086, 20002],

### block_p0301_b003

"priority": "high",

### block_p0301_b004

"expected_output": " 形成decision_logs 是否建表的最终结论和字段草案。"

### block_p0301_b005

}

### block_p0301_b006

],

### block_p0301_b007

"source_record_ids": [301, 302, 303, 304],

### block_p0301_b008

"related_task_ids": [401],

### block_p0301_b009

"related_incident_ids": [501],

### block_p0301_b010

"signature": {

### block_p0301_b011

"signature_required": true,

### block_p0301_b012

"signature_status": "signed",

### block_p0301_b013

"signed_by": 20001,

### block_p0301_b014

"signed_at": "2026-05-03T21:25:00+08:00",

### block_p0301_b015

"payload_hash": "sha256:manager_summary_hash",

### block_p0301_b016

"signature_source": "im"

### block_p0301_b017

},

### block_p0301_b018

"meta": {

### block_p0301_b019

"input_channel": "scheduled_job",

### block_p0301_b020

"agent_template_version": "manager_agent_v0.1"

### block_p0301_b021

}

### block_p0301_b022

}

### block_p0301_b023

}

### block_p0301_b024

14.6.3响应参数

### block_p0301_b025

{

### block_p0301_b026

"success": true,

### block_p0301_b027

"code": "OK",

### block_p0301_b028

"message": "Manager 汇总提交成功",

### block_p0301_b029

"data": {

### block_p0301_b030

"summary_id": 801,

### block_p0301_b031

"summary_type": "department_daily_summary",

### block_p0301_b032

"summary_date": "2026-05-03",

### block_p0301_b033

"status": "submitted",

### block_p0301_b034

"created_decision_candidate_ids": ["decision_tmp_001"],

### block_p0301_b035

"created_task_ids": [],

### block_p0301_b036

"audit_log_id": 7002

### block_p0301_b037

},

### block_p0301_b038

"request_id": "req_01HXAMPLE",

### block_p0301_b039

"server_time": "2026-05-03T21:25:05+08:00"

### block_p0301_b040

}

### block_p0301_b041

后端至少校验：

### block_p0301_b042

1. Manager Agent 是否有权读取source_record_ids。

### block_p0301_b043

2. source_record_ids 是否全部属于该部门。

### block_p0301_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0301_b045

AutoMage-2-MVP 架构设计文档·杨卓301

### block_p0301_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 301

## 表格

无。

## 备注

无。

<!-- 来自 page_0301.md 全文结束 -->

<!-- 来自 page_0302.md 全文开始 -->

# Page 0302

## 原始文本块

### block_p0302_b001

2026 年5 月3 日

### block_p0302_b002

3. pending_approvals 是否与need_executive_decision.length 一致。

### block_p0302_b003

4. overall_health 是否属于合法枚举。

### block_p0302_b004

5. 高风险和上推事项是否包含来源。

### block_p0302_b005

6. 签名人是否为部门负责人或授权Manager。

### block_p0302_b006

14.7Executive 决策提交接口

### block_p0302_b007

14.7.1POST /api/v1/decision/commit

### block_p0302_b008

该接口用于提交老板确认动作。它不是生成Executive Schema 的接口，而是老板对某个

### block_p0302_b009

决策项做出确认、驳回、补充信息或自定义方案后的提交接口。

### block_p0302_b010

Executive Agent 生成决策卡片后，老板通过IM 或前端确认，前端/ IM 将确认结果提

### block_p0302_b011

交到该接口。

### block_p0302_b012

14.7.2请求参数

### block_p0302_b013

请求头：

### block_p0302_b014

Authorization: Bearer <token>

### block_p0302_b015

Idempotency-Key: decision_confirm:decision_0001:30001

### block_p0302_b016

Content-Type: application/json

### block_p0302_b017

请求体：

### block_p0302_b018

{

### block_p0302_b019

"decision_id": "decision_0001",

### block_p0302_b020

"org_id": 1,

### block_p0302_b021

"executive_user_id": 30001,

### block_p0302_b022

"action": "confirm",

### block_p0302_b023

"confirmed_option": "A",

### block_p0302_b024

"confirmed_custom_plan": null,

### block_p0302_b025

"confirm_source": "im",

### block_p0302_b026

"comment": " 选择方案A，新增独立decision_logs 表。",

### block_p0302_b027

"signature": {

### block_p0302_b028

"signature_required": true,

### block_p0302_b029

"signature_source": "im"

### block_p0302_b030

}

### block_p0302_b031

}

### block_p0302_b032

字段说明：

### block_p0302_b033 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0302_b034

AutoMage-2-MVP 架构设计文档·杨卓302

### block_p0302_b035 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 302

## 表格

无。

## 备注

无。

<!-- 来自 page_0302.md 全文结束 -->

<!-- 来自 page_0303.md 全文开始 -->

# Page 0303

## 原始文本块

### block_p0303_b001

2026 年5 月3 日

### block_p0303_b002

字段类型是否必填说明

### block_p0303_b003

decision_idstring / number是决策ID

### block_p0303_b004

org_idnumber / string是组织ID

### block_p0303_b005

executive_user_idnumber / string是确认人ID

### block_p0303_b006

actionstring是确认动作

### block_p0303_b007

confirmed_optionstring条件必填选择的方案

### block_p0303_b008

confirmed_custom_planstring否自定义方案

### block_p0303_b009

confirm_sourcestring是确认来源

### block_p0303_b010

commentstring否补充说明

### block_p0303_b011

signatureobject是签名请求信息

### block_p0303_b012

action 建议枚举：

### block_p0303_b013

值含义

### block_p0303_b014

confirm确认

### block_p0303_b015

reject驳回

### block_p0303_b016

need_more_info需要补充信息

### block_p0303_b017

cancel取消

### block_p0303_b018

custom_confirm自定义方案确认

### block_p0303_b019

14.7.3响应参数

### block_p0303_b020

{

### block_p0303_b021

"success": true,

### block_p0303_b022

"code": "OK",

### block_p0303_b023

"message": " 决策确认成功",

### block_p0303_b024

"data": {

### block_p0303_b025

"decision_id": "decision_0001",

### block_p0303_b026

"status": "confirmed",

### block_p0303_b027

"confirmed_option": "A",

### block_p0303_b028

"confirmed_by": 30001,

### block_p0303_b029

"confirmed_at": "2026-05-04T08:16:30+08:00",

### block_p0303_b030

"generated_task_ids": [9001, 9002],

### block_p0303_b031

"signature": {

### block_p0303_b032

"signature_status": "signed",

### block_p0303_b033

"payload_hash": "sha256:decision_payload_hash",

### block_p0303_b034

"verify_status": "verified"

### block_p0303_b035

},

### block_p0303_b036

"audit_log_id": 7003

### block_p0303_b037

},

### block_p0303_b038

"request_id": "req_01HXAMPLE",

### block_p0303_b039

"server_time": "2026-05-04T08:16:30+08:00"

### block_p0303_b040

}

### block_p0303_b041

后端至少校验：

### block_p0303_b042

1. 决策是否存在。

### block_p0303_b043

2. 决策是否属于当前组织。

### block_p0303_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0303_b045

AutoMage-2-MVP 架构设计文档·杨卓303

### block_p0303_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 303

## 表格

无。

## 备注

无。

<!-- 来自 page_0303.md 全文结束 -->

<!-- 来自 page_0304.md 全文开始 -->

# Page 0304

## 原始文本块

### block_p0304_b001

2026 年5 月3 日

### block_p0304_b002

3. 当前用户是否有权确认。

### block_p0304_b003

4. 决策状态是否为pending。

### block_p0304_b004

5. confirmed_option 是否存在于候选方案中。

### block_p0304_b005

6. 如果是custom_confirm，是否填写自定义方案。

### block_p0304_b006

7. 是否已经确认过。

### block_p0304_b007

8. 是否可以生成任务。

### block_p0304_b008

9. 生成任务是否满足幂等。

### block_p0304_b009

14.8任务获取接口

### block_p0304_b010

14.8.1GET /api/v1/tasks

### block_p0304_b011

该接口用于获取任务列表。Staff Agent 用它获取员工每日任务，Manager Agent 用它获

### block_p0304_b012

取部门任务，Executive Agent 用它跟踪老板决策产生的关键任务。

### block_p0304_b013

14.8.2请求参数

### block_p0304_b014

Query 参数：

### block_p0304_b015

参数类型是否必填说明

### block_p0304_b016

org_idnumber / string是组织ID

### block_p0304_b017

assignee_user_idnumber / string否执行人

### block_p0304_b018

department_idnumber / string否部门ID

### block_p0304_b019

statusstring否任务状态

### block_p0304_b020

prioritystring否优先级

### block_p0304_b021

source_typestring否来源类型

### block_p0304_b022

source_decision_idstring / number否来源决策

### block_p0304_b023

due_fromstring否截止时间起点

### block_p0304_b024

due_tostring否截止时间终点

### block_p0304_b025

pagenumber否页码

### block_p0304_b026

page_sizenumber否每页数量

### block_p0304_b027

示例：

### block_p0304_b028

GET /api/v1/tasks?org_id=1&assignee_user_id=10086&status=pending&page=1&page_size=20

### block_p0304_b029

14.8.3响应参数

### block_p0304_b030

{

### block_p0304_b031

"success": true,

### block_p0304_b032

"code": "OK",

### block_p0304_b033

"message": "success",

### block_p0304_b034

"data": {

### block_p0304_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0304_b036

AutoMage-2-MVP 架构设计文档·杨卓304

### block_p0304_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 304

## 表格

无。

## 备注

无。

<!-- 来自 page_0304.md 全文结束 -->

<!-- 来自 page_0305.md 全文开始 -->

# Page 0305

## 原始文本块

### block_p0305_b001

2026 年5 月3 日

### block_p0305_b002

"items": [

### block_p0305_b003

{

### block_p0305_b004

"task_id": 9001,

### block_p0305_b005

"org_id": 1,

### block_p0305_b006

"department_id": 12,

### block_p0305_b007

"task_title": " 补充decision_logs 表结构草案",

### block_p0305_b008

"task_description": " 根据老板确认的方案A，设计独立decision_logs 表结构。",

### block_p0305_b009

"source_type": "executive_decision",

### block_p0305_b010

"source_decision_id": "decision_0001",

### block_p0305_b011

"assignee_user_id": 20002,

### block_p0305_b012

"assignee_role": "backend",

### block_p0305_b013

"priority": "high",

### block_p0305_b014

"status": "pending",

### block_p0305_b015

"due_at": "2026-05-04T18:00:00+08:00",

### block_p0305_b016

"confirm_required": true,

### block_p0305_b017

"created_at": "2026-05-04T08:16:35+08:00"

### block_p0305_b018

}

### block_p0305_b019

],

### block_p0305_b020

"pagination": {

### block_p0305_b021

"page": 1,

### block_p0305_b022

"page_size": 20,

### block_p0305_b023

"total": 1,

### block_p0305_b024

"has_more": false

### block_p0305_b025

}

### block_p0305_b026

},

### block_p0305_b027

"request_id": "req_01HXAMPLE",

### block_p0305_b028

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0305_b029

}

### block_p0305_b030

权限规则：

### block_p0305_b031

1. Staff Agent 只能查询本人任务。

### block_p0305_b032

2. Manager Agent 只能查询本部门任务。

### block_p0305_b033

3. Executive Agent 可以查询组织级关键任务。

### block_p0305_b034

4. 跨部门任务按授权范围返回。

### block_p0305_b035

5. 无权限任务不返回明细。

### block_p0305_b036

14.9汇总读取接口

### block_p0305_b037

14.9.1GET /api/v1/summaries

### block_p0305_b038

该接口用于读取Staff、Manager、Executive 或Dream 生成的汇总数据。

### block_p0305_b039

Manager Agent 读取Staff 汇总时，优先通过日报接口或Work Record 读取；Executive

### block_p0305_b040

Agent 读取部门汇总时，使用该接口读取Manager Summary；老板看板也可以使用该接口读

### block_p0305_b041

取组织级Summary。

### block_p0305_b042 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0305_b043

AutoMage-2-MVP 架构设计文档·杨卓305

### block_p0305_b044 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 305

## 表格

无。

## 备注

无。

<!-- 来自 page_0305.md 全文结束 -->

<!-- 来自 page_0306.md 全文开始 -->

# Page 0306

## 原始文本块

### block_p0306_b001

2026 年5 月3 日

### block_p0306_b002

14.9.2请求参数

### block_p0306_b003

参数类型是否必填说明

### block_p0306_b004

org_idnumber / string是组织ID

### block_p0306_b005

scope_typestring否汇总范围

### block_p0306_b006

scope_idnumber / string否用户、部门或组织ID

### block_p0306_b007

summary_typestring否汇总类型

### block_p0306_b008

summary_datestring否汇总日期

### block_p0306_b009

date_fromstring否起始日期

### block_p0306_b010

date_tostring否结束日期

### block_p0306_b011

department_idnumber / string否部门ID

### block_p0306_b012

statusstring否状态

### block_p0306_b013

pagenumber否页码

### block_p0306_b014

page_sizenumber否每页数量

### block_p0306_b015

示例：

### block_p0306_b016

GET /api/v1/summaries?org_id=1&summary_type=department_daily_summary&summary_date=2026-05-03

### block_p0306_b017

14.9.3响应参数

### block_p0306_b018

{

### block_p0306_b019

"success": true,

### block_p0306_b020

"code": "OK",

### block_p0306_b021

"message": "success",

### block_p0306_b022

"data": {

### block_p0306_b023

"items": [

### block_p0306_b024

{

### block_p0306_b025

"summary_id": 801,

### block_p0306_b026

"org_id": 1,

### block_p0306_b027

"department_id": 12,

### block_p0306_b028

"summary_type": "department_daily_summary",

### block_p0306_b029

"scope_type": "department",

### block_p0306_b030

"scope_id": 12,

### block_p0306_b031

"summary_date": "2026-05-03",

### block_p0306_b032

"title": "2026-05-03 架构组部门日报",

### block_p0306_b033

"content": " 今日架构组主要完成Staff Schema 字段定义和数据库映射梳理。",

### block_p0306_b034

"source_count": 8,

### block_p0306_b035

"status": "submitted",

### block_p0306_b036

"meta": {

### block_p0306_b037

"schema_id": "schema_v1_manager",

### block_p0306_b038

"schema_version": "1.0.0",

### block_p0306_b039

"overall_health": "yellow",

### block_p0306_b040

"top_3_risks": []

### block_p0306_b041

},

### block_p0306_b042

"created_at": "2026-05-03T21:25:00+08:00"

### block_p0306_b043

}

### block_p0306_b044 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0306_b045

AutoMage-2-MVP 架构设计文档·杨卓306

### block_p0306_b046 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 306

## 表格

无。

## 备注

无。

<!-- 来自 page_0306.md 全文结束 -->

<!-- 来自 page_0307.md 全文开始 -->

# Page 0307

## 原始文本块

### block_p0307_b001

2026 年5 月3 日

### block_p0307_b002

],

### block_p0307_b003

"pagination": {

### block_p0307_b004

"page": 1,

### block_p0307_b005

"page_size": 20,

### block_p0307_b006

"total": 1,

### block_p0307_b007

"has_more": false

### block_p0307_b008

}

### block_p0307_b009

},

### block_p0307_b010

"request_id": "req_01HXAMPLE",

### block_p0307_b011

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0307_b012

}

### block_p0307_b013

14.9.4来源追溯接口

### block_p0307_b014

如需查看某个Summary 的来源，可补充：

### block_p0307_b015

GET /api/v1/summaries/{summary_id}/sources

### block_p0307_b016

响应：

### block_p0307_b017

{

### block_p0307_b018

"success": true,

### block_p0307_b019

"code": "OK",

### block_p0307_b020

"message": "success",

### block_p0307_b021

"data": {

### block_p0307_b022

"summary_id": 801,

### block_p0307_b023

"sources": [

### block_p0307_b024

{

### block_p0307_b025

"source_type": "work_record",

### block_p0307_b026

"source_id": 301

### block_p0307_b027

},

### block_p0307_b028

{

### block_p0307_b029

"source_type": "work_record",

### block_p0307_b030

"source_id": 302

### block_p0307_b031

}

### block_p0307_b032

]

### block_p0307_b033

},

### block_p0307_b034

"request_id": "req_01HXAMPLE",

### block_p0307_b035

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0307_b036

}

### block_p0307_b037

14.10异常上报接口

### block_p0307_b038

14.10.1POST /api/v1/incidents

### block_p0307_b039

该接口用于创建异常或风险记录。Staff Agent、Manager Agent、Dream、后端规则都可

### block_p0307_b040

以在权限范围内调用。

### block_p0307_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0307_b042

AutoMage-2-MVP 架构设计文档·杨卓307

### block_p0307_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 307

## 表格

无。

## 备注

无。

<!-- 来自 page_0307.md 全文结束 -->

<!-- 来自 page_0308.md 全文开始 -->

# Page 0308

## 原始文本块

### block_p0308_b001

2026 年5 月3 日

### block_p0308_b002

14.10.2请求参数

### block_p0308_b003

请求头：

### block_p0308_b004

Authorization: Bearer <token>

### block_p0308_b005

Idempotency-Key: incident:manager_summary:801:decision_schema_missing

### block_p0308_b006

Content-Type: application/json

### block_p0308_b007

请求体：

### block_p0308_b008

{

### block_p0308_b009

"schema": {

### block_p0308_b010

"schema_id": "schema_v1_incident",

### block_p0308_b011

"schema_version": "1.0.0",

### block_p0308_b012

"org_id": 1,

### block_p0308_b013

"department_id": 12,

### block_p0308_b014

"incident_title": "Decision 表结构未确认导致任务阻塞",

### block_p0308_b015

"description": "当前Agent mock 流程中存在decision_logs 概念，但正式DDL

### block_p0308_b016

尚未建立独立决策表，影响Executive 决策确认和任务生成链路。",,→

### block_p0308_b017

"incident_type": "task_blocked",

### block_p0308_b018

"severity": "high",

### block_p0308_b019

"status": "open",

### block_p0308_b020

"source_type": "manager_summary",

### block_p0308_b021

"source_id": 801,

### block_p0308_b022

"source_record_ids": [301, 302],

### block_p0308_b023

"source_summary_ids": [801],

### block_p0308_b024

"related_task_ids": [9001],

### block_p0308_b025

"related_decision_ids": [],

### block_p0308_b026

"reporter_user_id": 20001,

### block_p0308_b027

"owner_user_id": 20002,

### block_p0308_b028

"owner_node_id": "manager_node_dept_12",

### block_p0308_b029

"need_escalation": true,

### block_p0308_b030

"escalation_level": "executive",

### block_p0308_b031

"attempted_solution": " 已在Manager Schema 中列出A/B 方案。",

### block_p0308_b032

"suggested_action": " 建议Executive Agent 将该事项整理为老板决策卡片。",

### block_p0308_b033

"meta": {

### block_p0308_b034

"input_channel": "scheduled_summary"

### block_p0308_b035

}

### block_p0308_b036

}

### block_p0308_b037

}

### block_p0308_b038

14.10.3响应参数

### block_p0308_b039

{

### block_p0308_b040

"success": true,

### block_p0308_b041

"code": "OK",

### block_p0308_b042

"message": " 异常上报成功",

### block_p0308_b043 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0308_b044

AutoMage-2-MVP 架构设计文档·杨卓308

### block_p0308_b045 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 308

## 表格

无。

## 备注

无。

<!-- 来自 page_0308.md 全文结束 -->

<!-- 来自 page_0309.md 全文开始 -->

# Page 0309

## 原始文本块

### block_p0309_b001

2026 年5 月3 日

### block_p0309_b002

"data": {

### block_p0309_b003

"incident_id": 501,

### block_p0309_b004

"status": "open",

### block_p0309_b005

"severity": "high",

### block_p0309_b006

"created_task_ids": [],

### block_p0309_b007

"escalation_required": true,

### block_p0309_b008

"audit_log_id": 7004

### block_p0309_b009

},

### block_p0309_b010

"request_id": "req_01HXAMPLE",

### block_p0309_b011

"server_time": "2026-05-04T10:30:00+08:00"

### block_p0309_b012

}

### block_p0309_b013

14.10.4异常状态更新接口

### block_p0309_b014

PATCH /api/v1/incidents/{incident_id}

### block_p0309_b015

请求体示例：

### block_p0309_b016

{

### block_p0309_b017

"status": "in_progress",

### block_p0309_b018

"owner_user_id": 20002,

### block_p0309_b019

"comment": " 后端负责人已开始确认decision_logs 表结构。",

### block_p0309_b020

"updated_by": 20001

### block_p0309_b021

}

### block_p0309_b022

用于更新异常处理状态、负责人、关闭原因、重新打开原因等。

### block_p0309_b023

14.11审计日志接口

### block_p0309_b024

14.11.1GET /api/v1/audit-logs

### block_p0309_b025

该接口用于读取审计日志。主要供管理员、Executive Agent、调试工具和复盘系统使用。

### block_p0309_b026

14.11.2请求参数

### block_p0309_b027

参数类型是否必填说明

### block_p0309_b028

org_idnumber / string是组织ID

### block_p0309_b029

actor_user_idnumber / string否操作人

### block_p0309_b030

actor_node_idstring否操作Agent

### block_p0309_b031

target_typestring否目标对象类型

### block_p0309_b032

target_idstring / number否目标对象ID

### block_p0309_b033

event_typestring否事件类型

### block_p0309_b034

date_fromstring否起始时间

### block_p0309_b035

date_tostring否结束时间

### block_p0309_b036

pagenumber否页码

### block_p0309_b037

page_sizenumber否每页数量

### block_p0309_b038 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0309_b039

AutoMage-2-MVP 架构设计文档·杨卓309

### block_p0309_b040 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 309

## 表格

无。

## 备注

无。

<!-- 来自 page_0309.md 全文结束 -->

<!-- 来自 page_0310.md 全文开始 -->

# Page 0310

## 原始文本块

### block_p0310_b001

2026 年5 月3 日

### block_p0310_b002

示例：

### block_p0310_b003

GET /api/v1/audit-logs?org_id=1&target_type=decision&target_id=decision_0001

### block_p0310_b004

14.11.3响应参数

### block_p0310_b005

{

### block_p0310_b006

"success": true,

### block_p0310_b007

"code": "OK",

### block_p0310_b008

"message": "success",

### block_p0310_b009

"data": {

### block_p0310_b010

"items": [

### block_p0310_b011

{

### block_p0310_b012

"audit_log_id": 7003,

### block_p0310_b013

"event_type": "executive_decision_confirmed",

### block_p0310_b014

"org_id": 1,

### block_p0310_b015

"actor_user_id": 30001,

### block_p0310_b016

"actor_node_id": "executive_node_org_1",

### block_p0310_b017

"target_type": "decision",

### block_p0310_b018

"target_id": "decision_0001",

### block_p0310_b019

"status_before": "pending",

### block_p0310_b020

"status_after": "confirmed",

### block_p0310_b021

"source_type": "executive_schema",

### block_p0310_b022

"source_id": "exec_schema_001",

### block_p0310_b023

"payload_summary": " 老板确认方案A：新增独立decision_logs 表。",

### block_p0310_b024

"event_at": "2026-05-04T08:16:30+08:00"

### block_p0310_b025

}

### block_p0310_b026

],

### block_p0310_b027

"pagination": {

### block_p0310_b028

"page": 1,

### block_p0310_b029

"page_size": 20,

### block_p0310_b030

"total": 1,

### block_p0310_b031

"has_more": false

### block_p0310_b032

}

### block_p0310_b033

},

### block_p0310_b034

"request_id": "req_01HXAMPLE",

### block_p0310_b035

"server_time": "2026-05-04T10:00:00+08:00"

### block_p0310_b036

}

### block_p0310_b037

14.11.4审计写入规则

### block_p0310_b038

审计日志一般由后端内部写入，不建议开放普通外部写接口。

### block_p0310_b039

必须写审计的事件包括：

### block_p0310_b040

1. Staff 日报提交。

### block_p0310_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0310_b042

AutoMage-2-MVP 架构设计文档·杨卓310

### block_p0310_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 310

## 表格

无。

## 备注

无。

<!-- 来自 page_0310.md 全文结束 -->

<!-- 来自 page_0311.md 全文开始 -->

# Page 0311

## 原始文本块

### block_p0311_b001

2026 年5 月3 日

### block_p0311_b002

2. Manager 汇总生成和确认。

### block_p0311_b003

3. Executive 决策生成、推送和确认。

### block_p0311_b004

4. 任务创建、分配、状态变化和关闭。

### block_p0311_b005

5. 异常创建、上推、关闭和重新打开。

### block_p0311_b006

6. 签名生成、失败、撤回和内容变更。

### block_p0311_b007

7. 权限失败。

### block_p0311_b008

8. 幂等重放。

### block_p0311_b009

9. Dream 运行成功或失败。

### block_p0311_b010

14.12API 与Schema 的映射关系

### block_p0311_b011

API 与Schema 的映射关系如下：

### block_p0311_b012

API输入Schema输出对象说明

### block_p0311_b013

POST

### block_p0311_b014

/api/v1/agent/init

### block_p0311_b015

无Agent Session初始化Agent 节点和权限

### block_p0311_b016

POST

### block_p0311_b017

/api/v1/report/staff

### block_p0311_b018

schema_v1_staffWork Record提交员工日报

### block_p0311_b019

POST

### block_p0311_b020

/api/v1/report/manager

### block_p0311_b021

schema_v1_managerSummary提交部门汇总

### block_p0311_b022

POST

### block_p0311_b023

/api/v1/decision/commit

### block_p0311_b024

决策确认动作Decision / Task老板确认决策并生成任务

### block_p0311_b025

GET /api/v1/tasks查询参数Task 列表获取任务

### block_p0311_b026

GET

### block_p0311_b027

/api/v1/summaries

### block_p0311_b028

查询参数Summary 列表读取汇总

### block_p0311_b029

GET

### block_p0311_b030

/api/v1/summaries/{id}/sources

### block_p0311_b031

路径参数来源记录追溯Summary 来源

### block_p0311_b032

POST

### block_p0311_b033

/api/v1/incidents

### block_p0311_b034

schema_v1_incidentIncident创建异常

### block_p0311_b035

PATCH

### block_p0311_b036

/api/v1/incidents/{id}

### block_p0311_b037

状态更新Incident更新异常状态

### block_p0311_b038

GET

### block_p0311_b039

/api/v1/audit-logs

### block_p0311_b040

查询参数Audit Log 列表读取审计日志

### block_p0311_b041

更完整的关系可以表示为：

### block_p0311_b042

schema_v1_staff

### block_p0311_b043

→POST /api/v1/report/staff

### block_p0311_b044

→work_records / work_record_items

### block_p0311_b045

schema_v1_manager

### block_p0311_b046

→POST /api/v1/report/manager

### block_p0311_b047

→summaries / summary_source_links

### block_p0311_b048

schema_v1_executive

### block_p0311_b049 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0311_b050

AutoMage-2-MVP 架构设计文档·杨卓311

### block_p0311_b051 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 311

## 表格

无。

## 备注

无。

<!-- 来自 page_0311.md 全文结束 -->

<!-- 来自 page_0312.md 全文开始 -->

# Page 0312

## 原始文本块

### block_p0312_b001

2026 年5 月3 日

### block_p0312_b002

→Dream / Executive Agent 生成

### block_p0312_b003

→summaries / decision candidate

### block_p0312_b004

decision confirm action

### block_p0312_b005

→POST /api/v1/decision/commit

### block_p0312_b006

→decisions / tasks / task_assignments

### block_p0312_b007

schema_v1_task

### block_p0312_b008

→后端任务创建逻辑

### block_p0312_b009

→tasks / task_assignments / task_updates

### block_p0312_b010

schema_v1_incident

### block_p0312_b011

→POST /api/v1/incidents

### block_p0312_b012

→incidents / incident_updates

### block_p0312_b013

需要注意，schema_v1_executive 通常由Dream 或Executive Agent 生成，并用于老板

### block_p0312_b014

卡片展示；老板确认动作本身通过/api/v1/decision/commit 提交。二者不要混淆。

### block_p0312_b015

14.13API 与数据库的映射关系

### block_p0312_b016

API 最终需要落到数据库事实表中。MVP 阶段建议按以下方式映射。

### block_p0312_b017

14.13.1Staff 日报提交映射

### block_p0312_b018

接口：

### block_p0312_b019

POST /api/v1/report/staff

### block_p0312_b020

数据库映射：

### block_p0312_b021

API / Schema 内容数据库对象说明

### block_p0312_b022

Staff Schema 主信息work_records日报主记录

### block_p0312_b023

work_progresswork_record_items字段明细

### block_p0312_b024

issues_facedwork_record_items字段明细

### block_p0312_b025

solution_attemptwork_record_items字段明细

### block_p0312_b026

need_supportwork_record_items字段明细

### block_p0312_b027

support_detailwork_record_items字段明细

### block_p0312_b028

next_day_planwork_record_items字段明细

### block_p0312_b029

resource_usagework_record_items字段明细

### block_p0312_b030

artifactsartifacts / artifact_links产出物

### block_p0312_b031

高风险或支持需求incidents条件生成

### block_p0312_b032

明确后续行动tasks条件生成

### block_p0312_b033

提交与签名行为audit_logs审计记录

### block_p0312_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0312_b035

AutoMage-2-MVP 架构设计文档·杨卓312

### block_p0312_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 312

## 表格

无。

## 备注

无。

<!-- 来自 page_0312.md 全文结束 -->

<!-- 来自 page_0313.md 全文开始 -->

# Page 0313

## 原始文本块

### block_p0313_b001

2026 年5 月3 日

### block_p0313_b002

14.13.2Manager 汇总提交映射

### block_p0313_b003

接口：

### block_p0313_b004

POST /api/v1/report/manager

### block_p0313_b005

数据库映射：

### block_p0313_b006

API / Schema 内容数据库对象说明

### block_p0313_b007

部门汇总主信息summaries部门日报

### block_p0313_b008

source_record_idssummary_source_links来源Staff 记录

### block_p0313_b009

top_3_riskssummaries.meta / incidents风险信息

### block_p0313_b010

blocked_itemsincidents条件生成异常

### block_p0313_b011

manager_decisionsDecision 相关表/ audit_logs部门内决策

### block_p0313_b012

need_executive_decisionDecision 候选对象/ summaries.meta上推老板事项

### block_p0313_b013

next_day_adjustmenttasksManager 确认后生成

### block_p0313_b014

签名与确认audit_logs审计记录

### block_p0313_b015

14.13.3Executive 决策确认映射

### block_p0313_b016

接口：

### block_p0313_b017

POST /api/v1/decision/commit

### block_p0313_b018

数据库映射：

### block_p0313_b019

API 内容数据库对象说明

### block_p0313_b020

决策确认结果Decision 表/ summaries.meta记录老板选择

### block_p0313_b021

confirmed_optionDecision 字段最终方案

### block_p0313_b022

confirmed_byDecision 字段确认人

### block_p0313_b023

confirmed_atDecision 字段确认时间

### block_p0313_b024

签名字段Decision 字段/ meta签名信息

### block_p0313_b025

generated_taskstasks创建正式任务

### block_p0313_b026

任务分配task_assignments分配执行人

### block_p0313_b027

任务创建动态task_updates创建记录

### block_p0313_b028

确认行为audit_logs审计记录

### block_p0313_b029

如果MVP 阶段暂未建立独立Decision 表，可以先用summaries.meta + audit_logs +

### block_p0313_b030

tasks.meta.source_decision_id 承载，但后续应补齐独立Decision 对象。

### block_p0313_b031

14.13.4任务读取映射

### block_p0313_b032

接口：

### block_p0313_b033

GET /api/v1/tasks

### block_p0313_b034 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0313_b035

AutoMage-2-MVP 架构设计文档·杨卓313

### block_p0313_b036 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 313

## 表格

无。

## 备注

无。

<!-- 来自 page_0313.md 全文结束 -->

<!-- 来自 page_0314.md 全文开始 -->

# Page 0314

## 原始文本块

### block_p0314_b001

2026 年5 月3 日

### block_p0314_b002

数据库映射：

### block_p0314_b003

API 查询参数数据库对象说明

### block_p0314_b004

assignee_user_idtask_assignments.user_id查询个人任务

### block_p0314_b005

department_idtasks.department_id查询部门任务

### block_p0314_b006

statustasks.status按状态过滤

### block_p0314_b007

prioritytasks.priority按优先级过滤

### block_p0314_b008

source_decision_idtasks.meta.source_decision_id按来源决策过滤

### block_p0314_b009

任务动态task_updates可选展开

### block_p0314_b010

14.13.5汇总读取映射

### block_p0314_b011

接口：

### block_p0314_b012

GET /api/v1/summaries

### block_p0314_b013

GET /api/v1/summaries/{summary_id}/sources

### block_p0314_b014

数据库映射：

### block_p0314_b015

API 内容数据库对象说明

### block_p0314_b016

汇总列表summaries读取部门或组织摘要

### block_p0314_b017

来源记录summary_source_links追溯来源

### block_p0314_b018

来源Staff 日报work_records下钻读取

### block_p0314_b019

来源字段明细work_record_items下钻读取

### block_p0314_b020

汇总元数据summaries.meta风险、Schema、签名等

### block_p0314_b021

14.13.6异常上报映射

### block_p0314_b022

接口：

### block_p0314_b023

POST /api/v1/incidents

### block_p0314_b024

PATCH /api/v1/incidents/{incident_id}

### block_p0314_b025

数据库映射：

### block_p0314_b026

API / Schema 内容数据库对象说明

### block_p0314_b027

Incident 主信息incidents异常主记录

### block_p0314_b028

状态变化incident_updates异常动态

### block_p0314_b029

生成任务tasks条件创建

### block_p0314_b030

关联任务incidents.meta.related_task_ids

### block_p0314_b031

或关系表

### block_p0314_b032

追踪处理任务

### block_p0314_b033

关联决策incidents.meta.related_decision_ids追踪上推决策

### block_p0314_b034

异常操作audit_logs审计记录

### block_p0314_b035 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0314_b036

AutoMage-2-MVP 架构设计文档·杨卓314

### block_p0314_b037 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 314

## 表格

无。

## 备注

无。

<!-- 来自 page_0314.md 全文结束 -->

<!-- 来自 page_0315.md 全文开始 -->

# Page 0315

## 原始文本块

### block_p0315_b001

2026 年5 月3 日

### block_p0315_b002

14.13.7审计日志读取映射

### block_p0315_b003

接口：

### block_p0315_b004

GET /api/v1/audit-logs

### block_p0315_b005

数据库映射：

### block_p0315_b006

API 查询参数数据库字段

### block_p0315_b007

org_idaudit_logs.org_id

### block_p0315_b008

actor_user_idaudit_logs.actor_user_id

### block_p0315_b009

actor_node_idaudit_logs.actor_node_id

### block_p0315_b010

target_typeaudit_logs.target_type

### block_p0315_b011

target_idaudit_logs.target_id

### block_p0315_b012

event_typeaudit_logs.event_type

### block_p0315_b013

date_from / date_toaudit_logs.event_at

### block_p0315_b014

14.14本章小结

### block_p0315_b015

API 契约是AutoMage-2 MVP 中连接Agent、IM、前端、后端和数据库的核心接口层。

### block_p0315_b016

它的重点不是接口数量多，而是每个接口都要有清楚的边界：谁可以调用，输入什么

### block_p0315_b017

Schema，后端校验什么，写入哪些表，失败时如何返回，重复调用如何处理，后续如何审计。

### block_p0315_b018

MVP 阶段至少要先跑通以下接口链路：

### block_p0315_b019

Agent 初始化

### block_p0315_b020

↓

### block_p0315_b021

Staff 日报提交

### block_p0315_b022

↓

### block_p0315_b023

Manager 汇总提交

### block_p0315_b024

↓

### block_p0315_b025

Executive 决策确认

### block_p0315_b026

↓

### block_p0315_b027

任务获取

### block_p0315_b028

↓

### block_p0315_b029

异常上报

### block_p0315_b030

↓

### block_p0315_b031

审计追踪

### block_p0315_b032

只要这组API 稳定，AutoMage-2 的核心闭环就可以进入真实联调：

### block_p0315_b033

员工日报

### block_p0315_b034

→部门汇总

### block_p0315_b035

→老板决策

### block_p0315_b036

→任务下发

### block_p0315_b037

→异常处理

### block_p0315_b038

→审计复盘

### block_p0315_b039

后续无论接入IM、Web 看板、小程序、行业模板还是更复杂的Dream 机制，都应建立

### block_p0315_b040

在这套API 契约之上。

### block_p0315_b041 [image]

[LOW_CONFIDENCE_BLOCK] 图像 xref 提取失败或未缓存，请对照原 PDF 该页。

### block_p0315_b042

AutoMage-2-MVP 架构设计文档·杨卓315

### block_p0315_b043 [image_supp]

![extracted](../04_ASSETS/images/image_xref_15.png)

## 图像 / 图表

- 04_ASSETS/images/image_xref_15.png
  - 来源位置：page 315

## 表格

无。

## 备注

无。

<!-- 来自 page_0315.md 全文结束 -->

## 结构化拆解

> 本小节仅作阅读辅助占位；可在此补充要点列表。**不得删除**上文「原文整理」中的任何内容。

## 关键引用锚点

- 请结合 `01_PAGES/page_XXXX.md` 内 `### block_` 标题作为锚点。

