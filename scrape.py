import os
import requests
from bs4 import BeautifulSoup
import pandas as pd


def scrape_netflix_articles(url="https://about.netflix.com/en/newsroom?search=what%2520we%2520watched", exports_folder='exports'):
    # Create the exports directory if it doesn't exist
    os.makedirs(exports_folder, exist_ok=True)

    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', {'data-testid': 'Article'})

        # Initialize a list to store article data
        articles_data = []

        # Process each article
        for article in articles:
            title_tag = article.find('p', {'data-testid': 'ArticleTitleLink'})
            link_tag = article.find('a', href=True)
            date_tag = article.find('span', {'data-testid': 'ArticleDate'}).text

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                article_link = "https://about.netflix.com" + link_tag['href']

                # Check if the title contains "What We Watched"
                if "What We Watched" in title:
                    article_data = fetch_article_data(article_link, headers, date_tag, exports_folder)
                    if article_data:
                        articles_data.append(article_data)

    # Create and format the DataFrame
    articles_df = create_articles_dataframe(articles_data)
    return articles_df


def fetch_article_data(article_link, headers, date_tag, exports_folder):
    """Fetch data from the individual article link."""
    article_response = requests.get(article_link, headers=headers)
    if article_response.status_code == 200:
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        all_links = article_soup.find_all('a')

        for link in all_links:
            if link.get('href') and '.xlsx' in link['href'] and link.string == "here":
                return download_excel_file(link['href'], date_tag, article_link, exports_folder)
    return None


def download_excel_file(download_url, date_tag, article_link, exports_folder):
    """Download the Excel file and return the data."""
    filename = os.path.basename(download_url)
    file_path = os.path.join(exports_folder, filename)

    # Download the file if it does not exist
    if not os.path.exists(file_path):
        file_response = requests.get(download_url)
        if file_response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(file_response.content)

    return {
        'File Name': filename,
        'Date Published': date_tag,
        'Article Link': article_link,
        'Excel Link': download_url
    }


def create_articles_dataframe(articles_data):
    """Create a DataFrame from the collected data and format the date."""
    articles_df = pd.DataFrame(articles_data)
    articles_df['Date Published'] = pd.to_datetime(articles_df['Date Published'], errors='coerce').dt.strftime('%b %d, %Y')
    return articles_df.sort_values(by='Date Published', ascending=False)[['Date Published', 'Article Link', 'Excel Link']]
