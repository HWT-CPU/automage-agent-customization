-- 08_readonly_db_check.sql
-- 仅包含只读语句（SELECT / WITH）。禁止在本文件中加入写操作。

-- 1) 表清单
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2) 字段清单
SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- 3) 主键
SELECT tc.table_name, tc.constraint_name, kcu.column_name, kcu.ordinal_position
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_catalog = kcu.constraint_catalog
 AND tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public' AND tc.constraint_type = 'PRIMARY KEY'
ORDER BY tc.table_name, kcu.ordinal_position;

-- 4) 外键
SELECT tc.table_name AS from_table, tc.constraint_name,
       kcu.column_name AS from_column,
       ccu.table_name AS to_table,
       ccu.column_name AS to_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_catalog = kcu.constraint_catalog
 AND tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_catalog = ccu.constraint_catalog
 AND tc.constraint_schema = ccu.constraint_schema
 AND tc.constraint_name = ccu.constraint_name
WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY from_table, constraint_name;

-- 5) 索引
SELECT tab.relname AS table_name, idx.relname AS index_name, pg_get_indexdef(i.indexrelid) AS index_def
FROM pg_index i
JOIN pg_class idx ON idx.oid = i.indexrelid
JOIN pg_class tab ON tab.oid = i.indrelid
JOIN pg_namespace n ON n.oid = tab.relnamespace
WHERE n.nspname = 'public' AND tab.relkind = 'r'
ORDER BY tab.relname, idx.relname;

-- 6) 行数估计
SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;

-- 7) Staff 日报相关表概览（示例：取少量列，避免全表扫描）
SELECT 'staff_reports' AS tbl, count(*)::bigint AS est_cnt FROM staff_reports;
SELECT 'work_records' AS tbl, count(*)::bigint AS est_cnt FROM work_records;
SELECT 'work_record_items' AS tbl, count(*)::bigint AS est_cnt FROM work_record_items;

-- 8) Manager 汇总相关
SELECT 'manager_reports' AS tbl, count(*)::bigint AS est_cnt FROM manager_reports;
SELECT 'summaries' AS tbl, count(*)::bigint AS est_cnt FROM summaries;
SELECT 'summary_source_links' AS tbl, count(*)::bigint AS est_cnt FROM summary_source_links;

-- 9) Executive 决策相关
SELECT 'decision_records' AS tbl, count(*)::bigint AS est_cnt FROM decision_records;
SELECT 'decision_logs' AS tbl, count(*)::bigint AS est_cnt FROM decision_logs;
SELECT 'agent_decision_logs' AS tbl, count(*)::bigint AS est_cnt FROM agent_decision_logs;

-- 10) Task 相关
SELECT 'tasks' AS tbl, count(*)::bigint AS est_cnt FROM tasks;
SELECT 'task_queue' AS tbl, count(*)::bigint AS est_cnt FROM task_queue;
SELECT 'task_assignments' AS tbl, count(*)::bigint AS est_cnt FROM task_assignments;
SELECT 'task_updates' AS tbl, count(*)::bigint AS est_cnt FROM task_updates;

-- 11) Audit
SELECT 'audit_logs' AS tbl, count(*)::bigint AS est_cnt FROM audit_logs;
