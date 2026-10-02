import os
import json
from ai.fuzzy_matcher import fuzzy_matcher

class SkillGapEngine:
    def __init__(self):
        self.career_paths_db = self._load_career_paths()

    def _load_career_paths(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'career_paths.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def analyze_job_skill_gap(self, user_skills, job_skills):
        """
        Compares User Skills vs Job Required Skills.
        user_skills: list of UserSkill objects or dicts {'name': ..., 'proficiency': ...}
        job_skills: list of JobSkill objects or dicts
        
        Returns:
          matched_skills: list of dicts with Strong Match
          partial_skills: list of dicts with Partial Match
          missing_skills: list of dicts with Missing status
          gap_score: overall percentage gap
        """
        user_map = {}
        for us in user_skills:
            sname = us.skill.name if hasattr(us, 'skill') else us.get('name')
            uprof = us.proficiency if hasattr(us, 'proficiency') else us.get('proficiency')
            user_map[sname.lower()] = uprof

        matched_skills = []
        partial_skills = []
        missing_skills = []

        total_weight = 0.0
        weighted_gap_sum = 0.0

        for js in job_skills:
            sname = js.skill.name if hasattr(js, 'skill') else js.get('name')
            rprof = js.required_proficiency if hasattr(js, 'required_proficiency') else js.get('required_proficiency')
            weight = js.weight if hasattr(js, 'weight') else js.get('weight', 20.0)
            total_weight += weight

            uprof = user_map.get(sname.lower())

            if uprof is None:
                # Skill is missing completely
                missing_skills.append({
                    'name': sname,
                    'user_proficiency': 'None',
                    'required_proficiency': rprof,
                    'status': 'Missing',
                    'weight': weight,
                    'match_percentage': 0,
                    'badge_class': 'bg-danger'
                })
                weighted_gap_sum += weight * 1.0  # 100% gap
            else:
                match_val = fuzzy_matcher.calculate_skill_match_score(uprof, rprof)
                match_pct = int(round(match_val * 100))
                
                if match_val >= 0.85:
                    matched_skills.append({
                        'name': sname,
                        'user_proficiency': uprof,
                        'required_proficiency': rprof,
                        'status': 'Strong Match',
                        'weight': weight,
                        'match_percentage': match_pct,
                        'badge_class': 'bg-success'
                    })
                    weighted_gap_sum += weight * (1.0 - match_val)
                else:
                    partial_skills.append({
                        'name': sname,
                        'user_proficiency': uprof,
                        'required_proficiency': rprof,
                        'status': 'Partial Match',
                        'weight': weight,
                        'match_percentage': match_pct,
                        'badge_class': 'bg-warning text-dark'
                    })
                    weighted_gap_sum += weight * (1.0 - match_val)

        overall_gap_pct = int(round((weighted_gap_sum / total_weight * 100))) if total_weight > 0 else 0

        # Prioritize top 3 skills to improve by weight
        gaps_to_improve = sorted(missing_skills + partial_skills, key=lambda x: x['weight'], reverse=True)

        return {
            'matched_skills': matched_skills,
            'partial_skills': partial_skills,
            'missing_skills': missing_skills,
            'gap_score': overall_gap_pct,
            'top_improvements': gaps_to_improve[:3]
        }

    def get_role_learning_path(self, target_role, user_skills):
        """
        Generates customized step-by-step learning path for a target job role based on user's current skills.
        """
        role_data = self.career_paths_db.get(target_role)
        if not role_data:
            # Fallback for dynamic roles
            role_data = self.career_paths_db.get('Backend Developer')

        user_skill_names = set()
        for us in user_skills:
            sname = us.skill.name if hasattr(us, 'skill') else us.get('name')
            if sname:
                user_skill_names.add(sname.lower())

        base_path = role_data.get('learning_path', [])
        customized_steps = []

        for step in base_path:
            sname = step['skill']
            is_mastered = any(sname.lower() in us or us in sname.lower() for us in user_skill_names)
            
            customized_steps.append({
                'step': step['step'],
                'skill': sname,
                'focus': step['focus'],
                'status': 'Mastered' if is_mastered else 'To Learn',
                'status_class': 'bg-success' if is_mastered else 'bg-primary'
            })

        return {
            'role_title': role_data['title'],
            'description': role_data['description'],
            'learning_path': customized_steps,
            'alternatives': role_data.get('alternatives', [])
        }


skill_gap_engine = SkillGapEngine()
