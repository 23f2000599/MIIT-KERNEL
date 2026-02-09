from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from database.db import db, User, StudySession, TAProfile, Match, Note, LiveSession, StudentPreference
from auth.utils import hash_password, verify_password, login_required, role_required
from services.real_speech_service import speech_service
from sqlalchemy import text
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_companion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
#main
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    # Create additional tables from schema
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                due_date DATETIME NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                study_hours INTEGER DEFAULT 5,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS timetable_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                subject VARCHAR(100),
                description TEXT,
                duration VARCHAR(50),
                priority VARCHAR(20) DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        db.session.commit()
    except Exception as e:
        print(f"Tables already exist or error: {e}")

# ==================== LANDING & ENTRY ====================
@app.route("/")
def landing():
    return render_template("landing.html")

# ==================== AUTHENTICATION ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        user = User.query.filter_by(email=email).first()
        if user and verify_password(user.password_hash, password):
            session["user_id"] = user.id
            session["email"] = user.email
            session["role"] = user.role
            session["name"] = user.name
            return redirect(url_for(f"{user.role}_dashboard"))
        else:
            flash("Invalid credentials", "error")
    
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    name = request.form["name"]
    role = request.form.get("role", "student")
    
    if User.query.filter_by(email=email).first():
        flash("Email already exists", "error")
        return redirect(url_for("login"))
    
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    
    session["user_id"] = user.id
    session["email"] = user.email
    session["role"] = user.role
    session["name"] = user.name
    
    if role == "student":
        return redirect(url_for("student_preferences"))
    
    return redirect(url_for(f"{role}_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ==================== STUDENT FLOW ====================
@app.route("/student/dashboard")
@login_required
@role_required("student")
def student_dashboard():
    user_id = session["user_id"]
    sessions = StudySession.query.filter_by(user_id=user_id).all()
    
    total_hours = sum(s.completed_duration for s in sessions) / 3600
    today_sessions = [s for s in sessions if s.created_at.date() == datetime.now().date()]
    daily_focus = sum(s.completed_duration for s in today_sessions) / 3600
    
    stats = {
        "total_hours": round(total_hours, 1),
        "daily_focus": f"{daily_focus:.1f}h",
        "active_streak": "5 days",
        "last_timer": sessions[-1].timer_type if sessions else "None",
        "match_status": "2 active matches"
    }
    
    return render_template("student/dashboard.html", stats=stats)

@app.route("/student/timers")
@login_required
@role_required("student")
def study_timers():
    timer_types = [
        "Pomodoro Timer", "Deep Focus Timer", "52-17 Timer", 
        "Timeboxing Timer", "Flowtime Timer", "Exam Countdown Timer",
        "Group Study Sync Timer", "Night Study Timer", 
        "Micro-Session Timer", "Custom Smart Timer"
    ]
    return render_template("student/timers.html", timer_types=timer_types)

@app.route("/student/timer/<timer_type>")
@login_required
@role_required("student")
def timer_session(timer_type):
    return render_template("student/timer_session.html", timer_type=timer_type)

@app.route("/api/start_timer", methods=["POST"])
@login_required
def start_timer():
    data = request.json
    session_obj = StudySession(
        user_id=session["user_id"],
        timer_type=data["timer_type"],
        duration=data["duration"]
    )
    db.session.add(session_obj)
    db.session.commit()
    return jsonify({"session_id": session_obj.id})

@app.route("/api/end_timer", methods=["POST"])
@login_required
def end_timer():
    data = request.json
    session_obj = StudySession.query.get(data["session_id"])
    if session_obj:
        session_obj.completed_duration = data["completed_duration"]
        session_obj.interruptions = data.get("interruptions", 0)
        session_obj.focus_score = data.get("focus_score", 0.0)
        db.session.commit()
    return jsonify({"success": True})

@app.route("/student/swipe")
@login_required
@role_required("student")
def swipe():
    # Create sample TA profiles including Sarah Chen
    ta_profiles = [
        {
            "id": 1,
            "name": "Sarah Chen",
            "subjects": "Mathematics, Physics",
            "bio": "PhD in Mathematics with 5 years teaching experience. Specializes in calculus and linear algebra.",
            "rating": 4.9
        },
        {
            "id": 2,
            "name": "Michael Rodriguez",
            "subjects": "Computer Science",
            "bio": "Software engineer turned educator. Expert in Python, algorithms, and data structures.",
            "rating": 4.7
        },
        {
            "id": 3,
            "name": "Emily Watson",
            "subjects": "Chemistry, Biology",
            "bio": "Research scientist with passion for teaching. Makes complex concepts simple.",
            "rating": 4.8
        }
    ]
    return render_template("student/swipe.html", ta_profiles=ta_profiles)

@app.route("/api/swipe", methods=["POST"])
@login_required
def handle_swipe():
    data = request.json
    match = Match(
        student_id=session["user_id"],
        ta_id=data["ta_id"],
        status="pending"
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/student/matches")
@login_required
@role_required("student")
def student_matches():
    # Sample accepted match with Sarah Chen
    matches = [{
        "match": {"id": 1, "status": "accepted", "created_at": datetime.now()},
        "ta": {"id": 1, "name": "Sarah Chen", "email": "sarah.chen@university.edu"}
    }]
    return render_template("student/matches.html", matches=matches)

@app.route("/student/live-class")
@login_required
@role_required("student")
def live_class():
    active_sessions = LiveSession.query.filter_by(is_active=True).all()
    return render_template("student/live_class.html", sessions=active_sessions)

@app.route("/api/note/<int:note_id>")
@login_required
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "subject": note.subject,
        "created_at": note.created_at.strftime('%B %d, %Y')
    })

@app.route("/api/save-live-notes", methods=["POST"])
@login_required
def save_live_notes():
    data = request.json
    notes_content = data.get('notes', '')
    
    if notes_content:
        note = Note(
            ta_id=session["user_id"],
            title=f"Live Notes - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            content=notes_content,
            subject="Live Speech Notes"
        )
        db.session.add(note)
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False})

