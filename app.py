import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io

# Set page config (must be the first Streamlit command)
st.set_page_config(page_title="Bijlagetool", page_icon="📎", layout="wide")

st.write("Full client config:", st.secrets["client_secrets"])

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

# Google Drive authentication function
def authenticate_google_drive():
    try:
        client_config = st.secrets["client_secrets"]
        st.write("Client config keys:", list(client_config.keys()))

        if 'web' not in client_config:
            raise ValueError("Client secrets must contain a 'web' key")

        web_config = client_config['web']
        st.write("Web config keys:", list(web_config.keys()))
        st.write("Redirect URI:", web_config.get("redirect_uris", ["None"])[0])

        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
            redirect_uri=web_config["redirect_uris"][0]
        )

        if 'credentials' not in st.session_state:
            authorization_url, _ = flow.authorization_url(prompt='consent')
            st.write("Authorization URL:", authorization_url)
            st.markdown(f'[Authenticate with Google Drive]({authorization_url})')
            st.stop()
        else:
            credentials = Credentials(**st.session_state.credentials)
            drive_service = build('drive', 'v3', credentials=credentials)
            return drive_service
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Error type:", type(e).__name__)
        import traceback
        st.write("Traceback:", traceback.format_exc())

    return None

# Callback for Google Drive authentication
def handle_google_auth():
    flow = Flow.from_client_config(
        st.secrets["client_secrets"],
        scopes=['https://www.googleapis.com/auth/drive.readonly'],
        state=st.query_params.get("state", None)
    )
    flow.redirect_uri = 'https://bijlagetool.streamlit.app/'

    flow.fetch_token(code=st.query_params.get("code", None))

    st.session_state.credentials = {
        'token': flow.credentials.token,
        'refresh_token': flow.credentials.refresh_token,
        'token_uri': flow.credentials.token_uri,
        'client_id': flow.credentials.client_id,
        'client_secret': flow.credentials.client_secret,
        'scopes': flow.credentials.scopes
    }

# Check for authentication callback
if 'code' in st.query_params:
    handle_google_auth()
    st.experimental_rerun()

# Authenticate with Google Drive
drive_service = authenticate_google_drive()

# Function to download file
def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

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

elif selected == "Zoeken":
    st.title("Zoek Bijlagen")

    search_query = st.text_input("Voer een zoekterm in (bijv. 'autoverzekering asr casco')")

    if search_query and drive_service:
        st.info(f"Zoeken naar: {search_query}")
        results = drive_service.files().list(
            q=f"name contains '{search_query}'",
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()

        files = results.get('files', [])
        if files:
            for file in files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {file['name']}")
                with col2:
                    file_content = download_file(file['id'], file['name'])
                    st.download_button(
                        label="Download",
                        data=file_content,
                        file_name=file['name'],
                        mime=file['mimeType']
                    )
        else:
            st.write("Geen documenten gevonden.")

elif selected == "Overzicht":
    st.title("Documentenoverzicht")

    if drive_service:
        results = drive_service.files().list(
            pageSize=10,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        files = results.get('files', [])

        if files:
            data = {
                'Document': [file['name'] for file in files],
                'Type': [file['mimeType'] for file in files],
                'Laatst gewijzigd': [file['modifiedTime'] for file in files]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("Geen documenten gevonden.")
    else:
        st.write("Authenticatie vereist om documenten te bekijken.")

elif selected == "Instellingen":
    st.title("Instellingen")

    st.write("Hier kunt u de app-instellingen beheren.")

    col1, col2 = st.columns(2)
    with col1:
        dark_mode = st.toggle("Donkere modus", value=False)
        notifications = st.toggle("Notificaties", value=True)
    with col2:
        language = st.selectbox("Taal", ["Nederlands", "Engels", "Duits"])
        max_results = st.number_input("Maximaal aantal zoekresultaten", min_value=5, max_value=50, value=10)

    if st.button("Instellingen opslaan"):
        st.session_state.dark_mode = dark_mode
        st.session_state.notifications = notifications
        st.session_state.language = language
        st.session_state.max_results = max_results
        st.success("Instellingen opgeslagen!")

# Footer
st.markdown("---")
st.markdown("© 2023 Bijlagetool | Ontwikkeld door Uw Bedrijf") 
