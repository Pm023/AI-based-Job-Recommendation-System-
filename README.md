# CareerMatch AI 🚀
### AI-Based Job Recommendation & Career Guidance System

> **TAGLINE:** *"Your Skills. Your Match. Your Next Opportunity."*

---

## 📌 Project Overview
**CareerMatch AI** is an explainable artificial intelligence system designed for 5th-semester B.Tech Computer Engineering students and job seekers. Unlike black-box machine learning models that generate opaque percentages, CareerMatch AI transparently analyzes user profiles, extracts skills from PDF resumes using Natural Language Processing (NLP), evaluates fuzzy proficiency levels, computes a 5-factor weighted compatibility score, applies rule-based expert system reasoning, and provides understandable job recommendations along with step-by-step career guidance.

---

## 🎯 Project Context & Objectives
- **Academic Context:** 5th-Semester B.Tech Computer Engineering Artificial Intelligence Group Project.
- **Explainability First:** Transparent AI reasoning—every recommendation score displays its exact mathematical breakdown and natural language rationale.
- **Defendable AI Usage:** Incorporates 5 key topics from the AI syllabus without over-engineering with unnecessary deep neural networks.

---

## 🧠 AI Syllabus Syllabus Concepts Implemented

1. **Natural Language Processing (NLP):**
   - Extracts tech skills from PDF resumes.
   - 6-Step Pipeline: Lowercasing $\rightarrow$ Noise Removal $\rightarrow$ Tokenization $\rightarrow$ Stopword Filtering $\rightarrow$ Alias Normalization $\rightarrow$ N-Gram Matching against a 45+ skill ontology dictionary.
2. **Fuzzy Logic Skill Matching:**
   - Evaluates gradual skill mastery rather than binary yes/no.
   - Textual proficiencies map to continuous fuzzy values: `Beginner` (0.25), `Basic` (0.40), `Intermediate` (0.60), `Advanced` (0.80), `Expert` (1.00).
   - Membership Categories: *Excellent* (0.85-1.00), *Good* (0.70-0.84), *Moderate* (0.50-0.69), *Low* (0.30-0.49), *Poor* (0.00-0.29).
3. **5-Factor Weighted Recommendation Score:**
   - Explicit mathematical formula calculating total compatibility between user profiles and job requirements:
     $$\text{Final Score} = 0.40 \cdot \text{SkillMatch} + 0.20 \cdot \text{EducationMatch} + 0.15 \cdot \text{ExperienceMatch} + 0.15 \cdot \text{InterestMatch} + 0.10 \cdot \text{LocationMatch}$$
4. **Knowledge Representation:**
   - Structured ontology connecting Job Roles $\rightarrow$ Core Required Skills $\rightarrow$ Secondary Skills $\rightarrow$ Step-by-Step Learning Paths.
5. **Rule-Based Expert System:**
   - Evaluates domain-specific IF-THEN rules for career suitability, missing skill warnings, and natural language explanation generation.

---

## 💻 Technology Stack

- **Frontend:** HTML5, CSS3 (Vanilla CSS variables + Bootstrap 5), JavaScript (Fetch API, Bootstrap Icons).
- **Backend:** Python, Flask.
- **Database:** SQLite, SQLAlchemy ORM.
- **AI & NLP:** Python, `scikit-learn`, `NumPy`, Regex N-Gram Parser.
- **Resume Processing:** `pypdf` / `PyMuPDF` with graceful fallback error handling.

---

## 📂 Project Structure

