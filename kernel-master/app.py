from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Study sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timer_type TEXT,
        duration INTEGER,
        completed_time INTEGER,
        focus_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # TA matches table
    c.execute('''CREATE TABLE IF NOT EXISTS ta_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        ta_id INTEGER,
        status TEXT DEFAULT 'pending',
        rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users (id),
        FOREIGN KEY (ta_id) REFERENCES users (id)
    )''')
    
    # Create deadlines table
    c.execute('''CREATE TABLE IF NOT EXISTS deadlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        subject TEXT,
        due_date DATETIME,
        priority TEXT,
        study_hours INTEGER,
        description TEXT,
        completed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Create timetable entries table
    c.execute('''CREATE TABLE IF NOT EXISTS timetable_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        start_time DATETIME,
        end_time DATETIME,
        subject TEXT,
        entry_type TEXT,
        priority TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Insert demo data
    demo_users = [
        ('student@demo.com', generate_password_hash('demo123'), 'student', 'Demo Student'),
        ('ta@demo.com', generate_password_hash('demo123'), 'ta', 'Demo TA'),
        ('admin@demo.com', generate_password_hash('demo123'), 'admin', 'Demo Admin'),
        ('john@student.com', generate_password_hash('demo123'), 'student', 'John Smith'),
        ('sarah@ta.com', generate_password_hash('demo123'), 'ta', 'Sarah Johnson'),
        ('mike@student.com', generate_password_hash('demo123'), 'student', 'Mike Wilson')
    ]
    
    for email, password, role, name in demo_users:
        c.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO users (email, password, role, name) VALUES (?, ?, ?, ?)',
                     (email, password, role, name))
    
    # Demo study sessions
    demo_sessions = [
        (1, 'Pomodoro', 25, 25, 85),
        (1, 'Deep Focus', 90, 87, 92),
        (4, 'Pomodoro', 25, 23, 78),
        (6, '52-17', 52, 52, 88)
    ]
    
    for user_id, timer_type, duration, completed, score in demo_sessions:
        c.execute('SELECT COUNT(*) FROM study_sessions WHERE user_id = ? AND timer_type = ?', (user_id, timer_type))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO study_sessions (user_id, timer_type, duration, completed_time, focus_score) VALUES (?, ?, ?, ?, ?)',
                     (user_id, timer_type, duration, completed, score))
    
    # Demo TA matches
    demo_matches = [
        (1, 2, 'matched', 5),
        (4, 5, 'matched', 4),
        (6, 2, 'pending', None)
    ]
    
    for student_id, ta_id, status, rating in demo_matches:
        c.execute('SELECT COUNT(*) FROM ta_matches WHERE student_id = ? AND ta_id = ?', (student_id, ta_id))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO ta_matches (student_id, ta_id, status, rating) VALUES (?, ?, ?, ?)',
                     (student_id, ta_id, status, rating))
    
    # Demo notes
    demo_notes = [
        (2, 'Calculus Derivatives', 'Key formulas for derivatives: d/dx(x^n) = nx^(n-1)', 'Mathematics'),
        (5, 'Python Basics', 'Variables, loops, and functions are fundamental concepts', 'Computer Science'),
        (2, 'Integration Techniques', 'Integration by parts: ∫u dv = uv - ∫v du', 'Mathematics')
    ]
    
    for ta_id, title, content, subject in demo_notes:
        c.execute('SELECT COUNT(*) FROM notes WHERE ta_id = ? AND title = ?', (ta_id, title))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO notes (ta_id, title, content, subject) VALUES (?, ?, ?, ?)',
                     (ta_id, title, content, subject))
    
    conn.commit()
    conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != role:
                flash('Access denied')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('study_app.db')
        c = conn.cursor()
        
        # Create demo accounts if they don't exist
        demo_accounts = [
            ('student@demo.com', generate_password_hash('demo123'), 'student', 'Demo Student'),
            ('ta@demo.com', generate_password_hash('demo123'), 'ta', 'Demo TA'),
            ('admin@demo.com', generate_password_hash('demo123'), 'admin', 'Demo Admin')
        ]
        
        for demo_email, demo_password, role, name in demo_accounts:
            c.execute('SELECT COUNT(*) FROM users WHERE email = ?', (demo_email,))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO users (email, password, role, name) VALUES (?, ?, ?, ?)',
                         (demo_email, demo_password, role, name))
        
        conn.commit()
        
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_role'] = user[3]
            session['user_name'] = user[4]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        
        conn = sqlite3.connect('study_app.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO users (email, password, role, name) VALUES (?, ?, ?, ?)',
                     (email, generate_password_hash(password), role, name))
            conn.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists')
        finally:
            conn.close()
    
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    if session['user_role'] == 'student':
        # Get student stats
        c.execute('SELECT SUM(completed_time), COUNT(*), AVG(focus_score) FROM study_sessions WHERE user_id = ?', 
                 (session['user_id'],))
        stats = c.fetchone()
        
        # Get recent sessions
        c.execute('SELECT * FROM study_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5', 
                 (session['user_id'],))
        recent_sessions = c.fetchall()
        
        # Get match status
        c.execute('SELECT COUNT(*) FROM ta_matches WHERE student_id = ? AND status = "matched"', 
                 (session['user_id'],))
        match_count = c.fetchone()[0]
        
        conn.close()
        return render_template('student_dashboard.html', stats=stats, recent_sessions=recent_sessions, match_count=match_count)
    
    elif session['user_role'] == 'ta':
        # Get TA stats
        c.execute('SELECT COUNT(*) FROM ta_matches WHERE ta_id = ? AND status = "matched"', 
                 (session['user_id'],))
        active_students = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM ta_matches WHERE ta_id = ? AND status = "pending"', 
                 (session['user_id'],))
        pending_requests = c.fetchone()[0]
        
        conn.close()
        return render_template('ta_dashboard.html', active_students=active_students, pending_requests=pending_requests)
    
    elif session['user_role'] == 'admin':
        # Get admin stats
        c.execute('SELECT COUNT(*) FROM users')
        total_users = c.fetchone()[0]
        
        c.execute('SELECT SUM(completed_time) FROM study_sessions')
        total_study_hours = c.fetchone()[0] or 0
        
        conn.close()
        return render_template('admin_dashboard.html', total_users=total_users, total_study_hours=total_study_hours)

