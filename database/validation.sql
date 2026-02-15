-- Database Validation Script for easeform

-- 1. Check for required tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('forms', 'questions', 'responses', 'profiles');

-- 2. Verify RLS is enabled on all tables
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- 3. List all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'public';

-- 4. Check for indexes on foreign keys and frequently queried columns
SELECT
    t.relname AS table_name,
    i.relname AS index_name,
    a.attname AS column_name
FROM
    pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a
WHERE
    t.oid = ix.indrelid
    AND i.oid = ix.indexrelid
    AND a.attrelid = t.oid
    AND a.attnum = ANY(ix.indkey)
    AND t.relkind = 'r'
    AND t.relname IN ('forms', 'questions', 'responses', 'profiles')
ORDER BY
    t.relname,
    i.relname;

-- 5. specific index checks (Mental check against this list)
-- forms: user_id (for listing), closed (for filtering), is_active (for filtering)
-- questions: form_id (for retrieval)
-- responses: form_id (for listing), device_hash (for uniqueness check)

