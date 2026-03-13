import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ratings = db.relationship('UserRating', backref='user', lazy=True)
    activities = db.relationship('UserActivity', backref='user', lazy=True)
    searches = db.relationship('SearchHistory', backref='user', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    university = db.Column(db.String(255))
    difficulty_level = db.Column(db.String(50))
    course_rating = db.Column(db.Float)
    course_url = db.Column(db.String(500))
    course_description = db.Column(db.Text)
    skills = db.Column(db.Text)
    
    ratings = db.relationship('UserRating', backref='course', lazy=True)
    activities = db.relationship('UserActivity', backref='course', lazy=True)

class UserRating(db.Model):
    __tablename__ = 'user_ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable for anonymous
    session_id = db.Column(db.String(100), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True) # Nullable for page views without course
    action_type = db.Column(db.String(50), nullable=False) # 'view', 'click'
    time_spent = db.Column(db.Integer, default=0) # in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    query = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    with app.app_context():
        db.create_all()
        # Automatically load courses.csv into the database if empty
        if Course.query.count() == 0:
            print("Database is empty. Loading courses from CSV...")
            try:
                courses_df = pd.read_csv('data/courses.csv')
                courses_df = courses_df.fillna('')
                for index, row in courses_df.iterrows():
                    # Parse course rating correctly
                    rating_val = row.get('Course Rating', 0)
                    try:
                        course_rating = float(rating_val)
                    except ValueError:
                        course_rating = 0.0

                    course = Course(
                        id=index, # Keep ID matching CSV index for compatibility with models
                        course_name=row.get('Course Name', ''),
                        university=row.get('University', ''),
                        difficulty_level=row.get('Difficulty Level', ''),
                        course_rating=course_rating,
                        course_url=row.get('Course URL', ''),
                        course_description=row.get('Course Description', ''),
                        skills=row.get('Skills', '')
                    )
                    db.session.add(course)
                db.session.commit()
                print(f"Loaded {Course.query.count()} courses into the database.")
            except Exception as e:
                print(f"Error loading courses from CSV: {e}")
                db.session.rollback()
        
        # Load user_ratings.csv if users are populated or handle dummy users
        if UserRating.query.count() == 0 and os.path.exists('data/user_ratings.csv') and Course.query.count() > 0:
            print("Loading user ratings from CSV...")
            try:
                ratings_df = pd.read_csv('data/user_ratings.csv')
                
                # First ensure dummy users exist
                unique_users = ratings_df['user_id'].unique()
                for user_id in unique_users:
                    u_id = int(user_id)
                    if not User.query.get(u_id):
                        dummy_user = User(
                            id=u_id,
                            name=f"User {u_id}",
                            email=f"user{u_id}@example.com",
                            password_hash="dummy" # no real password for seeded users unless registered
                        )
                        db.session.add(dummy_user)
                db.session.commit()

                # Add ratings
                for _, row in ratings_df.iterrows():
                    rating = UserRating(
                        user_id=int(row['user_id']),
                        course_id=int(row['course_id']),
                        rating=int(row['rating'])
                    )
                    db.session.add(rating)
                db.session.commit()
                print(f"Loaded {UserRating.query.count()} user ratings into the database.")
            except Exception as e:
                print(f"Error loading user ratings from CSV: {e}")
                db.session.rollback()