@app.route('/timers')
@login_required
def timers():
    return render_template('timers.html')

@app.route('/start_timer', methods=['POST'])
@login_required
def start_timer():
    timer_type = request.form['timer_type']
    duration = int(request.form['duration'])
    
    session['active_timer'] = {
        'type': timer_type,
        'duration': duration,
        'start_time': datetime.now().isoformat()
    }
    
    return render_template('active_timer.html', timer_type=timer_type, duration=duration)

@app.route('/complete_session', methods=['POST'])
@login_required
def complete_session():
    if 'active_timer' not in session:
        return redirect(url_for('timers'))
    
    timer_data = session['active_timer']
    completed_time = float(request.form['completed_time'])
    focus_score = int(request.form.get('focus_score', 80))
    
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('INSERT INTO study_sessions (user_id, timer_type, duration, completed_time, focus_score) VALUES (?, ?, ?, ?, ?)',
             (session['user_id'], timer_data['type'], timer_data['duration'], completed_time, focus_score))
    conn.commit()
    conn.close()
    
    del session['active_timer']
    flash('Session completed successfully!')
    return redirect(url_for('dashboard'))

@app.route('/swipe')
@login_required
@role_required('student')
def swipe():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM users WHERE role = "ta" AND id NOT IN (SELECT ta_id FROM ta_matches WHERE student_id = ?)', 
             (session['user_id'],))
    tas = c.fetchall()
    conn.close()
    return render_template('swipe.html', tas=tas)

@app.route('/match_ta', methods=['POST'])
@login_required
@role_required('student')
def match_ta():
    ta_id = request.form['ta_id']
    
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('INSERT INTO ta_matches (student_id, ta_id) VALUES (?, ?)', 
             (session['user_id'], ta_id))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/matches')
