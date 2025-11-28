# Employer Access to Resume Data - Best Practices Analysis

## Current Implementation

**Current Access Pattern:**
- Employers access resumes through `hiring_pipeline` → `resume_submissions` relationship
- **Limited fields:** Only `name` and `job_opening_id` are currently exposed
- **Line 30 in hiring_pipeline_tool.py:**
  ```python
  .select("*, resume_submissions!inner(name, job_opening_id)")
  ```

## Best Practice Recommendation

### ✅ YES - Grant Access, BUT Through Controlled Relationship

**Why this is best practice:**

1. **Principle of Least Privilege:**
   - Employers only see resumes for candidates **submitted to them** (via pipeline)
   - No direct table access = can't browse all resumes
   - Access is scoped to their hiring pipeline

2. **Audit Trail:**
   - Access through pipeline creates automatic audit trail
   - Can track which employers viewed which resumes
   - Know when resume was accessed (via pipeline query)

3. **Data Privacy:**
   - Candidates are only visible after recruiter submits them
   - Respects candidate consent (submission = consent to share)
   - Can add Row Level Security (RLS) policies in Supabase

4. **Workflow Alignment:**
   - Matches real-world process: Recruiter submits → Employer reviews
   - Employers don't need to see all resumes, only submitted ones

## Recommended Implementation

### Option 1: Expand Pipeline Query (Recommended)

Update `hiring_pipeline_tool.py` to include more resume fields:

```python
.select("*, resume_submissions!inner(*)")
# Or selectively:
.select("*, resume_submissions!inner(id, name, email, phone, resume_filename, resume_data, file_type, summary, extracted_text, skills, years_experience, candidate_github, candidate_linkedin)")
```

**Pros:**
- Simple, one query
- Maintains relationship-based access
- All data in one response

**Cons:**
- Large payload if many candidates
- Includes all fields (even if not needed)

### Option 2: Add New MCP Tool for Resume Details

Create `get_candidate_resume` tool that:
- Takes `submission_id` as parameter
- Verifies submission exists in `hiring_pipeline` (employer has access)
- Returns full resume data

**Pros:**
- More granular control
- Can add additional security checks
- Lazy loading (only fetch when needed)

**Cons:**
- More complex
- Requires additional tool

### Option 3: Hybrid Approach (Best of Both)

1. **Pipeline status:** Include basic resume fields (name, email, skills summary)
2. **Resume details tool:** Full resume data when employer requests details

**Pros:**
- Efficient (basic data in list, details on demand)
- Better UX (faster initial load)
- Still relationship-based

**Cons:**
- Two queries needed for full details

## Security Considerations

### Supabase Row Level Security (RLS)

Add RLS policies to ensure employers only see their submissions:

```sql
-- Policy: Employers can only see resumes for candidates in their pipeline
CREATE POLICY "Employers can view submitted resumes"
ON resume_submissions FOR SELECT
USING (
  id IN (
    SELECT submission_id 
    FROM hiring_pipeline 
    WHERE job_opening_id IN (
      SELECT id FROM job_flow WHERE employer_id = auth.uid()
    )
  )
);
```

### Access Control in Code

1. **Verify relationship exists:**
   - Before returning resume data, verify `submission_id` exists in `hiring_pipeline`
   - This ensures employer has legitimate access

2. **Log access:**
   - Log when employers access resume data
   - Track for audit purposes

## Recommended Fields to Expose

**For Pipeline List View:**
- `id`, `name`, `email`, `phone`
- `skills` (summary), `years_experience`
- `candidate_github`, `candidate_linkedin`
- `summary`, `match_score`

**For Detailed Resume View:**
- All above fields
- `resume_filename`, `resume_data`, `file_type`
- `extracted_text` (full resume text)
- `classification_details`, `candidate_tier`

## Implementation Recommendation

**Go with Option 1 (Expand Pipeline Query) + RLS Policies:**

1. Update `hiring_pipeline_tool.py` to select more resume fields
2. Add Supabase RLS policies for additional security
3. Keep access through relationship (no direct table access)

This provides:
- ✅ Security (relationship-based access)
- ✅ Privacy (only submitted candidates)
- ✅ Audit trail (pipeline queries)
- ✅ Simplicity (one query)
- ✅ Flexibility (can add RLS later)

