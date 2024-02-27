import streamlit as st
from gogettr import PublicClient
import pandas as pd

# Initialize GoGettr PublicClient
client = PublicClient()

def fetch_and_display_data(fetch_function, **kwargs):
    data = fetch_function(**kwargs)
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)  # Display the data in a dataframe
        search_query = st.text_input('Search within results:')
        if search_query:
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            st.dataframe(filtered_df)  # Display the filtered dataframe
    else:
        st.write("No data found.")

st.title('GoGettr Data Explorer')

options = ['Pull Posts', 'Pull Comments', 'Trending Hashtags', 'Suggested Users', 'Trending Posts',
           'User Posts', 'User Comments', 'User Likes', 'User Profile Info', 'User Followers', 'Users Followed',
           'Comments on a Post']
choice = st.selectbox('Choose an action:', options)

if choice == 'Pull Posts':
    max_posts = st.number_input('Max posts to pull', min_value=1, value=100)
    fetch_and_display_data(client.all, max=max_posts, type='posts')

elif choice == 'Pull Comments':
    post_id = st.text_input('Enter Post ID:')
    if post_id:
        max_comments = st.number_input('Max comments to pull', min_value=1, value=100)
        fetch_and_display_data(client.comments, post_id=post_id, max=max_comments)

elif choice == 'Trending Hashtags':
    fetch_and_display_data(client.hashtags, max=100)

elif choice == 'Suggested Users':
    fetch_and_display_data(client.suggested, max=100)

elif choice == 'Trending Posts':
    fetch_and_display_data(client.trends, max=100)

elif choice in ['User Posts', 'User Comments', 'User Likes']:
    username = st.text_input('Enter Username:')
    if username:
        type_map = {'User Posts': 'posts', 'User Comments': 'comments', 'User Likes': 'likes'}
        max_items = st.number_input('Max items to pull', min_value=1, value=100)
        fetch_and_display_data(client.user_activity, username=username, type=type_map[choice], max=max_items)

elif choice == 'User Profile Info':
    username = st.text_input('Enter Username:')
    if username:
        fetch_and_display_data(client.user_info, username=username)

elif choice == 'User Followers':
    username = st.text_input('Enter Username:')
    if username:
        fetch_and_display_data(client.user_followers, username=username, max=100)

elif choice == 'Users Followed':
    username = st.text_input('Enter Username:')
    if username:
        fetch_and_display_data(client.user_following, username=username, max=100)

elif choice == 'Comments on a Post':
    post_id = st.text_input('Enter Post ID for Comments:')
    if post_id:
        fetch_and_display_data(client.comments, post_id=post_id, max=100)