@login_required
def matches():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    if session['user_role'] == 'student':
        c.execute('''SELECT tm.id, tm.student_id, tm.ta_id, tm.status, u.name, u.email, tm.rating, tm.created_at FROM ta_matches tm 
                    JOIN users u ON tm.ta_id = u.id 
                    WHERE tm.student_id = ?''', (session['user_id'],))
    else:
        c.execute('''SELECT tm.id, tm.student_id, tm.ta_id, tm.status, u.name, u.email, tm.rating, tm.created_at FROM ta_matches tm 
                    JOIN users u ON tm.student_id = u.id 
                    WHERE tm.ta_id = ?''', (session['user_id'],))
    
    matches = c.fetchall()
    conn.close()
    return render_template('matches.html', matches=matches)

@app.route('/notes')
@login_required
def notes():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    if session['user_role'] == 'ta':
        c.execute('SELECT * FROM notes WHERE ta_id = ? ORDER BY created_at DESC', (session['user_id'],))
    else:
        # Students see notes from their matched TAs
        c.execute('''SELECT n.* FROM notes n 
                    JOIN ta_matches tm ON n.ta_id = tm.ta_id 
                    WHERE tm.student_id = ? AND tm.status = "matched"
                    ORDER BY n.created_at DESC''', (session['user_id'],))
    
    notes = c.fetchall()
    conn.close()
    return render_template('notes.html', notes=notes)

@app.route('/add_note', methods=['POST'])
@login_required
@role_required('ta')
def add_note():
    title = request.form['title']
    content = request.form['content']
    subject = request.form['subject']
    
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('INSERT INTO notes (ta_id, title, content, subject) VALUES (?, ?, ?, ?)',
             (session['user_id'], title, content, subject))
    conn.commit()
    conn.close()
    
    flash('Note added successfully!')
    return redirect(url_for('notes'))

@app.route('/stats')
@login_required
def stats():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    if session['user_role'] == 'student':
        c.execute('SELECT timer_type, SUM(completed_time), COUNT(*) FROM study_sessions WHERE user_id = ? GROUP BY timer_type', 
                 (session['user_id'],))
        timer_stats = c.fetchall()
        
        c.execute('SELECT DATE(created_at), SUM(completed_time) FROM study_sessions WHERE user_id = ? GROUP BY DATE(created_at) ORDER BY DATE(created_at) DESC LIMIT 7', 
                 (session['user_id'],))
        daily_stats = c.fetchall()
        
        conn.close()
        return render_template('student_stats.html', timer_stats=timer_stats, daily_stats=daily_stats)
    
    elif session['user_role'] == 'ta':
        c.execute('SELECT AVG(rating), COUNT(*) FROM ta_matches WHERE ta_id = ? AND rating IS NOT NULL', 
                 (session['user_id'],))
        rating_stats = c.fetchone()
        
        conn.close()
        return render_template('ta_stats.html', rating_stats=rating_stats)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/calendar')
@login_required
@role_required('student')
def calendar():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    # Get user's deadlines
    c.execute('SELECT * FROM deadlines WHERE user_id = ? ORDER BY due_date ASC', (session['user_id'],))
    deadlines = c.fetchall()
    
    # Get user's timetable entries
    c.execute('SELECT * FROM timetable_entries WHERE user_id = ? ORDER BY start_time ASC', (session['user_id'],))
    timetable_entries = c.fetchall()
    
    conn.close()
    return render_template('calendar.html', deadlines=deadlines, timetable_entries=timetable_entries)

@app.route('/calendar/add-deadline', methods=['POST'])
@login_required
@role_required('student')
def add_deadline():
    title = request.form['title']
    subject = request.form['subject']
    due_date = request.form['due_date']
    priority = request.form['priority']
    study_hours = int(request.form['study_hours'])
    description = request.form.get('description', '')
    
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('INSERT INTO deadlines (user_id, title, subject, due_date, priority, study_hours, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
             (session['user_id'], title, subject, due_date, priority, study_hours, description))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/calendar/generate-timetable', methods=['POST'])
