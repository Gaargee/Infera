
import requests
import os
from bs4 import BeautifulSoup
import urllib
import urllib3
from urllib.parse import urljoin, urlparse
from collections import deque, Counter, defaultdict
import math
import re
import pickle
import time
ALLOWED_DOMAINS = [
    "wikipedia.org",
    "python.org",
    "realpython.com",
    "geeksforgeeks.org",
    "w3schools.com",
    "numpy.org",
    "pandas.pydata.org",
    "scikit-learn.org",
    "tensorflow.org",
    "pytorch.org"
]

stop_words = {
    "i","me","my","we","our","you","your","he","she","it","they","them",
    "is","am","are","was","were","be","been","being",
    "have","has","had","do","does","did",
    "a","an","the","and","but","if","or","because","as","until","while",
    "of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from",
    "up","down","in","out","on","off","over","under"
}
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()

    filtered = []
    for word in words:
        if word not in stop_words:
            filtered.append(word)

    return filtered


def create_snippet(text, query, length=180):
    text = " ".join(text.split())
    position = text.lower().find(query.lower())

    if position == -1:
        return text[:length] + "..."

    start = max(0, position - 80)
    end = min(len(text), position + 100)

    # snippet = text[start:end]
    # snippet = " ".join(snippet.split())
    return "..." + text[start:end] + "..."


def bfs_crawl(start_url, max_pages, visited, page_info, document_frequency, inverted_index):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    queue = deque([start_url])
    visited.add(start_url)
    pages_crawled = 0   

    while queue and pages_crawled < max_pages:

        current_url = queue.popleft()
        pages_crawled += 1

        print("\n========================")
        print("Crawling:", current_url)

        try:
            response = session.get(
                current_url,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text() if soup.title else "No title"
        text = soup.get_text(separator=" ")
        cleaned_words = clean_text(text)
        if len(cleaned_words) < 80:
          continue
        
        title_words = clean_text(title)
        page_keywords = set(title_words + cleaned_words[:200])

       

        word_count = Counter(cleaned_words)

        file_path = os.path.join(DATA_DIR, "pages.txt")
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"\nURL: {current_url}\n")
            file.write(" ".join(cleaned_words))
            file.write("\n" + "=" * 50 + "\n")

        duplicate = False

        for info in page_info.values():
            if info["title"] == title:
               duplicate = True
               break

        if duplicate:
             continue  
        page_info[current_url] = {
            "title": title,
            "word_count": len(cleaned_words),
            "word_freq": word_count,
            "text": text,
            "url": current_url
        }
        for word in set(cleaned_words):
         if current_url not in inverted_index[word]:
             inverted_index[word].append(current_url)
             document_frequency[word] += 1

        links = soup.find_all("a")

        for link in links:
            href = link.get("href")
            if href is None:
                continue
            href = href.strip()
            if href == "":
                continue
            blocked_extensions = ( ".pdf", ".jpg", ".jpeg", ".  png", ".gif",
               ".svg", ".zip", ".tar", ".tar.gz", ".tar.xz",
              ".whl", ".exe", ".msi", ".msix", ".pkg",
              ".dmg", ".iso", ".7z", ".rar", ".gz"
              
            )
            if href.lower().endswith(blocked_extensions):
                continue
           

            full_url = urljoin(current_url, href).split('#')[0]
            if "wikipedia.org" in full_url and "en.wikipedia.org" not in full_url:
                continue

            if any(x in full_url for x in ["special","Category:", "Template:","Help:", "Talk:", "File:", "mobileaction:", "oldid=", "action="
                   ]):
                continue
            if not any(domain in full_url for domain in ALLOWED_DOMAINS):     
                  continue
                
            page_name = urlparse(full_url).path.replace("/", " ")
            if ":" in page_name:
                continue
            if full_url  in visited:
                continue
            # ---------- Topic relevance ----------
            page_title_words = clean_text(page_name.replace("_", " "))

            common = len(set(page_title_words) & page_keywords)
            

            if common == 0 and len(page_title_words) > 2:
                continue
            visited.add(full_url)
            if common >= 2:
                queue.appendleft(full_url)
            else:
                queue.append(full_url)

    print("\nTotal pages crawled:", pages_crawled)

    return inverted_index, page_info, document_frequency


