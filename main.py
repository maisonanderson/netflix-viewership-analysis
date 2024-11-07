from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import streamlit as st

# Set up headless mode for Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure that the browser runs in headless mode
chrome_options.add_argument("--no-sandbox")  # Useful for Docker or certain environments
chrome_options.add_argument("--disable-dev-shm-usage")

# Specify the path to your chromedriver
driver = webdriver.Chrome(executable_path="path_to_your_chromedriver", options=chrome_options)

# Open the page in Selenium
url = "https://about.netflix.com/en/newsroom?search=what%2520we%2520watched"
driver.get(url)

# Give the page some time to load if needed (adjust sleep time)
driver.implicitly_wait(10)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Display the page content in Streamlit
st.write(soup.prettify())  # Pretty print the HTML content

# Close the driver
driver.quit()
