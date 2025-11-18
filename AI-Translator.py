import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os
import json
from datetime import datetime
import re
from io import BytesIO
import base64
import PyPDF2
import pdfplumber
from docx import Document
import tempfile
import hashlib
import pandas as pd

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .feature-box {
        padding: 20px;
        border-radius: 12px;
        background: white;
        border: 1px solid #e0e0e0;
        margin: 10px 0px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .feature-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stats-box {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border-radius: 12px;
        margin: 10px 0px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .category-box {
        padding: 12px;
        border-radius: 8px;
        background: white;
        border-left: 4px solid #2E86AB;
        margin: 6px 0px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
        font-size: 0.9rem;
    }
    .metric-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
    }
    .auth-box {
        padding: 25px;
        border-radius: 12px;
        background: white;
        border: 2px solid #2E86AB;
        margin: 15px 0px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .user-welcome {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0px;
    }
    .progress-bar {
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        margin: 10px 0px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Authentication System
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_data():
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

def save_user_data(username, data):
    st.session_state.user_data[username] = data

def get_user_data(username):
    return st.session_state.user_data.get(username, {
        'translation_history': [],
        'preferences': {},
        'usage_stats': {'translations': 0, 'characters': 0}
    })

# -----------------------------
# Enhanced Language List
# -----------------------------
LANGUAGES = {
    'Auto Detect': 'auto',
    'English': 'en', 
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
    'Arabic': 'ar',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Urdu': 'ur',
    'Dutch': 'nl',
    'Greek': 'el',
    'Hebrew': 'he',
    'Turkish': 'tr',
    'Polish': 'pl',
    'Ukrainian': 'uk',
    'Romanian': 'ro',
    'Czech': 'cs',
    'Swedish': 'sv',
    'Norwegian': 'no',
    'Danish': 'da',
    'Finnish': 'fi',
    'Hungarian': 'hu',
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Malay': 'ms',
    'Filipino': 'tl',
    'Persian': 'fa',
    'Punjabi': 'pa',
    'Marathi': 'mr',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Sinhala': 'si',
    'Nepali': 'ne',
    'Burmese': 'my',
    'Khmer': 'km',
    'Lao': 'lo',
    'Swahili': 'sw',
    'Amharic': 'am',
    'Yoruba': 'yo',
    'Igbo': 'ig',
    'Hausa': 'ha',
    'Zulu': 'zu',
    'Afrikaans': 'af',
}

# -----------------------------
# File Processing Functions
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text.strip()
        
        uploaded_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except:
        uploaded_file.seek(0)
        text = uploaded_file.read().decode('latin-1')
        return text

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

# -----------------------------
# Text-to-Speech Functions
# -----------------------------
def text_to_speech_enhanced(text, lang_code, slow=False):
    """Enhanced text-to-speech for all languages"""
    try:
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        try:
            engine = pyttsx3.init()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            engine.save_to_file(text, temp_file.name)
            engine.runAndWait()
            
            with open(temp_file.name, 'rb') as f:
                audio_bytes = BytesIO(f.read())
            
            os.unlink(temp_file.name)
            return audio_bytes
        except Exception as e2:
            st.error(f"Audio generation failed: {e2}")
            return None

# -----------------------------
# Translation Functions
# -----------------------------
def detect_roman_urdu(text):
    """Detect Roman Urdu text"""
    roman_urdu_words = [
        'tum', 'tu', 'aap', 'wo', 'main', 'hum', 'mera', 'tera', 'hamara', 
        'tumhara', 'uska', 'unka', 'kyun', 'kaise', 'kahan', 'kab', 'kitna',
        'nahi', 'nhi', 'haan', 'ji', 'han', 'jee', 'acha', 'accha', 'theek',
        'sahi', 'galat', 'shukriya', 'meherbani', 'mazeed', 'hai', 'ho',
        'hain', 'tha', 'thi', 'the', 'lekin', 'magar', 'agar', 'kyunki'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    if len(words) == 0:
        return False
        
    roman_word_count = sum(1 for word in words if word in roman_urdu_words)
    return (roman_word_count / len(words)) > 0.2

def translate_text(text, target_lang, source_lang='auto'):
    """Translate text using Google Translator"""
    try:
        if source_lang == 'auto' and detect_roman_urdu(text):
            source_lang = 'ur'
        
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")

# -----------------------------
# Session State Management
# -----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

init_user_data()

# -----------------------------
# Authentication Interface
# -----------------------------
def show_auth_interface():
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.markdown("### 🔐 Welcome to AI Translator")
    
    auth_tabs = st.tabs(["🚀 Guest Access", "📝 Sign Up", "🔑 Login"])
    
    with auth_tabs[0]:
        st.markdown("### Continue as Guest")
        st.info("Experience basic features without an account")
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.current_user = "guest"
            st.rerun()
    
    with auth_tabs[1]:
        st.markdown("### Create Account")
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Create Account", use_container_width=True):
                if username and email and password:
                    if password == confirm_password:
                        if username not in st.session_state.users:
                            st.session_state.users[username] = {
                                'email': email,
                                'password': hash_password(password)
                            }
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill all fields")
    
    with auth_tabs[2]:
        st.markdown("### Login to Your Account")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if login_username in st.session_state.users:
                    if st.session_state.users[login_username]['password'] == hash_password(login_password):
                        st.session_state.current_user = login_username
                        st.success(f"Welcome back, {login_username}!")
                        st.rerun()
                    else:
                        st.error("Invalid password")
                else:
                    st.error("Username not found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Main App Interface (After Authentication)
# -----------------------------
def show_main_interface():
    # User Welcome Section
    if st.session_state.current_user != "guest":
        user_data = get_user_data(st.session_state.current_user)
        st.markdown(f'''
        <div class="user-welcome">
            <h3>👋 Welcome, {st.session_state.current_user}!</h3>
            <p>Your Translation Statistics: {user_data['usage_stats']['translations']} translations | {user_data['usage_stats']['characters']} characters</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Translator</h1>', unsafe_allow_html=True)
    st.markdown("### Intelligent Translation Platform with Comprehensive Language Support")
    
    # Language Statistics
    total_languages = len([lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'])
    language_categories = {
        "Global Languages": 20,
        "European Languages": 25,
        "Asian Languages": 30,
        "Middle Eastern": 15,
        "African Languages": 12
    }
    
    # Sidebar
    with st.sidebar:
        if st.session_state.current_user != "guest":
            st.markdown(f"### 👤 {st.session_state.current_user}")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.current_user = None
                st.rerun()
        else:
            st.markdown("### 👤 Guest User")
            if st.button("🔐 Create Account", use_container_width=True):
                st.session_state.show_auth = True
                st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        # Language Statistics
        st.markdown(f"""
        <div class="stats-box">
            <h4 style='margin:0;'>🌐 Language Support</h4>
            <h3 style='margin:10px 0;'>Comprehensive</h3>
            <p style='margin:0; font-size:0.9rem;'>Worldwide coverage</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Translation Settings
        st.markdown("#### 🔤 Translation")
        source_lang = st.selectbox(
            "Source Language",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index("English")
        )
        
        target_lang = st.selectbox(
            "Target Language",
            [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
            index=list(LANGUAGES.keys()).index("Hindi")
        )
        
        # Speech Settings
        st.markdown("#### 🔊 Speech")
        enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
        slow_speech = st.checkbox("Slow speech mode", value=False)
        
        # File Settings
        st.markdown("#### 📁 Documents")
        st.info("""
        **Supported formats:**
        - PDF Documents
        - Text Files (.txt)
        - Word Documents (.docx)
        """)
        
        st.markdown("---")
        st.markdown("#### 🎯 Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.input_text = ""
                st.rerun()
        with col2:
            if st.button("📊 History", use_container_width=True):
                st.session_state.show_history = True
        
        # Language Categories Info
        st.markdown("---")
        st.markdown("#### 🗺️ Language Groups")
        for category, count in language_categories.items():
            st.markdown(f'<div class="category-box"><b>{category}</b><br><small>{count} languages</small></div>', unsafe_allow_html=True)
    
    # Main Content Area
    st.markdown("### 📝 Translation Interface")
    
    # Input Methods Tabs
    tab1, tab2 = st.tabs(["✏️ Text Input", "📁 Document Upload"])
    
    with tab1:
        input_text = st.text_area(
            "Enter text to translate:",
            placeholder="Type or paste your text here...\n\nExamples:\n• English: Hello, how are you?\n• Roman Urdu: Aap kaisay hain?\n• Spanish: ¿Cómo estás?",
            height=180,
            key="text_input"
        )
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload document for translation",
            type=['pdf', 'txt', 'docx'],
            help="Supported formats: PDF, TXT, DOCX"
        )
        
        if uploaded_file is not None:
            st.success(f"Document uploaded: {uploaded_file.name}")
            
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            if file_ext == 'pdf':
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif file_ext == 'txt':
                extracted_text = extract_text_from_txt(uploaded_file)
            elif file_ext == 'docx':
                extracted_text = extract_text_from_docx(uploaded_file)
            else:
                extracted_text = ""
            
            if extracted_text:
                st.text_area("Extracted content", extracted_text, height=150)
                input_text = extracted_text
            else:
                st.error("Could not extract text from the document")
    
    # Translate Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        translate_btn = st.button("🚀 Translate Text", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # -----------------------------
    # Translation Logic
    # -----------------------------
    if translate_btn and input_text.strip():
        try:
            with st.spinner("🔄 Processing translation..."):
                if source_lang == 'Auto Detect':
                    if detect_roman_urdu(input_text):
                        detected_source = "Roman Urdu"
                        source_code = 'ur'
                    else:
                        detected_source = "Auto-detected"
                        source_code = 'auto'
                else:
                    detected_source = source_lang
                    source_code = LANGUAGES[source_lang]
                
                translated_text = translate_text(input_text, LANGUAGES[target_lang], source_code)
                
                # Update user statistics
                if st.session_state.current_user != "guest":
                    user_data = get_user_data(st.session_state.current_user)
                    user_data['usage_stats']['translations'] += 1
                    user_data['usage_stats']['characters'] += len(input_text)
                    save_user_data(st.session_state.current_user, user_data)
                
                # Display Results
                st.markdown("### 🎯 Translation Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**📥 Original Text**")
                    st.text_area(
                        "Original",
                        input_text,
                        height=200,
                        key="original_output",
                        label_visibility="collapsed"
                    )
                    st.caption(f"Language: {detected_source} • Characters: {len(input_text)}")
                    
                with col2:
                    st.markdown(f"**📤 Translated Text**")
                    st.text_area(
                        "Translated",
                        translated_text,
                        height=200,
                        key="translated_output",
                        label_visibility="collapsed"
                    )
                    st.caption(f"Language: {target_lang} • Characters: {len(translated_text)}")
                
                # Text-to-Speech Section
                if enable_tts:
                    st.markdown("#### 🔊 Audio Output")
                    
                    audio_bytes = text_to_speech_enhanced(translated_text, LANGUAGES[target_lang], slow_speech)
                    
                    if audio_bytes:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.audio(audio_bytes, format="audio/mp3")
                        with col2:
                            st.download_button(
                                label="📥 Download Audio",
                                data=audio_bytes,
                                file_name=f"translation_{target_lang}_{datetime.now().strftime('%H%M%S')}.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                        
                        st.success(f"Audio generated for {target_lang} translation")
                    else:
                        st.warning("Audio generation is not available for this language")
                
                # Save to translation history
                history_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": detected_source,
                    "target": target_lang,
                    "original": input_text,
                    "translated": translated_text
                }
                
                if st.session_state.current_user != "guest":
                    user_data = get_user_data(st.session_state.current_user)
                    user_data['translation_history'].append(history_entry)
                    save_user_data(st.session_state.current_user, user_data)
                else:
                    st.session_state.translation_history.append(history_entry)
                
                st.success("✅ Translation completed successfully")
    
        except Exception as e:
            st.error(f"❌ Translation error: {str(e)}")
    
    elif translate_btn:
        st.warning("⚠️ Please enter text or upload a document to translate")
    
    # -----------------------------
    # Translation History
    # -----------------------------
    translation_history = []
    if st.session_state.current_user != "guest":
        user_data = get_user_data(st.session_state.current_user)
        translation_history = user_data['translation_history']
    else:
        translation_history = st.session_state.translation_history
    
    if translation_history:
        st.markdown("---")
        st.markdown("### 📚 Recent Translations")
        
        for i, entry in enumerate(reversed(translation_history[-5:])):
            with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Text:**")
                    st.write(entry['original'])
                with col2:
                    st.markdown("**Translated Text:**")
                    st.write(entry['translated'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🔊 Audio", key=f"audio_{i}"):
                        audio_bytes = text_to_speech_enhanced(entry['translated'], LANGUAGES[entry['target']])
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                with col2:
                    st.download_button(
                        label="📥 Download",
                        data=entry['translated'],
                        file_name=f"translation_{entry['target']}_{i}.txt",
                        key=f"download_{i}"
                    )
                with col3:
                    if st.button(f"🗑️ Remove", key=f"delete_{i}"):
                        if st.session_state.current_user != "guest":
                            user_data = get_user_data(st.session_state.current_user)
                            user_data['translation_history'].pop(-(i+1))
                            save_user_data(st.session_state.current_user, user_data)
                        else:
                            st.session_state.translation_history.pop(-(i+1))
                        st.rerun()
    
    # -----------------------------
    # Features Section
    # -----------------------------
    st.markdown("---")
    st.markdown("### ✨ Platform Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-box">' +
                    '<h4>🌍 Global Reach</h4>' +
                    '<p>Comprehensive language support covering major world languages and regional dialects</p>' +
                    '</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box">' +
                    '<h4>📁 Document Support</h4>' +
                    '<p>Translate PDF, Word, and text documents with accurate text extraction</p>' +
                    '</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-box">' +
                    '<h4>🔊 Audio Output</h4>' +
                    '<p>Listen to translations with high-quality text-to-speech technology</p>' +
                    '</div>', unsafe_allow_html=True)
    
    # Language Coverage Metrics
    st.markdown("---")
    st.markdown("### 🗺️ Language Coverage")
    
    metric_cols = st.columns(5)
    with metric_cols[0]:
        st.markdown('<div class="metric-box">'
                    '<h3>Global</h3>'
                    '<p>World Languages</p>'
                    '</div>', unsafe_allow_html=True)
    with metric_cols[1]:
        st.markdown('<div class="metric-box">'
                    '<h3>European</h3>'
                    '<p>Language Family</p>'
                    '</div>', unsafe_allow_html=True)
    with metric_cols[2]:
        st.markdown('<div class="metric-box">'
                    '<h3>Asian</h3>'
                    '<p>Language Family</p>'
                    '</div>', unsafe_allow_html=True)
    with metric_cols[3]:
        st.markdown('<div class="metric-box">'
                    '<h3>Middle East</h3>'
                    '<p>Language Family</p>'
                    '</div>', unsafe_allow_html=True)
    with metric_cols[4]:
        st.markdown('<div class="metric-box">'
                    '<h3>African</h3>'
                    '<p>Language Family</p>'
                    '</div>', unsafe_allow_html=True)
    
    # -----------------------------
    # Footer
    # -----------------------------
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h4 style='color: #2E86AB; margin-bottom: 10px;'>🤖 AI Translator</h4>
        <p style='color: #666; margin-bottom: 15px;'>Intelligent Translation Platform</p>
        <div style='font-size: 0.9rem; color: #888;'>
            <span>Powered by: Streamlit • Google Translate • gTTS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("© 2024 AI Translator - All rights reserved")

# -----------------------------
# Main App Flow
# -----------------------------
if st.session_state.current_user is None:
    show_auth_interface()
else:
    show_main_interface()
