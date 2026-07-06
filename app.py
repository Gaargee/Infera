from flask import Flask, render_template, request
import pickle
import math
from difflib import get_close_matches
app = Flask(__name__)
with open("crawler/search_index.pkl", "rb") as file:
    inverted_index, page_info, document_frequency = pickle.load(file)
def create_snippet(text, query, length=180):

    # Remove extra spaces
    text = " ".join(text.split())

    text_lower = text.lower()

    # Try to find the complete query first
    position = text_lower.find(query.lower())

    # If complete query isn't found, search word by word
    if position == -1:

        for word in query.lower().split():

            position = text_lower.find(word)

            if position != -1:
                break

    # If nothing is found, start from beginning
    if position == -1:
        position = 0

    # Show text around the keyword
    start = max(0, position - 80)
    end = min(len(text), position + 100)

    snippet = text[start:end]

    # Add "..." if snippet is from the middle
    if start > 0:
        snippet = "... " + snippet

    if end < len(text):
        snippet += " ..."

    # Highlight searched words
    for word in query.split():

        snippet = snippet.replace(
            word,
            f"<mark>{word}</mark>"
        )

        snippet = snippet.replace(
            word.capitalize(),
            f"<mark>{word.capitalize()}</mark>"
        )

    return snippet  
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"].lower()

    query_words = query.split()
    did_you_mean = None

    corrected_words = []
    for word in query_words:

      if word in inverted_index:
        corrected_words.append(word)
      else:
           match = get_close_matches(
            word,
            inverted_index.keys(),
            n=1,
            cutoff=0.75
        )
           if match:
            corrected_words.append(match[0])
           else:
            corrected_words.append(word)  
    corrected_query = " ".join(corrected_words)

    if corrected_query != query:
     did_you_mean = corrected_query       
    results = {}
    common_urls = None

    for word in query_words:

        if word not in inverted_index:
            common_urls = set()
            break

        urls = set(inverted_index[word])

        if common_urls is None:
            common_urls = urls
        else:
            common_urls = common_urls.intersection(urls)

    if common_urls is None:
        common_urls = set()

    for url in common_urls:

        score = 0
        title = page_info[url]["title"].lower()
        for word in query_words:

            frequency = page_info[url]["word_freq"][word]
            total_words = page_info[url]["word_count"]

            tf = frequency / total_words
            idf = math.log(len(page_info) / document_frequency[word])

            score += tf * idf
            if word in title:
              score += 0.5
            if query in title:
             score += 2
            score += min(frequency * 0.02, 0.4)
            if word in url.lower():
             score += 0.3
            text = page_info[url]["text"].lower()
            position = text.find(word)
            if position != -1:
             score += max(0, 0.5 - (position / 5000))
        results[url] = score

    sorted_results = sorted(
        results.items(),
        key=lambda item: item[1],
        reverse=True
    )
    result_count = len(sorted_results)
    snippets = {}

    for url, score in sorted_results:
     snippets[url] = create_snippet(
        page_info[url]["text"],
        query
    )

    return render_template(
    "results.html",
    query=query,
    results=sorted_results,
    page_info=page_info,
    snippets=snippets,
    result_count=result_count,
    search_time=round(0.001, 3),
    did_you_mean=did_you_mean,
    )
@app.route("/admin")
def admin():
    return render_template("admin.html")
@app.route("/suggest")
def suggest():

    query = request.args.get("q", "").lower()

    suggestions = []

    if query:

        for word in inverted_index.keys():

            if word.startswith(query):

                suggestions.append(word)

            if len(suggestions) == 8:
                break

    return {"suggestions": suggestions}
if __name__ == "__main__":
    app.run(debug=True)