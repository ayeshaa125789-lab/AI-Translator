import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import pdfplumber
from docx import Document
import hashlib
import sqlite3
import time
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('ai_translator_simple.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            source_text TEXT,
            translated_text TEXT,
            target_lang TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

conn = init_db()

# -----------------------------
# User Functions
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username exists"
    except:
        return False, "Error"

def login_user(username, password):
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = c.fetchone()
    if user:
        return True, {"id": user[0], "username": user[1]}
    return False, None

def save_translation(user_id, source_text, translated_text, target_lang):
    c = conn.cursor()
    c.execute(
        "INSERT INTO translations (user_id, timestamp, source_text, translated_text, target_lang) VALUES (?, ?, ?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), source_text[:500], translated_text[:500], target_lang)
    )
    conn.commit()

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS - NO HIGHLIGHT, NO DASHBOARD
st.markdown("""
<style>
    .css-1lsmgbg { display: none; }
    .stDeployButton { display: none; }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .translation-box {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin: 10px 0;
    }
    
    .stButton > button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
    }
    
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 30px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

# -----------------------------
# Languages
# -----------------------------
LANGUAGES = {
    'English': 'en', 'Urdu': 'ur', 'Hindi': 'hi', 'Arabic': 'ar',
    'Pashto': 'ps', 'Persian': 'fa', 'Turkish': 'tr', 'Spanish': 'es',
    'French': 'fr', 'German': 'de', 'Chinese': 'zh-CN', 'Russian': 'ru',
    'Portuguese': 'pt', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko',
    'Bengali': 'bn', 'Punjabi': 'pa'
}

# -----------------------------
# Translation Functions
# -----------------------------
def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(target=target_lang)
        return translator.translate(text)
    except:
        return "Translation error"

def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except:
        return None

def extract_text(file):
    try:
        if file.name.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                return " ".join([page.extract_text() or "" for page in pdf.pages[:3]])
        elif file.name.endswith('.txt'):
            return file.read().decode('utf-8')
        elif file.name.endswith('.docx'):
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs[:50]])
        return ""
    except:
        return ""

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    st.write("### AI Translator")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            if username and password:
                success, user = login_user(username, password)
                if success:
                    st.session_state.user = user
                    st.session_state.page = "translator"
                    st.rerun()
                else:
                    st.error("Invalid")
            else:
                st.warning("Enter details")
    
    with col2:
        if st.button("Guest", use_container_width=True):
            st.session_state.user = {"id": 0, "username": "Guest"}
            st.session_state.page = "translator"
            st.rerun()
    
    # Register
    st.markdown("---")
    st.write("New user?")
    new_user = st.text_input("New username", key="new_user")
    new_pass = st.text_input("New password", type="password", key="new_pass")
    
    if st.button("Register", use_container_width=True):
        if new_user and new_pass:
            success, msg = register_user(new_user, new_pass)
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Translator Page (MAIN INTERFACE - NO DASHBOARD)
# -----------------------------
def translator_page():
    # Simple header - NO user info on front
    st.write("## AI Translator")
    
    # Language selection
    target_lang = st.selectbox(
        "Translate to:",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.target_lang)
    )
    
    # Main translation interface
    col1, col2 = st.columns(2)
    
    with col1:
        input_text = st.text_area(
            "Enter text:",
            height=250,
            placeholder="Type or paste here..."
        )
        
        if st.button("Translate", use_container_width=True, type="primary"):
            if input_text.strip():
                with st.spinner("Translating..."):
                    translated = translate_text(input_text, LANGUAGES[target_lang])
                    
                    # Save if registered user
                    if st.session_state.user and st.session_state.user["id"] != 0:
                        save_translation(
                            st.session_state.user["id"],
                            input_text,
                            translated,
                            target_lang
                        )
                    
                    st.session_state.translated_text = translated
                    st.session_state.target_lang = target_lang
                    st.success("Done")
                    st.rerun()
            else:
                st.warning("Enter text")
    
    with col2:
        if st.session_state.translated_text:
            st.text_area(
                f"Translated ({target_lang}):",
                value=st.session_state.translated_text,
                height=250
            )
            
            # Simple actions
            if st.button("Clear", use_container_width=True):
                st.session_state.translated_text = ""
                st.rerun()
            
            # Audio
            audio = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
            if audio:
                st.audio(audio, format="audio/mp3")
            
            # Download
            st.download_button(
                "Download",
                data=st.session_state.translated_text,
                file_name=f"translation_{target_lang}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("Translation appears here")
    
    # Document translation (simple)
    st.markdown("---")
    st.write("**Document Translation**")
    
    uploaded_file = st.file_uploader("Upload file:", type=['pdf', 'txt', 'docx'])
    
    if uploaded_file:
        doc_text = extract_text(uploaded_file)
        if doc_text:
            if st.button("Translate Document", use_container_width=True):
                with st.spinner("Translating document..."):
                    doc_translated = translate_text(doc_text, LANGUAGES[target_lang])
                    
                    st.text_area("Result:", value=doc_translated, height=150)
                    
                    st.download_button(
                        "Download Document",
                        data=doc_translated,
                        file_name=f"translated_{uploaded_file.name}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
    
    # Simple logout at bottom
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = "login"
        st.session_state.translated_text = ""
        st.rerun()

# -----------------------------
# Main App
# -----------------------------
def main():
    # Simple routing
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "translator":
        translator_page()

if __name__ == "__main__":
    main()
