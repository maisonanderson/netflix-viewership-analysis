import streamlit as st
from scrape import scrape_netflix_articles
import queries
import pandas as pd
from datetime import datetime, timedelta
import requests

# HEADER
st.set_page_config(page_title='Netflix Viewership Dashboard', layout='wide')

st.title('Netflix Viewership Dashboard')
st.markdown('<strong>Created by:</strong> [Maison Anderson](https://www.linkedin.com/in/maisonanderson/)',
            unsafe_allow_html=True)


import streamlit as st
import requests
from bs4 import BeautifulSoup

url = "https://about.netflix.com/en/newsroom?search=what%2520we%2520watched"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

# Make the GET request
response = requests.get(url, headers=headers)

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Option 1: Display the entire HTML as raw text
st.write(soup.prettify())  # This formats the HTML nicely


# article_df = scrape_netflix_articles()
# st.write(articles_df)
# latest_publish = pd.to_datetime(article_df['Date Published']).max()

st.markdown(
    f"""
    On December 12, 2023, Netflix made history as the first streaming service to release comprehensive viewership data 
    for its entire catalog. This dashboard provides high-level insights into Netflix’s viewership trends from all data 
    releases since the initial publication. Each time this page loads, it checks for new data updates, with the latest 
    release published on September 19, 2024. For more details on previous data releases, please 
    refer to the Info section at the bottom of this page, which also includes a list of the key assumptions made during 
    data processing.
    """
)

# VISUALIZATION #1
col1, col2 = st.columns(2)

with col1:
    st.markdown('### Most Viewed Films 📽️')
    col_a, col_b, _ = st.columns([2, 2, 2])

    with col_a:
        top_films_choice = st.selectbox(
            'Choose a metric:',
            options=['Views', 'Hours Viewed'],
            key='top_films_choice'
        )

    with col_b:
        max_films = queries.film_data_grouped['# of Films'].max()
        min_films = queries.film_data_grouped['# of Films'].min()
        films_filter = st.select_slider(
            'Filter by # of Films:',
            options=list(range(min_films, int(max_films) + 1)),
            value=(min_films, max_films),  # Default to the full range
            key='films_filter'
        )

    filtered_films = queries.film_data_grouped[
        queries.film_data_grouped['# of Films'].between(films_filter[0], films_filter[1])
    ]
    st.dataframe(queries.get_top_n_titles(filtered_films, 10, top_films_choice))

with col2:
    st.markdown('### Most Viewed TV Shows 📺')
    col_a, col_b, _ = st.columns([2, 2, 2])

    with col_a:
        top_tv_choice = st.selectbox(
            'Choose a metric:',
            options=['Views', 'Hours Viewed'],
            key='top_tv_choice'
        )

    with col_b:
        max_seasons = queries.tv_data_grouped['# of Seasons'].max()
        min_seasons = queries.tv_data_grouped['# of Seasons'].min()
        seasons_filter = st.select_slider(
            'Filter by # of Seasons:',
            options=list(range(min_seasons, int(max_seasons) + 1)),
            value=(min_seasons, max_seasons),  # Default to the full range
            key='seasons_filter'
        )

    filtered_tv = queries.tv_data_grouped[
        queries.tv_data_grouped['# of Seasons'].between(seasons_filter[0], seasons_filter[1])
    ]
    st.dataframe(queries.get_top_n_titles(filtered_tv, 10, top_tv_choice))

# VISUALIZATION #2
st.header('Total Views by Fiscal Half')
col1, col2 = st.columns([1, 4])

with col1:
    column_choice = st.selectbox(
        'Choose a grouping:',
        options=['Media', 'Ownership']
    )

# Use a variable to store the last date the cache was updated
if 'last_cache_update' not in st.session_state:
    st.session_state.last_cache_update = datetime.min


@st.cache_data
def create_cached_fiscal_half_chart(column_choice):
    return queries.create_fiscal_half_chart(column_choice)


# Check if we need to refresh the cache based on the latest published date
if latest_publish > st.session_state.last_cache_update:
    with st.spinner("Loading..."):
        date_range_chart = create_cached_fiscal_half_chart(column_choice)
        st.session_state.last_cache_update = latest_publish  # Update the cache timestamp

else:
    date_range_chart = create_cached_fiscal_half_chart(column_choice)  # Use cached data

st.altair_chart(date_range_chart, use_container_width=True)

# INFO SECTION
st.header('Info')

st.subheader('Data Sources')
st.dataframe(article_df, hide_index=True, column_config={
    'Article Link': st.column_config.LinkColumn(),
    'Excel Link': st.column_config.LinkColumn(display_text=r'\/([^\/]+)$')
})

st.subheader('Assumptions')
col1, _ = st.columns([3, 2])

with col1:
    st.markdown("""
    **General Assumptions:**
    - **Ownership:** Netflix describes "Release Date" as "the premiere date for any Netflix TV series or film." 
    Therefore, titles with a blank "Release Date" are assumed to be licensed content in this dashboard.
    - **Title:** A new column is created to group related seasons and films under a unified title, enabling higher-
    level insights. Titles are grouped using the following criteria:
        - Titles containing a colon (e.g., *Bridgerton: Season 3*)
        - Titles with "//" as a delimiter (e.g., *The Seven Deadly Sins // 七つの大罪*)
        - Titles ending with a single-digit number (e.g., *Despicable Me 2*)

    **Initial Publish:** 
    - **Media:** The H1 2023 dataset did not categorize content between "Film" and "TV." This dashboard categorizes 
    each title based on classifications found in later datasets. If a title's classification is missing, it defaults 
    to "TV" if the title contains the word "season"; otherwise, it is set to "Film."
    - **Runtime:** The H1 2023 dataset excluded "Runtime." This dashboard fills in missing runtime values by matching 
    titles with later datasets; if unavailable, the runtime is set to the average within the Media classification 
    ("Film" or "TV").
    """)
