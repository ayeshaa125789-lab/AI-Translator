import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import json
from datetime import datetime
from io import BytesIO
import PyPDF2
import pdfplumber
from docx import Document
import tempfile
import hashlib
import sqlite3
import time

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('translator_app.db', check_same_thread=False)
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
        CREATE TABLE IF NOT EXISTS user_translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            source_text TEXT,
            translated_text TEXT,
            source_lang TEXT,
            target_lang TEXT,
            characters INTEGER,
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
        c.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username, password):
    c = conn.cursor()
    password_hash = hash_password(password)
    
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    user = c.fetchone()
    
    if user:
        return True, {"id": user[0], "username": user[1]}
    return False, None

def save_translation(user_id, source_text, translated_text, source_lang, target_lang, characters):
    c = conn.cursor()
    c.execute(
        """INSERT INTO user_translations 
           (user_id, timestamp, source_text, translated_text, source_lang, target_lang, characters) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), source_text[:500], 
         translated_text[:500], source_lang, target_lang, characters)
    )
    conn.commit()

def get_user_translations(user_id, limit=50):
    c = conn.cursor()
    c.execute(
        """SELECT * FROM user_translations 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    )
    return c.fetchall()

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple CSS - NO HIGHLIGHTING
st.markdown("""
<style>
    /* Hide Streamlit elements */
    .css-1lsmgbg { display: none; }
    .stDeployButton { display: none; }
    
    /* Simple container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Simple header */
    .app-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Simple card */
    .card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }
    
    /* Simple button */
    .stButton > button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #4338ca;
    }
    
    /* Simple tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8fafc;
        padding: 5px;
        border-radius: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    /* Login card */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    .login-box {
        background: white;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
    }
    
    /* Dashboard layout */
    .dashboard {
        display: flex;
        height: 100vh;
    }
    
    .sidebar {
        width: 250px;
        background: #f8fafc;
        border-right: 1px solid #e5e7eb;
        padding: 20px;
    }
    
    .main-content {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
    }
    
    /* User info - simple */
    .user-display {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 20px;
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
if "view" not in st.session_state:
    st.session_state.view = "translate"

# -----------------------------
# Complete Languages (Including Pashto and more)
# -----------------------------
LANGUAGES = {
    'English': 'en',
    'Urdu': 'ur',
    'Hindi': 'hi',
    'Arabic': 'ar',
    'Pashto': 'ps',  # Added Pashto
    'Persian': 'fa',
    'Turkish': 'tr',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Chinese': 'zh-CN',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Bengali': 'bn',
    'Punjabi': 'pa',
    'Marathi': 'mr',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Sinhala': 'si',
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Malay': 'ms',
    'Filipino': 'tl',
    'Swahili': 'sw',
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chichewa': 'ny',
    'Corsican': 'co',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Finnish': 'fi',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'Greek': 'el',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hebrew': 'he',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Irish': 'ga',
    'Javanese': 'jw',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Kinyarwanda': 'rw',
    'Kurdish (Kurmanji)': 'ku',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latin': 'la',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Luxembourgish': 'lb',
    'Macedonian': 'mk',
    'Malagasy': 'mg',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Odia (Oriya)': 'or',
    'Polish': 'pl',
    'Romanian': 'ro',
    'Samoan': 'sm',
    'Scots Gaelic': 'gd',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Shona': 'sn',
    'Sindhi': 'sd',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Sundanese': 'su',
    'Swedish': 'sv',
    'Tajik': 'tg',
    'Tatar': 'tt',
    'Turkmen': 'tk',
    'Ukrainian': 'uk',
    'Uyghur': 'ug',
    'Uzbek': 'uz',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu'
}

# -----------------------------
# Translation Functions
# -----------------------------
def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return f"Error: {str(e)}"

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
            return "\n".join([p.text for p in doc.paragraphs])
        return ""
    except:
        return ""

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    st.markdown('<div class="app-header">🌐 AI Translator</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                if username and password:
                    success, user = login_user(username, password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.success("Login successful")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Enter username and password")
        
        with col2:
            if st.button("Guest", use_container_width=True):
                st.session_state.user = {"id": 0, "username": "Guest"}
                st.session_state.page = "dashboard"
                st.rerun()
    
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        if st.button("Create Account", use_container_width=True):
            if not new_user or not new_pass:
                st.warning("Enter all fields")
            elif new_pass != confirm_pass:
                st.error("Passwords don't match")
            else:
                success, msg = register_user(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Dashboard Sidebar
# -----------------------------
def sidebar():
    with st.sidebar:
        # Simple user display - NO HIGHLIGHT
        if st.session_state.user:
            st.write(f"**User:** {st.session_state.user['username']}")
        
        st.markdown("---")
        
        # Navigation - Simple
        if st.button("🏠 Translate", use_container_width=True):
            st.session_state.view = "translate"
            st.rerun()
        
        if st.button("📚 History", use_container_width=True):
            st.session_state.view = "history"
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.view = "settings"
            st.rerun()
        
        st.markdown("---")
        
        # Logout button - Simple
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "login"
            st.session_state.translated_text = ""
            st.rerun()

# -----------------------------
# Translate View
# -----------------------------
def translate_view():
    st.markdown('<div class="app-header">🌐 Translate</div>', unsafe_allow_html=True)
    
    # Language selection
    col1, col2 = st.columns([3, 1])
    with col1:
        target_lang = st.selectbox(
            "Translate to:",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.target_lang),
            key="target_lang_select"
        )
        st.session_state.target_lang = target_lang
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.translated_text = ""
            st.rerun()
    
    # Translation interface
    tab1, tab2 = st.tabs(["Text", "Document"])
    
    with tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            input_text = st.text_area(
                "Enter text:",
                height=250,
                placeholder="Type or paste here..."
            )
            
            if st.button("Translate", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("Translating..."):
                        translated = translate_text(input_text, LANGUAGES[target_lang])
                        
                        # Save if logged in user
                        if st.session_state.user and st.session_state.user["id"] != 0:
                            save_translation(
                                st.session_state.user["id"],
                                input_text,
                                translated,
                                "auto",
                                target_lang,
                                len(input_text)
                            )
                        
                        st.session_state.translated_text = translated
                        st.success("Translation complete")
                        st.rerun()
                else:
                    st.warning("Enter text first")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.session_state.translated_text:
                st.text_area(
                    f"Translated ({target_lang}):",
                    value=st.session_state.translated_text,
                    height=250
                )
                
                # Actions
                col_a, col_b = st.columns(2)
                with col_a:
                    audio = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio:
                        st.audio(audio, format="audio/mp3")
                
                with col_b:
                    st.download_button(
                        "Download",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.info("Translation will appear here")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("**Document Translation**")
        
        uploaded_file = st.file_uploader(
            "Upload file (PDF, TXT, DOCX):",
            type=['pdf', 'txt', 'docx']
        )
        
        if uploaded_file:
            with st.spinner("Reading file..."):
                doc_text = extract_text(uploaded_file)
            
            if doc_text:
                st.info(f"Text extracted: {len(doc_text)} characters")
                
                if st.button("Translate Document", use_container_width=True, type="primary"):
                    with st.spinner("Translating..."):
                        doc_translated = translate_text(doc_text, LANGUAGES[target_lang])
                        
                        st.success("Document translated")
                        
                        st.text_area(
                            "Translated Document:",
                            value=doc_translated,
                            height=200
                        )
                        
                        st.download_button(
                            "Download Translation",
                            data=doc_translated,
                            file_name=f"translated_{uploaded_file.name}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            else:
                st.error("Could not read file")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# History View
# -----------------------------
def history_view():
    st.markdown('<div class="app-header">📚 Translation History</div>', unsafe_allow_html=True)
    
    if st.session_state.user and st.session_state.user["id"] != 0:
        translations = get_user_translations(st.session_state.user["id"])
        
        if translations:
            for trans in translations:
                with st.expander(f"{trans[2]} | {trans[6]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Original:**")
                        st.write(trans[3])
                    with col2:
                        st.write("**Translated:**")
                        st.write(trans[4])
                    
                    if st.button("Use This", key=f"use_{trans[0]}"):
                        st.session_state.translated_text = trans[4]
                        st.session_state.target_lang = trans[6]
                        st.session_state.view = "translate"
                        st.rerun()
        else:
            st.info("No translation history")
    else:
        st.info("Guest mode - History not saved")

# -----------------------------
# Settings View
# -----------------------------
def settings_view():
    st.markdown('<div class="app-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("**Account Information**")
    
    if st.session_state.user:
        st.write(f"Username: {st.session_state.user['username']}")
        
        if st.session_state.user["id"] != 0:
            st.write("Account Type: Registered User")
        else:
            st.write("Account Type: Guest")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("**Clear Data**")
    
    if st.button("Clear All History", use_container_width=True):
        if st.session_state.user and st.session_state.user["id"] != 0:
            c = conn.cursor()
            c.execute("DELETE FROM user_translations WHERE user_id = ?", 
                     (st.session_state.user["id"],))
            conn.commit()
            st.success("History cleared")
            st.rerun()
        else:
            st.info("Guest history not saved")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Dashboard Main
# -----------------------------
def dashboard():
    # Dashboard layout
    col1, col2 = st.columns([1, 4])
    
    with col1:
        sidebar()
    
    with col2:
        if st.session_state.view == "translate":
            translate_view()
        elif st.session_state.view == "history":
            history_view()
        elif st.session_state.view == "settings":
            settings_view()

# -----------------------------
# Main App
# -----------------------------
def main():
    # Route pages
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "dashboard":
        dashboard()

if __name__ == "__main__":
    main()
