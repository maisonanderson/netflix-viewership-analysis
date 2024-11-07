import streamlit as st
import requests
from bs4 import BeautifulSoup

# URL and headers for the GET request
url = "https://about.netflix.com/en/newsroom?search=what%2520we%2520watched"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

# Send GET request
response = requests.get(url, headers=headers)

# Debugging: print response status code
st.write(f"Response Status Code: {response.status_code}")

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    st.write(soup.prettify())  # Display formatted HTML
else:
    # If the request fails, show the error status code
    st.write(f"Request failed with status code: {response.status_code}")
    soup = None

# Additional check to make sure soup is properly initialized
if soup:
    st.write("Soup is initialized successfully.")
else:
    st.write("Soup is not initialized.")
