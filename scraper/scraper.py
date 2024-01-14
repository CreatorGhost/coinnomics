from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime
import time


def extract_urls_and_times(soup):
    # Find all headers containing URLs
    headers = soup.find_all("h3", class_="rpwe-title")
    articles_info = []

    for header in headers:
        link = header.find('a')
        if link and 'href' in link.attrs:
            url = link['href']

            # Find the corresponding time element
            time_element = header.find_next("time", class_="rpwe-time published")
            if time_element and 'datetime' in time_element.attrs:
                unix_timestamp = datetime.strptime(time_element['datetime'], '%Y-%m-%dT%H:%M:%S+00:00').timestamp()
                articles_info.append({"unix_timestamp": unix_timestamp, "url": url})

    return articles_info

def extract_title(soup):
    title_element = soup.find('span', class_="breadcrumb_last")
    return title_element.text if title_element else 'No Title'

def extract_content(soup):
    content_section = soup.find("div", class_="coincodex-content")
    paragraphs = content_section.find_all(['p', 'h2']) if content_section else []
    return "\n\n".join(paragraph.text for paragraph in paragraphs)

def extract_tags(soup):
    tags_section = soup.find('div', class_="entry-tags")
    tags = [tag.text for tag in tags_section.find_all('a')] if tags_section else []
    return tags

def extract_article_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract article components
    title = extract_title(soup)
    content = extract_content(soup)
    tags = extract_tags(soup)

    article = title + "\n\n" + content
    return {"tags": tags, "article": article,"title":title}

def main(file_name):
    url = "https://cryptopotato.com/crypto-news/"
    response = requests.get(url)
    base_soup = BeautifulSoup(response.content,"html.parser")
    news_url_and_time = extract_urls_and_times(base_soup)
    print(news_url_and_time)
    all_data = []
    for data in news_url_and_time:
        print("Doing for 1")
        url = data['url']
        time_stamp = data["unix_timestamp"]
        news = extract_article_data(url)
        news_info = [url,time_stamp,news["title"],news["article"],news["tags"]]

        all_data.append(news_info)
    
    # Create a DataFrame for all_data containing all news information
    df = pd.DataFrame(all_data, columns=['url', 'timestamp', 'title', 'article', 'tags'])

    df.to_csv(file_name)

if __name__ == "__main__":
    main("clean.csv")



