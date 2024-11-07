import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Streamlit title and description
st.title('Netflix Web Scraper Using Selenium')
st.markdown("This script uses Selenium and Streamlit to scrape Netflix data.")

# Function to initialize Selenium WebDriver
def initialize_driver():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver with the new Service method
    service = Service(ChromeDriverManager().install())  # Automatically installs the correct chromedriver

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to scrape Netflix articles
def scrape_netflix_articles():
    # URL of the page to scrape
    url = "https://about.netflix.com/en/newsroom?search=what%2520we%2520watched"

    # Initialize the WebDriver
    driver = initialize_driver()

    # Navigate to the page
    driver.get(url)

    # Get page source after Selenium has fully loaded the page
    page_source = driver.page_source

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Close the Selenium WebDriver
    driver.quit()

    # Extract articles from the page using BeautifulSoup
    articles = soup.find_all('div', {'data-testid': 'Article'})

    # Initialize a list to store the results
    articles_data = []

    # Iterate through each article
    for article in articles:
        # Find the title, link, and date
        title_tag = article.find('p', {'data-testid': 'ArticleTitleLink'})
        link_tag = article.find('a', href=True)
        date_tag = article.find('span', {'data-testid': 'ArticleDate'}).text if article.find('span', {'data-testid': 'ArticleDate'}) else None

        if title_tag and link_tag and date_tag:
            title = title_tag.get_text(strip=True)
            article_link = "https://about.netflix.com" + link_tag['href']  # Append the base URL to the relative link

            # Check if the title contains "What We Watched"
            if "What We Watched" in title:
                # Append the article data to the list
                articles_data.append({
                    'Title': title,
                    'Date Published': date_tag,
                    'Article Link': article_link
                })

    # Check if any articles were found
    if not articles_data:
        st.write("No articles matching 'What We Watched' were found.")
    else:
        # Display the results in Streamlit
        articles_df = pd.DataFrame(articles_data)
        st.write(articles_df)

# Call the function to scrape the articles
scrape_netflix_articles()
