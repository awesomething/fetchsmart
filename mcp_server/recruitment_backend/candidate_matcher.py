"""
Intelligent Candidate Matching Engine
Matches job requirements to GitHub profiles with scoring and reasoning
"""

import re
import random
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class CandidateMatcher:
    """
    Matches candidates to job requirements using multi-factor scoring.
    For MVP: Keyword and skill-based matching
    Future: Semantic embeddings, ML-based ranking
    """
    
    def __init__(self):
        self.skill_synonyms = {
            # Frontend
            "react": ["reactjs", "react.js", "react-native"],
            "vue": ["vuejs", "vue.js"],
            "angular": ["angularjs"],
            "frontend": ["front-end", "ui", "user-interface"],
            
            # Backend
            "node": ["nodejs", "node.js"],
            "backend": ["back-end", "server-side"],
            "api": ["rest", "graphql", "restful"],
            
            # DevOps
            "kubernetes": ["k8s"],
            "ci/cd": ["cicd", "continuous-integration", "continuous-deployment"],
            "aws": ["amazon-web-services"],
            
            # Languages
            "javascript": ["js", "es6", "typescript"],
            "typescript": ["ts"],
            "python": ["py"],
        }
        
        self.experience_keywords = {
            "junior": ["junior", "entry", "1-3 years", "graduate"],
            "mid": ["mid", "intermediate", "3-5 years", "mid-level"],
            "senior": ["senior", "sr", "5+ years", "lead", "staff", "principal"]
        }
    
    def extract_requirements(self, job_description: str) -> Dict:
        """Extract key requirements from job description"""
        text = job_description.lower()
        
        # Extract skills (common tech keywords)
        tech_keywords = [
            "react", "vue", "angular", "javascript", "typescript", "python", "java",
            "go", "rust", "node", "django", "flask", "fastapi", "express",
            "kubernetes", "docker", "aws", "gcp", "azure", "terraform",
            "postgresql", "mongodb", "redis", "graphql", "rest", "api",
            "machine learning", "tensorflow", "pytorch", "data science",
            "mobile", "ios", "android", "react native"
        ]
        
        found_skills = [skill for skill in tech_keywords if skill in text]
        
        # Extract experience level
        experience_level = "mid"  # default
        for level, keywords in self.experience_keywords.items():
            if any(keyword in text for keyword in keywords):
                experience_level = level
                break
        
        # Extract years of experience
        years_match = re.search(r'(\d+)\+?\s*years?', text)
        min_years = int(years_match.group(1)) if years_match else None
        
        # Check for open source preference
        prefers_open_source = any(keyword in text for keyword in 
                                  ["open source", "open-source", "oss", "github", "contributions"])
        
        # Check for location requirements
        location_keywords = ["remote", "san francisco", "new york", "seattle", 
                           "austin", "boston", "london", "berlin"]
        location = next((loc for loc in location_keywords if loc in text), None)
        
        return {
            "skills": found_skills,
            "experience_level": experience_level,
            "min_years": min_years,
            "prefers_open_source": prefers_open_source,
            "location": location,
            "raw_text": text
        }
    
    def calculate_skill_match(self, candidate: Dict, required_skills: List[str]) -> Tuple[float, List[str]]:
        """Calculate skill match score and identify matching skills"""
        if not required_skills:
            return 0.5, []  # Neutral score if no specific skills required
        
        candidate_skills = set()
        
        # Gather all candidate skills
        candidate_skills.update([s.lower() for s in candidate.get('languages', [])])
        candidate_skills.update([s.lower() for s in candidate.get('skills', [])])
        candidate_skills.add(candidate.get('primary_language', '').lower())
        
        # Add skills from bio and tech stack summary (handle None values)
        bio = candidate.get('bio') or ''
        tech_stack = candidate.get('tech_stack_summary') or ''
        bio_text = (bio + ' ' + tech_stack).lower()
        for skill in required_skills:
            if skill in bio_text:
                candidate_skills.add(skill)
        
        # Check for synonyms
        expanded_candidate_skills = set(candidate_skills)
        for skill in candidate_skills:
            if skill in self.skill_synonyms:
                expanded_candidate_skills.update(self.skill_synonyms[skill])
        
        # Calculate matches
        matched_skills = []
        for required_skill in required_skills:
            # Direct match
            if required_skill in expanded_candidate_skills:
                matched_skills.append(required_skill)
            # Synonym match
            elif required_skill in self.skill_synonyms:
                if any(syn in expanded_candidate_skills for syn in self.skill_synonyms[required_skill]):
                    matched_skills.append(required_skill)
            # Fuzzy match (for typos or variations)
            else:
                for cand_skill in expanded_candidate_skills:
                    similarity = SequenceMatcher(None, required_skill, cand_skill).ratio()
                    if similarity > 0.8:
                        matched_skills.append(required_skill)
                        break
        
        score = len(matched_skills) / len(required_skills)
        return score, matched_skills
    
    def calculate_experience_match(self, candidate: Dict, requirements: Dict) -> Tuple[float, str]:
        """Calculate experience level match"""
        candidate_level = candidate.get('estimated_experience_level', 'Mid').lower()
        required_level = requirements.get('experience_level', 'mid').lower()
        
        level_order = ["junior", "mid", "senior"]
        
        try:
            cand_idx = level_order.index(candidate_level)
            req_idx = level_order.index(required_level)
            
            # Exact match is best
            if cand_idx == req_idx:
                return 1.0, f"Perfect match: {candidate_level.title()} level"
            # One level up is good (overqualified)
            elif cand_idx == req_idx + 1:
                return 0.9, f"Overqualified: {candidate_level.title()} for {required_level.title()} role"
            # One level down is acceptable
            elif cand_idx == req_idx - 1:
                return 0.7, f"Slightly underqualified: {candidate_level.title()} for {required_level.title()} role"
            # Two levels difference
            else:
                return 0.4, f"Experience mismatch: {candidate_level.title()} vs {required_level.title()} required"
        except:
            return 0.5, "Unable to determine experience match"
    
    def calculate_github_activity_score(self, candidate: Dict) -> Tuple[float, List[str]]:
        """Score candidate based on GitHub activity and presence"""
        reasons = []
        score = 0.0
        
        # Public repos (max 0.2)
        repos = candidate.get('public_repos', 0)
        if repos > 50:
            score += 0.2
            reasons.append(f"{repos} public repositories")
        elif repos > 20:
            score += 0.15
            reasons.append(f"{repos} public repositories")
        elif repos > 10:
            score += 0.1
        
        # Stars (max 0.3)
        stars = candidate.get('total_stars', 0)
        if stars > 500:
            score += 0.3
            reasons.append(f"{stars} GitHub stars")
        elif stars > 100:
            score += 0.2
            reasons.append(f"{stars} GitHub stars")
        elif stars > 50:
            score += 0.1
        
        # Followers (max 0.2)
        followers = candidate.get('followers', 0)
        if followers > 200:
            score += 0.2
            reasons.append(f"{followers} followers")
        elif followers > 100:
            score += 0.15
        elif followers > 50:
            score += 0.1
        
        # Popular repos (max 0.15)
        if candidate.get('has_popular_repos'):
            score += 0.15
            reasons.append("Has popular open source projects")
        
        # Open source contributor (max 0.15)
        if candidate.get('open_source_contributor'):
            score += 0.15
            reasons.append("Active open source contributor")
        
        return min(score, 1.0), reasons
    
    def match_candidates(self, candidates: List[Dict], job_description: str, 
                        job_title: str = "", limit: int = 8) -> Dict:
        """
        Match candidates to a job description and return ranked results
        """
        # Extract requirements
        requirements = self.extract_requirements(job_description)
        
        # Add job title to requirements if provided
        if job_title:
            title_skills = self.extract_requirements(job_title)
            requirements['skills'].extend(title_skills['skills'])
            requirements['skills'] = list(set(requirements['skills']))  # Remove duplicates
        
        # Score each candidate
        scored_candidates = []
        
        for candidate in candidates:
            # Calculate component scores
            skill_score, matched_skills = self.calculate_skill_match(candidate, requirements['skills'])
            exp_score, exp_reason = self.calculate_experience_match(candidate, requirements)
            activity_score, activity_reasons = self.calculate_github_activity_score(candidate)
            
            # Weighted total score
            total_score = (
                skill_score * 0.5 +      # Skills are most important
                exp_score * 0.3 +        # Experience level
                activity_score * 0.2     # GitHub activity
            )
            
            # Build match reasons
            match_reasons = []
            
            if matched_skills:
                skills_str = ", ".join(matched_skills[:5])
                match_reasons.append(f"✓ Skills: {skills_str}")
            
            match_reasons.append(f"✓ {exp_reason}")
            
            if activity_reasons:
                match_reasons.extend([f"✓ {reason}" for reason in activity_reasons[:2]])
            
            # Location bonus
            if requirements['location'] and candidate.get('location'):
                if requirements['location'] in candidate['location'].lower():
                    total_score += 0.05
                    match_reasons.append(f"✓ Location: {candidate['location']}")
            
            # Open source bonus
            if requirements['prefers_open_source'] and candidate.get('open_source_contributor'):
                total_score += 0.05
            
            # Cap score at 1.0
            total_score = min(total_score, 1.0)
            
            scored_candidates.append({
                "candidate": candidate,
                "match_score": round(total_score * 100, 1),  # Convert to 0-100
                "match_reasons": match_reasons[:4],  # Top 4 reasons
                "matched_skills": matched_skills,
                "skill_score": round(skill_score * 100, 1),
                "experience_score": round(exp_score * 100, 1),
                "activity_score": round(activity_score * 100, 1)
            })
        
        # Sort by match score
        scored_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Randomize the candidate window so repeated searches surface more variety
        window_size = min(len(scored_candidates), max(limit * 5, limit))
        candidate_window = scored_candidates[:window_size]

        if len(candidate_window) <= limit:
            selected_candidates = candidate_window
        else:
            selected_candidates = random.sample(candidate_window, limit)

        selected_candidates.sort(key=lambda x: x['match_score'], reverse=True)

        # Return top N
        top_candidates = selected_candidates
        
        return {
            "total_matches": len([c for c in scored_candidates if c['match_score'] > 50]),
            "search_query": job_description[:200],
            "requirements": requirements,
            "top_candidates": top_candidates,
            "showing": len(top_candidates)
        }


# Test function
def test_matcher():
    """Test the matcher with sample data"""
    sample_candidate = {
        "name": "John Doe",
        "github_username": "johndoe",
        "primary_language": "JavaScript",
        "languages": ["JavaScript", "TypeScript", "Python"],
        "skills": ["react", "nodejs", "docker"],
        "public_repos": 45,
        "total_stars": 320,
        "followers": 180,
        "estimated_experience_level": "Senior",
        "open_source_contributor": True,
        "has_popular_repos": True,
        "bio": "Full stack developer passionate about React and Node.js",
        "tech_stack_summary": "JavaScript developer with expertise in react, nodejs, docker"
    }
    
    job_desc = """
    Looking for a Senior Frontend Engineer with strong React and TypeScript experience.
    5+ years of experience required. Must be comfortable with modern web development.
    Open source contributions are a plus.
    """
    
    matcher = CandidateMatcher()
    results = matcher.match_candidates([sample_candidate], job_desc, "Senior React Engineer", limit=1)
    
    print("🧪 Test Results:")
    print(f"Match Score: {results['top_candidates'][0]['match_score']}")
    print(f"Reasons: {results['top_candidates'][0]['match_reasons']}")


if __name__ == "__main__":
    test_matcher()