@app.route("/student/notes")
@login_required
@role_required("student")
def student_notes():
    try:
        notes = Note.query.all()
    except:
        notes = []
    return render_template("student/notes.html", notes=notes)

@app.route("/student/stats")
@login_required
@role_required("student")
def student_stats():
    user_id = session["user_id"]
    sessions = StudySession.query.filter_by(user_id=user_id).all()
    
    # Timer usage stats
    timer_stats = []
    timer_types = {}
    for s in sessions:
        if s.timer_type not in timer_types:
            timer_types[s.timer_type] = {'total_time': 0, 'count': 0}
        timer_types[s.timer_type]['total_time'] += s.completed_duration / 60
        timer_types[s.timer_type]['count'] += 1
    
    for timer_type, data in timer_types.items():
        timer_stats.append([timer_type, int(data['total_time']), data['count']])
    
    # Daily stats (last 7 days)
    daily_stats = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        day_sessions = [s for s in sessions if s.created_at.date() == date.date()]
        total_minutes = sum(s.completed_duration for s in day_sessions) / 60
        daily_stats.append([date.strftime('%a'), int(total_minutes)])
    
    return render_template("student/stats_fixed.html", timer_stats=timer_stats, daily_stats=daily_stats)

# ==================== SETTINGS ====================
@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

# ==================== TA FLOW ====================
@app.route("/ta/dashboard")
@login_required
@role_required("ta")
def ta_dashboard():
    ta_id = session["user_id"]
    matches = Match.query.filter_by(ta_id=ta_id, status="accepted").all()
    pending_matches = Match.query.filter_by(ta_id=ta_id, status="pending").all()
    
    ta_stats = {
        "active_students": len(matches),
        "pending_requests": len(pending_matches),
        "hours_taught": 25,
        "rating": 4.8
    }
    return render_template("ta/dashboard.html", ta_stats=ta_stats)

