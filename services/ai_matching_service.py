import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIMatchingService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def get_ta_recommendations(self, student_preferences, available_tas):
        if not self.model or not student_preferences:
            return self._fallback_ranking(available_tas)
        
        try:
            subjects = json.loads(student_preferences.subjects) if isinstance(student_preferences.subjects, str) else student_preferences.subjects
            confidence = json.loads(student_preferences.confidence_levels) if isinstance(student_preferences.confidence_levels, str) else student_preferences.confidence_levels
            
            prompt = f"""You are an AI matching system for students and teaching assistants.

Student Profile:
- Subjects needed: {', '.join(subjects)}
- Confidence levels: {json.dumps(confidence)}
- Deadlines: {student_preferences.deadlines or 'Not specified'}
- Learning style: {student_preferences.learning_style or 'Not specified'}

Available TAs:
{json.dumps([{'id': ta['id'], 'name': ta['name'], 'subjects': ta['subjects'], 'bio': ta['bio'], 'rating': ta['rating']} for ta in available_tas], indent=2)}

Rank these TAs from best to worst match for this student. Consider:
1. Subject expertise match
2. Student's confidence level (lower confidence needs more patient TAs)
3. TA rating and experience
4. Urgency of deadlines

Return ONLY a JSON array of TA IDs in ranked order, like: [3, 1, 2]"""

            response = self.model.generate_content(prompt)
            ranked_ids = json.loads(response.text.strip())
            
            ranked_tas = []
            for ta_id in ranked_ids:
                ta = next((t for t in available_tas if t['id'] == ta_id), None)
                if ta:
                    ranked_tas.append(ta)
            
            for ta in available_tas:
                if ta not in ranked_tas:
                    ranked_tas.append(ta)
            
            return ranked_tas
        except Exception as e:
            print(f"AI matching error: {e}")
            return self._fallback_ranking(available_tas)
    
    def _fallback_ranking(self, tas):
        return sorted(tas, key=lambda x: x.get('rating', 0), reverse=True)

ai_matching_service = AIMatchingService()
