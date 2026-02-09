from app import app, db
from database.db import User, TAProfile
from auth.utils import hash_password
from sqlalchemy import text

def migrate_and_seed():
    with app.app_context():
        # Add profile_image column to existing table
        try:
            db.session.execute(text("ALTER TABLE ta_profiles ADD COLUMN profile_image VARCHAR(500) DEFAULT 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face'"))
            db.session.commit()
            print("Added profile_image column")
        except Exception as e:
            print(f"Column might already exist: {e}")
            db.session.rollback()
        
        # Clear existing data
        TAProfile.query.delete()
        User.query.filter_by(role='ta').delete()
        db.session.commit()
        
        # Sample TA data with profile images
        tas_data = [
            {
                'name': 'Sarah Chen',
                'email': 'sarah.chen@university.edu',
                'subjects': 'Mathematics, Calculus, Linear Algebra',
                'bio': 'PhD in Mathematics | 5+ years tutoring experience | Specializes in making complex concepts simple',
                'rating': 4.9,
                'total_hours': 120,
                'availability': 'Mon-Fri: 2PM-8PM, Weekends: 10AM-6PM',
                'profile_image': 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'Alex Rodriguez',
                'email': 'alex.rodriguez@university.edu',
                'subjects': 'Computer Science, Python, Data Structures',
                'bio': 'Software Engineer & CS Tutor | Expert in algorithms and programming | Patient and encouraging',
                'rating': 4.8,
                'total_hours': 95,
                'availability': 'Mon-Wed: 6PM-10PM, Sat-Sun: 1PM-7PM',
                'profile_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'Emma Thompson',
                'email': 'emma.thompson@university.edu',
                'subjects': 'Physics, Chemistry, Engineering',
                'bio': 'Chemical Engineering graduate | Love helping students understand STEM concepts | Fun and interactive sessions',
                'rating': 4.7,
                'total_hours': 85,
                'availability': 'Tue-Thu: 4PM-9PM, Fri: 3PM-8PM',
                'profile_image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'Michael Park',
                'email': 'michael.park@university.edu',
                'subjects': 'Statistics, Economics, Business Math',
                'bio': 'Economics PhD candidate | 3 years TA experience | Specializes in statistical analysis and business applications',
                'rating': 4.6,
                'total_hours': 75,
                'availability': 'Mon-Fri: 5PM-9PM',
                'profile_image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'Zara Ahmed',
                'email': 'zara.ahmed@university.edu',
                'subjects': 'Biology, Organic Chemistry, Biochemistry',
                'bio': 'Pre-med student with 4.0 GPA | Passionate about life sciences | Helped 50+ students improve grades',
                'rating': 4.9,
                'total_hours': 110,
                'availability': 'Daily: 7PM-11PM, Weekends: 9AM-5PM',
                'profile_image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'David Kim',
                'email': 'david.kim@university.edu',
                'subjects': 'Machine Learning, AI, Advanced Programming',
                'bio': 'AI Research Assistant | Expert in ML algorithms | Published researcher | Makes AI accessible to everyone',
                'rating': 4.8,
                'total_hours': 65,
                'availability': 'Wed-Fri: 6PM-10PM, Weekends: 2PM-8PM',
                'profile_image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'Lisa Wang',
                'email': 'lisa.wang@university.edu',
                'subjects': 'English Literature, Writing, Essay Help',
                'bio': 'English Literature Masters | Writing tutor for 4 years | Helps with essays, analysis, and creative writing',
                'rating': 4.7,
                'total_hours': 90,
                'availability': 'Mon-Thu: 3PM-7PM, Sat: 10AM-4PM',
                'profile_image': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=face'
            },
            {
                'name': 'James Wilson',
                'email': 'james.wilson@university.edu',
                'subjects': 'History, Political Science, Research Methods',
                'bio': 'History PhD student | Research methodology expert | Helps with papers, citations, and critical thinking',
                'rating': 4.5,
                'total_hours': 55,
                'availability': 'Tue-Thu: 5PM-9PM, Sun: 1PM-6PM',
                'profile_image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=face'
            }
        ]
        
        for ta_data in tas_data:
            user = User(
                name=ta_data['name'],
                email=ta_data['email'],
                password_hash=hash_password('password123'),
                role='ta'
            )
            db.session.add(user)
            db.session.flush()
            
            profile = TAProfile(
                user_id=user.id,
                subjects=ta_data['subjects'],
                bio=ta_data['bio'],
                rating=ta_data['rating'],
                total_hours=ta_data['total_hours'],
                availability=ta_data['availability'],
                profile_image=ta_data['profile_image']
            )
            db.session.add(profile)
        
        db.session.commit()
        print(f"Successfully created {len(tas_data)} TA profiles with images!")

if __name__ == '__main__':
    migrate_and_seed()