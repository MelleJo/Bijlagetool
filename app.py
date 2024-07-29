import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Set page config
st.set_page_config(page_title="Bijlagetool", page_icon="📎", layout="wide")

# Custom CSS to inject
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 0;
        margin: 0;
    }
    .st-bw {
        background-color: #f0f2f6;
    }
    .st-eb {
        border-radius: 10px;
    }
    .stButton>button {
        border-radius: 20px;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        padding-top: 2rem;
        padding-left: 0;
        padding-right: 0;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }
    .css-1d391kg {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    selected = option_menu(
        menu_title="Navigatie",
        options=["Home", "Zoeken", "Overzicht", "Instellingen"],
        icons=["house", "search", "list-ul", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

# Main content
if selected == "Home":
    st.title("Welkom bij de Bijlagetool")
    st.write("Selecteer een optie in het navigatiemenu om te beginnen.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("👀 Bekijk recente documenten")
    with col2:
        st.success("🔍 Zoek specifieke bijlagen")
    with col3:
        st.warning("⚙️ Beheer instellingen")

# ... (rest of the code remains the same)

# Footer
st.markdown("---")
st.markdown("© 2023 Bijlagetool | Veldhuis Advies")