from flask_socketio import emit
from database.db import db
from sqlalchemy import text
from datetime import datetime
import json

class RealSpeechService:
    def __init__(self):
        self.current_session = None
        self.is_active = False
        
    def start_transcription(self, user_id, language='en-US'):
        self.current_session = {
            'user_id': user_id,
            'start_time': datetime.now(),
            'transcript': '',
            'language': language
        }
        self.is_active = True
        return True
    
    def process_speech_result(self, transcript, is_final=True):
        if not self.is_active or not self.current_session:
            return
            
        if is_final:
            self.current_session['transcript'] += transcript + ' '
            
        emit('transcript_update', {
            'transcript': transcript,
            'is_final': is_final,
            'confidence': 0.95
        })
    
    def stop_transcription(self):
        if self.is_active and self.current_session:
            self.is_active = False
            ai_notes = self.generate_ai_notes()
            self.save_notes(ai_notes)
            return ai_notes
        return None
    
    def generate_ai_notes(self):
        transcript = self.current_session['transcript'].strip()
        if not transcript:
            return "No speech detected."
            
        # Use actual transcript, not mock data
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        duration = datetime.now() - self.current_session['start_time']
        
        notes = f"""# 📚 AI-Generated Lecture Notes

## 📊 Session Summary
- **Date**: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M')}
- **Duration**: {str(duration).split('.')[0]}
- **Language**: {self.current_session['language']}

## 🔑 Key Points
"""
        
        for i, sentence in enumerate(sentences[:10], 1):
            if len(sentence) > 10:
                notes += f"{i}. {sentence.capitalize()}.\n"
        
        notes += f"""

## 📝 Full Transcript
{transcript}

---
*Generated automatically from live speech recognition*
"""
        return notes
    
    def save_notes(self, ai_notes):
        try:
            db.session.execute(
                text("""
                    INSERT INTO notes (user_id, title, content, subject, created_at) 
                    VALUES (:user_id, :title, :content, :subject, :created_at)
                """),
                {
                    'user_id': self.current_session['user_id'],
                    'title': f"Live Notes - {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M')}",
                    'content': ai_notes,
                    'subject': 'Live Speech Notes',
                    'created_at': datetime.now()
                }
            )
            db.session.commit()
        except Exception as e:
            print(f"Error saving notes: {e}")
            db.session.rollback()

# Global service instance
speech_service = RealSpeechService()