```
CareerMatch-AI/
│
├── app.py                      # Application entry point & Database Seeder
├── config.py                   # App Configuration (Secret keys, DB URI, Upload folder)
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Documentation & Viva Guide
│
├── models/                     # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── user.py                 # User model (auth, password hashing)
│   ├── profile.py              # UserProfile model
│   ├── skill.py                # Skill, UserSkill, UserInterest models
│   ├── job.py                  # Job, JobSkill models
│   └── recommendation.py       # Recommendation, Rule, SkillGap models
│
├── routes/                     # Modular Flask Blueprints
│   ├── __init__.py
│   ├── auth.py                 # User & Admin Authentication
│   ├── user.py                 # Dashboard, Profile Setup, Profile Edit
│   ├── jobs.py                 # Recommended Jobs list, Search, Filters, Job Details
│   ├── recommendations.py      # Skill Gap Analysis, Career Guidance, How-It-Works
│   ├── admin.py                # Admin Dashboard, Job Management (CRUD)
│   └── resume.py               # PDF Resume Upload & NLP Skill Extraction API
│
├── ai/                         # Explainable AI Engine
│   ├── __init__.py
│   ├── nlp_engine.py           # NLP Text cleaning, Tokenization, Stopwords, Skill Extraction
│   ├── fuzzy_matcher.py        # Fuzzy Logic proficiency scale & membership categories
│   ├── recommendation_engine.py# 5-factor weighted score formula & job ranking
│   ├── expert_system.py        # IF-THEN rules & natural language explanation generation
│   ├── skill_gap.py            # Skill classification (Strong/Partial/Missing) & Gap score
│   └── career_guidance.py      # Career path recommendations & next skills to learn
│
├── data/                       # Knowledge Base & Seed Data
│   ├── skills.json             # 40+ Tech skills with categories & aliases
│   ├── jobs.json               # 30+ Tech jobs with required skill proficiencies & weights
│   ├── rules.json              # Expert System IF-THEN rules
│   └── career_paths.json       # Career roles ontology & learning paths
│
├── templates/                  # Bootstrap 5 Responsive HTML Templates (15 pages)
│   ├── base.html               # Master Layout (Navbar, Footer, Modals)
│   ├── index.html              # 1. Landing Page
│   ├── login.html              # 2. Student Login Page
│   ├── register.html           # 3. Student Registration Page
│   ├── profile_setup.html      # 4. Multi-section Profile Setup Page
│   ├── dashboard.html          # 5. User Dashboard
│   ├── jobs.html               # 6. Job Recommendations Page
│   ├── job_details.html        # 7. Job Details & Match Explanation Page
│   ├── skill_gap.html          # 8. Skill Gap Analysis Page
│   ├── career_guidance.html    # 9. AI Career Guidance Page
│   ├── profile.html            # 10. Profile View Page
│   ├── resume_upload.html      # 11. Resume Upload & Confirmation Page
│   ├── how_it_works.html       # Academic AI Pipeline & Viva Page
│   ├── admin_login.html        # 12. Admin Login Page
│   ├── admin_dashboard.html    # 13. Admin Dashboard
│   ├── manage_jobs.html        # 14. Admin Manage Jobs Page
│   └── job_form.html           # 15. Admin Add/Edit Job Form
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom CSS variables, glassmorphic design system
│   └── js/
│       ├── app.js              # Global utilities & alerts
│       ├── jobs.js             # Job filtering & search
│       └── profile.js          # Dynamic skill rows & AJAX resume parser
│
└── uploads/                    # Resume PDF uploads directory
```

---

## 🔑 Demo Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Student (Job Seeker)** | `demo@careermatch.ai` | `Demo@123` | Dashboard, Recommendations, Skill Gap, Profile, Resume |
| **Administrator** | `admin@careermatch.ai` | `Admin@123` | Admin Dashboard, Add/Edit/Delete Jobs, System Stats |

---

## ⚡ How to Run the Project

1. **Clone/Navigate to Workspace:**
   ```bash
   cd "e:\AI Project"
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Flask Application:**
   ```bash
   python app.py
   ```

4. **Access in Web Browser:**
   Open `http://127.0.0.1:5000` in your web browser.

---

## 👥 5-Member Team Responsibilities Breakdown

- **Member 1 (Frontend / UI Engineer):** Designed Bootstrap 5 layouts, custom CSS color variable design system, landing page, dashboard cards, and mobile responsiveness.
- **Member 2 (Backend Developer):** Configured Flask framework, SQLite database, SQLAlchemy ORM models, authentication sessions, and route controllers.
- **Member 3 (NLP Engineer):** Developed resume PDF text extraction, tokenization, stopword filtering, and skill alias matching engine (`nlp_engine.py`).
- **Member 4 (AI Recommendation Engineer):** Implemented fuzzy logic proficiency scale, 5-factor weighted scoring formula, and ranking engine (`fuzzy_matcher.py` & `recommendation_engine.py`).
- **Member 5 (Knowledge & Expert System Engineer):** Built IF-THEN rules, skill gap classifier, learning path generator, and academic documentation (`expert_system.py`, `skill_gap.py`, `career_guidance.py`).

---

