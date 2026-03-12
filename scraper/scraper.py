import requests
from bs4 import BeautifulSoup

def scrape_course(url):

    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("h1")

    description = soup.find("p")

    return {
        "title": title.text if title else "",
        "description": description.text if description else ""
    }

def search_coursera(query):
    """
    Search Coursera for courses and return a list of dictionaries.
    """
    url = f"https://www.coursera.org/search?query={query.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        results = []
        
        # Look for all links that might be courses
        links = soup.find_all("a", href=True)
        seen_courses = set()
        
        for link in links:
            href = link["href"]
            if "/learn/" in href:
                # Resolve full URL
                full_url = href if href.startswith("http") else "https://www.coursera.org" + href
                course_id = href.split("/")[-1]
                
                if course_id in seen_courses:
                    continue
                seen_courses.add(course_id)
                
                # Title is usually the text of the link or an h3 nearby
                title = link.text.strip()
                if not title or len(title) < 5:
                    # Try to find an h3 in the parent or nearby
                    parent = link.find_parent("div")
                    h3 = parent.find("h3") if parent else None
                    if h3:
                        title = h3.text.strip()
                
                if not title:
                    title = course_id.replace("-", " ").title()
                
                results.append({
                    "Course Name": title,
                    "University": "Coursera Partner",
                    "Difficulty Level": "Beginner",
                    "Course Rating": "N/A",
                    "Course URL": full_url,
                    "Skills": "Online Course",
                    "similarity_score": 1.0
                })
                
                if len(results) >= 5:
                    break
            
        return results
    except Exception as e:
        print(f"Scraping error: {e}")
        return []