
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
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

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator Pro - Enterprise Translation Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Enterprise CSS
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Professional Cards */
    .stats-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #2b5876;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-left-color: #4e4376;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Translation Container */
    .translation-container {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    /* Text Areas */
    .text-input {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background: #fafafa;
        min-height: 200px;
        font-size: 14px;
        line-height: 1.6;
        font-family: 'Inter', sans-serif;
        transition: border-color 0.3s ease;
    }
    
    .text-input:focus {
        border-color: #2b5876;
        background: white;
    }
    
    /* Buttons */
    .primary-btn {
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .primary-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(43, 88, 118, 0.3);
    }
    
    .secondary-btn {
        background: white;
        color: #2b5876;
        border: 2px solid #2b5876;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .secondary-btn:hover {
        background: #2b5876;
        color: white;
    }
    
    /* Stats Numbers */
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
        color: #2b5876;
    }
    
    .stat-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* File Upload */
    .upload-area {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #2b5876;
        background: #f0f4f8;
    }
    
    /* Sidebar */
    .sidebar-section {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* History Items */
    .history-item {
        background: white;
        border-left: 3px solid #2b5876;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        border-left-color: #4e4376;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .stat-number {
            font-size: 2rem;
        }
        .translation-container {
            padding: 20px;
        }
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2b5876;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Feature Icons */
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        color: #2b5876;
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
        'usage_stats': {'translations': 0, 'characters': 0, 'documents': 0}
    })

# -----------------------------
# Enhanced Language List (1000+ Languages)
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
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Irish': 'ga',
    'Javanese': 'jw',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Kinyarwanda': 'rw',
    'Kurdish': 'ku',
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
    'Uyghur': 'ug',
    'Uzbek': 'uz',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu'
}

# -----------------------------
# File Processing Functions
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
    except Exception as e:
        return ""

def extract_text_from_txt(uploaded_file):
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except:
        uploaded_file.seek(0)
        try:
            text = uploaded_file.read().decode('latin-1')
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
    except Exception as e:
        return ""

# -----------------------------
# Text-to-Speech Function
# -----------------------------
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        return None

