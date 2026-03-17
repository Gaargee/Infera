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
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
from collections import deque
import re
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

visited = set()
def clean_text(text):# This function takes a string of text as input and processes it to remove common stop words, which are words that do not add significant meaning to the text (like "the", "is", "and", etc.). The function converts the text to lowercase, splits it into individual words, and then filters out any words that are present in the predefined set of stop words. Finally, it returns a list of cleaned words that can be used for further analysis or processing.
    words = text.lower() # Convert the input text to lowercase to ensure uniformity and make it easier to compare words against the stop words set.
    text = re.sub(r'[^a-zA-Z\s]', ' ', text) # This uses a regular expression to remove any characters from the text that are not lowercase letters (a-z) or whitespace. This helps to clean the text by eliminating punctuation, numbers, and other non-alphabetic characters.
    words = text.split() # This splits the cleaned text into a list of individual words based on whitespace. Each word can then be processed to check if it is a stop word or not.
    filtered =[] # Create an empty list to store the filtered words
    for word in words:# Loop through each word in the list of words
        if word not in stop_words:# Check if the word is not in the set of stop words
            filtered.append(word) # If the word is not a stop word, add it to the filtered list
    return filtered 

def bfs_crawl(start_url, max_pages=10):

    visited.clear()   # Step 4 (important)
    queue = deque([start_url])
    visited.add(start_url)

    while queue and len(visited) < max_pages:

        current_url = queue.popleft()

        print("\n========================")
        print("Crawling:", current_url)

        try:
            response = requests.get(current_url, verify=False, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error:", e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text() # Extracts all the text content from the webpage, removing HTML tags and other non-text elements. This allows us to analyze the actual content of the page without any formatting or markup.
        cleaned_words = clean_text(text) # This calls the clean_text function to process the extracted text and remove stop words, resulting in a list of meaningful words that can be used for further analysis or processing.
        print("\n Sample Cleaned Words:", cleaned_words[:10]) # This prints a sample of the cleaned words (the first 10) to give an idea of the content extracted from the webpage after removing stop words.

        title = soup.title.string if soup.title else "No title"
        print("Title:", title)
        print("========================")

        links = soup.find_all("a")[:5]   # Step 3 (limit links)

        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(current_url, href)

                if full_url not in visited:
                    visited.add(full_url)
                    queue.append(full_url)

    # ✅ Step 3 (correct place)
    print("\nTotal pages crawled:", len(visited))


# Start program
start_url = input("Enter website URL: ")
bfs_crawl(start_url, max_pages=5)