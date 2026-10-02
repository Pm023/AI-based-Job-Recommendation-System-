import os
import re
import json

# Standard English Stopwords list for lightweight NLP pipeline
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
    "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how",
    "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
])

class NLPEngine:
    def __init__(self):
        self.skills_db = self._load_skills_dictionary()

    def _load_skills_dictionary(self):
        skills_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skills.json')
        if os.path.exists(skills_path):
            with open(skills_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def clean_text(self, text):
        """Step 1 & 2: Lowercase and sanitize text preserving special tech characters like C++"""
        if not text:
            return ""
        text = text.lower()
        # Protect C++ before removing punctuation
        text = re.sub(r'c\+\+', 'cpp', text)
        # Remove non-alphanumeric except space, +, #, .
        text = re.sub(r'[^a-z0-9\s\+#\.]', ' ', text)
        return text

    def tokenize_and_remove_stopwords(self, text):
        """Step 3, 4 & 5: Tokenization, stopword removal, and normalization"""
        cleaned = self.clean_text(text)
        words = cleaned.split()
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 1]
        return filtered

    def extract_skills(self, text):
        """
        Step 6: Skill extraction algorithm using N-gram keyword matching against controlled dictionary & aliases.
        Returns list of matched skill dicts with canonical name, category, and matched phrase.
        """
        if not text:
            return []

        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_and_remove_stopwords(text)
        text_blob = " " + " ".join(tokens) + " " + cleaned_text + " "

        detected_skills = []
        detected_names = set()

        for skill_entry in self.skills_db:
            canonical_name = skill_entry['name']
            aliases = skill_entry.get('aliases', [])
            all_patterns = [canonical_name.lower()] + [a.lower() for a in aliases]

            for pattern in all_patterns:
                # Handle cpp replacement back
                pattern_search = pattern.replace('c++', 'cpp')
                # Use regex word boundary check
                escaped_pattern = re.escape(pattern_search)
                regex = r'(?:^|\b|\s)' + escaped_pattern + r'(?:$|\b|\s)'
                
                if re.search(regex, text_blob):
                    if canonical_name not in detected_names:
                        detected_names.add(canonical_name)
                        detected_skills.append({
                            'id': skill_entry.get('id'),
                            'name': canonical_name,
                            'category': skill_entry.get('category', 'General Tech'),
                            'matched_by': pattern,
                            'default_proficiency': 'Intermediate'
                        })
                    break

        return detected_skills


nlp_engine = NLPEngine()
