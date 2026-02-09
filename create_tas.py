from app import app, db
from sqlalchemy import text
from auth.utils import hash_password

def create_sample_tas():
    with app.app_context():
        # Clear existing TA data
        db.session.execute(text("DELETE FROM ta_profiles"))
        db.session.execute(text("DELETE FROM users WHERE role = 'ta'"))
        db.session.commit()
        
        # Sample TAs with images
        tas = [
            ('Sarah Chen', 'sarah.chen@university.edu', 'Mathematics, Calculus, Linear Algebra', 'PhD in Mathematics | 5+ years tutoring experience', 4.9, 120, 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face'),
            ('Alex Rodriguez', 'alex.rodriguez@university.edu', 'Computer Science, Python, Data Structures', 'Software Engineer & CS Tutor | Expert in algorithms', 4.8, 95, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face'),
            ('Emma Thompson', 'emma.thompson@university.edu', 'Physics, Chemistry, Engineering', 'Chemical Engineering graduate | Fun interactive sessions', 4.7, 85, 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face'),
            ('Michael Park', 'michael.park@university.edu', 'Statistics, Economics, Business Math', 'Economics PhD candidate | 3 years TA experience', 4.6, 75, 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face'),
            ('Zara Ahmed', 'zara.ahmed@university.edu', 'Biology, Organic Chemistry, Biochemistry', 'Pre-med student with 4.0 GPA | Passionate about life sciences', 4.9, 110, 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face'),
            ('David Kim', 'david.kim@university.edu', 'Machine Learning, AI, Advanced Programming', 'AI Research Assistant | Expert in ML algorithms', 4.8, 65, 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face')
        ]
        
        for name, email, subjects, bio, rating, hours, image in tas:
            password_hash = hash_password('password123')
            
            # Insert user
            result = db.session.execute(text(
                "INSERT INTO users (name, email, password_hash, role) VALUES (:name, :email, :password_hash, 'ta')"
            ), {'name': name, 'email': email, 'password_hash': password_hash})
            
            user_id = result.lastrowid
            
            # Insert TA profile
            db.session.execute(text(
                "INSERT INTO ta_profiles (user_id, subjects, bio, rating, total_hours, profile_image) VALUES (:user_id, :subjects, :bio, :rating, :hours, :image)"
            ), {'user_id': user_id, 'subjects': subjects, 'bio': bio, 'rating': rating, 'hours': hours, 'image': image})
        
        db.session.commit()
        print(f"Created {len(tas)} TA profiles with images!")

if __name__ == '__main__':
    create_sample_tas()