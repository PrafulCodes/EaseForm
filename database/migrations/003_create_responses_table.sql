-- ============================================
-- RESPONSES TABLE MIGRATION
-- ============================================
-- Purpose: Store form responses with device-based deduplication
-- Author: EaseForm Backend Team
-- Date: 2026-02-10

-- Create responses table
CREATE TABLE IF NOT EXISTS public.responses (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to forms table
    form_id UUID NOT NULL REFERENCES public.forms(id) ON DELETE CASCADE,
    
    -- Response data stored as JSONB
    -- Structure: { "question_id": "answer_value", ... }
    answers JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Device identification hash (SHA-256 of user agent + IP + form_id)
    -- Used to enforce one-response-per-device
    device_hash TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_answers CHECK (jsonb_typeof(answers) = 'object'),
    CONSTRAINT device_hash_not_empty CHECK (length(device_hash) > 0)
);

-- ============================================
-- INDEXES
-- ============================================

-- Index for querying responses by form
CREATE INDEX idx_responses_form_id ON public.responses(form_id);

-- Index for device hash lookups (one-response-per-device check)
CREATE INDEX idx_responses_device_hash ON public.responses(device_hash, form_id);

-- Index for created_at (for sorting and filtering)
CREATE INDEX idx_responses_created_at ON public.responses(created_at DESC);

-- Composite index for form owner queries
CREATE INDEX idx_responses_form_created ON public.responses(form_id, created_at DESC);

-- ============================================
-- UNIQUE CONSTRAINT (One Response Per Device)
-- ============================================

-- Enforce one response per device per form at database level
CREATE UNIQUE INDEX unique_device_per_form ON public.responses(form_id, device_hash);

-- ============================================
-- TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_responses_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_responses_updated_at
    BEFORE UPDATE ON public.responses
    FOR EACH ROW
    EXECUTE FUNCTION update_responses_updated_at();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on responses table
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- Policy 1: Public INSERT (anyone can submit responses via FastAPI)
-- FastAPI will validate form is active and enforce device hash
CREATE POLICY "responses_insert_public"
    ON public.responses
    FOR INSERT
    TO public
    WITH CHECK (true);

-- Policy 2: Hosts can SELECT their own form responses
-- Only the form owner can read responses
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

-- Policy 3: No UPDATE allowed (responses are immutable)
-- Responses cannot be edited once submitted
CREATE POLICY "responses_no_update"
    ON public.responses
    FOR UPDATE
    TO public
    USING (false);

-- Policy 4: Hosts can DELETE their own form responses
-- Only the form owner can delete responses
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
-- REALTIME
-- ============================================

-- Enable realtime for responses table
-- Hosts will receive live updates when new responses arrive
ALTER PUBLICATION supabase_realtime ADD TABLE public.responses;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE public.responses IS 'Stores form responses with device-based deduplication';
COMMENT ON COLUMN public.responses.id IS 'Unique response identifier';
COMMENT ON COLUMN public.responses.form_id IS 'Reference to the form this response belongs to';
COMMENT ON COLUMN public.responses.answers IS 'JSONB object containing question-answer pairs';
COMMENT ON COLUMN public.responses.device_hash IS 'SHA-256 hash of device fingerprint for deduplication';
COMMENT ON COLUMN public.responses.created_at IS 'Timestamp when response was submitted';
COMMENT ON COLUMN public.responses.updated_at IS 'Timestamp when response was last updated';