@app.route("/ta/matches")
@login_required
@role_required("ta")
def ta_matches():
    pending = db.session.query(Match, User).join(User, Match.student_id == User.id).filter(
        Match.ta_id == session["user_id"], Match.status == "pending"
    ).all()
    accepted = db.session.query(Match, User).join(User, Match.student_id == User.id).filter(
        Match.ta_id == session["user_id"], Match.status == "accepted"
    ).all()
    return render_template("ta/matches.html", pending=pending, accepted=accepted)

@app.route("/api/match/<int:match_id>/<action>", methods=["POST"])
@login_required
def handle_match(match_id, action):
    match = Match.query.get(match_id)
    if match and match.ta_id == session["user_id"]:
        match.status = action
        db.session.commit()
    return jsonify({"success": True})

@app.route("/ta/live-class")
@login_required
@role_required("ta")
def ta_live_class():
    sessions = LiveSession.query.filter_by(ta_id=session["user_id"]).all()
    return render_template("ta/live_class.html", sessions=sessions)

@app.route("/ta/notes")
@login_required
@role_required("ta")
def ta_notes():
    notes = Note.query.filter_by(ta_id=session["user_id"]).all()
    return render_template("ta/notes.html", notes=notes)

@app.route("/ta/notes/create", methods=["POST"])
@login_required
@role_required("ta")
def create_note():
    note = Note(
        ta_id=session["user_id"],
        title=request.form["title"],
        content=request.form["content"],
        subject=request.form["subject"]
    )
    db.session.add(note)
    db.session.commit()
    return redirect(url_for("ta_notes"))

# ==================== ADMIN FLOW ====================
@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    total_users = User.query.count()
    active_sessions = StudySession.query.filter(
        StudySession.created_at >= datetime.now() - timedelta(hours=1)
    ).count()
    total_study_hours = db.session.query(db.func.sum(StudySession.completed_duration)).scalar() or 0
    
    admin_stats = {
        "total_users": total_users,
        "active_sessions": active_sessions,
        "study_hours_logged": round(total_study_hours / 3600, 1),
        "total_matches": Match.query.count()
    }
    return render_template("admin/dashboard.html", admin_stats=admin_stats)

@app.route("/admin/users")
@login_required
@role_required("admin")
def admin_users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@app.route("/admin/analytics")
@login_required
@role_required("admin")
def admin_analytics():
    matches = Match.query.all()
    match_stats = {
        "total_matches": len(matches),
        "pending": len([m for m in matches if m.status == "pending"]),
        "accepted": len([m for m in matches if m.status == "accepted"]),
        "rejected": len([m for m in matches if m.status == "rejected"])
    }
    return render_template("admin/analytics.html", match_stats=match_stats)

# ==================== WEBSOCKET SPEECH RECOGNITION ====================
@socketio.on('start_transcription')
def handle_start_transcription(data):
    user_id = session.get('user_id')
    language = data.get('language', 'en-US')
    
    if not user_id:
        emit('error', {'message': 'Not authenticated'})
        return
    
    try:
        success = speech_service.start_transcription(user_id, language)
        if success:
            emit('transcription_started', {'status': 'success'})
        else:
            emit('error', {'message': 'Failed to start transcription'})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('speech_result')
def handle_speech_result(data):
    try:
        transcript = data.get('transcript', '')
        is_final = data.get('is_final', True)
        speech_service.process_speech_result(transcript, is_final)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_transcription')
def handle_stop_transcription():
    try:
        ai_notes = speech_service.stop_transcription()
        emit('transcription_stopped', {
            'status': 'success',
            'ai_notes': ai_notes
        })
    except Exception as e:
        emit('error', {'message': str(e)})

@app.route("/student/live-notes")
@login_required
@role_required("student")
def student_live_notes():
    return render_template("student/live_notes_simple.html")

