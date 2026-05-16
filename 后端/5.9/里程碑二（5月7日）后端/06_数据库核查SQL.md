# 数据库核查 SQL

## 1. 数据库信息

- Host：`182.92.93.16`
- Database：`automage`
- User：`automage`

说明：

- 本文档用于联调后核查正式表是否真实写入
- 默认按 PostgreSQL 语法编写

---

## 2. 基础数据核查

```sql
select 'organizations' as table_name, count(*) as total_count from organizations
union all
select 'departments', count(*) from departments
union all
select 'users', count(*) from users
union all
select 'roles', count(*) from roles
union all
select 'agent_profiles', count(*) from agent_profiles;
```

---

## 3. Staff 日报链路核查

### 3.1 最近日报主记录

```sql
select id, public_id, org_id, department_id, user_id, node_id, record_date, created_at
from work_records
order by id desc
limit 20;
```

### 3.2 最近日报明细

```sql
select id, work_record_id, field_key, field_label, created_at
from work_record_items
order by id desc
limit 50;
```

### 3.3 快照镜像核查

```sql
select id, node_id, user_id, role, created_at
from staff_reports
order by id desc
limit 20;
```

---

## 4. 高风险异常链路核查

### 4.1 最近异常主记录

```sql
select id, public_id, source_record_id, reporter_user_id, severity, status, created_at
from incidents
order by id desc
limit 20;
```

### 4.2 最近异常更新记录

```sql
select id, incident_id, actor_user_id, status_before, status_after, event_at
from incident_updates
order by id desc
limit 50;
```

---

## 5. Manager 汇总链路核查

### 5.1 最近汇总主记录

```sql
select id, public_id, department_id, summary_date, status, source_count, created_at
from summaries
order by id desc
limit 20;
```

### 5.2 汇总来源关联

```sql
select id, summary_id, source_type, source_id, created_at
from summary_source_links
order by id desc
limit 50;
```

### 5.3 快照镜像核查

```sql
select id, node_id, user_id, role, created_at
from manager_reports
order by id desc
limit 20;
```

---

## 6. Dream / 决策链路核查

### 6.1 最近正式决策

```sql
select id, public_id, source_summary_id, requester_user_id, selected_option_key, status, created_at
from decision_records
order by id desc
limit 20;
```

### 6.2 最近决策日志

```sql
select id, decision_record_id, actor_user_id, action_type, status_before, status_after, event_at
from decision_logs
order by id desc
limit 50;
```

### 6.3 兼容镜像核查

```sql
select id, node_id, user_id, role, created_at
from agent_decision_logs
order by id desc
limit 20;
```

---

## 7. 正式任务链路核查

### 7.1 最近正式任务

```sql
select id, public_id, decision_record_id, creator_user_id, title, status, created_at
from tasks
order by id desc
limit 20;
```

### 7.2 最近任务指派

```sql
select id, task_id, user_id, assignment_type, created_at
from task_assignments
order by id desc
limit 50;
```

### 7.3 最近任务更新

```sql
select id, task_id, actor_user_id, update_type, status_before, status_after, event_at
from task_updates
order by id desc
limit 50;
```

### 7.4 快照镜像核查

```sql
select id, task_id, assignee_user_id, title, status, created_at
from task_queue
order by id desc
limit 50;
```

---

## 8. 审计日志核查

```sql
select id, actor_user_id, target_type, target_id, action, summary, event_at
from audit_logs
order by id desc
limit 100;
```

---

## 9. 最小闭环专项核查

### 9.1 查询某天日报是否落库

```sql
select id, public_id, user_id, record_date, created_at
from work_records
where record_date = date '2026-05-07'
order by id desc;
```

### 9.2 查询某次汇总是否关联了来源日报

```sql
select s.id as summary_id, s.public_id, l.source_type, l.source_id
from summaries s
join summary_source_links l on l.summary_id = s.id
order by s.id desc, l.id desc
limit 50;
```

### 9.3 查询某次决策是否生成了正式任务

```sql
select d.public_id as decision_public_id, t.public_id as task_public_id, t.title, t.status
from decision_records d
left join tasks t on t.decision_record_id = d.id
order by d.id desc, t.id desc
limit 50;
```

### 9.4 查询任务更新是否产生了事件记录

```sql
select t.public_id as task_public_id, u.id as update_id, u.status_before, u.status_after, u.event_at
from tasks t
join task_updates u on u.task_id = t.id
order by u.id desc
limit 50;
```

### 9.5 查询最近关键审计动作

```sql
select actor_user_id, target_type, action, summary, event_at
from audit_logs
where target_type in ('work_records', 'summaries', 'decision_records', 'tasks')
order by id desc
limit 50;
```
