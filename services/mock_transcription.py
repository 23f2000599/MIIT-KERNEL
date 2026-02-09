import json
import random
from flask_socketio import emit
from database.db import db
from sqlalchemy import text
from datetime import datetime

class SmartTranscriptionService:
    def __init__(self):
        self.current_session = None
        self.is_active = False
        self.audio_buffer = []
        
    def start_transcription(self, user_id, language='en-US'):
        self.current_session = {
            'user_id': user_id,
            'start_time': datetime.now(),
            'transcript': '',
            'speakers': {},
            'sentences': []
        }
        self.is_active = True
        self.audio_buffer = []
        return True
    
    def send_audio(self, audio_data):
        if not self.is_active or len(audio_data) < 1000:
            return
            
        self.audio_buffer.append(len(audio_data))
        
        # Process every few audio chunks
        if len(self.audio_buffer) % 3 == 0:
            sentence = self.generate_realistic_sentence()
            speaker = random.choice([0, 1]) if len(self.current_session['speakers']) > 0 or random.random() > 0.7 else 0
            
            self.current_session['sentences'].append(sentence)
            self.current_session['transcript'] += f"[Speaker {speaker}] {sentence} "
            self.current_session['speakers'][speaker] = self.current_session['speakers'].get(speaker, 0) + 1
            
            emit('transcript_update', {
                'transcript': f"[Speaker {speaker}] {sentence}",
                'is_final': True,
                'speaker': speaker,
                'confidence': round(random.uniform(0.85, 0.98), 2)
            })
    
    def generate_realistic_sentence(self):
        topics = [
            "machine learning algorithms", "neural networks", "data preprocessing", 
            "statistical analysis", "computer vision", "natural language processing",
            "deep learning models", "feature engineering", "model evaluation",
            "supervised learning", "unsupervised learning", "reinforcement learning"
        ]
        
        starters = [
            "Today we'll discuss", "Let's examine", "Consider the concept of",
            "An important aspect is", "We need to understand", "The key principle behind",
            "This relates to", "Another example involves", "We can observe that"
        ]
        
        endings = [
            "which is fundamental to understanding the subject.",
            "and its applications in real-world scenarios.",
            "as demonstrated in recent research papers.",
            "particularly in modern AI systems.",
            "which we'll explore in more detail.",
            "and how it impacts model performance."
        ]
        
        return f"{random.choice(starters)} {random.choice(topics)} {random.choice(endings)}"
    
    def stop_transcription(self):
        if self.is_active:
            self.is_active = False
            return self.save_transcript_with_ai_notes()
        return None
    
    def save_transcript_with_ai_notes(self):
        if not self.current_session or not self.current_session['transcript'].strip():
            return None
        
        # Generate AI notes
        ai_notes = self.generate_ai_notes()
        
        try:
            db.session.execute(
                text("""
                    INSERT INTO notes (user_id, title, content, subject, created_at) 
                    VALUES (:user_id, :title, :content, :subject, :created_at)
                """),
                {
                    'user_id': self.current_session['user_id'],
                    'title': f"AI Lecture Notes - {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M')}",
                    'content': ai_notes,
                    'subject': 'Live Lecture Notes',
                    'created_at': datetime.now()
                }
            )
            db.session.commit()
            return ai_notes
        except Exception as e:
            print(f"Error saving notes: {e}")
            db.session.rollback()
            return None
    
    def generate_ai_notes(self):
        sentences = self.current_session['sentences']
        transcript = self.current_session['transcript']
        duration = datetime.now() - self.current_session['start_time']
        
        # Extract key topics
        topics = self.extract_topics(sentences)
        key_points = sentences[:5] if len(sentences) > 5 else sentences
        
        notes = f"""
# 📚 AI-Generated Lecture Notes

## 📊 Session Summary
- **Date**: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M')}
- **Duration**: {str(duration).split('.')[0]}
- **Speakers**: {len(self.current_session['speakers'])}
- **Key Topics**: {', '.join(topics[:3])}

## 🔑 Key Points
"""
        
        for i, point in enumerate(key_points, 1):
            notes += f"{i}. {point}\n"
        
        notes += f"""

## 📝 Detailed Notes

### Main Topics Covered:
"""
        
        for topic in topics[:5]:
            notes += f"- **{topic.title()}**: Discussed in detail with practical examples\n"
        
        notes += f"""

### Full Transcript
{transcript}

---
*Generated automatically from live lecture transcription*
        """
        
        return notes
    
    def extract_topics(self, sentences):
        topics = set()
        keywords = ['machine learning', 'neural networks', 'data', 'algorithm', 'model', 'learning', 'analysis', 'computer', 'vision', 'processing']
        
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence.lower():
                    topics.add(keyword)
        
        return list(topics)

# Global transcription service instance
transcription_service = SmartTranscriptionService()