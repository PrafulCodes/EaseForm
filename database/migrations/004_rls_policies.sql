-- ============================================
-- COMPREHENSIVE RLS POLICIES FOR ALL TABLES
-- ============================================
-- Purpose: Enforce security at database level
-- Author: EaseForm Backend Team
-- Date: 2026-02-10

-- ============================================
-- HOSTS TABLE RLS POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.hosts ENABLE ROW LEVEL SECURITY;

-- Policy: Hosts can read their own profile
CREATE POLICY "hosts_select_own"
    ON public.hosts
    FOR SELECT
    TO authenticated
    USING (id = auth.uid());

-- Policy: Hosts can update their own profile
CREATE POLICY "hosts_update_own"
    ON public.hosts
    FOR UPDATE
    TO authenticated
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Policy: New users can insert their own profile (on signup)
CREATE POLICY "hosts_insert_own"
    ON public.hosts
    FOR INSERT
    TO authenticated
    WITH CHECK (id = auth.uid());

-- Policy: Hosts cannot delete their own profile (prevent accidental deletion)
-- If deletion is needed, it should be done via admin or special procedure
CREATE POLICY "hosts_no_delete"
    ON public.hosts
    FOR DELETE
    TO authenticated
    USING (false);

-- ============================================
-- FORMS TABLE RLS POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.forms ENABLE ROW LEVEL SECURITY;

-- Policy: Public can SELECT active forms (for filling out)
-- This allows anyone to view and fill out active forms
CREATE POLICY "forms_select_active_public"
    ON public.forms
    FOR SELECT
    TO public
    USING (is_active = true);

-- Policy: Hosts can SELECT their own forms (including inactive)
CREATE POLICY "forms_select_own"
    ON public.forms
    FOR SELECT
    TO authenticated
    USING (host_id = auth.uid());

-- Policy: Hosts can INSERT their own forms
CREATE POLICY "forms_insert_own"
    ON public.forms
    FOR INSERT
    TO authenticated
    WITH CHECK (host_id = auth.uid());

-- Policy: Hosts can UPDATE their own forms
CREATE POLICY "forms_update_own"
    ON public.forms
    FOR UPDATE
    TO authenticated
    USING (host_id = auth.uid())
    WITH CHECK (host_id = auth.uid());

-- Policy: Hosts can DELETE their own forms
CREATE POLICY "forms_delete_own"
    ON public.forms
    FOR DELETE
    TO authenticated
    USING (host_id = auth.uid());

-- ============================================
-- RESPONSES TABLE RLS POLICIES
-- ============================================
-- (Already defined in 003_create_responses_table.sql)
-- Included here for completeness

ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- Policy: Public INSERT (anyone can submit responses)
CREATE POLICY "responses_insert_public"
    ON public.responses
    FOR INSERT
    TO public
    WITH CHECK (true);

-- Policy: Hosts can SELECT their own form responses
CREATE POLICY "responses_select_owner"
    ON public.responses
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.forms
            WHERE forms.id = responses.form_id
            AND forms.host_id = auth.uid()
        )
    );

-- Policy: No UPDATE (responses are immutable)
CREATE POLICY "responses_no_update"
    ON public.responses
    FOR UPDATE
    TO public
    USING (false);

-- Policy: Hosts can DELETE their own form responses
CREATE POLICY "responses_delete_owner"
    ON public.responses
    FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.forms
            WHERE forms.id = responses.form_id
            AND forms.host_id = auth.uid()
        )
    );

-- ============================================
-- HELPER FUNCTIONS FOR RLS
-- ============================================

-- Function to check if a user is the form owner
CREATE OR REPLACE FUNCTION is_form_owner(form_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.forms
        WHERE id = form_uuid
        AND host_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if a form is active
CREATE OR REPLACE FUNCTION is_form_active(form_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.forms
        WHERE id = form_uuid
        AND is_active = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON POLICY "hosts_select_own" ON public.hosts IS 'Hosts can read their own profile';
COMMENT ON POLICY "forms_select_active_public" ON public.forms IS 'Public can view active forms for filling';
COMMENT ON POLICY "forms_select_own" ON public.forms IS 'Hosts can view all their own forms';
COMMENT ON POLICY "responses_insert_public" ON public.responses IS 'Anyone can submit responses (validated by FastAPI)';
COMMENT ON POLICY "responses_select_owner" ON public.responses IS 'Only form owners can read responses';
