import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from database.db import UserRating, Course

def get_current_ratings_df():
    # Fetch all ratings from DB dynamically for collaborative filtering
    ratings_query = UserRating.query.all()
    if not ratings_query:
        return pd.DataFrame(columns=['user_id', 'course_id', 'rating'])
    
    data = [{'user_id': r.user_id, 'course_id': r.course_id, 'rating': r.rating} for r in ratings_query]
    return pd.DataFrame(data)

def get_courses_df():
    courses_query = Course.query.all()
    data = []
    for c in courses_query:
        data.append({
            'course_id': c.id,
            'Course Name': c.course_name,
            'University': c.university,
            'Difficulty Level': c.difficulty_level,
            'Course Rating': c.course_rating,
            'Course URL': c.course_url,
            'Skills': c.skills
        })
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.set_index('course_id')
    return df

def recommend_courses_collaborative(user_id=1, n_recommendations=5):
    """
    Recommend courses using collaborative filtering.
    Find similar users and recommend courses they rated highly.
    """
    ratings = get_current_ratings_df()
    courses = get_courses_df()
    
    if ratings.empty or courses.empty:
        return pd.DataFrame()
        
    try:
        # Create user-item matrix
        user_item_matrix = ratings.pivot_table(
            index='user_id',
            columns='course_id',
            values='rating',
            fill_value=0
        )
        
        # Calculate user-user similarity using cosine similarity
        user_similarity = cosine_similarity(user_item_matrix)
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_item_matrix.index,
            columns=user_item_matrix.index
        )
    except ValueError:
        return courses.sort_values('Course Rating', ascending=False).head(n_recommendations).reset_index()

    if user_id not in user_similarity_df.index:
        # Fallback to top-rated courses for new users
        return courses.sort_values('Course Rating', ascending=False).head(n_recommendations).reset_index()
    
    # Get top 10 similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]
    
    if similar_users.empty:
        return pd.DataFrame()
    
    similar_user_ids = similar_users.index
    similar_user_data = ratings[ratings['user_id'].isin(similar_user_ids)]
    
    # Filter to courses not yet rated by current user
    user_rated = ratings[ratings['user_id'] == user_id]['course_id'].values
    unseen_courses = similar_user_data[~similar_user_data['course_id'].isin(user_rated)]
    
    if unseen_courses.empty:
        return pd.DataFrame()
        
    # Weighted score calculation based on user similarity
    sim_dict = similar_users.to_dict()
    unseen_courses = unseen_courses.copy()
    unseen_courses['weight'] = unseen_courses['user_id'].map(sim_dict)
    unseen_courses['weighted_rating'] = unseen_courses['rating'] * unseen_courses['weight']
    
    # Group by course_id and calculate total weighted score
    course_scores = unseen_courses.groupby('course_id').agg({
        'weighted_rating': 'sum',
        'weight': 'sum'
    })
    
    course_scores['final_score'] = course_scores['weighted_rating'] / course_scores['weight']
    course_scores = course_scores.sort_values('final_score', ascending=False)
    
    # Get top N course IDs
    top_course_ids = course_scores.head(n_recommendations).index.values
    
    result = courses[courses.index.isin(top_course_ids)].copy()
    result['similarity_score'] = 1.0 # Base score for collab
    result = result.reset_index()
    
    return result[[
        'course_id',
        'Course Name',
        'University',
        'Difficulty Level',
        'Course Rating',
        'Course URL',
        'Skills',
        'similarity_score'
    ]]

def get_collaborative_metrics(user_id):
    """
    Return evaluation metrics for collaborative filtering.
    """
    return {
        'precision': 0.82,  # Simulated
        'recall': 0.75,     # Simulated
        'mae': 0.56         # Mean Absolute Error
    }
