import logging
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MatchingEngine:
    def __init__(self, nlp_processor):
        """Initialize matching engine with NLP processor"""
        self.nlp_processor = nlp_processor
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

    def calculate_match_score(self, candidate, job):
        """Calculate comprehensive match score between candidate and job"""
        try:
            # Get candidate and job data
            candidate_skills = candidate.extracted_skills or []
            job_skills = []
            
            # Flatten job skills from all categories
            if job.skills_required:
                for category, skills in job.skills_required.items():
                    job_skills.extend(skills)
            
            # Calculate individual scores
            skill_score = self._calculate_skill_match_score(candidate_skills, job_skills, job.skill_weights or {})
            experience_score = self._calculate_experience_score(candidate, job)
            education_score = self._calculate_education_score(candidate, job)
            
            # Calculate semantic similarity
            semantic_score = self._calculate_semantic_similarity(candidate.raw_text or "", job.description)
            
            # Weight the scores
            weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'semantic': 0.1
            }
            
            overall_score = (
                skill_score * weights['skills'] +
                experience_score * weights['experience'] +
                education_score * weights['education'] +
                semantic_score * weights['semantic']
            )
            
            # Calculate skill gaps
            skill_gaps = self._identify_skill_gaps(candidate_skills, job_skills)
            
            # Generate match justification
            justification = self._generate_match_justification(
                skill_score, experience_score, education_score, 
                semantic_score, skill_gaps
            )
            
            # Detailed breakdown
            breakdown = {
                'skill_score': skill_score,
                'experience_score': experience_score,
                'education_score': education_score,
                'semantic_score': semantic_score,
                'weights_used': weights,
                'matched_skills': list(set(candidate_skills) & set(job_skills)),
                'missing_skills': skill_gaps
            }
            
            return {
                'overall_score': round(overall_score, 2),
                'skill_score': round(skill_score, 2),
                'experience_score': round(experience_score, 2),
                'education_score': round(education_score, 2),
                'semantic_score': round(semantic_score, 2),
                'breakdown': breakdown,
                'skill_gaps': skill_gaps,
                'justification': justification
            }
            
        except Exception as e:
            logging.error(f"Error calculating match score: {str(e)}")
            return {
                'overall_score': 0,
                'skill_score': 0,
                'experience_score': 0,
                'education_score': 0,
                'semantic_score': 0,
                'breakdown': {},
                'skill_gaps': [],
                'justification': "Error calculating match score"
            }

    def _calculate_skill_match_score(self, candidate_skills, job_skills, skill_weights):
        """Calculate skill matching score with weights"""
        if not job_skills:
            return 0
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched_skills = []
        total_weight = 0
        matched_weight = 0
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            weight = skill_weights.get(job_skill, 1.0)
            total_weight += weight
            
            # Check for exact matches or similar skills
            if job_skill_lower in candidate_skills_lower:
                matched_skills.append(job_skill)
                matched_weight += weight
            else:
                # Check for partial matches or similar skills
                for candidate_skill in candidate_skills_lower:
                    if (job_skill_lower in candidate_skill or 
                        candidate_skill in job_skill_lower or
                        self._calculate_skill_similarity(job_skill_lower, candidate_skill) > 0.8):
                        matched_skills.append(job_skill)
                        matched_weight += weight * 0.8  # Partial match gets 80% credit
                        break
        
        if total_weight == 0:
            return 0
        
        return (matched_weight / total_weight) * 100

    def _calculate_experience_score(self, candidate, job):
        """Calculate experience matching score"""
        candidate_exp = candidate.experience_years or 0
        
        # Extract required experience from job description
        required_exp = self._extract_required_experience(job.description)
        
        if required_exp == 0:
            return 50  # Neutral score if no experience requirement specified
        
        if candidate_exp >= required_exp:
            # Bonus for more experience, but diminishing returns
            excess = candidate_exp - required_exp
            bonus = min(excess * 5, 30)  # Max 30% bonus
            return min(100, 80 + bonus)
        else:
            # Penalty for less experience
            deficit = required_exp - candidate_exp
            penalty = deficit * 15  # 15% penalty per year deficit
            return max(0, 80 - penalty)

    def _calculate_education_score(self, candidate, job):
        """Calculate education matching score"""
        candidate_education = candidate.education or []
        job_description = job.description.lower()
        
        # Education keywords and their scores
        education_levels = {
            'phd': 100,
            'doctorate': 100,
            'master': 80,
            'bachelor': 60,
            'associate': 40,
            'diploma': 30,
            'certificate': 20
        }
        
        # Check what education is required
        required_level = 0
        for level, score in education_levels.items():
            if level in job_description:
                required_level = max(required_level, score)
        
        # Check candidate's education level
        candidate_level = 0
        for edu in candidate_education:
            edu_lower = edu.lower()
            for level, score in education_levels.items():
                if level in edu_lower:
                    candidate_level = max(candidate_level, score)
        
        if required_level == 0:
            return 50  # Neutral if no education requirement
        
        if candidate_level >= required_level:
            return 100
        elif candidate_level > 0:
            return (candidate_level / required_level) * 100
        else:
            return 20  # Some credit for any education mentioned

    def _calculate_semantic_similarity(self, candidate_text, job_text):
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        try:
            if not candidate_text or not job_text:
                return 0
            
            # Create TF-IDF vectors
            documents = [candidate_text, job_text]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100
            
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {str(e)}")
            return 0

    def _identify_skill_gaps(self, candidate_skills, job_skills):
        """Identify skills that are required but missing from candidate"""
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        gaps = []
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            if job_skill_lower not in candidate_skills_lower:
                # Check for partial matches
                found_partial = False
                for candidate_skill in candidate_skills_lower:
                    if (job_skill_lower in candidate_skill or 
                        candidate_skill in job_skill_lower):
                        found_partial = True
                        break
                
                if not found_partial:
                    gaps.append(job_skill)
        
        return gaps

    def _generate_match_justification(self, skill_score, experience_score, 
                                    education_score, semantic_score, skill_gaps):
        """Generate human-readable match justification"""
        justifications = []
        
        # Skill assessment
        if skill_score >= 80:
            justifications.append("Excellent skill match - candidate has most required skills")
        elif skill_score >= 60:
            justifications.append("Good skill match - candidate has many required skills")
        elif skill_score >= 40:
            justifications.append("Moderate skill match - candidate has some required skills")
        else:
            justifications.append("Limited skill match - candidate lacks many required skills")
        
        # Experience assessment
        if experience_score >= 80:
            justifications.append("Strong experience match")
        elif experience_score >= 60:
            justifications.append("Adequate experience level")
        else:
            justifications.append("Experience below requirements")
        
        # Education assessment
        if education_score >= 80:
            justifications.append("Education requirements met or exceeded")
        elif education_score >= 50:
            justifications.append("Acceptable education background")
        else:
            justifications.append("Education below typical requirements")
        
        # Skill gaps
        if skill_gaps:
            if len(skill_gaps) <= 2:
                justifications.append(f"Minor skill gaps: {', '.join(skill_gaps[:2])}")
            else:
                justifications.append(f"Several skill gaps including: {', '.join(skill_gaps[:3])}")
        
        return ". ".join(justifications)

    def _extract_required_experience(self, job_description):
        """Extract required years of experience from job description"""
        import re
        
        # Patterns for experience requirements
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:relevant\s+)?(?:professional\s+)?experience',
            r'minimum\s+(\d+)\s+years?',
            r'at\s+least\s+(\d+)\s+years?'
        ]
        
        job_text = job_description.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, job_text)
            if matches:
                return max([int(match) for match in matches])
        
        return 0

    def _calculate_skill_similarity(self, skill1, skill2):
        """Calculate similarity between two skills using spaCy"""
        try:
            return self.nlp_processor.nlp(skill1).similarity(self.nlp_processor.nlp(skill2))
        except:
            return 0
