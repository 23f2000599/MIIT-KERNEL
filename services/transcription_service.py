import asyncio
import websockets
import json
import os
from deepgram import DeepgramClientClient
from flask_socketio import SocketIO, emit
from database.db import db, Note
from sqlalchemy import text
from datetime import datetime

class DeepgramTranscriptionService:
    def __init__(self, api_key):
        self.dg_client = DeepgramClient(api_key)
        self.live_transcription = None
        self.transcript_buffer = []
        self.current_session = None
        
    async def start_transcription(self, user_id, language='en-US'):
        self.current_session = {
            'user_id': user_id,
            'start_time': datetime.now(),
            'transcript': '',
            'speakers': {}
        }
        
        try:
            self.live_transcription = self.dg_client.listen.websocket.v("1")
            
            connection = await self.live_transcription.start({
                'punctuate': True,
                'interim_results': True,
                'language': language,
                'model': 'nova-2',
                'smart_format': True,
                'diarize': True,
                'channels': 1,
                'sample_rate': 16000
            })
            
            connection.on("Results", self.on_message)
            connection.on("Close", lambda c: print(f"Connection closed with code {c}"))
            
            return True
        except Exception as e:
            print(f"Error starting transcription: {e}")
            return False
    
    def on_message(self, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        
        if len(sentence) == 0:
            return
        
        if result.is_final:
            # Handle speaker diarization
            speaker_info = ""
            speaker = 0
            if result.channel.alternatives[0].words:
                words = result.channel.alternatives[0].words
                if len(words) > 0 and hasattr(words[0], 'speaker'):
                    speaker = words[0].speaker
                    speaker_info = f"[Speaker {speaker}] "
                    self.current_session['speakers'][speaker] = self.current_session['speakers'].get(speaker, 0) + 1
            
            formatted_transcript = f"{speaker_info}{sentence}"
            self.current_session['transcript'] += formatted_transcript + " "
            
            # Emit to frontend
            emit('transcript_update', {
                'transcript': formatted_transcript,
                'is_final': True,
                'speaker': speaker,
                'confidence': result.channel.alternatives[0].confidence
            })
        else:
            # Interim results
            emit('transcript_update', {
                'transcript': sentence,
                'is_final': False,
                'confidence': result.channel.alternatives[0].confidence
            })
    
    async def send_audio(self, audio_data):
        if self.live_transcription:
            self.live_transcription.send(bytes(audio_data))
    
    async def stop_transcription(self):
        if self.live_transcription:
            self.live_transcription.finish()
            return self.save_transcript()
        return None
    
    def save_transcript(self):
        if not self.current_session or not self.current_session['transcript'].strip():
            return None
        
        try:
            # Save to database
            db.session.execute(
                text("""
                    INSERT INTO notes (user_id, title, content, subject, transcript_data, created_at) 
                    VALUES (:user_id, :title, :content, :subject, :transcript_data, :created_at)
                """),
                {
                    'user_id': self.current_session['user_id'],
                    'title': f"Live Transcript - {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M')}",
                    'content': self.current_session['transcript'],
                    'subject': 'Live Transcription',
                    'transcript_data': json.dumps({
                        'speakers': self.current_session['speakers'],
                        'duration': str(datetime.now() - self.current_session['start_time']),
                        'word_count': len(self.current_session['transcript'].split())
                    }),
                    'created_at': datetime.now()
                }
            )
            db.session.commit()
            return self.current_session['transcript']
        except Exception as e:
            print(f"Error saving transcript: {e}")
            db.session.rollback()
            return None

# Global transcription service instance
transcription_service = None

def init_transcription_service(api_key):
    global transcription_service
    transcription_service = DeepgramTranscriptionService(api_key)
    return transcription_service