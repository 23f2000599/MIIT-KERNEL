# StudyFocus App

A comprehensive study management platform with timer functionality, TA matching, and role-based access control.

## Features

### For Students
- **Study Timers**: Pomodoro, Deep Focus, 52-17, Timeboxing, Flowtime, Exam Countdown timers
- **Focus Enhancement**: Ambient sounds, distraction blocking, focus lock mode
- **TA Matching**: Swipe-based system to find and match with teaching assistants
- **Live Learning**: Access to TA notes and exam preparation materials
- **Statistics**: Track study hours, focus scores, and progress

### For Teaching Assistants
- **Student Management**: Accept/decline match requests, manage active students
- **Content Sharing**: Upload notes and exam preparation materials
- **Live Sessions**: Conduct live learning sessions
- **Performance Analytics**: View ratings and engagement metrics

### For Admins
- **User Management**: Manage all users, roles, and permissions
- **Platform Analytics**: Monitor usage, study hours, and match efficiency
- **Content Moderation**: Oversee notes and exam materials

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open your browser and go to `http://localhost:5000`
   - The database will be automatically created on first run

## Default Test Accounts

Create accounts through the signup page with these roles:
- **Student**: Select "Student" role during signup
- **Teaching Assistant**: Select "Teaching Assistant" role during signup  
- **Admin**: Select "Admin" role during signup

## Application Flow

1. **Landing Page** → Product overview and features
2. **Authentication** → Login/Signup with role selection
3. **Role-Based Dashboard** → Customized dashboard based on user role
4. **Feature Access** → Timer, matching, notes, stats based on permissions
5. **Logout** → Session termination and redirect to landing

## Database Schema

- **users**: User accounts with roles (student, ta, admin)
- **study_sessions**: Timer sessions and focus tracking
- **ta_matches**: Student-TA matching system
- **notes**: TA-shared notes and materials

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Charts**: Chart.js for statistics visualization

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── study_app.db          # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── signup.html
│   ├── student_dashboard.html
│   ├── ta_dashboard.html
│   ├── admin_dashboard.html
│   ├── timers.html
│   ├── active_timer.html
│   ├── swipe.html
│   ├── matches.html
│   ├── notes.html
│   ├── student_stats.html
│   ├── ta_stats.html
│   ├── settings.html
│   └── admin_users.html
└── static/
    └── style.css         # Custom CSS styles
```

## Usage

1. **Start by creating an account** on the signup page
2. **Choose your role** (Student, TA, or Admin)
3. **Access role-specific features** through the navigation menu
4. **Students**: Use timers, find TAs, view notes and stats
5. **TAs**: Manage students, upload notes, view performance metrics
6. **Admins**: Manage users and monitor platform analytics

## Future Enhancements

- Spotify API integration for focus playlists
- Real-time notifications
- Advanced analytics and reporting
- Mobile app development
- Video calling for live sessions
- Advanced distraction blocking