@login_required
@role_required('student')
def generate_timetable():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    # Get user's pending deadlines
    c.execute('SELECT * FROM deadlines WHERE user_id = ? AND completed = 0 ORDER BY due_date ASC', (session['user_id'],))
    deadlines = c.fetchall()
    
    if not deadlines:
        return jsonify({'success': False, 'message': 'No deadlines found to generate timetable'})
    
    # Generate AI timetable based on actual deadlines
    timetable = generate_ai_timetable(deadlines)
    
    conn.close()
    return jsonify({'success': True, 'timetable': timetable})

@app.route('/calendar/apply-timetable', methods=['POST'])
@login_required
@role_required('student')
def apply_timetable():
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    
    # Clear existing timetable entries
    c.execute('DELETE FROM timetable_entries WHERE user_id = ?', (session['user_id'],))
    
    # Get user's deadlines to generate actual timetable entries
    c.execute('SELECT * FROM deadlines WHERE user_id = ? AND completed = 0 ORDER BY due_date ASC', (session['user_id'],))
    deadlines = c.fetchall()
    
    if deadlines:
        from datetime import datetime, timedelta
        
        # Generate timetable entries based on deadlines
        working_deadlines = []
        for d in deadlines:
            due_date = datetime.fromisoformat(d[4].replace('T', ' '))
            working_deadlines.append({
                'title': d[1],
                'subject': d[2],
                'due_date': due_date,
                'priority': d[5],
                'remaining_hours': d[6]
            })
        
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for i in range(7):
            date = base_date + timedelta(days=i)
            
            for deadline in working_deadlines:
                if deadline['remaining_hours'] <= 0:
                    continue
                    
                days_until_due = (deadline['due_date'] - date).days
                
                if days_until_due <= 0:
                    # Due today - intensive study
                    hours_today = min(6, deadline['remaining_hours'])
                    if hours_today > 0:
                        end_time = date + timedelta(hours=hours_today)
                        c.execute('INSERT INTO timetable_entries (user_id, title, start_time, end_time, subject, entry_type, priority) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                 (session['user_id'], f'CRITICAL: {deadline["title"]}', date.isoformat(), end_time.isoformat(), deadline['subject'], 'study', 'critical'))
                        deadline['remaining_hours'] -= hours_today
                        
                elif days_until_due == 1:
                    # Due tomorrow - heavy study
                    hours_today = min(4, deadline['remaining_hours'])
                    if hours_today > 0:
                        end_time = date + timedelta(hours=hours_today)
                        c.execute('INSERT INTO timetable_entries (user_id, title, start_time, end_time, subject, entry_type, priority) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                 (session['user_id'], f'URGENT: {deadline["title"]}', date.isoformat(), end_time.isoformat(), deadline['subject'], 'study', 'high'))
                        deadline['remaining_hours'] -= hours_today
                        
                elif days_until_due <= 3:
                    # Due in 2-3 days - moderate study
                    hours_today = min(3, deadline['remaining_hours'])
                    if hours_today > 0:
                        afternoon = date.replace(hour=14)
                        end_time = afternoon + timedelta(hours=hours_today)
                        c.execute('INSERT INTO timetable_entries (user_id, title, start_time, end_time, subject, entry_type, priority) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                 (session['user_id'], f'Study: {deadline["title"]}', afternoon.isoformat(), end_time.isoformat(), deadline['subject'], 'study', 'medium'))
                        deadline['remaining_hours'] -= hours_today
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Timetable applied to calendar'})

def generate_ai_timetable(deadlines):
    from datetime import datetime, timedelta
    
    total_hours = sum(d[6] for d in deadlines)
    schedule = []
    base_date = datetime.now()
    
    # Create a working copy of deadlines with remaining hours
    working_deadlines = []
    for d in deadlines:
        due_date = datetime.fromisoformat(d[4].replace('T', ' '))
        working_deadlines.append({
            'id': d[0],
            'title': d[1],
            'subject': d[2],
            'due_date': due_date,
            'priority': d[5],
            'remaining_hours': d[6],
            'description': d[7]
        })
    
    # Sort by due date (most urgent first)
    working_deadlines.sort(key=lambda x: x['due_date'])
    
    for i in range(7):
        date = base_date + timedelta(days=i)
        day_sessions = []
        
        for deadline in working_deadlines:
            if deadline['remaining_hours'] <= 0:
                continue
                
            days_until_due = (deadline['due_date'] - date).days
            
            # Allocate hours based on urgency
            if days_until_due <= 0:
                # Due today - intensive study
                hours_today = min(6, deadline['remaining_hours'])
                if hours_today > 0:
                    day_sessions.append({
                        'title': f'CRITICAL: {deadline["title"]}',
                        'time': f'09:00 - {9+hours_today:02d}:00',
                        'duration': f'{hours_today} hours',
                        'description': f'Final preparation for {deadline["subject"]} - DUE TODAY!',
                        'priority': 'critical',
                        'stress_level': 'critical'
                    })
                    deadline['remaining_hours'] -= hours_today
                    
            elif days_until_due == 1:
                # Due tomorrow - heavy study
                hours_today = min(4, deadline['remaining_hours'])
                if hours_today > 0:
                    day_sessions.append({
                        'title': f'URGENT: {deadline["title"]}',
                        'time': f'09:00 - {9+hours_today:02d}:00',
                        'duration': f'{hours_today} hours',
                        'description': f'Intensive study for {deadline["subject"]} - Due tomorrow!',
                        'priority': 'high',
                        'stress_level': 'high'
                    })
                    deadline['remaining_hours'] -= hours_today
                    
            elif days_until_due <= 3:
                # Due in 2-3 days - moderate study
                hours_today = min(3, deadline['remaining_hours'])
                if hours_today > 0 and len(day_sessions) == 0:
                    day_sessions.append({
                        'title': f'Study: {deadline["title"]}',
                        'time': f'14:00 - {14+hours_today:02d}:00',
                        'duration': f'{hours_today} hours',
                        'description': f'Prepare for {deadline["subject"]} - Due in {days_until_due} days',
                        'priority': deadline['priority'],
                        'stress_level': 'medium'
                    })
                    deadline['remaining_hours'] -= hours_today
                    
            elif days_until_due <= 7:
                # Due in 4-7 days - light study
                hours_today = min(2, deadline['remaining_hours'])
                if hours_today > 0 and len(day_sessions) < 2:
                    day_sessions.append({
                        'title': f'Review: {deadline["title"]}',
                        'time': f'19:00 - {19+hours_today:02d}:00',
                        'duration': f'{hours_today} hours',
                        'description': f'Early preparation for {deadline["subject"]}',
                        'priority': 'low',
                        'stress_level': 'low'
                    })
                    deadline['remaining_hours'] -= hours_today
        
        # Add breaks between long sessions
        if any(int(s['duration'].split()[0]) >= 3 for s in day_sessions):
            day_sessions.insert(1, {
                'title': 'Study Break',
                'time': '11:30 - 12:00',
                'duration': '30 minutes',
                'description': 'Rest and refresh',
                'priority': 'low',
                'stress_level': 'low'
            })
        
        schedule.append({
            'date': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'sessions': day_sessions
        })
    
    return {
        'total_sessions': len([s for day in schedule for s in day['sessions'] if 'Break' not in s['title']]),
        'total_hours': total_hours,
        'subjects': list(set(d[2] for d in deadlines if d[2])),
        'daily_schedule': schedule
    }

@app.route('/calendar/email-timetable', methods=['POST'])
@login_required
@role_required('student')
def email_timetable():
    # Simulate email sending
    return jsonify({'success': True, 'message': 'Timetable emailed successfully'})

@app.route('/update_match/<int:match_id>/<status>', methods=['POST'])
@login_required
@role_required('ta')
def update_match(match_id, status):
    conn = sqlite3.connect('study_app.db')
    c = conn.cursor()
    c.execute('UPDATE ta_matches SET status = ? WHERE id = ? AND ta_id = ?', 
             (status, match_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash(f'Match request {status}!')
    return redirect(url_for('matches'))

@app.route('/live_notes')
@login_required
def live_notes():
    return render_template('live_notes.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)