-- Users table with RBAC
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    name VARCHAR(80) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Study sessions
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timer_type VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL,
    completed_duration INTEGER DEFAULT 0,
    interruptions INTEGER DEFAULT 0,
    focus_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- TA profiles
CREATE TABLE ta_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subjects TEXT,
    bio TEXT,
    rating FLOAT DEFAULT 0.0,
    total_hours INTEGER DEFAULT 0,
    availability TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Matches between students and TAs
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    ta_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (ta_id) REFERENCES users (id)
);

-- Notes shared by TAs
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ta_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    subject VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ta_id) REFERENCES users (id)
);

-- Deadlines table
CREATE TABLE deadlines (
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
);

-- Timetable entries
CREATE TABLE timetable_entries (
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
);