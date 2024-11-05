import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_netflix_articles(url="https://about.netflix.com/en/newsroom?search=what%2520we%2520watched", exports_folder='exports'):
    # Create the exports directory if it doesn't exist
    os.makedirs(exports_folder, exist_ok=True)

    # Initialize a list to store the results
    articles_data = []

    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all articles in the news section
        articles = soup.find_all('div', {'data-testid': 'Article'})

        # Iterate through each article
        for article in articles:
            # Find the title and link
            title_tag = article.find('p', {'data-testid': 'ArticleTitleLink'})
            link_tag = article.find('a', href=True)
            date_tag = article.find('span', {'data-testid': 'ArticleDate'}).text

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                article_link = "https://about.netflix.com" + link_tag['href']  # Append the base URL to the relative link

                # Check if the title contains "What We Watched"
                if "What We Watched" in title:
                    # Send a GET request to the article link
                    article_response = requests.get(article_link, headers=headers)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        # Find all download links in the article content
                        all_links = article_soup.find_all('a')

                        # Iterate through the found links
                        for link in all_links:
                            # Check if the 'href' contains '.xlsx' and if the link text is "here"
                            if link.get('href') and '.xlsx' in link['href'] and link.string == "here":
                                download_url = link['href']

                                # Construct the full filename to save the file
                                filename = os.path.basename(download_url)
                                file_path = os.path.join(exports_folder, filename)

                                # Check if the file already exists
                                if not os.path.exists(file_path):
                                    # Download the file if it does not exist
                                    file_response = requests.get(download_url)
                                    if file_response.status_code == 200:
                                        with open(file_path, 'wb') as f:
                                            f.write(file_response.content)

                                # Append the file, date, and article link information
                                articles_data.append({
                                    'File Name': filename,
                                    'Date Published': date_tag,
                                    'Article Link': article_link,
                                    'Excel Link': download_url
                                })

    # Create a DataFrame from the collected data
    articles_df = pd.DataFrame(articles_data)

    # Convert 'Date Published' column to proper date format and format it as "Sep 30, 2024"
    articles_df['Date Published'] = pd.to_datetime(articles_df['Date Published'], errors='coerce')
    articles_df['Date Published'] = articles_df['Date Published'].dt.strftime('%b %d, %Y')  # Format the date

    # Sort the DataFrame by 'Date Published' in descending order
    articles_df = articles_df.sort_values(by='Date Published', ascending=False)[
        ['Date Published', 'Article Link', 'Excel Link']]

    return articles_df
