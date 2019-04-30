import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib import parse
from collections import deque
from domain import *
import os


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'a']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def extract_text(soup, url, file_number):
    body = soup.findAll(text=True)
    text = filter(tag_visible, body)
    visible_text = []
    with open(PROJECT_DIR + str(file_number) + '.txt', "w") as file:
        for element in text:
            visible_text.append(element)
        visible_text = " ".join(t.strip() for t in visible_text)
        file.write(visible_text)
    with open(PROJECT_DIR + "mapping.txt", "a") as file:
        file.write(str(file_number) + " " + url + "\n")


def first_spider(url):
    VISITED.add(url)
    domain = "uic.edu"
    url = "http://www." + url
    links = []
    try:
        source = requests.get(url)
        plain_text = source.text
        soup = BeautifulSoup(plain_text, features="html.parser")
        extract_text(soup, url, FILE_COUNTER)
        for link in soup.find_all('a'):
            if '#' in link or 'mailto' in link:
                continue
            h = link.get('href')
            href = parse.urljoin(url, h)
            if get_domain_name(href) == domain:
                if href[-1] == "/":
                    href = href[:-1]
                links.append(href)
                href = href.replace("http://", "")
                href = href.replace("https://", "")
                href = href.replace("www.", "")
                if href not in LINKS and href not in VISITED:
                    LINKS.append(href)
        if len(links) > 0:
            OUTLINKS[FILE_COUNTER] = links
    except:
        print("cant open url: " + url)
        with open(PROJECT_DIR + "bad_links.txt", "a") as file:
            file.write(url + "\n")


def spider(url, file_number):
    VISITED.add(url)
    domain = "uic.edu"
    url = "http://www." + url
    try:
        source = requests.get(url)
        plain_text = source.text
        soup = BeautifulSoup(plain_text, features="html.parser")
        extract_text(soup, url, file_number)
        links = []
        for link in soup.find_all('a'):
            if '#' in link or 'mailto' in link:
                continue
            h = link.get('href')
            href = parse.urljoin(url, h)
            if get_domain_name(href) == domain:
                if href[-1] == "/":
                    href = href[:-1]
                links.append(href)
                href = href.replace("http://", "")
                href = href.replace("https://", "")
                href = href.replace("www.", "")
                if href not in LINKS and href not in VISITED:
                    LINKS.append(href)
        if len(links) > 0:
            OUTLINKS[file_number] = links
    except:
        print("cant open url: " + url)
        with open(PROJECT_DIR + "bad_links.txt", "a") as file:
            file.write(url + "\n")


def crawl(file_counter):
    file_number = file_counter
    while len(VISITED) <= 4000:
        link = LINKS.popleft()
        print("crawling page: " + link)
        print("Visited pages: " + str(len(VISITED)))
        print("Pages to crawl: " + str(len(LINKS)))
        spider(link, file_number)
        file_number += 1


def crawl_bad_links(links, file_number):
    for link in links:
        link = link.replace("http://www.", "https://www.")
        try:
            print("crawling link: " + link)
            source = requests.get(link)
            plain_text = source.text
            soup = BeautifulSoup(plain_text, features="html.parser")
            extract_text(soup, link, file_number)
            file_number += 1
        except:
            print("cant open url: " + link)
            with open(PROJECT_DIR + "bad_links1.txt", "a") as file:
                file.write(link + "\n")


def write_outlinks_file(outlinks):
    with open(PROJECT_DIR + 'outlinks.txt', 'a') as file:
        for key, value in outlinks.items():
            val = ""
            for item in value:
                val += item + " "
            file.write(str(key) + " " + val + "\n")


PROJECT_DIR = 'UIC_CS2/'
VISITED = set()
OUTLINKS = {}
LINKS = deque()
FILE_COUNTER = 1
create_directory(PROJECT_DIR)
first_spider("cs.uic.edu")
crawl(2)
if len(OUTLINKS) == 0:
    print("No outlinks found")
write_outlinks_file(OUTLINKS)