## 🎓 20 Viva Questions & Answers (Academic Defense)

1. **Q: Where exactly is AI used in this system?**  
   *A:* AI is used in 5 modules: (1) NLP for resume skill extraction, (2) Fuzzy Logic for gradual skill proficiency matching, (3) 5-Factor Weighted Score for ranking, (4) Knowledge Representation for job-skill ontologies, and (5) Rule-Based Expert System for suitability and explanations.

2. **Q: Why did you use NLP instead of standard form fields?**  
   *A:* Resumes are unstructured text documents. NLP extracts structured skill data using tokenization, stopword removal, and dictionary mapping.

3. **Q: Why did you use Fuzzy Logic instead of exact keyword matching?**  
   *A:* Skill mastery is gradual rather than binary. A student with "Basic" Python is a 60% match for an "Advanced" Python job requirement, not 0%. Fuzzy logic handles this continuous mapping.

4. **Q: What is a Fuzzy Membership Value?**  
   *A:* A numerical value between 0.0 and 1.0 representing degree of membership (e.g., Intermediate = 0.60).

5. **Q: How is the Match Percentage calculated?**  
   *A:* Using the formula: \(Score = 0.40(Skill) + 0.20(Education) + 0.15(Experience) + 0.15(Interest) + 0.10(Location)\).

6. **Q: Why not simple keyword matching?**  
   *A:* Keyword matching ignores proficiency depth, location preferences, education fields, and experience requirements.

7. **Q: What is your Knowledge Base?**  
   *A:* JSON ontologies (`skills.json`, `career_paths.json`) storing relations between job roles, required skills, secondary skills, and learning paths.

8. **Q: What is your Expert System?**  
   *A:* A inference engine evaluating IF-THEN rules against user profile skills to recommend career paths and explain matches.

9. **Q: What is an example IF-THEN rule in your code?**  
   *A:* `IF Python >= Intermediate AND SQL >= Intermediate THEN Backend Developer Suitability = High`.

10. **Q: How does resume processing work?**  
    *A:* `pypdf`/`PyMuPDF` extracts PDF text \(\rightarrow\) text is cleaned \(\rightarrow\) tokenized \(\rightarrow\) stopwords removed \(\rightarrow\) matched against `skills.json`.

11. **Q: How are skills extracted from text?**  
    *A:* Using regex word-boundary N-gram pattern matching across skill canonical names and aliases.

12. **Q: How are missing skills identified?**  
    *A:* By comparing job required skills against the user's skill inventory. Any job skill not present in user profile is classified as "Missing".

13. **Q: How are jobs ranked?**  
    *A:* Jobs are sorted descending by the computed overall 5-factor compatibility score.

14. **Q: What happens if two jobs have the same score?**  
    *A:* The system breaks ties using the primary skill sub-score, followed by creation timestamp.

15. **Q: What happens if the user has no skills listed?**  
    *A:* The system prompts the user to add skills or upload a resume, returning baseline recommendations based on education and location.

16. **Q: What happens if no job matches?**  
    *A:* A friendly empty state is displayed suggesting filter adjustments or skill profile updates.

17. **Q: Is this Machine Learning?**  
    *A:* No. It is an Explainable AI system based on Knowledge Representation, NLP, Fuzzy Logic, and Expert Systems.

18. **Q: What are the main limitations of the system?**  
    *A:* Job datasets are sample academic records; PDF parsing depends on readable text layers; fuzzy weights are tuned for this prototype.

19. **Q: What is the difference between recommendation and prediction?**  
    *A:* Recommendation measures profile-to-job compatibility. Prediction claims to foresee future hiring decisions (which we explicitly do not claim).

20. **Q: Why is your system explainable?**  
    *A:* Because every match displays a 5-factor score breakdown, matched/missing skill badges, and natural language reasoning text explaining the score.

---

## 🚨 Limitations & Future Scope

### Project Limitations:
- Job dataset consists of academic sample records (30+ fictional jobs).
- PDF resume skill extraction requires readable text layers (scanned image PDFs require OCR).
- Fuzzy membership thresholds are calibrated for academic prototype demonstration.

### Future Scope:
- Integration with live job market APIs (LinkedIn, Indeed).
- Transformer-based NLP embeddings (BERT / Sentence-Transformers).
- Multilingual resume processing.
- Real-time learning path integration with external course APIs (Coursera, Udemy).
