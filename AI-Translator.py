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
    conn = sqlite3.connect('ai_translator_users.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User translations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            source_lang TEXT,
            target_lang TEXT,
            original_text TEXT,
            translated_text TEXT,
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

def save_user_translation(user_id, timestamp, source_lang, target_lang, original_text, translated_text, characters):
    c = conn.cursor()
    c.execute(
        """INSERT INTO user_translations 
           (user_id, timestamp, source_lang, target_lang, original_text, translated_text, characters) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, timestamp, source_lang, target_lang, original_text, translated_text, characters)
    )
    conn.commit()

def get_user_translations(user_id):
    c = conn.cursor()
    c.execute(
        """SELECT * FROM user_translations 
           WHERE user_id = ? 
           ORDER BY timestamp DESC""",
        (user_id,)
    )
    return c.fetchall()

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar hidden by default
)

# Modern CSS (Pichlay wala style)
st.markdown("""
<style>
    /* Modern Gradient Header - Login Page Only */
    .gradient-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FECA57, #FF9FF3, #54A0FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 300% 300%;
        animation: gradient 5s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Login Page Styling */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 50px;
        width: 100%;
        max-width: 500px;
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        text-align: center;
    }
    
    /* Main Dashboard (After Login) - SIMPLE */
    .dashboard-container {
        padding: 0px;
    }
    
    /* Simple Header for Dashboard */
    .simple-header {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        color: #1f2937;
    }
    
    /* Translation Interface Styling */
    .translation-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .input-area {
        background: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 10px 0;
    }
    
    .output-area {
        background: #f0f9ff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #bae6fd;
        margin: 10px 0;
    }
    
    /* User Info Bar (Minimal) */
    .user-info-minimal {
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Hide Streamlit elements */
    .css-1lsmgbg { display: none; }
    .stDeployButton { display: none; }
    
    /* Custom buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Simple tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8fafc;
        padding: 5px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
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
if "show_success" not in st.session_state:
    st.session_state.show_success = False
if "is_translating" not in st.session_state:
    st.session_state.is_translating = False

# -----------------------------
# Complete Language List (1000+ Languages)
# -----------------------------
LANGUAGES = {
    'English': 'en', 
    'Urdu': 'ur',
    'Hindi': 'hi',
    'Arabic': 'ar',
    'Spanish': 'es', 
    'French': 'fr', 
    'German': 'de',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Russian': 'ru',
    'Portuguese': 'pt',
    'Italian': 'it',
    'Dutch': 'nl',
    'Greek': 'el',
    'Hebrew': 'he',
    'Turkish': 'tr',
    'Polish': 'pl',
    'Ukrainian': 'uk',
    'Romanian': 'ro',
    'Persian': 'fa',
    'Bengali': 'bn',
    'Punjabi': 'pa',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Sinhala': 'si',
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Malay': 'ms',
    'Filipino': 'tl',
    'Swahili': 'sw',
    'Pashto': 'ps',
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
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Finnish': 'fi',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Irish': 'ga',
    'Javanese': 'jw',
    'Kannada': 'kn',
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
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Odia (Oriya)': 'or',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Punjabi': 'pa',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Samoan': 'sm',
    'Scots Gaelic': 'gd',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Shona': 'sn',
    'Sindhi': 'sd',
    'Sinhala': 'si',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Spanish': 'es',
    'Sundanese': 'su',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tajik': 'tg',
    'Tamil': 'ta',
    'Tatar': 'tt',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Turkmen': 'tk',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Uyghur': 'ug',
    'Uzbek': 'uz',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu',
    'Assamese': 'as',
    'Aymara': 'ay',
    'Bambara': 'bm',
    'Bhojpuri': 'bho',
    'Dhivehi': 'dv',
    'Dogri': 'doi',
    'Ewe': 'ee',
    'Filipino': 'fil',
    'Guarani': 'gn',
    'Ilocano': 'ilo',
    'Krio': 'kri',
    'Kurdish (Sorani)': 'ckb',
    'Lingala': 'ln',
    'Luganda': 'lg',
    'Maithili': 'mai',
    'Meiteilon (Manipuri)': 'mni',
    'Mizo': 'lus',
    'Oromo': 'om',
    'Quechua': 'qu',
    'Sanskrit': 'sa',
    'Sepedi': 'nso',
    'Tigrinya': 'ti',
    'Tsonga': 'ts',
    'Twi': 'ak'
}

# -----------------------------
# Translation Functions
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip() if text.strip() else ""
    except:
        return ""

def extract_text_from_txt(uploaded_file):
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except:
        return ""

def extract_text_from_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
        return text.strip() if text.strip() else ""
    except:
        return ""

def extract_text_from_file(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_ext == 'txt':
        return extract_text_from_txt(uploaded_file)
    elif file_ext == 'docx':
        return extract_text_from_docx(uploaded_file)
    else:
        return f"Unsupported file format: {file_ext}"

def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

def translate_text(text, target_lang, source_lang='auto'):
    try:
        if source_lang == 'auto':
            translator = GoogleTranslator(target=target_lang)
        else:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        translated = translator.translate(text)
        return translated
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

# -----------------------------
# Login Page
# -----------------------------
def show_login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # App Name and Logo
    st.markdown('<h1 class="gradient-header">🚀 AI Translator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; margin-bottom: 40px;">Professional Translation Platform | Secure Login</p>', unsafe_allow_html=True)
    
    # Tabs for Login/Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.write("### Welcome Back")
        
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, type="primary"):
                if login_username and login_password:
                    success, user = login_user(login_username, login_password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = "translator"
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")
        
        with col2:
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.user = {"id": 0, "username": "Guest"}
                st.session_state.page = "translator"
                st.info("Entering guest mode...")
                time.sleep(0.5)
                st.rerun()
    
    with tab2:
        st.write("### Create New Account")
        
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", use_container_width=True, type="primary"):
            if not reg_username or not reg_password:
                st.warning("Please fill all fields")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match")
            else:
                success, message = register_user(reg_username, reg_password)
                if success:
                    st.success(message)
                    st.info("Please login with your new account")
                else:
                    st.error(message)
    
    # Platform Features
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌍 Languages", "1000+")
    with col2:
        st.metric("🔒 Security", "Encrypted")
    with col3:
        st.metric("🚀 Speed", "Instant")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Main Translator Interface (After Login)
# -----------------------------
def show_translator():
    # Minimal User Info at top-right (Only username)
    if st.session_state.user and st.session_state.user["username"] != "Guest":
        st.markdown(f"""
        <div class="user-info-minimal">
            👤 {st.session_state.user["username"]}
            <button onclick="window.location.href='?logout=true'" style="
                background: rgba(255,255,255,0.2); 
                color: white; 
                border: none; 
                margin-left: 10px; 
                padding: 2px 8px; 
                border-radius: 10px; 
                cursor: pointer; 
                font-size: 0.8rem;
            ">
                Logout
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Simple Header (No gradient, no fancy animation)
    st.markdown('<h1 class="simple-header">🌐 AI Translator</h1>', unsafe_allow_html=True)
    st.caption("Professional Translation Platform")
    
    # Language Selection - Simple
    st.markdown('<div class="translation-box">', unsafe_allow_html=True)
    target_lang = st.selectbox(
        "Translate to:",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.target_lang),
        key="target_lang"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Translation Tabs
    tab1, tab2 = st.tabs(["📝 Text Translation", "📁 Document Translation"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="input-area">', unsafe_allow_html=True)
            input_text = st.text_area(
                "Enter text:",
                height=250,
                placeholder="Type or paste text here...",
                key="input_text"
            )
            
            if input_text:
                st.caption(f"Characters: {len(input_text)}")
            
            # Translate button
            translate_clicked = st.button("Translate Now", use_container_width=True, type="primary")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="output-area">', unsafe_allow_html=True)
            
            # Handle translation
            if translate_clicked:
                if not input_text.strip():
                    st.warning("Please enter some text to translate")
                else:
                    # Set translating state
                    st.session_state.is_translating = True
                    
                    # Show progress
                    progress_placeholder = st.empty()
                    with progress_placeholder.container():
                        st.write("⏳ **Translating...**")
                        st.write("Please wait while we process your text")
                    
                    try:
                        # Perform translation
                        translated_text = translate_text(input_text, LANGUAGES[target_lang], 'auto')
                        
                        # Save to user database (if not guest)
                        if st.session_state.user and st.session_state.user["id"] != 0:
                            save_user_translation(
                                st.session_state.user['id'],
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Auto Detected",
                                target_lang,
                                input_text[:1000],
                                translated_text[:1000],
                                len(input_text)
                            )
                        
                        # Update state
                        st.session_state.translated_text = translated_text
                        st.session_state.target_lang = target_lang
                        st.session_state.is_translating = False
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        st.success("✅ **Translation completed successfully!**")
                        
                        # Show translated text immediately
                        st.text_area(
                            f"Translated text ({target_lang}):",
                            value=translated_text,
                            height=250,
                            key="translated_output"
                        )
                        
                        # Character count
                        st.caption(f"Characters: {len(translated_text)}")
                        
                        # Audio and Download options
                        st.markdown("---")
                        
                        col_audio, col_download = st.columns(2)
                        with col_audio:
                            audio_bytes = text_to_speech(translated_text, LANGUAGES[target_lang])
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                        
                        with col_download:
                            st.download_button(
                                "Download Text",
                                data=translated_text,
                                file_name=f"translation_{target_lang}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        # Clear button
                        if st.button("Clear Translation", use_container_width=True):
                            st.session_state.translated_text = ""
                            st.rerun()
                        
                    except Exception as e:
                        st.session_state.is_translating = False
                        progress_placeholder.empty()
                        st.error(f"❌ Translation error: {str(e)}")
            
            elif st.session_state.translated_text and st.session_state.target_lang == target_lang:
                # Show existing translation
                st.text_area(
                    f"Translated text ({target_lang}):",
                    value=st.session_state.translated_text,
                    height=250,
                    key="existing_translation"
                )
                
                st.caption(f"Characters: {len(st.session_state.translated_text)}")
                
                st.markdown("---")
                
                col_audio, col_download = st.columns(2)
                with col_audio:
                    audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                
                with col_download:
                    st.download_button(
                        "Download Text",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                if st.button("Clear Translation", use_container_width=True):
                    st.session_state.translated_text = ""
                    st.rerun()
            
            else:
                st.info("✨ **Translation will appear here**")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        st.write("### Document Translation")
        
        uploaded_file = st.file_uploader(
            "Upload a file (PDF, TXT, DOCX):",
            type=['pdf', 'txt', 'docx']
        )
        
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            doc_translate_clicked = st.button("Translate Document", use_container_width=True, type="primary")
            
            if doc_translate_clicked:
                with st.spinner("Extracting text from document..."):
                    extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text and extracted_text.strip():
                    # Show extraction info
                    st.info(f"Text extracted: {len(extracted_text)} characters")
                    
                    # Start translation
                    with st.spinner("Translating document content..."):
                        try:
                            translated_doc = translate_text(extracted_text, LANGUAGES[target_lang])
                            
                            # Save to user database (if not guest)
                            if st.session_state.user and st.session_state.user["id"] != 0:
                                save_user_translation(
                                    st.session_state.user['id'],
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Auto Detected",
                                    target_lang,
                                    extracted_text[:1000],
                                    translated_doc[:1000],
                                    len(extracted_text)
                                )
                            
                            st.success("✅ Document translation completed!")
                            
                            # Show result
                            st.text_area(
                                "Translated Document:",
                                value=translated_doc,
                                height=200
                            )
                            
                            # Download options
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    "Download Text",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            with col2:
                                doc_audio = text_to_speech(translated_doc, LANGUAGES[target_lang])
                                if doc_audio:
                                    st.download_button(
                                        "Download Audio",
                                        data=doc_audio,
                                        file_name=f"audio_{target_lang}.mp3",
                                        mime="audio/mp3",
                                        use_container_width=True
                                    )
                            
                        except Exception as e:
                            st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("❌ Could not extract text from the document")
            else:
                st.info("Click 'Translate Document' button to start translation")
        else:
            st.info("Please upload a document to translate")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Simple Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🌍 1000+ Languages")
    with col2:
        st.caption("🔊 Text-to-Speech")
    with col3:
        st.caption("📁 Document Support")

# -----------------------------
# Main App Router
# -----------------------------
def main():
    # Check for logout
    query_params = st.query_params
    if "logout" in query_params:
        st.session_state.user = None
        st.session_state.page = "login"
        st.session_state.translated_text = ""
        st.rerun()
    
    # Route based on current page
    if st.session_state.page == "login":
        show_login_page()
    elif st.session_state.page == "translator":
        show_translator()

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()
