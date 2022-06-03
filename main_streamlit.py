"""
LINK: https://share.streamlit.io/sononicola/design-of-concrete-structures/main/main_streamlit.py

This is the main of the Streamlit web app above. The real code is inside 'pages' folder
"""

import streamlit as st

# -- GENERAL PAGE SETUP --
st.set_page_config(
    page_title="Reinforced Concrete design",
    page_icon="👷‍♂️",
    initial_sidebar_state="expanded",
    layout="wide",
)


# -- PAGE CONTENT --
st.title("Home page - Reinforced Concrete design")
st.markdown("Select an app from the menu on the left!")
