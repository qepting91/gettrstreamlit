import streamlit as st
import pandas as pd
from gogettr import PublicClient
from gogettr.errors import GettrApiError
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import bokeh.plotting as bp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from requests.exceptions import JSONDecodeError

# Initialize the gogettr client
client = PublicClient()

# --- Improved Functions for User Data and Network ---

def display_user_info(username):
    try:
        user_info = client.user_info(username=username)
        if user_info:
            st.json(user_info)
        else:
            st.error("User not found.")
    except errors.GettrApiError as e:
        st.error(f"Failed to fetch user info: {str(e)}")
    except requests.exceptions.JSONDecodeError as e:
        st.error("Failed to decode the response from the GETTR API. Please try again later.")

def display_posts_by_keyword(keyword, max_results=100):
    try:
        posts = list(client.search(query=keyword, max=max_results))
        if posts:
            df = pd.DataFrame(posts)
            st.dataframe(df)
        else:
            st.error("No posts found.")
    except Exception as e:
        st.error(f"Error fetching posts by keyword: {str(e)}")

def display_user_posts(username, max_results=100):
    try:
        posts = list(client.user_activity(username=username, max=max_results, type="posts"))
        if posts:
            df = pd.DataFrame(posts)
            st.dataframe(df) 
            # ... add pagination if needed
        else:
            st.error("No posts found for this user.")
    except GettrApiError as e:
        st.error(f"Failed to fetch user posts: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        
def display_user_comments(username, max_results=100):
    try:
        comments = list(client.user_activity(username=username, max=max_results, type="comments"))
        if comments:
            df = pd.DataFrame(comments)
            st.dataframe(df) 
            # ... add pagination if needed
        else:
            st.error("No comments found for this user.")
    except GettrApiError as e:
        st.error(f"Failed to fetch user comments: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

def display_user_likes(username, max_results=100):
    try:
        likes = list(client.user_activity(username=username, max=max_results, type="likes"))
        if likes:
            df = pd.DataFrame(likes)
            st.dataframe(df) 
            # ... add pagination if needed
        else:
            st.error("No likes found for this user.")
    except GettrApiError as e:
        st.error(f"Failed to fetch user likes: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

def get_user_followers(username, max_results=100):
    try:
        followers = list(client.user_relationships(username=username, type="followers", max=max_results))
        return pd.DataFrame(followers)
    except GettrApiError as e:
        st.error(f"Failed to fetch user followers: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

def get_user_following(username, max_results=100):
    try:
        following = list(client.user_relationships(username=username, type="following", max=max_results))
        return pd.DataFrame(following)
    except GettrApiError as e:
        st.error(f"Failed to fetch users the user is following: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

# --- Functions for Analysis ---

def display_posts_with_sentiment(keyword, max_results=100):
    try:
        posts = list(client.search(query=keyword, max=max_results))
        if posts:
            df = pd.DataFrame(posts)
            analyzer = SentimentIntensityAnalyzer()
            df['sentiment_compound'] = df['text'].apply(lambda text: analyzer.polarity_scores(text)['compound'])
            st.dataframe(df)
        else:
            st.error("No posts found.")
    except Exception as e:
        st.error(f"Failed to analyze sentiment: {str(e)}")

# --- Streamlit App Layout ---

st.title("GETTR OSINT Tool")

# User Search and Analysis Section
st.header("User Search and Analysis")
user_to_search = st.text_input("Enter username to search", key="user_search")
if st.button("Search User", key="search_user_btn"):
    display_user_info(user_to_search)

# Content Retrieval Section
st.header("Content Retrieval")
keyword_to_search = st.text_input("Enter keyword or hashtag to search", key="keyword_search")
max_results = st.slider("Max results", min_value=10, max_value=500, value=100, key="max_results_slider")
if st.button("Search Posts", key="search_posts_btn"):
    display_posts_by_keyword(keyword_to_search, max_results)

# User Posts Section
st.header("User Posts")
user_for_posts = st.text_input("Enter username to get posts")
if st.button("Get User Activities"):
    display_user_posts(user_for_posts)
    display_user_comments(user_for_posts)
    display_user_likes(user_for_posts) 

# Sentiment Analysis Section
st.header("Sentiment Analysis")
keyword_for_sentiment = st.text_input("Enter keyword or hashtag for sentiment", key="keyword_sentiment")
if st.button("Analyze Sentiment", key="sentiment_btn"):
    display_posts_with_sentiment(keyword_for_sentiment)

st.header("User Network")
user_for_network = st.text_input("Enter username to analyze network")

if st.button("Get Followers"):
    followers_df = get_user_followers(user_for_network)
    st.dataframe(followers_df)

if st.button("Get Following"):
    following_df = get_user_following(user_for_network)
    st.dataframe(following_df)

    
