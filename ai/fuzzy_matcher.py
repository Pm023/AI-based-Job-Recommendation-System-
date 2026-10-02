class FuzzySkillMatcher:
    PROFICIENCY_SCALE = {
        'beginner': 0.25,
        'basic': 0.40,
        'intermediate': 0.60,
        'advanced': 0.80,
        'expert': 1.00
    }

    @classmethod
    def get_numerical_value(cls, proficiency_str):
        """Converts textual proficiency string into numerical value on [0.0, 1.0] scale."""
        if not proficiency_str:
            return 0.0
        key = str(proficiency_str).strip().lower()
        return cls.PROFICIENCY_SCALE.get(key, 0.50)

    @classmethod
    def calculate_skill_match_score(cls, user_prof_str, req_prof_str):
        """
        Fuzzy skill matching function:
        Calculates match score between user skill proficiency and job requirement.
        - If user level >= required level: Match = 1.00 (100%)
        - If user level < required level: Match = 1.0 - (Required - User)
        - If user does not have skill: Match = 0.00
        """
        if user_prof_str is None:
            return 0.0

        user_val = cls.get_numerical_value(user_prof_str)
        req_val = cls.get_numerical_value(req_prof_str)

        if user_val >= req_val:
            return 1.00
        else:
            diff = req_val - user_val
            match_val = max(0.0, 1.0 - diff)
            return round(match_val, 2)

    @classmethod
    def get_membership_category(cls, match_score):
        """
        Classifies match score (0.0 to 1.0) into fuzzy membership categories:
        - 0.00 - 0.29 = Poor
        - 0.30 - 0.49 = Low
        - 0.50 - 0.69 = Moderate
        - 0.70 - 0.84 = Good
        - 0.85 - 1.00 = Excellent
        """
        score = float(match_score)
        if score >= 0.85:
            return "Excellent"
        elif score >= 0.70:
            return "Good"
        elif score >= 0.50:
            return "Moderate"
        elif score >= 0.30:
            return "Low"
        else:
            return "Poor"


fuzzy_matcher = FuzzySkillMatcher()
