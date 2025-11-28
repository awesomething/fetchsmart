-- Migration: Add optional columns to resume_submissions table
-- Run this in Supabase SQL Editor or via CLI
-- All columns are nullable (optional) - safe to run on existing tables

-- Add optional columns to existing resume_submissions table
-- Note: job_opening_id is a plain INTEGER (no foreign key) to keep tables independent
ALTER TABLE resume_submissions 
ADD COLUMN IF NOT EXISTS job_opening_id INTEGER NULL,
ADD COLUMN IF NOT EXISTS submission_number VARCHAR(50) UNIQUE NULL,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'submitted' NULL,
ADD COLUMN IF NOT EXISTS match_score DECIMAL(3,2) NULL,
ADD COLUMN IF NOT EXISTS notes TEXT NULL,
ADD COLUMN IF NOT EXISTS recruiter_id UUID REFERENCES recruiters(id) NULL,
ADD COLUMN IF NOT EXISTS candidate_github TEXT NULL,
ADD COLUMN IF NOT EXISTS candidate_linkedin TEXT NULL;

-- Verify columns were added (optional check)
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'resume_submissions'
AND column_name IN (
  'job_opening_id', 'submission_number', 'status', 'match_score',
  'notes', 'recruiter_id', 'candidate_github', 'candidate_linkedin'
)
ORDER BY column_name;

