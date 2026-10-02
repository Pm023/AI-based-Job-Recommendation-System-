import os
import json
from ai.expert_system import expert_system

class CareerGuidanceEngine:
    def __init__(self):
        self.career_paths_db = self._load_career_paths()

    def _load_career_paths(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'career_paths.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def generate_career_guidance(self, user, profile, user_skills, user_interests):
        """
        Analyzes user's skill inventory, interests, and background to recommend:
        1. Primary Career Direction
        2. Alternative Career Directions
        3. Top recommended next skills to learn with explicit rule-based justifications.
        """
        skills_dict = {}
        for us in user_skills:
            sname = us.skill.name if hasattr(us, 'skill') else us.get('name')
            uprof = us.proficiency if hasattr(us, 'proficiency') else us.get('proficiency')
            skills_dict[sname] = uprof

        # Evaluate expert rules
        rule_results = expert_system.evaluate_suitability_rules(skills_dict)

        # Primary direction derived from preferred_role or top rule match
        primary_role = profile.preferred_role if profile and profile.preferred_role else "Backend Developer"
        
        path_info = self.career_paths_db.get(primary_role)
        if not path_info:
            # Fallback matching
            if "Data" in primary_role or "Analyst" in primary_role:
                path_info = self.career_paths_db.get("Data Analyst")
            elif "AI" in primary_role or "ML" in primary_role:
                path_info = self.career_paths_db.get("AI Engineer")
            elif "Full" in primary_role or "Frontend" in primary_role:
                path_info = self.career_paths_db.get("Full Stack Developer")
            else:
                path_info = self.career_paths_db.get("Backend Developer")

        # Determine missing next skills to learn
        core_reqs = path_info.get('core_skills', []) + path_info.get('secondary_skills', [])
        user_lower_skills = {k.lower() for k in skills_dict.keys()}
        
        next_skills = []
        for req in core_reqs:
            if req.lower() not in user_lower_skills:
                next_skills.append(req)
            if len(next_skills) >= 4:
                break

        # Generate reason narrative
        has_skills = [s for s, p in skills_dict.items() if p in ['Intermediate', 'Advanced', 'Expert']]
        if has_skills:
            top_skills_str = ", ".join(has_skills[:3])
            reason = f"You already have strong {top_skills_str} foundation. Learning {', '.join(next_skills[:2]) if next_skills else 'advanced architecture patterns'} will maximize your market readiness."
        else:
            reason = "Building foundational skills in Python, SQL, and Git will open up immediate entry-level tech opportunities."

        return {
            'primary_role': path_info['title'],
            'primary_description': path_info['description'],
            'alternative_roles': path_info.get('alternatives', []),
            'recommended_next_skills': next_skills,
            'reason': reason,
            'suitability_rules': rule_results
        }


career_guidance_engine = CareerGuidanceEngine()
