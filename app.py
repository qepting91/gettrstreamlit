import streamlit as st
import pandas as pd
from gogettr import PublicClient, errors
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import bokeh.plotting as bp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral4

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
        posts = list(client.user_activity(username=username, type="posts", max=max_results))
        if posts:
            df = pd.DataFrame(posts)
            st.dataframe(df)
        else:
            st.error("No posts found for this user.")
    except errors.GettrApiError as e:
        st.error(f"Failed to fetch user posts: {str(e)}")

def visualize_user_network(username):
    try:
        followers = list(client.user_relationships(username=username, type="followers", max=100))
        following = list(client.user_relationships(username=username, type="following", max=100))
        
        G = nx.DiGraph()
        G.add_node(username, role='central')
        for follower in followers:
            G.add_node(follower['ousername'], role='follower')
            G.add_edge(follower['ousername'], username)
        for followee in following:
            G.add_node(followee['ousername'], role='following')
            G.add_edge(username, followee['ousername'])
        
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=2500, node_color="lightblue", font_size=10, font_weight="bold")
        plt.title(f"Network of {username}: Followers and Following")
        st.pyplot(plt)
    except errors.GettrApiError as e:
        st.error(f"Failed to visualize user network: {str(e)}")

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
        
def display_posts_with_location(keyword, max_results=100):
    try:
        posts = list(client.search(query=keyword, max=max_results))
        if not posts:
            st.error("No posts found.")
            return

        # Assuming posts have a 'location' field or similar
        # This part of the implementation is highly dependent on the actual structure of the data returned by the API
        locations = [post.get('location', 'Unknown location') for post in posts]
        df = pd.DataFrame(posts)
        df['location'] = locations
        
        # Display the DataFrame
        st.dataframe(df)
        
        # Optional: If you have coordinates, you could also display these posts on a map
        # For simplicity, this step is omitted but could involve using st.map or PyDeck for visualizations
        
    except Exception as e:
        st.error(f"Failed to display posts with location: {str(e)}")


def visualize_network_interactively(username):
    try:
        # Fetch data
        followers = list(client.user_relationships(username=username, type="followers", max=100))
        following = list(client.user_relationships(username=username, type="following", max=100))
        
        # Assuming the usage of NetworkX to create and manipulate the network graph
        G = nx.DiGraph()
        # Add nodes and edges as previously shown
        
        # Convert the graph into a format compatible with Bokeh for visualization
        # This involves creating data sources for nodes and edges, setting up the figure, and adding glyphs
        
        plot = figure(title=f"Interactive Network of {username}", x_range=(-1.1,1.1), y_range=(-1.1,1.1))
        
        # Add hover tool
        hover = HoverTool(tooltips=[("Username", "@username"), ("Role", "@role")])
        plot.add_tools(hover)
        
        # Add network graph rendering here
        # Example: plot.line('x0', 'y0', 'x1', 'y1', source=edge_source, line_width=1, color="navy")
        
        st.bokeh_chart(plot)
        
    except Exception as e:
        st.error(f"Failed to visualize network interactively: {str(e)}")

def perform_topic_modeling(keyword, num_topics=5):
    try:
        posts = list(client.search(query=keyword, max=100))
        texts = [post['text'] for post in posts if 'text' in post]

        # Preprocess texts if necessary (e.g., removing stopwords, tokenization)
        
        # Vectorize the text data
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        dtm = vectorizer.fit_transform(texts)
        
        # Fit the LDA model
        lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=0)
        lda_model.fit(dtm)
        
        # Display topics
        for index, topic in enumerate(lda_model.components_):
            st.write(f"Topic #{index}")
            st.write([vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]])
            
    except Exception as e:
        st.error(f"Failed to perform topic modeling: {str(e)}")
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
user_for_posts = st.text_input("Enter username to get posts", key="user_posts")
if st.button("Get User Posts", key="get_user_posts_btn"):
    display_user_posts(user_for_posts, max_results)

# Sentiment Analysis Section
st.header("Sentiment Analysis")
keyword_for_sentiment = st.text_input("Enter keyword or hashtag for sentiment", key="keyword_sentiment")
if st.button("Analyze Sentiment", key="sentiment_btn"):
    display_posts_with_sentiment(keyword_for_sentiment)

# Advanced Network Analysis
st.header("Advanced Network Analysis")
user_for_network = st.text_input("Enter username to visualize network (Advanced)", key="network_user")
if st.button("Visualize Network (Interactive)", key="visualize_network_btn"):
    visualize_network_interactively(user_for_network)

# Trend Analysis
st.header("Trend Analysis")
keyword_for_trend = st.text_input("Enter keyword or hashtag for trend analysis", key="keyword_trend")
if st.button("Perform Topic Modeling", key="topic_modeling_btn"):
    perform_topic_modeling(keyword_for_trend)
    
# Geospatial Analysis (Example)
st.header("Geospatial Analysis")
keyword_for_location = st.text_input("Enter keyword or hashtag for location analysis", key="keyword_location")
if st.button("Analyze Posts with Location", key="location_analysis"):
    display_posts_with_location(keyword_for_location)