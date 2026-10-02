class RuleBasedExpertSystem:
    def evaluate_suitability_rules(self, user_skills_dict):
        """
        Evaluates IF-THEN rules on user profile skills to determine career domain suitability.
        user_skills_dict = {'Python': 'Advanced', 'SQL': 'Intermediate', ...}
        """
        conclusions = []
        
        # Rule 1: Backend Development Rule
        py_prof = user_skills_dict.get('Python')
        sql_prof = user_skills_dict.get('SQL')
        api_prof = user_skills_dict.get('REST API') or user_skills_dict.get('FastAPI') or user_skills_dict.get('Flask')
        if py_prof and sql_prof:
            conclusions.append({
                'rule_name': 'Backend Development Rule',
                'conclusion': 'High Backend Developer Suitability',
                'reason': 'Strong foundation in server-side programming (Python) and relational databases (SQL).'
            })

        # Rule 2: Data Analytics Rule
        pandas_prof = user_skills_dict.get('Pandas')
        excel_prof = user_skills_dict.get('Excel')
        bi_prof = user_skills_dict.get('Power BI')
        if py_prof and (sql_prof or pandas_prof or excel_prof or bi_prof):
            conclusions.append({
                'rule_name': 'Data Analysis Rule',
                'conclusion': 'High Data Analyst Suitability',
                'reason': 'Equipped with data transformation, querying, and analytical capabilities.'
            })

        # Rule 3: AI/ML Engineering Rule
        ml_prof = user_skills_dict.get('Machine Learning')
        nlp_prof = user_skills_dict.get('NLP')
        dl_prof = user_skills_dict.get('Deep Learning')
        if py_prof and (ml_prof or nlp_prof or dl_prof):
            conclusions.append({
                'rule_name': 'AI Engineering Rule',
                'conclusion': 'High AI Engineer Suitability',
                'reason': 'Demonstrates intelligence modeling, NLP, and machine learning skillsets.'
            })

        # Rule 4: Frontend / Web Development Rule
        html_prof = user_skills_dict.get('HTML')
        css_prof = user_skills_dict.get('CSS')
        js_prof = user_skills_dict.get('JavaScript')
        if html_prof and css_prof and js_prof:
            conclusions.append({
                'rule_name': 'Web Development Rule',
                'conclusion': 'High Web Developer Suitability',
                'reason': 'Solid grasp of core web UI technologies (HTML, CSS, JavaScript).'
            })

        return conclusions

    def generate_recommendation_explanation(self, user_profile, job, matched_skills, partial_skills, missing_skills, sub_scores):
        """
        Generates dynamic, transparent, human-readable natural language explanation for why a job was recommended.
        Combines score breakdown analysis with skill match rules.
        """
        explanation_parts = []

        # Part 1: Strong skills highlight
        if matched_skills:
            strong_names = [s['name'] for s in matched_skills[:4]]
            if len(strong_names) == 1:
                skills_str = strong_names[0]
            elif len(strong_names) == 2:
                skills_str = f"{strong_names[0]} and {strong_names[1]}"
            else:
                skills_str = f"{', '.join(strong_names[:-1])}, and {strong_names[-1]}"
            
            explanation_parts.append(
                f"Recommended because your {skills_str} skill{'s' if len(strong_names)>1 else ''} strongly match{'es' if len(strong_names)==1 else ''} the core requirements of this role."
            )
        else:
            explanation_parts.append("This position aligns with your broader background and career preferences.")

        # Part 2: Career Interest alignment
        if sub_scores.get('interest_score', 0) >= 80 and user_profile.preferred_role:
            explanation_parts.append(f"The title '{job.title}' closely matches your preferred career direction ({user_profile.preferred_role}).")

        # Part 3: Location match
        if sub_scores.get('location_score', 0) == 100:
            explanation_parts.append(f"The job location ({job.location}) directly matches your preferred work location.")
        elif sub_scores.get('location_score', 0) == 80:
            explanation_parts.append(f"This role offers a flexible remote arrangement matching your preferences.")

        # Part 4: Gaps & Improvement Suggestions
        if missing_skills or partial_skills:
            gap_names = [s['name'] for s in (missing_skills + partial_skills)[:3]]
            if len(gap_names) == 1:
                gap_str = gap_names[0]
            else:
                gap_str = f"{', '.join(gap_names[:-1])} and {gap_names[-1]}"
            
            improvement_text = f"Learning or refining {gap_str} could further elevate your compatibility score for this position."
        else:
            improvement_text = "You possess comprehensive skill coverage for this job profile!"

        full_explanation = " ".join(explanation_parts)

        return {
            'main_explanation': full_explanation,
            'improvement_suggestion': improvement_text
        }


expert_system = RuleBasedExpertSystem()
