import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
courses = pd.read_csv("data/courses.csv")

courses = courses.fillna("")

# Combine important text features
courses["features"] = (
    courses["Course Name"] +
    " " +
    courses["Course Description"] +
    " " +
    courses["Skills"] +
    " " +
    courses["Difficulty Level"]
)

# TF-IDF vectorization
vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(courses["features"])

# Cosine similarity
similarity_matrix = cosine_similarity(tfidf_matrix)


def recommend_courses(topic, level=None, n_recommendations=5):
    """
    Recommend courses using vector similarity between the query and course features.
    """
    if not topic:
        return pd.DataFrame()

    # Transform query into the same TF-IDF space
    query_vector = vectorizer.transform([topic.lower()])
    
    # Calculate similarity between query and all courses
    query_similarity = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Create a copy of courses with similarity scores
    results = courses.copy()
    results["similarity_score"] = query_similarity
    results["course_id"] = results.index
    
    # Apply difficulty level filter if provided
    if level and level != "Any":
        results = results[
            results["Difficulty Level"].str.contains(level, case=False, na=False)
        ]
    
    # Sort by similarity score
    results = results.sort_values("similarity_score", ascending=False)
    
    # Filter out zero similarity results (to avoid completely irrelevant matches)
    results = results[results["similarity_score"] > 0]
    
    # Return top N
    return results.head(n_recommendations)[[
        "course_id",
        "Course Name",
        "University",
        "Difficulty Level",
        "Course Rating",
        "Course URL",
        "Skills",
        "similarity_score"
    ]]