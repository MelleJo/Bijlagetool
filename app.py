import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import sys
import secrets

# Set page config (must be the first Streamlit command)
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

def authenticate_google_drive():
    if 'credentials' in st.session_state:
        creds = st.session_state['credentials']
    else:
        # Ensure the client secrets file is correctly referenced
        client_secrets_path = os.path.join(os.getcwd(), 'client_secrets.json')
        if not os.path.exists(client_secrets_path):
            st.error("Client secrets file not found. Please upload or check the file path.")
            return None

        flow = Flow.from_client_secrets_file(
            client_secrets_path,
            scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
            redirect_uri='https://bijlagetool.streamlit.app/'
        )

        auth_url, state = flow.authorization_url(prompt='consent')

        st.session_state['state'] = state

        st.markdown(f"[Authorize]({auth_url})")

        query_params = st.query_params
        if 'code' in query_params:
            code = query_params['code'][0]
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state['credentials'] = creds

    return build('drive', 'v3', credentials=creds)



def handle_google_auth():
    try:
        client_config = st.secrets["client_secrets"]["web"]
        flow = Flow.from_client_config(
            {"web": client_config},
            scopes=['https://www.googleapis.com/auth/drive.file'],
            redirect_uri="https://bijlagetool.streamlit.app/"
        )
        
        query_params = st.query_params
        code = query_params.get("code", [None])[0]
        state = query_params.get("state", [None])[0]
        stored_state = st.session_state.get('state')

        if code is None:
            st.error("No authorization code found in the URL parameters.")
            return

        if state is None or state != stored_state:
            st.error("Invalid state parameter. Please try authenticating again.")
            st.set_query_params()  # Clear query params
            return

        flow.fetch_token(code=code)
        creds = flow.credentials

        st.session_state['credentials'] = creds
        st.success("Successfully authenticated!")
        st.set_query_params()  # Clear query params
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred during authentication: {str(e)}")
        st.write("Error type:", type(e).__name__)
        import traceback
        st.write("Traceback:", traceback.format_exc())
        st.write("Query parameters:", st.query_params)
        st.write("Session state keys:", list(st.session_state.keys()))


def download_file(drive_service, file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def main():
    st.title("Bijlagetool")

    if st.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.set_query_params()
        st.success("Session state cleared. Please refresh the page.")

    # Ensure secrets are accessed properly
    try:
        client_secrets = st.secrets["client_secrets"]
        st.write("Full client config:", client_secrets)
    except Exception as e:
        st.error(f"Error accessing client secrets: {e}")

    query_params = st.query_params

    if 'state' in st.session_state and st.session_state['state'] != query_params.get('state', [None])[0]:
        st.error("Invalid state parameter. Please try authenticating again.")
        return

    if "code" in query_params and "state" in query_params:
        handle_google_auth()
    elif 'credentials' not in st.session_state:
        drive_service = authenticate_google_drive()
        if not drive_service:
            return  # Exit the function if there's an issue with authentication
    else:
        drive_service = st.session_state['credentials']

    if drive_service:
        st.success("Successfully authenticated!")

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
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "#ff4b4b"},
                },
            )

        # Main content
        if selected == "Home":
            st.header("Welkom bij de Bijlagetool")
            st.write("Selecteer een optie in het navigatiemenu om te beginnen.")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("👀 Bekijk recente documenten")
            with col2:
                st.info("🔍 Zoek naar documenten")
            with col3:
                st.info("⚙️ Beheer instellingen")

        elif selected == "Zoeken":
            st.header("Zoeken naar Documenten")
            query = st.text_input("Voer een zoekterm in")
            if st.button("Zoek"):
                results = drive_service.files().list(
                    q=f"name contains '{query}'",
                    pageSize=10,
                    fields="files(id, name)"
                ).execute()
                files = results.get('files', [])

                if files:
                    for file in files:
                        st.write(f"Document: {file['name']} (ID: {file['id']})")
                else:
                    st.write("Geen documenten gevonden.")

        elif selected == "Overzicht":
            st.header("Documentenoverzicht")
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

        elif selected == "Instellingen":
            st.header("Instellingen")
            st.write("Hier kunt u de app-instellingen beheren.")

            col1, col2 = st.columns(2)
            with col1:
                dark_mode = st.checkbox("Donkere modus", value=False)
                notifications = st.checkbox("Notificaties", value=True)
            with col2:
                language = st.selectbox("Taal", ["Nederlands", "Engels", "Duits"])
                max_results = st.number_input("Maximaal aantal zoekresultaten", min_value=5, max_value=50, value=10)

            if st.button("Instellingen opslaan"):
                st.session_state.dark_mode = dark_mode
                st.session_state.notifications = notifications
                st.session_state.language = language
                st.session_state.max_results = max_results
                st.success("Instellingen opgeslagen!")

    else:
        st.warning("Please authenticate to use the Bijlagetool.")

    # Footer
    st.markdown("---")
    st.markdown("© 2023 Bijlagetool | Ontwikkeld door Uw Bedrijf")

if __name__ == "__main__":
    main()