# ---------------- MAIN ----------------

choice = input("Load saved index? (y/n): ").strip().lower()

if choice == "y":
    with open("search_index.pkl", "rb") as file:
        inverted_index, page_info, document_frequency = pickle.load(file)



else:
    seed_urls = [
      "https://en.wikipedia.org/wiki/Computer_science",

      "https://www.python.org/",

      "https://realpython.com/",

      "https://www.geeksforgeeks.org/python-programming-language/",

      "https://www.w3schools.com/python/",

      "https://numpy.org/doc/stable/",

      "https://pandas.pydata.org/docs/",

      "https://scikit-learn.org/stable/",

      "https://www.tensorflow.org/tutorials",

      "https://pytorch.org/tutorials/",

      "https://en.wikipedia.org/wiki/Virat_Kohli",

      "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",

      "https://en.wikipedia.org/wiki/India"

     ]

    visited = set()
    page_info = {}
    document_frequency = Counter()
    inverted_index = defaultdict(list)

    for start_url in seed_urls:

      print(f"\n\nStarting crawl from: {start_url}")

      inverted_index, page_info, document_frequency = bfs_crawl(
          start_url,
          max_pages=75,
          visited=visited,
          page_info=page_info,
          document_frequency=document_frequency,
          inverted_index=inverted_index
      )

    with open("search_index.pkl", "wb") as file:
        pickle.dump(
            (inverted_index, page_info, document_frequency),
            file
        )

while True:



    query = input("\nSearch word (type 'exit' to quit): ").lower()

    if query == "exit":
        break

    query_words = clean_text(query)
    results = {}
    start = time.time()
    candidate_urls = set()

    for word in query_words:
        if word in inverted_index:
           candidate_urls.update(inverted_index[word])

    for url in candidate_urls:
        if url not in page_info:
            continue
        score = 0
        matched_words = 0
        title = page_info[url]["title"].lower()
        url_lower = url.lower()
        text_lower = page_info[url]["text"].lower()
        for word in query_words:
            frequency = page_info[url]["word_freq"].get(word, 0)
            if frequency == 0:
                continue
            matched_words += 1
            tf = frequency / page_info[url]["word_count"]
            idf = math.log(
               (len(page_info) + 1) /
               (document_frequency[word] + 1)
            )
            score += tf * idf * 10
        # score += matched_words * 2    
        # score += math.log(page_info[url]["word_count"] + 1) / 10
        # for word in query_words:
        #     if word in title:
        #         score += 3  
        if " ".join(query_words) in title:
            score += 20
        for word in query_words:
            if word in title:
                score += 8
            if word in url_lower:
                score += 3     
            score += min(text_lower.count(word), 15) * 0.3 
        score += math.log(page_info[url]["word_count"] + 1) / 5 
        bad_words = [
            "tag", "category", "archive", "forum", "mailing", "discussion", "author", "jobs"
        ]
        if any(x in url_lower for x in bad_words):
            score -= 0.4
        results[url] = score

    if not results:
        print("\nWord not found.")

        suggestions = []

        for word in inverted_index:
            for q in query_words:
             if q in word:
                suggestions.append(word)
                break
        if suggestions:
            print("\nDid you mean:")
            for word in sorted(suggestions)[:5]:
                print("-", word)

        continue

    sorted_results = sorted(
        results.items(),
        key=lambda item: item[1],
        reverse=True
    )
    end = time.time()

    print(f"\n{len(sorted_results)} results found in {end-start:.3f} seconds\n")

    for url, score in sorted_results[:10]:
        print("Title :", page_info[url]["title"])

        snippet = create_snippet(page_info[url]["text"], " ".join(query_words))
        print("Snippet :", snippet)

        print("URL   :", url)
        print("TF-IDF Score :", round(score, 4))
        print("-" * 40)