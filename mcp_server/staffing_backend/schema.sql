-- Staffing Agency Database Schema
-- Run these SQL commands in your Supabase SQL editor

-- 1. Create employers table (replaces suppliers)
CREATE TABLE IF NOT EXISTS employers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name VARCHAR(255) NOT NULL,
  industry VARCHAR(100),
  contact_name VARCHAR(255),
  contact_email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  website VARCHAR(255),
  address TEXT,
  company_size VARCHAR(50), -- startup, small, medium, enterprise
  preferred_staffing_types TEXT[], -- contract, contract-to-hire, direct-hire
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create recruiters table (replaces buyer accounts)
CREATE TABLE IF NOT EXISTS recruiters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50),
  agency_name VARCHAR(255),
  specializations TEXT[], -- e.g., ['frontend', 'backend', 'devops']
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Create hiring_pipeline table (replaces production queue)
CREATE TABLE IF NOT EXISTS hiring_pipeline (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  submission_id INTEGER REFERENCES resume_submissions(id),
  stage VARCHAR(50) NOT NULL, -- screening, technical-interview, cultural-fit, offer, hired
  stage_status VARCHAR(50) DEFAULT 'pending', -- pending, in-progress, completed, rejected
  scheduled_date TIMESTAMP,
  completed_date TIMESTAMP,
  interviewer VARCHAR(255),
  feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Add optional columns to existing resume_submissions table
-- All columns are nullable (optional) - existing rows will have NULL values
-- DEFAULT values are provided for convenience but columns can still be NULL
ALTER TABLE resume_submissions 
ADD COLUMN IF NOT EXISTS job_opening_id INTEGER NULL,
ADD COLUMN IF NOT EXISTS submission_number VARCHAR(50) UNIQUE NULL,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'submitted' NULL,
ADD COLUMN IF NOT EXISTS match_score DECIMAL(3,2) NULL,
ADD COLUMN IF NOT EXISTS notes TEXT NULL,
ADD COLUMN IF NOT EXISTS recruiter_id UUID REFERENCES recruiters(id) NULL,
ADD COLUMN IF NOT EXISTS candidate_github TEXT NULL,
ADD COLUMN IF NOT EXISTS candidate_linkedin TEXT NULL;

-- Note: In PostgreSQL, columns are NULL by default unless you specify NOT NULL
-- The explicit NULL here is for clarity, but it's the default behavior
-- This ensures:
-- 1. Existing rows won't break (they get NULL for new columns)
-- 2. New rows can omit these fields (they'll be NULL)
-- 3. Code can check for NULL to determine if fields are provided

-- 6. Add optional columns to existing job_flow table (if needed for enhanced filtering)
-- All columns are nullable (optional) - existing rows will have NULL values
-- DEFAULT values are provided for convenience but columns can still be NULL
ALTER TABLE job_flow 
ADD COLUMN IF NOT EXISTS job_description TEXT NULL,
ADD COLUMN IF NOT EXISTS tech_stack TEXT[] NULL, -- Array of technologies
ADD COLUMN IF NOT EXISTS years_experience INTEGER NULL,
ADD COLUMN IF NOT EXISTS work_type VARCHAR(50) NULL, -- contract, contract-to-hire, direct-hire
ADD COLUMN IF NOT EXISTS remote_type VARCHAR(50) NULL, -- remote, hybrid, on-site
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'open' NULL, -- open, filled, closed
ADD COLUMN IF NOT EXISTS urgency VARCHAR(50) DEFAULT 'medium' NULL, -- low, medium, high, critical
ADD COLUMN IF NOT EXISTS posted_date TIMESTAMP DEFAULT NOW() NULL;

-- 7. Create indexes for performance
--CREATE INDEX IF NOT EXISTS idx_resume_status ON resume_submissions(status);
CREATE INDEX IF NOT EXISTS idx_resume_job ON resume_submissions(job_opening_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_stage ON hiring_pipeline(stage, stage_status);
CREATE INDEX IF NOT EXISTS idx_employers_active ON employers(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_recruiters_active ON recruiters(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_job_location ON job_flow(job_location);
--CREATE INDEX IF NOT EXISTS idx_job_status ON job_flow(status) WHERE status IS NOT NULL;
--CREATE INDEX IF NOT EXISTS idx_job_urgency ON job_flow(urgency) WHERE urgency IS NOT NULL;

