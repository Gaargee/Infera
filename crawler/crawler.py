# # import requests
# # This library is used to send HTTP requests
# import requests
# from bs4 import BeautifulSoup
# url = input("Enter website URL: ")
# # This stores the website address in a variable
# try:#send req used try as tjis req part is risky and can fail due to various reasons like network issues, invalid URL, etc.
#     response = requests.get(url, verify=False, timeout=5)
#     response.raise_for_status()
# except requests.exceptions.RequestException as e:
#     print("\nError occurred:", e)
#     exit()
# # This sends a GET request to the specified URL and stores the response
# print("\nstatus code:",response.status_code)
# # This prints the status code of the response to check if the request was successful
# soup=BeautifulSoup(response.text,"html.parser")
# #here the response.text contains raw HTML content of the webpage, and BeautifulSoup is used to parse it(how to read the HTML)
# #Without this step → you cannot extract data cleanly.)
# title = soup.title.string if soup.title else "No title found"
# # This extracts the title of the webpage using BeautifulSoup and stores it in a variable
# print("\nTitle",title)
# paragraphs = soup.find_all("p")
# # This finds all the paragraph tags in the HTML and stores them in a list
# print("\nparagraphs:\n")
# for p in paragraphs:
#     print(p.text)
# # This loops through the list of paragraphs and prints the text content of each paragraph
# links = soup.find_all("a")
# # This finds all the anchor tags (links) in the HTML and stores them in a list
# print("\nLinks found:\n")
# for link in links:
#     href = link.get("href")
#     if href:
#         print(href)




# import requests
# from bs4 import BeautifulSoup
# import urllib3
# from urllib.parse import urljoin

# # Disable SSL warning
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# visited = set()  # To avoid duplicate visits


# def crawl(url, depth, max_depth):
#     if depth > max_depth:
#         return
# # Check if the URL has already been visited to avoid cycles and redundant crawling
#     if url in visited:
#         return
#     #graph travelsal ogic as ig we are visiting the url for the first time we add it to visited set and then we will visit all the links in that url and repeat the process until we reach max depth or we have already visited the url

#     print(f"\nCrawling: {url}")
#     visited.add(url)
# # This prints the URL being crawled and adds it to the visited set to keep track of visited URLs
#     try:
#         response = requests.get(url, verify=False, timeout=5)
#         response.raise_for_status()
#         # This sends a GET request to the specified URL, disables SSL verification, and sets a timeout. If the request fails or returns an error status code, it raises an exception.
#     except requests.exceptions.RequestException as e:
#         print("Error:", e)
#         return

#     soup = BeautifulSoup(response.text, "html.parser")
# #converts raw html in structuted format and allows us to easily navigate and extract data from the webpage
#     title = soup.title.string if soup.title else "No title"
#     print("Title:", title)

#     links = soup.find_all("a")

#     for link in links:
#         href = link.get("href")
#         if href:
#             full_url = urljoin(url, href)  # handle relative links
#             #enshures that every link is converted to an absolute URL, which is necessary for crawling and avoids issues with relative paths

#             crawl(full_url, depth + 1, max_depth)
#             # This recursively calls the crawl function for each link found on the page, increasing the depth by 1. The recursion continues until the maximum depth is reached or there are no more links to crawl.


# # User input
# start_url = input("Enter website URL: ")

# max_depth = 1  # Change to 2 if you want deeper crawling

# crawl(start_url, 0, max_depth)


# # in this whole code the big concept is graph travelsal (DFS) as we are visiting the url for the first time we add it to visited set and then we will visit all the links in that url and repeat the process until we reach max depth or we have already visited the url


import requests
import os
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
from collections import deque, Counter, defaultdict
import math
import re
import pickle

stop_words = {
    "i","me","my","we","our","you","your","he","she","it","they","them",
    "is","am","are","was","were","be","been","being",
    "have","has","had","do","does","did",
    "a","an","the","and","but","if","or","because","as","until","while",
    "of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from",
    "up","down","in","out","on","off","over","under"
}

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


def bfs_crawl(start_url, max_pages, visited, page_info, document_frequency, inverted_index):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    queue = deque([start_url])
    pages_crawled = 0

    while queue and pages_crawled < max_pages:

        current_url = queue.popleft()
        pages_crawled += 1

        print("\n========================")
        print("Crawling:", current_url)

        try:
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(
                current_url,
                headers=headers,
                verify=False,
                timeout=5
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(separator=" ")
        cleaned_words = clean_text(text)

        for word in set(cleaned_words):
            inverted_index[word].append(current_url)
            document_frequency[word] += 1

        word_count = Counter(cleaned_words)

        file_path = os.path.join(DATA_DIR, "pages.txt")
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"\nURL: {current_url}\n")
            file.write(" ".join(cleaned_words))
            file.write("\n" + "=" * 50 + "\n")

        title = soup.title.get_text() if soup.title else "No title"

        page_info[current_url] = {
            "title": title,
            "word_count": len(cleaned_words),
            "word_freq": word_count,
            "text": text
        }

        links = soup.find_all("a")[:100]

        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(current_url, href).split('#')[0]

                if (
                    full_url.startswith("https://en.wikipedia.org/wiki/")
                    and ":" not in full_url
                    and full_url not in visited
                 ): 
                    visited.add(full_url)
                    queue.append(full_url)

    print("\nTotal pages crawled:", pages_crawled)

    return inverted_index, page_info, document_frequency


# ---------------- MAIN ----------------

choice = input("Load saved index? (y/n): ").strip().lower()

if choice == "y":
    with open("search_index.pkl", "rb") as file:
        inverted_index, page_info, document_frequency = pickle.load(file)



else:
    start_url = input("Enter website URL: ")

    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "https://" + start_url

    visited = set()
    page_info = {}
    document_frequency = Counter()
    inverted_index = defaultdict(list)

    inverted_index, page_info, document_frequency = bfs_crawl(
        start_url,
        max_pages=50,
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

    if not results:
        print("\nWord not found.")

        suggestions = []

        for word in inverted_index:
            for q in query_words:
             if word.startswith(q):
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

    print("\nFound in:\n")

    for url, score in sorted_results:
        print("Title :", page_info[url]["title"])

        snippet = create_snippet(page_info[url]["text"], " ".join(query_words))
        print("Snippet :", snippet)

        print("URL   :", url)
        print("TF-IDF Score :", round(score, 4))
        print("-" * 40)