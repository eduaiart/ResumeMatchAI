import spacy
import re
import logging
from collections import Counter
import json

class NLPProcessor:
    def __init__(self):
        """Initialize spaCy NLP processor"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("spaCy model loaded successfully")
        except IOError:
            logging.error("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            raise
        
        # Define skill categories and common skills
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web_dev': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'tableau', 'power bi'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop']
        }
        
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical thinking',
            'creativity', 'adaptability', 'time management', 'project management', 'collaboration',
            'critical thinking', 'decision making', 'negotiation', 'presentation', 'mentoring'
        ]
        
        # Create flat list of all technical skills
        self.all_technical_skills = []
        for category in self.technical_skills.values():
            self.all_technical_skills.extend(category)

    def extract_candidate_info(self, text):
        """Extract structured information from resume text"""
        doc = self.nlp(text)
        
        # Extract basic information
        name = self._extract_name(doc, text)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract experience
        experience_years = self._extract_experience_years(text)
        work_experience = self._extract_work_experience(text)
        
        # Extract education
        education = self._extract_education(text)
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'experience_years': experience_years,
            'work_experience': work_experience,
            'education': education
        }

    def analyze_job_description(self, text):
        """Analyze job description to extract requirements and skills"""
        doc = self.nlp(text)
        
        # Extract required skills
        required_skills = self._extract_skills(text)
        
        # Categorize skills
        categorized_skills = self._categorize_skills(required_skills)
        
        # Extract requirements sections
        requirements = self._extract_requirements(text)
        
        # Generate default skill weights
        skill_weights = self._generate_skill_weights(categorized_skills)
        
        return {
            'skills': categorized_skills,
            'requirements': requirements,
            'skill_weights': skill_weights
        }

    def _extract_name(self, doc, text):
        """Extract candidate name from resume"""
        # First try to find PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                return ent.text.strip()
        
        # Fallback: look for name patterns at the beginning
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if len(line.split()) == 2 and not any(char.isdigit() for char in line):
                if not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'resume']):
                    return line
        
        return "Unknown"

    def _extract_email(self, text):
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text):
        """Extract phone number from text"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else None

    def _extract_skills(self, text):
        """Extract skills from text using pattern matching and NLP"""
        text_lower = text.lower()
        found_skills = []
        
        # Check for technical skills
        for skill in self.all_technical_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Check for soft skills
        for skill in self.soft_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Use spaCy to find additional skills (noun phrases that might be skills)
        doc = self.nlp(text)
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            # Skip very short or very long phrases
            if 2 <= len(chunk_text.split()) <= 3:
                # Check if it contains skill-like keywords
                if any(keyword in chunk_text for keyword in ['development', 'management', 'analysis', 'design']):
                    found_skills.append(chunk.text.strip())
        
        # Remove duplicates and return
        return list(set(found_skills))

    def _categorize_skills(self, skills):
        """Categorize skills into technical, soft, and domain-specific"""
        categorized = {
            'technical': [],
            'soft': [],
            'domain_specific': []
        }
        
        skills_lower = [skill.lower() for skill in skills]
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if it's a technical skill
            if skill_lower in self.all_technical_skills:
                categorized['technical'].append(skill)
            # Check if it's a soft skill
            elif skill_lower in [s.lower() for s in self.soft_skills]:
                categorized['soft'].append(skill)
            else:
                # Everything else is domain-specific
                categorized['domain_specific'].append(skill)
        
        return categorized

    def _extract_experience_years(self, text):
        """Extract years of experience from text"""
        # Pattern for "X years of experience"
        pattern = r'(\d+)[\s\-\+]*(?:years?|yrs?)[\s]*(?:of\s+)?(?:experience|exp)'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            return max([int(match) for match in matches])
        
        # Look for date ranges to calculate experience
        date_pattern = r'(19|20)\d{2}'
        years = re.findall(date_pattern, text)
        if len(years) >= 2:
            years = [int(year + decade) for year, decade in years]
            years.sort()
            return max(years) - min(years)
        
        return 0

    def _extract_work_experience(self, text):
        """Extract work experience entries"""
        # This is a simplified extraction - in practice, you'd want more sophisticated parsing
        lines = text.split('\n')
        work_sections = []
        
        current_section = []
        in_work_section = False
        
        work_keywords = ['experience', 'employment', 'work history', 'professional experience']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a work section
            if any(keyword in line.lower() for keyword in work_keywords):
                in_work_section = True
                continue
            
            # Check if this line starts a new section (education, skills, etc.)
            if any(keyword in line.lower() for keyword in ['education', 'skills', 'certifications']):
                in_work_section = False
                if current_section:
                    work_sections.append(' '.join(current_section))
                    current_section = []
                continue
            
            if in_work_section:
                current_section.append(line)
        
        if current_section:
            work_sections.append(' '.join(current_section))
        
        return work_sections

    def _extract_education(self, text):
        """Extract education information"""
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'institute']
        lines = text.split('\n')
        education_entries = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in education_keywords):
                education_entries.append(line)
        
        return education_entries

    def _extract_requirements(self, text):
        """Extract requirement sections from job description"""
        requirements = []
        lines = text.split('\n')
        
        requirement_keywords = ['requirements', 'qualifications', 'must have', 'required', 'responsibilities']
        
        in_requirements = False
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a requirements section
            if any(keyword in line.lower() for keyword in requirement_keywords):
                in_requirements = True
                current_section = [line]
                continue
            
            # Check if we've moved to a different section
            if line.lower().startswith(('about', 'company', 'benefits', 'salary')):
                if current_section and in_requirements:
                    requirements.extend(current_section)
                in_requirements = False
                current_section = []
                continue
            
            if in_requirements:
                current_section.append(line)
        
        if current_section and in_requirements:
            requirements.extend(current_section)
        
        return requirements

    def _generate_skill_weights(self, categorized_skills):
        """Generate default weights for different skill categories"""
        weights = {}
        
        # Default weights by category
        default_weights = {
            'technical': 0.6,
            'soft': 0.3,
            'domain_specific': 0.4
        }
        
        for category, skills in categorized_skills.items():
            category_weight = default_weights.get(category, 0.3)
            for skill in skills:
                weights[skill] = category_weight
        
        return weights

    def calculate_text_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts using spaCy"""
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        
        return doc1.similarity(doc2)