@app.route("/student/timetable")
@login_required
@role_required("student")
def student_timetable():
    user_id = session["user_id"]
    
    try:
        # Get deadlines for the user
        deadlines = db.session.execute(
            text("SELECT * FROM deadlines WHERE user_id = :user_id ORDER BY due_date"),
            {"user_id": user_id}
        ).fetchall()
        
        # Get timetable entries for the user
        timetable_entries = db.session.execute(
            text("SELECT * FROM timetable_entries WHERE user_id = :user_id ORDER BY start_time"),
            {"user_id": user_id}
        ).fetchall()
        
        # Add sample data if no deadlines exist
        if not deadlines:
            from datetime import datetime, timedelta
            now = datetime.now()
            sample_deadlines = [
                (1, user_id, "Machine Learning Assignment", "Computer Science", (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"), "high", 8, "Complete neural network project with documentation", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (2, user_id, "Calculus Midterm Exam", "Mathematics", (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "critical", 12, "Study integration, differentiation, and limits", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (3, user_id, "Physics Lab Report", "Physics", (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"), "medium", 6, "Analyze pendulum motion experiment results", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (4, user_id, "English Essay", "English", (now + timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S"), "low", 4, "Write 1500-word essay on Shakespeare's themes", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (5, user_id, "Chemistry Quiz", "Chemistry", (now + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"), "medium", 3, "Organic chemistry reactions and mechanisms", False, now.strftime("%Y-%m-%d %H:%M:%S"))
            ]
            deadlines = sample_deadlines
            
    except Exception as e:
        print(f"Database error: {e}")
        # Provide sample data on error
        from datetime import datetime, timedelta
        now = datetime.now()
        sample_deadlines = [
            (1, user_id, "Machine Learning Assignment", "Computer Science", (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"), "high", 8, "Complete neural network project with documentation", False, now.strftime("%Y-%m-%d %H:%M:%S")),
            (2, user_id, "Calculus Midterm Exam", "Mathematics", (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "critical", 12, "Study integration, differentiation, and limits", False, now.strftime("%Y-%m-%d %H:%M:%S")),
            (3, user_id, "Physics Lab Report", "Physics", (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"), "medium", 6, "Analyze pendulum motion experiment results", False, now.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        deadlines = sample_deadlines
        timetable_entries = []
    
    return render_template("student/timetable_formatted.html", 
                         deadlines=deadlines, 
                         timetable_entries=timetable_entries)

@app.route("/calendar/add-deadline", methods=["POST"])
@login_required
def add_deadline():
    user_id = session["user_id"]
    title = request.form["title"]
    subject = request.form["subject"]
    due_date = request.form["due_date"]
    priority = request.form["priority"]
    study_hours = int(request.form["study_hours"])
    description = request.form.get("description", "")
    
    try:
        db.session.execute(
            text("INSERT INTO deadlines (user_id, title, subject, due_date, priority, study_hours, description) VALUES (:user_id, :title, :subject, :due_date, :priority, :study_hours, :description)"),
            {
                "user_id": user_id,
                "title": title,
                "subject": subject,
                "due_date": due_date,
                "priority": priority,
                "study_hours": study_hours,
                "description": description
            }
        )
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route("/calendar/generate-timetable", methods=["POST"])
@login_required
def generate_timetable():
    user_id = session["user_id"]
    
    try:
        # Get pending deadlines
        deadlines = db.session.execute(
            text("SELECT * FROM deadlines WHERE user_id = :user_id AND completed = 0 ORDER BY due_date"),
            {"user_id": user_id}
        ).fetchall()
        
        # Use sample data if no deadlines exist
        if not deadlines:
            from datetime import datetime, timedelta
            now = datetime.now()
            sample_deadlines = [
                (1, user_id, "Machine Learning Assignment", "Computer Science", (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"), "high", 8, "Complete neural network project", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (2, user_id, "Calculus Midterm Exam", "Mathematics", (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "critical", 12, "Study calculus concepts", False, now.strftime("%Y-%m-%d %H:%M:%S")),
                (3, user_id, "Physics Lab Report", "Physics", (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"), "medium", 6, "Complete lab analysis", False, now.strftime("%Y-%m-%d %H:%M:%S"))
            ]
            deadlines = sample_deadlines
        
        # Generate AI timetable
        timetable = generate_ai_timetable(deadlines)
        
        return jsonify({"success": True, "timetable": timetable})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error generating timetable: {str(e)}"})

@app.route("/calendar/apply-timetable", methods=["POST"])
@login_required
def apply_timetable():
    user_id = session["user_id"]
    timetable_data = request.json["timetable"]
    
    try:
        # Clear existing timetable entries
        db.session.execute(
            text("DELETE FROM timetable_entries WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        
        # Add new timetable entries
        for day in timetable_data["daily_schedule"]:
            for session in day["sessions"]:
                if "Break" not in session["title"]:
                    db.session.execute(
                        text("INSERT INTO timetable_entries (user_id, title, start_time, end_time, subject, description, duration, priority) VALUES (:user_id, :title, :start_time, :end_time, :subject, :description, :duration, :priority)"),
                        {
                            "user_id": user_id,
                            "title": session["title"],
                            "start_time": f"{day['date']} {session['time'].split(' - ')[0]}:00",
                            "end_time": f"{day['date']} {session['time'].split(' - ')[1]}:00",
                            "subject": session.get("subject", "Study"),
                            "description": session["description"],
                            "duration": session["duration"],
                            "priority": session.get("stress_level", "medium")
                        }
                    )
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

def generate_ai_timetable(deadlines):
    from datetime import datetime, timedelta
    import random
    
    timetable = {
        "total_sessions": 0,
        "total_hours": 0,
        "subjects": [],
        "daily_schedule": []
    }
    
    subjects = list(set([d[2] for d in deadlines]))  # subject column
    timetable["subjects"] = subjects
    
    # Generate 7-day schedule
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        day_schedule = {
            "day_name": date.strftime("%A"),
            "date": date.strftime("%Y-%m-%d"),
            "sessions": []
        }
        
        # Morning session (9-11 AM)
        if deadlines:
            deadline = deadlines[i % len(deadlines)]
            day_schedule["sessions"].append({
                "time": "09:00 - 11:00",
                "title": f"Study: {deadline[1]}",  # title column
                "description": f"Focus on {deadline[2]} concepts",  # subject column
                "duration": "2 hours",
                "stress_level": deadline[5],  # priority column
                "subject": deadline[2]  # subject column
            })
            timetable["total_sessions"] += 1
            timetable["total_hours"] += 2
        
        # Break
        day_schedule["sessions"].append({
            "time": "11:00 - 11:30",
            "title": "Break Time",
            "description": "Rest and refresh",
            "duration": "30 minutes",
            "stress_level": "low"
        })
        
        # Afternoon session (2-4 PM)
        if len(deadlines) > 1:
            deadline = deadlines[(i + 1) % len(deadlines)]
            day_schedule["sessions"].append({
                "time": "14:00 - 16:00",
                "title": f"Practice: {deadline[1]}",
                "description": f"Solve problems for {deadline[2]}",
                "duration": "2 hours",
                "stress_level": deadline[5],
                "subject": deadline[2]
            })
            timetable["total_sessions"] += 1
            timetable["total_hours"] += 2
        
        # Evening review (7-8 PM)
        day_schedule["sessions"].append({
            "time": "19:00 - 20:00",
            "title": "Daily Review",
            "description": "Review today's learning",
            "duration": "1 hour",
            "stress_level": "medium"
        })
        timetable["total_sessions"] += 1
        timetable["total_hours"] += 1
        
        timetable["daily_schedule"].append(day_schedule)
    
    return timetable

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)