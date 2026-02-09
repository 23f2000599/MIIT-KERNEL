# AI-Powered TA Matching System

## New Features

### 1. Student Preferences Collection
When a student signs up, they are now prompted to set their learning preferences:
- **Subjects to focus on**: Select from Mathematics, Physics, Chemistry, Biology, Computer Science, English, History, Engineering
- **Confidence levels**: Rate confidence in each subject (1-5 scale)
- **Upcoming deadlines**: Enter important deadlines to help prioritize
- **Learning style**: Visual, Auditory, Reading/Writing, Kinesthetic, or Mixed

### 2. AI-Based TA Recommendations
The system uses **Gemini AI** to rank TAs based on:
- Subject expertise match with student needs
- Student confidence levels (lower confidence gets more patient TAs)
- TA ratings and experience
- Urgency of student deadlines

### 3. Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the migration to create the preferences table:
```bash
python add_preferences_table.py
```

3. Start the application:
```bash
python app.py
```

### 4. How It Works

**For New Students:**
1. Sign up as a student
2. Automatically redirected to preferences page
3. Fill out subjects, confidence levels, deadlines, and learning style
4. Click "Save Preferences & Find TAs"
5. Go to "Find Your Perfect TA" to see AI-ranked recommendations

**For Existing Students:**
1. Go to Dashboard
2. Click "Manage Preferences" card
3. Update preferences anytime
4. AI recommendations update automatically

### 5. API Configuration

The system uses the Gemini API key from your `.env` file:

If Gemini API fails, the system falls back to rating-based sorting.

### 6. Files Modified/Created

**New Files:**
- `services/ai_matching_service.py` - AI matching logic using Gemini
- `templates/student/preferences.html` - Preferences form
- `add_preferences_table.py` - Database migration script

**Modified Files:**
- `app.py` - Added preferences routes and AI integration
- `database/db.py` - Added StudentPreference model
- `templates/student/dashboard.html` - Added preferences link
- `templates/student/swipe.html` - Added AI badge and preference prompt
- `requirements.txt` - Added google-generativeai and python-dotenv

### 7. Features

✅ Collects student preferences on signup
✅ Stores confidence levels per subject
✅ Uses Gemini AI for intelligent TA ranking
✅ Shows AI-powered badge when preferences are set
✅ Allows updating preferences anytime
✅ Fallback to rating-based sorting if AI fails
