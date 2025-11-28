"""
GitHub Profile Scraper for Recruitment
Collects 100 diverse tech profiles with rich data for talent sourcing
"""

import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import os
from collections import Counter

class GitHubProfileScraper:
    def __init__(self, github_token: str):
        self.token = github_token
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        self.profiles = []
    
    def search_users(self, query: str, per_page: int = 30) -> List[str]:
        """Search GitHub users and return usernames"""
        url = f"{self.base_url}/search/users"
        params = {"q": query, "per_page": per_page, "sort": "followers"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return [user['login'] for user in data.get('items', [])]
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Fetch complete user profile with stats"""
        try:
            # Get user info
            user_url = f"{self.base_url}/users/{username}"
            user_response = requests.get(user_url, headers=self.headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get user repos
            repos_url = f"{self.base_url}/users/{username}/repos"
            repos_params = {"sort": "stars", "per_page": 10, "type": "owner"}
            repos_response = requests.get(repos_url, headers=self.headers, params=repos_params)
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            
            # Calculate stats
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data)
            languages = [repo.get('language') for repo in repos_data if repo.get('language')]
            language_counts = Counter(languages)
            primary_language = language_counts.most_common(1)[0][0] if language_counts else "Unknown"
            
            # Get unique topics/skills from repos
            all_topics = []
            for repo in repos_data:
                all_topics.extend(repo.get('topics', []))
            unique_topics = list(set(all_topics))[:10]  # Top 10 unique topics
            
            # Build notable repos list
            notable_repos = [
                {
                    "name": repo.get('name'),
                    "description": repo.get('description', ''),
                    "stars": repo.get('stargazers_count', 0),
                    "language": repo.get('language', ''),
                    "topics": repo.get('topics', [])[:5],
                    "url": repo.get('html_url', '')
                }
                for repo in repos_data[:5]
            ]
            
            # Infer experience level based on account age and activity
            created_at = datetime.strptime(user_data.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
            account_age = (datetime.now() - created_at).days / 365.25
            
            if account_age >= 7 and total_stars > 200:
                experience_level = "Senior"
            elif account_age >= 5 and total_stars > 50:
                experience_level = "Mid"
            elif account_age >= 3:
                experience_level = "Mid"
            else:
                experience_level = "Junior"
            
            # Build profile
            profile = {
                "id": f"GITHUB-{user_data.get('id')}",
                "github_username": username,
                "name": user_data.get('name') or username,
                "avatar_url": user_data.get('avatar_url'),
                "bio": user_data.get('bio', ''),
                "location": user_data.get('location', ''),
                "company": user_data.get('company', ''),
                "email": user_data.get('email', ''),
                "blog": user_data.get('blog', ''),
                "twitter_username": user_data.get('twitter_username', ''),
                "hireable": user_data.get('hireable', False),
                
                # GitHub Stats
                "public_repos": user_data.get('public_repos', 0),
                "followers": user_data.get('followers', 0),
                "following": user_data.get('following', 0),
                "total_stars": total_stars,
                
                # Languages & Skills
                "languages": list(language_counts.keys())[:5],
                "primary_language": primary_language,
                "skills": unique_topics,
                
                # Notable Work
                "notable_repos": notable_repos,
                "has_popular_repos": total_stars > 100,
                
                # Experience
                "account_age_years": round(account_age, 1),
                "estimated_experience_level": experience_level,
                "open_source_contributor": user_data.get('public_repos', 0) > 5,
                
                # Links
                "github_profile_url": user_data.get('html_url'),
                
                # Recruiter-Friendly
                "tech_stack_summary": f"{primary_language} developer" + (f" with expertise in {', '.join(unique_topics[:3])}" if unique_topics else ""),
                "likely_roles": self._infer_roles(primary_language, unique_topics, experience_level),
                
                # Metadata
                "scraped_at": datetime.now().isoformat()
            }
            
            return profile
            
        except Exception as e:
            print(f"Error fetching profile for {username}: {e}")
            return None
    
    def _infer_roles(self, primary_language: str, topics: List[str], experience: str) -> List[str]:
        """Infer likely job roles based on tech stack"""
        roles = []
        
        # Language-based roles
        lang_roles = {
            "JavaScript": ["Frontend Engineer", "Full Stack Engineer"],
            "TypeScript": ["Frontend Engineer", "Full Stack Engineer"],
            "Python": ["Backend Engineer", "Data Engineer", "ML Engineer"],
            "Go": ["Backend Engineer", "DevOps Engineer"],
            "Rust": ["Systems Engineer", "Backend Engineer"],
            "Java": ["Backend Engineer", "Android Engineer"],
            "Swift": ["iOS Engineer"],
            "Kotlin": ["Android Engineer", "Backend Engineer"],
            "Ruby": ["Backend Engineer", "Full Stack Engineer"],
            "PHP": ["Backend Engineer", "Full Stack Engineer"]
        }
        
        roles.extend(lang_roles.get(primary_language, ["Software Engineer"]))
        
        # Topic-based specializations
        if any(t in topics for t in ['react', 'vue', 'angular', 'frontend']):
            roles.append("Frontend Engineer")
        if any(t in topics for t in ['nodejs', 'express', 'fastapi', 'backend']):
            roles.append("Backend Engineer")
        if any(t in topics for t in ['kubernetes', 'docker', 'devops', 'terraform']):
            roles.append("DevOps Engineer")
        if any(t in topics for t in ['machine-learning', 'deep-learning', 'pytorch', 'tensorflow']):
            roles.append("ML Engineer")
        if any(t in topics for t in ['react-native', 'ios', 'android', 'mobile']):
            roles.append("Mobile Engineer")
        
        # Add experience prefix
        roles = [f"{experience} {role}" if experience != "Junior" else role for role in list(set(roles))]
        
        return roles[:3]  # Return top 3 likely roles
    
    def scrape_diverse_profiles(self, target_count: int = 100) -> List[Dict]:
        """Scrape diverse profiles across different tech stacks"""
        
        search_queries = [
            # JavaScript/TypeScript ecosystem
            "language:javascript followers:>100 repos:>10",
            "language:typescript followers:>50 repos:>10",
            "react followers:>100",
            "vue followers:>50",
            "angular followers:>50",
            "nodejs followers:>100",
            
            # Python ecosystem
            "language:python followers:>100 repos:>10",
            "django followers:>50",
            "fastapi followers:>50",
            "machine-learning language:python followers:>50",
            
            # Backend languages
            "language:go followers:>50 repos:>5",
            "language:rust followers:>50 repos:>5",
            "language:java followers:>100 repos:>10",
            
            # Mobile
            "language:swift followers:>50",
            "language:kotlin followers:>50",
            "react-native followers:>50",
            
            # DevOps/Infrastructure
            "kubernetes followers:>100",
            "docker followers:>100",
            "terraform followers:>50",
            
            # Data & ML
            "pytorch followers:>50",
            "tensorflow followers:>50",
            "data-science followers:>100",
        ]
        
        all_usernames = set()
        
        print(f"🚀 Starting GitHub profile scraping...")
        print(f"🎯 Target: {target_count} diverse profiles\n")
        
        for i, query in enumerate(search_queries):
            print(f"[{i+1}/{len(search_queries)}] Searching: {query}")
            usernames = self.search_users(query, per_page=15)
            all_usernames.update(usernames)
            print(f"   Found {len(usernames)} users. Total unique: {len(all_usernames)}")
            
            # Rate limiting
            time.sleep(2)
            
            if len(all_usernames) >= target_count:
                break
        
        print(f"\n✅ Collected {len(all_usernames)} unique usernames")
        print(f"📥 Fetching detailed profiles...\n")
        
        # Fetch detailed profiles
        profiles = []
        for i, username in enumerate(list(all_usernames)[:target_count]):
            print(f"[{i+1}/{min(target_count, len(all_usernames))}] Fetching {username}...", end=" ")
            
            profile = self.get_user_profile(username)
            if profile:
                profiles.append(profile)
                print(f"✓ ({profile['primary_language']}, {profile['followers']} followers)")
            else:
                print("✗ Failed")
            
            # Rate limiting (be nice to GitHub API)
            time.sleep(1)
            
            if len(profiles) >= target_count:
                break
        
        print(f"\n🎉 Successfully scraped {len(profiles)} profiles!")
        return profiles
    
    def save_profiles(self, profiles: List[Dict], filename: str = "github_profiles_100.json"):
        """Save profiles to JSON file"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(profiles, f, indent=2)
        print(f"\n💾 Saved {len(profiles)} profiles to {filepath}")
    
    def generate_stats(self, profiles: List[Dict]):
        """Generate statistics about scraped profiles"""
        print("\n📊 Profile Statistics:")
        print("=" * 50)
        
        languages = Counter()
        experience_levels = Counter()
        locations = Counter()
        
        for profile in profiles:
            languages[profile['primary_language']] += 1
            experience_levels[profile['estimated_experience_level']] += 1
            if profile['location']:
                locations[profile['location']] += 1
        
        print(f"\n🔤 Top Languages:")
        for lang, count in languages.most_common(10):
            print(f"  {lang}: {count}")
        
        print(f"\n👔 Experience Levels:")
        for level, count in experience_levels.most_common():
            print(f"  {level}: {count}")
        
        print(f"\n🌍 Top Locations:")
        for loc, count in list(locations.most_common(10)):
            print(f"  {loc}: {count}")
        
        print("\n" + "=" * 50)


def main():
    """Main scraper execution"""
    # Get GitHub token from environment
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("💡 Get a token from: https://github.com/settings/tokens")
        print("💡 Then run: export GITHUB_TOKEN='your_token_here'")
        return
    
    scraper = GitHubProfileScraper(github_token)
    
    # Scrape profiles
    profiles = scraper.scrape_diverse_profiles(target_count=100)
    
    # Generate stats
    scraper.generate_stats(profiles)
    
    # Save to file
    scraper.save_profiles(profiles)
    
    print("\n✅ Scraping complete! Next steps:")
    print("1. Review github_profiles_100.json")
    print("2. Run: python -c 'from recruitment_service import MockRecruitmentService; svc = MockRecruitmentService(); print(len(svc.candidates))'")
    print("3. Test search: Make a query to the recruitment backend")


if __name__ == "__main__":
    main()

