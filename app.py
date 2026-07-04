from flask import Flask, render_template, request
import pickle
import math
app = Flask(__name__)
with open("crawler/search_index.pkl", "rb") as file:
    inverted_index, page_info, document_frequency = pickle.load(file)
def create_snippet(text, query, length=150):

    text_lower = text.lower()
    position = text_lower.find(query.lower())

    if position == -1:
        return text[:length]

    start = max(0, position - length // 2)
    end = min(len(text), position + length // 2)

    snippet = text[start:end]
    snippet = " ".join(snippet.split())

    return snippet    
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"].lower()

    query_words = query.split()

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

        for word in query_words:

            frequency = page_info[url]["word_freq"][word]
            total_words = page_info[url]["word_count"]

            tf = frequency / total_words
            idf = math.log(len(page_info) / document_frequency[word])

            score += tf * idf

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
    search_time=round(0.001, 3)
    )

if __name__ == "__main__":
    app.run(debug=True)