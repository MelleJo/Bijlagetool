import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Set page config
st.set_page_config(page_title="Bijlagetool", page_icon="📎", layout="wide")

# Custom CSS to inject
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
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

elif selected == "Zoeken":
    st.title("Zoek Bijlagen")
    
    search_query = st.text_input("Voer een zoekterm in (bijv. 'autoverzekering asr casco')")
    
    if search_query:
        st.info(f"Zoeken naar: {search_query}")
        # Placeholder for search results
        st.write("Gevonden documenten:")
        documents = [
            {"name": "ASR Autoverzekering - Voorwaarden", "type": "PDF"},
            {"name": "Casco Dekking Overzicht", "type": "DOCX"},
            {"name": "Schadeformulier ASR", "type": "PDF"}
        ]
        for doc in documents:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {doc['name']}")
            with col2:
                st.button(f"Download {doc['type']}", key=doc['name'])

elif selected == "Overzicht":
    st.title("Documentenoverzicht")
    
    # Placeholder data
    data = {
        'Document': ['ASR Polis', 'Allianz Voorwaarden', 'NN Schadeformulier'],
        'Type': ['PDF', 'DOCX', 'PDF'],
        'Laatst gewijzigd': ['2023-07-15', '2023-08-01', '2023-08-10']
    }
    df = pd.DataFrame(data)
    
    st.dataframe(df, use_container_width=True)

elif selected == "Instellingen":
    st.title("Instellingen")
    
    st.write("Hier kunt u de app-instellingen beheren.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.toggle("Donkere modus")
        st.toggle("Notificaties")
    with col2:
        st.selectbox("Taal", ["Nederlands", "Engels", "Duits"])
        st.number_input("Maximaal aantal zoekresultaten", min_value=5, max_value=50, value=10)

# Footer
st.markdown("---")
st.markdown("© 2023 Bijlagetool | Ontwikkeld door Uw Bedrijf")