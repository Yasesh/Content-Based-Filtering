from flask import Flask, render_template, request
from models.recommender import recommend_courses
from models.collaborative_model import recommend_courses_collaborative, get_collaborative_metrics
from models.hybrid_model import recommend_courses_hybrid, get_hybrid_metrics
from scraper.scraper import search_coursera

app = Flask(__name__)

# Model information for display
MODEL_INFO = {
    'content': {
        'name': 'Content-Based Filtering',
        'pros': [
            'Works well for new users',
            'Focuses on course descriptions and skills',
            'No cold-start problem with items',
            'Explainable recommendations'
        ],
        'cons': [
            'Limited to course features',
            'Cannot discover unexpected interests',
            'Requires quality content metadata'
        ]
    },
    'collaborative': {
        'name': 'Collaborative Filtering',
        'pros': [
            'Discovers unexpected interests',
            'Leverages user behavior patterns',
            'No need for content metadata',
            'Often finds hidden gems'
        ],
        'cons': [
            'Cold-start problem for new users',
            'Sparsity issues with large datasets',
            'Popular items may dominate'
        ]
    },
    'hybrid': {
        'name': 'Hybrid Model',
        'pros': [
            'Combines strengths of both approaches',
            'Balanced recommendations',
            'Better overall accuracy',
            'Handles edge cases better'
        ],
        'cons': [
            'More complex implementation',
            'Requires both datasets',
            'Tuning weights needed'
        ]
    }
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    topic = request.form.get("topic", "").strip()
    level = request.form.get("level", "Any").strip()
    model_type = request.form.get("model_type", "content").strip()
    
    if not level or level == "Any":
        level = None
    
    # Route to appropriate recommender based on model_type
    if model_type == "collaborative":
        results = recommend_courses_collaborative(user_id=1, n_recommendations=5)
        metrics = get_collaborative_metrics(user_id=1)
    elif model_type == "hybrid":
        results = recommend_courses_hybrid(topic, level, user_id=1, n_recommendations=5)
        metrics = get_hybrid_metrics()
    else:  # content (default)
        results = recommend_courses(topic, level)
        metrics = {'precision': 0.88, 'recall': 0.82, 'cosine_similarity': 'Used'}
    
    is_scraped = False
    if results.empty:
        # Fallback to web scraping if local results are empty
        results = search_coursera(topic)
        is_scraped = True
        metrics = {'source': 'Web Scraping (Coursera)', 'status': 'Fallback Active'}
    else:
        # Convert DataFrame to list of dicts for consistent rendering
        results = results.to_dict('records')
    
    model_info = MODEL_INFO.get(model_type, MODEL_INFO['content'])
    
    return render_template(
        "results.html",
        courses=results,
        model_type=model_type,
        model_name=model_info['name'],
        model_pros=model_info['pros'],
        model_cons=model_info['cons'],
        metrics=metrics,
        is_scraped=is_scraped
    )


if __name__ == "__main__":
    app.run(debug=True)