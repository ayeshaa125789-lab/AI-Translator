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
import hashlib
import sqlite3
import time

# -----------------------------
# Database Setup for User Management
# -----------------------------
def init_db():
    conn = sqlite3.connect('translator_users.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Translations table (user-specific)
    c.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            source_text TEXT,
            translated_text TEXT,
            source_lang TEXT,
            target_lang TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            characters INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_db()

# -----------------------------
# User Authentication Functions
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=""):
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_user(username, password):
    c = conn.cursor()
    password_hash = hash_password(password)
    
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    user = c.fetchone()
    
    if user:
        return True, user
    return False, None

def save_translation(user_id, source_text, translated_text, source_lang, target_lang, characters):
    c = conn.cursor()
    c.execute(
        """INSERT INTO translations 
           (user_id, source_text, translated_text, source_lang, target_lang, characters) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, source_text, translated_text, source_lang, target_lang, characters)
    )
    conn.commit()

def get_user_translations(user_id, limit=50):
    c = conn.cursor()
    c.execute(
        """SELECT * FROM translations 
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
    page_title="AI Translator Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fast CSS - Minimal
st.markdown("""
<style>
    /* Hide Streamlit elements */
    .css-1lsmgbg { display: none; }
    .stDeployButton { display: none; }
    
    /* Fast loading */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .login-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 50px auto;
    }
    
    .translation-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    /* Fast buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Fast input */
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
    }
    
    /* User info */
    .user-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State Management
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"
if "is_translating" not in st.session_state:
    st.session_state.is_translating = False

# -----------------------------
# Translation Cache for Speed
# -----------------------------
_translation_cache = {}

# -----------------------------
# Complete Language List
# -----------------------------
LANGUAGES = {
    'English': 'en', 'Urdu': 'ur', 'Hindi': 'hi', 'Arabic': 'ar',
    'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Chinese': 'zh-CN',
    'Japanese': 'ja', 'Korean': 'ko', 'Russian': 'ru', 'Portuguese': 'pt',
    'Italian': 'it', 'Turkish': 'tr', 'Persian': 'fa', 'Bengali': 'bn',
    'Punjabi': 'pa', 'Marathi': 'mr', 'Gujarati': 'gu', 'Tamil': 'ta',
    'Telugu': 'te', 'Kannada': 'kn', 'Malayalam': 'ml', 'Thai': 'th',
    'Vietnamese': 'vi', 'Indonesian': 'id', 'Dutch': 'nl', 'Greek': 'el',
    'Hebrew': 'he', 'Polish': 'pl', 'Ukrainian': 'uk', 'Romanian': 'ro'
}

# -----------------------------
# Fast Functions
# -----------------------------
def fast_translate(text, target_lang):
    """Fast translation with caching"""
    cache_key = f"{text[:100]}_{target_lang}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        translator = GoogleTranslator(target=target_lang)
        result = translator.translate(text)
        _translation_cache[cache_key] = result
        return result
    except Exception as e:
        return f"Error: {str(e)[:50]}"

def fast_extract_text(file):
    """Fast text extraction"""
    try:
        if file.name.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                return " ".join([page.extract_text() or "" for page in pdf.pages[:3]])
        elif file.name.endswith('.txt'):
            return file.read().decode('utf-8')[:5000]
        elif file.name.endswith('.docx'):
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs[:50]])
        return ""
    except:
        return ""

def text_to_speech_fast(text, lang_code):
    """Fast audio generation"""
    try:
        tts = gTTS(text=text[:500], lang=lang_code)  # Limit for speed
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

# -----------------------------
# Login/Register Page
# -----------------------------
def show_auth_page():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.write("### Welcome Back")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    success, user = authenticate_user(username, password)
                    if success:
                        st.session_state.user = {"id": user[0], "username": user[1]}
                        st.session_state.page = "translator"
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")
        
        with col2:
            if st.button("Guest Mode", use_container_width=True):
                st.session_state.user = {"id": 0, "username": "Guest"}
                st.session_state.page = "translator"
                st.info("Entering guest mode...")
                time.sleep(0.5)
                st.rerun()
    
    with tab2:
        st.write("### Create Account")
        
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email (optional)", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", use_container_width=True, type="primary"):
            if not new_username or not new_password:
                st.warning("Please fill all required fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = register_user(new_username, new_password, new_email)
                if success:
                    st.success(message)
                    st.info("Please login with your new account")
                else:
                    st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Fast Translator Interface
# -----------------------------
def show_translator():
    # User Info Bar
    if st.session_state.user:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f'<div class="user-info">👤 {st.session_state.user["username"]} | AI Translator Pro</div>', unsafe_allow_html=True)
        with col2:
            if st.button("📊 My History", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()
    
    # Main Translator
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Language Selection
    col1, col2 = st.columns([3, 1])
    with col1:
        target_lang = st.selectbox(
            "Translate to:",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.target_lang),
            key="target_lang"
        )
        st.session_state.target_lang = target_lang
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.translated_text = ""
            st.rerun()
    
    # Fast Tabs
    tab1, tab2 = st.tabs(["📝 Quick Translate", "📁 Document"])
    
    with tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            input_text = st.text_area(
                "Enter text:",
                height=200,
                placeholder="Type or paste here...",
                key="input_text"
            )
            
            translate_now = st.button(
                "🚀 Translate Now", 
                type="primary", 
                use_container_width=True,
                disabled=not input_text.strip()
            )
        
        with col_right:
            # Handle translation
            if translate_now and input_text.strip():
                # Show loading
                with st.spinner("Translating..."):
                    # Fast translation
                    translated = fast_translate(input_text, LANGUAGES[target_lang])
                    
                    # Save to user history
                    if st.session_state.user and st.session_state.user["id"] != 0:  # Not guest
                        save_translation(
                            st.session_state.user["id"],
                            input_text[:1000],
                            translated[:1000],
                            "auto",
                            target_lang,
                            len(input_text)
                        )
                    
                    # Update state
                    st.session_state.translated_text = translated
                    st.success("✅ Translation complete!")
            
            # Display result
            if st.session_state.translated_text:
                st.text_area(
                    f"Translated ({target_lang}):",
                    value=st.session_state.translated_text,
                    height=200,
                    key="output_text"
                )
                
                # Actions
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    audio = text_to_speech_fast(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio:
                        st.audio(audio, format="audio/mp3")
                
                with col_act2:
                    st.download_button(
                        "📥 Download",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.info("Translation will appear here")
    
    with tab2:
        st.write("### Document Translation")
        
        uploaded_file = st.file_uploader(
            "Upload file (PDF, TXT, DOCX):",
            type=['pdf', 'txt', 'docx']
        )
        
        if uploaded_file:
            # Quick extraction
            doc_text = fast_extract_text(uploaded_file)
            
            if doc_text:
                st.info(f"✅ Ready to translate ({len(doc_text)} chars)")
                
                if st.button("🚀 Translate Document", type="primary", use_container_width=True):
                    with st.spinner("Translating document..."):
                        doc_translated = fast_translate(doc_text, LANGUAGES[target_lang])
                        
                        # Save if logged in
                        if st.session_state.user and st.session_state.user["id"] != 0:
                            save_translation(
                                st.session_state.user["id"],
                                doc_text[:500],
                                doc_translated[:500],
                                "auto",
                                target_lang,
                                len(doc_text)
                            )
                        
                        st.success("✅ Document translated!")
                        
                        # Show result
                        st.text_area(
                            "Translated Document:",
                            value=doc_translated,
                            height=150
                        )
                        
                        # Download
                        st.download_button(
                            "📥 Download Document",
                            data=doc_translated,
                            file_name=f"translated_{uploaded_file.name}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            else:
                st.error("Could not read file")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# User History Page
# -----------------------------
def show_history_page():
    st.markdown(f'<div class="user-info">📊 Translation History - {st.session_state.user["username"]}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("← Back to Translator", use_container_width=True):
            st.session_state.page = "translator"
            st.rerun()
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            c = conn.cursor()
            c.execute("DELETE FROM translations WHERE user_id = ?", (st.session_state.user["id"],))
            conn.commit()
            st.success("History cleared!")
            time.sleep(0.5)
            st.rerun()
    
    # Get user translations
    if st.session_state.user["id"] != 0:  # Not guest
        translations = get_user_translations(st.session_state.user["id"])
        
        if translations:
            for trans in translations:
                with st.expander(f"{trans[6]} | {trans[5]} | {trans[7]} chars"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Original:**")
                        st.write(trans[2][:200] + "..." if len(trans[2]) > 200 else trans[2])
                    with col2:
                        st.write(f"**Translated ({trans[5]}):**")
                        st.write(trans[3][:200] + "..." if len(trans[3]) > 200 else trans[3])
                    
                    if st.button("Use This", key=f"use_{trans[0]}"):
                        st.session_state.translated_text = trans[3]
                        st.session_state.target_lang = trans[5]
                        st.session_state.page = "translator"
                        st.rerun()
        else:
            st.info("No translation history found")
    else:
        st.info("Guest mode - History not saved")

# -----------------------------
# Main App Router
# -----------------------------
def main():
    # Route based on current page
    if st.session_state.page == "login":
        show_auth_page()
    elif st.session_state.page == "translator":
        show_translator()
    elif st.session_state.page == "history":
        show_history_page()

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()