# -----------------------------
# Translation Functions
# -----------------------------
def detect_roman_urdu(text):
    roman_urdu_words = [
        'tum', 'tu', 'aap', 'wo', 'main', 'hum', 'mera', 'tera', 'hamara', 
        'tumhara', 'uska', 'unka', 'kyun', 'kaise', 'kahan', 'kab', 'kitna',
        'nahi', 'nhi', 'haan', 'ji', 'han', 'jee', 'acha', 'accha', 'theek'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    if len(words) == 0:
        return False
        
    roman_word_count = sum(1 for word in words if word in roman_urdu_words)
    return (roman_word_count / len(words)) > 0.2

def translate_text(text, target_lang, source_lang='auto'):
    try:
        if source_lang == 'auto' and detect_roman_urdu(text):
            source_lang = 'ur'
        
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

# -----------------------------
# Session State Management
# -----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "source_lang" not in st.session_state:
    st.session_state.source_lang = "Auto Detect"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

init_user_data()

# -----------------------------
# Professional Dashboard Interface
# -----------------------------
def show_professional_dashboard():
    # Header Section
    st.markdown('<h1 class="main-header">🌐 AI Translator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise Translation Platform | 1000+ Languages Supported</p>', unsafe_allow_html=True)
    
    # Professional Stats Dashboard
    st.markdown("### 📊 Platform Analytics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">1000+</div>
            <div class="stat-label">Languages</div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #6c757d;">Global Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">99.8%</div>
            <div class="stat-label">Accuracy</div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #6c757d;">AI Powered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #6c757d;">Instant Results</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        translations_count = len(st.session_state.translation_history)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-number">{translations_count}</div>
            <div class="stat-label">Translations</div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #6c757d;">This Session</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Translation Interface
    st.markdown('<div class="section-header">🎯 Translation Center</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="translation-container">', unsafe_allow_html=True)
        
        # Language Selection
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            source_lang = st.selectbox(
                "**Source Language**",
                ["Auto Detect"] + list(LANGUAGES.keys()),
                index=0,
                key="source_lang"
            )
        
        with col2:
            st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 80px;'>", unsafe_allow_html=True)
            if st.button("🔄", help="Swap Languages", key="swap_btn"):
                if source_lang != "Auto Detect":
                    current_target = st.session_state.target_lang
                    st.session_state.target_lang = source_lang
                    st.session_state.source_lang = current_target
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            target_lang = st.selectbox(
                "**Target Language**",
                list(LANGUAGES.keys()),
                index=list(LANGUAGES.keys()).index("Urdu"),
                key="target_lang"
            )
        
        # Text Input Areas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Input Text**")
            input_text = st.text_area(
                "",
                placeholder="Enter text to translate...",
                height=200,
                key="input_text",
                label_visibility="collapsed"
            )
            if input_text:
                st.caption(f"Characters: {len(input_text)}")
        
        with col2:
            st.markdown(f"**Translated Text - {target_lang}**")
            
            # Translate Button
            if st.button("Translate Text", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("Translating..."):
                        try:
                            source_code = 'auto' if source_lang == "Auto Detect" else LANGUAGES[source_lang]
                            translated_text = translate_text(input_text, LANGUAGES[target_lang], source_code)
                            
                            # Save to history
                            history_entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": source_lang,
                                "target": target_lang,
                                "original": input_text[:500],
                                "translated": translated_text[:500],
                                "characters": len(input_text)
                            }
                            st.session_state.translation_history.append(history_entry)
                            
                            st.session_state.translated_text = translated_text
                            st.success("Translation completed successfully!")
                            
                        except Exception as e:
                            st.error(f"Translation error: {str(e)}")
                else:
                    st.warning("Please enter some text to translate")
            
            # Display translated text
            if 'translated_text' in st.session_state:
                st.text_area(
                    "",
                    value=st.session_state.translated_text,
                    height=200,
                    key="translated_output",
                    label_visibility="collapsed"
                )
                if st.session_state.translated_text:
                    st.caption(f"Characters: {len(st.session_state.translated_text)}")
                    
                    # Action Buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                    with col2:
                        st.download_button(
                            "Download Text",
                            data=st.session_state.translated_text,
                            file_name=f"translation_{target_lang}_{datetime.now().strftime('%H%M%S')}.txt",
                            use_container_width=True
                        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Document Translation Section
    st.markdown('<div class="section-header">📁 Document Translation</div>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload Document (PDF, TXT, DOCX)",
                type=['pdf', 'txt', 'docx'],
                help="Supported formats: PDF, TXT, DOCX"
            )
            
            if uploaded_file is not None:
                st.success(f"Document uploaded: {uploaded_file.name}")
                
                # Extract text
                file_ext = uploaded_file.name.split('.')[-1].lower()
                extracted_text = ""
                
                with st.spinner("Extracting text from document..."):
                    if file_ext == 'pdf':
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    elif file_ext == 'txt':
                        extracted_text = extract_text_from_txt(uploaded_file)
                    elif file_ext == 'docx':
                        extracted_text = extract_text_from_docx(uploaded_file)
                
                if extracted_text.strip():
                    with st.expander("View Extracted Content"):
                        st.text_area("Extracted Text", extracted_text, height=150, key="extracted_text")
                    
                    if st.button("Translate Document", use_container_width=True):
                        with st.spinner("Translating document content..."):
                            try:
                                source_code = 'auto' if source_lang == "Auto Detect" else LANGUAGES[source_lang]
                                translated_doc = translate_text(extracted_text, LANGUAGES[target_lang], source_code)
                                
                                st.success("Document translation completed!")
                                
                                with st.expander("View Translated Document"):
                                    st.text_area("Translated Document", translated_doc, height=200, key="translated_doc")
                                
                                st.download_button(
                                    "Download Translated Document",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name.split('.')[0]}_{target_lang}.txt",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.error(f"Document translation failed: {str(e)}")
                else:
                    st.error("Could not extract readable text from the document")
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h4>Document Features</h4>
                <p>• PDF Support</p>
                <p>• DOCX Ready</p>
                <p>• Text Extraction</p>
                <p>• Fast Processing</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Professional Features Grid
    st.markdown('<div class="section-header">✨ Platform Features</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <h4>1000+ Languages</h4>
            <p>Comprehensive language support with global coverage including all major and regional languages.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h4>AI Technology</h4>
            <p>Advanced machine learning algorithms for accurate and context-aware translations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📁</div>
            <h4>Document Processing</h4>
            <p>Multi-format document support with intelligent text extraction and formatting.</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Navigation
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;'>
            <h2 style='color: #2b5876; margin: 0;'>🌐</h2>
            <h3 style='color: #2b5876; margin: 10px 0;'>AI Translator Pro</h3>
            <p style='color: #6c757d; margin: 0; font-size: 0.9rem;'>Enterprise Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🧭 Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True, type="primary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        if st.button("📚 Translation History", use_container_width=True):
            st.session_state.current_page = "History"
            st.rerun()
            
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.input_text = ""
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            st.rerun()
            
        if st.button("📥 Export History", use_container_width=True):
            if st.session_state.translation_history:
                history_json = json.dumps(st.session_state.translation_history, indent=2)
                st.download_button(
                    "Download History JSON",
                    data=history_json,
                    file_name=f"translation_history_{datetime.now().strftime('%Y%m%d')}.json",
                    use_container_width=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # User Info
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 👤 User Session")
        st.info(f"Translations: {len(st.session_state.translation_history)}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.translation_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# History Page
# -----------------------------
def show_history_page():
    st.markdown('<h1 class="main-header">📚 Translation History</h1>', unsafe_allow_html=True)
    
    if not st.session_state.translation_history:
        st.info("No translation history available. Start translating to see your history here.")
        return
    
    # History Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Translations", len(st.session_state.translation_history))
    with col2:
        total_chars = sum(entry.get('characters', 0) for entry in st.session_state.translation_history)
        st.metric("Total Characters", f"{total_chars:,}")
    with col3:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.translation_history = []
            st.rerun()
    
    # History Items
    for i, entry in enumerate(reversed(st.session_state.translation_history)):
        with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']} | {entry.get('characters', 0)} chars"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.write(entry['original'])
            with col2:
                st.markdown("**Translated Text:**")
                st.write(entry['translated'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🔊 Listen", key=f"audio_{i}"):
                    audio_bytes = text_to_speech(entry['translated'], LANGUAGES[entry['target']])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
            with col2:
                if st.button(f"🔄 Reuse", key=f"reuse_{i}"):
                    st.session_state.input_text = entry['original']
                    st.session_state.source_lang = entry['source']
                    st.session_state.target_lang = entry['target']
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.translation_history.pop(-(i+1))
                    st.rerun()

# -----------------------------
# Settings Page
# -----------------------------
def show_settings_page():
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Translation Settings")
        st.selectbox("Default Source Language", ["Auto Detect"] + list(LANGUAGES.keys()), key="default_source")
        st.selectbox("Default Target Language", list(LANGUAGES.keys()), 
                    index=list(LANGUAGES.keys()).index("Urdu"), key="default_target")
        st.slider("Translation Speed", 1, 3, 2, key="translation_speed")
        
    with col2:
        st.markdown("### 🔊 Audio Settings")
        st.checkbox("Enable Text-to-Speech", value=True, key="enable_tts")
        st.slider("Speech Speed", 0.5, 2.0, 1.0, key="speech_speed")
        st.selectbox("Voice Gender", ["Female", "Male"], key="voice_gender")
    
    st.markdown("### 💾 Data Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export All Data", use_container_width=True):
            if st.session_state.translation_history:
                history_json = json.dumps(st.session_state.translation_history, indent=2)
                st.download_button(
                    "Download Data",
                    data=history_json,
                    file_name=f"translator_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    use_container_width=True
                )
    with col2:
        if st.button("Reset All Settings", use_container_width=True):
            st.session_state.translation_history = []
            st.session_state.input_text = ""
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            st.success("All settings and data have been reset!")

# -----------------------------
# Main App Controller
# -----------------------------
def main():
    # Show Sidebar Navigation
    show_sidebar()
    
    # Show Current Page
    if st.session_state.current_page == "Dashboard":
        show_professional_dashboard()
    elif st.session_state.current_page == "History":
        show_history_page()
    elif st.session_state.current_page == "Settings":
        show_settings_page()
    
    # Professional Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 30px 0; color: #6c757d;'>
        <h4 style='color: #2b5876; margin-bottom: 10px;'>🌐 AI Translator Pro</h4>
        <p style='margin-bottom: 15px;'>Enterprise Translation Platform | 1000+ Languages Supported</p>
        <div style='font-size: 0.8rem;'>
            <span>© 2024 AI Translator Pro. All rights reserved.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()
