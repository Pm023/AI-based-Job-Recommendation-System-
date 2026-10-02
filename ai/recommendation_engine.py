from ai.fuzzy_matcher import fuzzy_matcher
from ai.expert_system import expert_system
from ai.skill_gap import skill_gap_engine
from models import db
from models.recommendation import Recommendation, SkillGap

class AIRecommendationEngine:
    def calculate_job_compatibility(self, user, profile, user_skills, user_interests, job):
        """
        Calculates 5-factor weighted recommendation compatibility score:
        Score = 0.40*SkillMatch + 0.20*EducationMatch + 0.15*ExperienceMatch + 0.15*InterestMatch + 0.10*LocationMatch
        """
        # --- 1. SKILL MATCH (40% Weight) ---
        skill_analysis = skill_gap_engine.analyze_job_skill_gap(user_skills, job.job_skills)
        matched_skills = skill_analysis['matched_skills']
        partial_skills = skill_analysis['partial_skills']
        missing_skills = skill_analysis['missing_skills']

        if job.job_skills:
            total_weight = sum(js.weight for js in job.job_skills)
            weighted_match_sum = 0.0
            
            # Map user skills
            user_skill_map = {us.skill.name.lower(): us.proficiency for us in user_skills if us.skill}

            for js in job.job_skills:
                sname = js.skill.name.lower() if js.skill else ''
                uprof = user_skill_map.get(sname)
                match_val = fuzzy_matcher.calculate_skill_match_score(uprof, js.required_proficiency)
                weighted_match_sum += js.weight * match_val

            skill_score = (weighted_match_sum / total_weight) * 100.0 if total_weight > 0 else 70.0
        else:
            skill_score = 70.0

        # --- 2. EDUCATION MATCH (20% Weight) ---
        edu_score = 100.0
        degree_text = (profile.degree + " " + profile.field).lower() if profile else "computer engineering"
        # Most CS/Engineering backgrounds match IT/software roles perfectly
        if any(term in degree_text for term in ['computer', 'engineering', 'it', 'data', 'science', 'technology', 'b.tech', 'bca', 'mca', 'bs']):
            edu_score = 100.0
        else:
            edu_score = 75.0

        # --- 3. EXPERIENCE MATCH (15% Weight) ---
        user_exp = (profile.experience_level if profile else 'Fresher').lower()
        job_exp = (job.experience or '0-2 Years').lower()

        if user_exp == job_exp or 'fresher' in user_exp and 'fresher' in job_exp:
            exp_score = 100.0
        elif 'fresher' in user_exp and '0-2' in job_exp:
            exp_score = 90.0
        elif '0-1' in user_exp and '0-2' in job_exp:
            exp_score = 95.0
        elif '1-3' in user_exp or '3+' in user_exp:
            exp_score = 100.0
        else:
            exp_score = 70.0

        # --- 4. INTEREST MATCH (15% Weight) ---
        pref_role = (profile.preferred_role if profile else '').lower()
        job_title = job.title.lower()
        interests = [i.interest.lower() for i in user_interests] if user_interests else []

        interest_score = 60.0
        if pref_role and (pref_role in job_title or job_title in pref_role):
            interest_score = 100.0
        elif any(intr in job_title or intr in job.description.lower() for intr in interests):
            interest_score = 85.0
        elif any(word in job_title for word in pref_role.split()):
            interest_score = 80.0

        # --- 5. LOCATION MATCH (10% Weight) ---
        pref_loc = (profile.preferred_location if profile else '').lower()
        job_loc = job.location.lower()

        if pref_loc and (pref_loc in job_loc or job_loc in pref_loc):
            location_score = 100.0
        elif 'remote' in job_loc or 'remote' in pref_loc:
            location_score = 85.0
        else:
            location_score = 60.0

        # --- COMPUTE WEIGHTED OVERALL COMPATIBILITY ---
        overall_score = (
            0.40 * skill_score +
            0.20 * edu_score +
            0.15 * exp_score +
            0.15 * interest_score +
            0.10 * location_score
        )

        sub_scores = {
            'skill_score': round(skill_score, 1),
            'education_score': round(edu_score, 1),
            'experience_score': round(exp_score, 1),
            'interest_score': round(interest_score, 1),
            'location_score': round(location_score, 1)
        }

        # Generate Rule-Based Explanation
        explanation_data = expert_system.generate_recommendation_explanation(
            profile, job, matched_skills, partial_skills, missing_skills, sub_scores
        )

        return {
            'overall_score': round(overall_score, 1),
            'overall_score_int': int(round(overall_score)),
            'sub_scores': sub_scores,
            'explanation': explanation_data['main_explanation'],
            'improvement_suggestion': explanation_data['improvement_suggestion'],
            'matched_skills': matched_skills,
            'partial_skills': partial_skills,
            'missing_skills': missing_skills,
            'gap_score': skill_analysis['gap_score']
        }

    def generate_and_save_recommendations_for_user(self, user):
        """
        Executes full recommendation pipeline for user against all active jobs in the DB.
        Updates or inserts Recommendation and SkillGap records into SQLite database.
        Returns list of recommendation objects sorted descending by overall_score.
        """
        from models.job import Job
        from models.skill import UserSkill, UserInterest
        from models.profile import UserProfile

        profile = UserProfile.query.filter_by(user_id=user.id).first()
        user_skills = UserSkill.query.filter_by(user_id=user.id).all()
        user_interests = UserInterest.query.filter_by(user_id=user.id).all()
        jobs = Job.query.filter_by(status='active').all()

        recommendation_results = []

        for job in jobs:
            match_data = self.calculate_job_compatibility(user, profile, user_skills, user_interests, job)
            
            # Find existing DB record or build new
            rec = Recommendation.query.filter_by(user_id=user.id, job_id=job.id).first()
            if not rec:
                rec = Recommendation(user_id=user.id, job_id=job.id)
                db.session.add(rec)

            rec.overall_score = match_data['overall_score']
            rec.skill_score = match_data['sub_scores']['skill_score']
            rec.education_score = match_data['sub_scores']['education_score']
            rec.experience_score = match_data['sub_scores']['experience_score']
            rec.interest_score = match_data['sub_scores']['interest_score']
            rec.location_score = match_data['sub_scores']['location_score']
            rec.explanation = match_data['explanation']

            # Also update SkillGap DB records for this user and job
            SkillGap.query.filter_by(user_id=user.id, job_id=job.id).delete()
            for ms in match_data['matched_skills']:
                if 'id' in ms:
                    sg = SkillGap(user_id=user.id, job_id=job.id, skill_id=ms['id'], gap_level='Strong Match')
                    db.session.add(sg)
            for ps in match_data['partial_skills']:
                if 'id' in ps:
                    sg = SkillGap(user_id=user.id, job_id=job.id, skill_id=ps['id'], gap_level='Partial Match')
                    db.session.add(sg)
            for ms in match_data['missing_skills']:
                if 'id' in ms:
                    sg = SkillGap(user_id=user.id, job_id=job.id, skill_id=ms['id'], gap_level='Missing')
                    db.session.add(sg)

            recommendation_results.append({
                'recommendation': rec,
                'job': job,
                'overall_score': match_data['overall_score'],
                'overall_score_int': match_data['overall_score_int'],
                'sub_scores': match_data['sub_scores'],
                'explanation': match_data['explanation'],
                'improvement_suggestion': match_data['improvement_suggestion'],
                'matched_skills': match_data['matched_skills'],
                'partial_skills': match_data['partial_skills'],
                'missing_skills': match_data['missing_skills'],
                'gap_score': match_data['gap_score']
            })

        db.session.commit()

        # Rank descending by overall score
        recommendation_results.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendation_results


recommendation_engine = AIRecommendationEngine()
