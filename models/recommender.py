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


def recommend_courses(topic, level=None):

    filtered = courses[
        courses["Course Name"].str.contains(topic, case=False, na=False)
    ]

    if level:
        filtered = filtered[
            filtered["Difficulty Level"].str.contains(level, case=False, na=False)
        ]

    if filtered.empty:
        return []

    idx = filtered.index[0]

    similarity_scores = list(enumerate(similarity_matrix[idx]))

    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    similarity_scores = similarity_scores[1:6]

    course_indices = [i[0] for i in similarity_scores]

    return courses.iloc[course_indices][[
        "Course Name",
        "University",
        "Difficulty Level",
        "Course Rating",
        "Course URL",
        "Skills"
    ]]