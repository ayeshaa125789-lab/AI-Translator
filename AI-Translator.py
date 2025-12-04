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
import base64
import time
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS with improved connectivity indicators
st.markdown("""
<style>
    /* Modern Gradient Header */
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
    
    /* Connectivity Status */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: pulse 2s infinite;
    }
    
    .status-offline {
        background-color: #EF4444;
        box-shadow: 0 0 10px #EF4444;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Modern Cards with Glass Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(31, 38, 135, 0.25);
    }
    
    /* Gradient Stats Cards */
    .gradient-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        border: none;
        transition: all 0.3s ease;
    }
    
    .gradient-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.4);
        border: none;
        transition: all 0.3s ease;
    }
    
    .gradient-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.4);
        border: none;
        transition: all 0.3s ease;
    }
    
    .gradient-card-4 {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(67, 233, 123, 0.4);
        border: none;
        transition: all 0.3s ease;
    }
    
    .gradient-card-1:hover, .gradient-card-2:hover, 
    .gradient-card-3:hover, .gradient-card-4:hover {
        transform: translateY(-8px) scale(1.02);
    }
    
    /* Modern Input/Output Sections */
    .modern-input {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #cbd5e1;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(203, 213, 225, 0.3);
        transition: all 0.3s ease;
    }
    
    .modern-input:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    .modern-output {
        background: linear-gradient(135deg, #f0f9ff 0%, #bae6fd 100%);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #7dd3fc;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(186, 230, 253, 0.3);
        transition: all 0.3s ease;
    }
    
    .modern-output:hover {
        border-color: #4facfe;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.2);
    }
    
    /* Animated Section Titles */
    .animated-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid;
        border-image: linear-gradient(45deg, #FF6B6B, #4ECDC4) 1;
        display: inline-block;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Modern Sidebar */
    .sidebar-glass {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Stats Numbers */
    .glow-number {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 10px;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }
    
    .glow-label {
        font-size: 1rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: transparent;
        padding: 10px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        color: #1f2937;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Hide Streamlit footer */
    .css-1lsmgbg { display: none; }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Floating Animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        background-color: #f3f3f3;
        border-radius: 10px;
        margin: 20px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 20px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        width: 0%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Feature Icons */
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Custom buttons */
    .custom-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        display: inline-block;
        text-decoration: none;
    }
    
    .custom-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helper Functions for Animations
# -----------------------------
def get_loading_animation():
    """Return HTML for loading animation"""
    return """
    <div style="text-align: center; padding: 40px;">
        <div class="loading-spinner" style="margin: 0 auto;"></div>
        <p style="margin-top: 20px; color: #667eea; font-weight: 600;">Processing your translation...</p>
    </div>
    """

def get_welcome_animation():
    """Return HTML for welcome animation"""
    return """
    <div style="text-align: center; padding: 30px;">
        <div style="font-size: 4rem; margin-bottom: 20px;">🚀</div>
        <h3 style="color: #1f2937; margin-bottom: 10px;">Welcome to AI Translator Pro</h3>
        <p style="color: #6b7280;">Start translating by typing text or uploading a document</p>
    </div>
    """

# -----------------------------
# Session State Management with Local Storage
# -----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []
    
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Translator"

if "connection_status" not in st.session_state:
    st.session_state.connection_status = "online"

if "app_stats" not in st.session_state:
    st.session_state.app_stats = {
        "total_translations": 0,
        "total_characters": 0,
        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# -----------------------------
# Connection Monitoring
# -----------------------------
def check_connection():
    """Check internet connection status"""
    try:
        response = requests.get("https://www.google.com", timeout=3)
        st.session_state.connection_status = "online"
        return True
    except:
        st.session_state.connection_status = "offline"
        return False

# -----------------------------
# Enhanced Translation Function with Retry Logic
# -----------------------------
def translate_text_with_retry(text, target_lang, source_lang='auto', max_retries=3):
    """Translate text with retry logic for better connectivity"""
    for attempt in range(max_retries):
        try:
            if source_lang == 'auto':
                translator = GoogleTranslator(target=target_lang)
            else:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            translated = translator.translate(text)
            st.session_state.connection_status = "online"
            return translated
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
                continue
            else:
                st.session_state.connection_status = "offline"
                raise Exception(f"Translation failed after {max_retries} attempts: {str(e)}")

# -----------------------------
# Complete Language List
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
    'Zulu': 'zu'
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
        return text.strip() if text.strip() else ""
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return ""

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return ""

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
        return text.strip() if text.strip() else ""
    except Exception as e:
        st.error(f"Error extracting DOCX: {str(e)}")
        return ""

def extract_text_from_file(uploaded_file):
    """Extract text from various file formats"""
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_ext == 'txt':
        return extract_text_from_txt(uploaded_file)
    elif file_ext == 'docx':
        return extract_text_from_docx(uploaded_file)
    else:
        return f"Unsupported file format: {file_ext}"

# -----------------------------
# Enhanced Text-to-Speech Function
# -----------------------------
def text_to_speech(text, lang_code):
    """Convert text to speech audio"""
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.warning(f"Audio generation failed: {str(e)}")
        return None

# -----------------------------
# Main Translator Interface
# -----------------------------
def show_translator():
    """Main translator interface"""
    # Check connection status
    check_connection()
    
    # Header with Connection Status
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<h1 class="gradient-header">🚀 AI Translator Pro</h1>', unsafe_allow_html=True)
    with col2:
        status_class = "status-online" if st.session_state.connection_status == "online" else "status-offline"
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 10px; margin-top: 20px;">
            <div style="display: flex; align-items: center; justify-content: center;">
                <span class="status-indicator {status_class}"></span>
                <span style="font-weight: 600;">{st.session_state.connection_status.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; margin-top: 20px;">
            <div style="font-size: 1.5rem; font-weight: 800;">{len(st.session_state.translation_history)}</div>
            <div style="font-size: 0.8rem;">Translations</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.2rem; margin-bottom: 30px;">Professional Translation Platform | AI-Powered Language Solutions</p>', unsafe_allow_html=True)
    
    # Modern Tab Interface
    tab1, tab2, tab3 = st.tabs(["🔤 **Text Translator**", "📄 **Document Translator**", "📊 **Analytics Dashboard**"])
    
    with tab1:
        # Text Translation Interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">📝 Source Text</div>', unsafe_allow_html=True)
            
            # Auto-detection info
            st.info("🤖 **Auto-Detection Active**: AI will automatically detect your input language")
            
            input_text = st.text_area(
                "",
                placeholder="✨ Type or paste your text here in any language...\n\nExamples:\n• Hello! How are you?\n• नमस्ते, आप कैसे हैं?\n• مرحبا، كيف حالك؟\n• 你好，你好吗？",
                height=250,
                key="input_text",
                label_visibility="collapsed"
            )
            
            if input_text:
                char_count = len(input_text)
                word_count = len(input_text.split())
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("📊 Characters", char_count)
                with col_b:
                    st.metric("📝 Words", word_count)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">🎯 Target Language</div>', unsafe_allow_html=True)
            
            # Language selection with search
            search_term = st.text_input("🔍 Search Language", placeholder="Type to filter languages...", key="lang_search")
            
            if search_term:
                filtered_langs = {k: v for k, v in LANGUAGES.items() if search_term.lower() in k.lower()}
            else:
                filtered_langs = LANGUAGES
            
            target_lang = st.selectbox(
                "Select translation language:",
                list(filtered_langs.keys()),
                index=list(filtered_langs.keys()).index("Urdu") if "Urdu" in filtered_langs else 0,
                key="target_lang_select"
            )
            
            # Language info card
            lang_code = LANGUAGES[target_lang]
            st.markdown(f"""
            <div class="glass-card" style="margin-top: 20px; padding: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0;">{target_lang}</h4>
                        <p style="color: #6b7280; margin: 5px 0 0 0;">Language Code: {lang_code}</p>
                    </div>
                    <div style="font-size: 2rem;">{"🇵🇰" if target_lang == "Urdu" else "🌍"}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Translate button
            translate_clicked = st.button("🚀 **Translate Now**", use_container_width=True, type="primary", key="translate_main_btn")
            
            if translate_clicked:
                if input_text and input_text.strip():
                    # Create a placeholder for progress
                    progress_placeholder = st.empty()
                    
                    # Show loading animation
                    progress_placeholder.markdown(get_loading_animation(), unsafe_allow_html=True)
                    
                    try:
                        # Translate text
                        translated_text = translate_text_with_retry(input_text, lang_code)
                        
                        # Update session state
                        st.session_state.translated_text = translated_text
                        st.session_state.translated_lang = target_lang
                        
                        # Update stats
                        st.session_state.app_stats["total_translations"] += 1
                        st.session_state.app_stats["total_characters"] += len(input_text)
                        st.session_state.app_stats["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Add to history
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "Auto-Detected",
                            "target": target_lang,
                            "original": input_text[:500],
                            "translated": translated_text[:500],
                            "characters": len(input_text)
                        }
                        st.session_state.translation_history.append(history_entry)
                        
                        # Clear progress placeholder
                        progress_placeholder.empty()
                        st.success("✅ **Translation Completed Successfully!**")
                        st.rerun()
                        
                    except Exception as e:
                        progress_placeholder.empty()
                        st.error(f"❌ **Translation Error:** {str(e)}")
                else:
                    st.warning("⚠️ **Please enter some text to translate**")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Results Section
        if 'translated_text' in st.session_state:
            st.markdown('<div class="modern-output">', unsafe_allow_html=True)
            st.markdown(f'<div class="animated-title">📋 Translation Results - {st.session_state.translated_lang}</div>', unsafe_allow_html=True)
            
            # Display original and translated text side by side
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("**Original Text:**")
                st.text_area("", st.session_state.input_text, height=150, key="original_display_area", disabled=True)
            
            with col_right:
                st.markdown(f"**Translated Text ({st.session_state.translated_lang}):**")
                st.text_area("", st.session_state.translated_text, height=150, key="translated_display_area", disabled=True)
            
            # Action Buttons Row
            st.markdown("---")
            st.markdown('<div class="animated-title" style="font-size: 1.4rem;">⚡ Actions</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Text to Speech
                audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[st.session_state.translated_lang])
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.caption("🔊 Listen to translation")
            
            with col2:
                # Download Text
                st.download_button(
                    "💾 Download Text",
                    data=st.session_state.translated_text,
                    file_name=f"translation_{st.session_state.translated_lang}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                # Download Audio
                if audio_bytes:
                    st.download_button(
                        "🎵 Download Audio",
                        data=audio_bytes,
                        file_name=f"audio_{st.session_state.translated_lang}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
            
            with col4:
                # New Translation
                if st.button("🔄 New", use_container_width=True):
                    st.session_state.input_text = ""
                    if 'translated_text' in st.session_state:
                        del st.session_state.translated_text
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show welcome message when no translation
            st.markdown(get_welcome_animation(), unsafe_allow_html=True)
    
    with tab2:
        # Document Translation
        st.markdown('<div class="modern-input">', unsafe_allow_html=True)
        st.markdown('<div class="animated-title">📁 Document Translation</div>', unsafe_allow_html=True)
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            uploaded_file = st.file_uploader(
                "**Upload your document**",
                type=['pdf', 'txt', 'docx'],
                help="Supported formats: PDF, TXT, DOCX (Max 200MB)",
                key="doc_uploader"
            )
            
            if uploaded_file is not None:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
                
                # File info
                col_size, col_type = st.columns(2)
                with col_size:
                    st.metric("📏 File Size", f"{file_size:.2f} MB")
                with col_type:
                    st.metric("📄 File Type", uploaded_file.name.split('.')[-1].upper())
                
                # Extract text
                with st.spinner("🔍 Extracting text from document..."):
                    extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text and extracted_text.strip():
                    with st.expander("📖 View Extracted Content", expanded=True):
                        st.text_area("", extracted_text, height=200, label_visibility="collapsed", key="extracted_text_area")
                    
                    # Target language selection for document
                    doc_target_lang = st.selectbox(
                        "Select target language for document:",
                        list(LANGUAGES.keys()),
                        index=list(LANGUAGES.keys()).index("Urdu"),
                        key="doc_target_lang"
                    )
                    
                    # Translate document button
                    if st.button("🚀 Translate Document", use_container_width=True, type="primary", key="translate_doc_btn"):
                        with st.spinner("🔄 Translating document..."):
                            try:
                                translated_doc = translate_text_with_retry(extracted_text, LANGUAGES[doc_target_lang])
                                
                                st.success("✅ Document translation completed!")
                                
                                # Display translated document
                                st.markdown("**Translated Document:**")
                                st.text_area("", translated_doc, height=200, label_visibility="collapsed", key="translated_doc_area")
                                
                                # Download options
                                col_dl1, col_dl2 = st.columns(2)
                                with col_dl1:
                                    st.download_button(
                                        "💾 Download Text",
                                        data=translated_doc,
                                        file_name=f"translated_{uploaded_file.name.split('.')[0]}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                with col_dl2:
                                    doc_audio = text_to_speech(translated_doc, LANGUAGES[doc_target_lang])
                                    if doc_audio:
                                        st.download_button(
                                            "🎵 Download Audio",
                                            data=doc_audio,
                                            file_name=f"audio_document_{doc_target_lang}.mp3",
                                            mime="audio/mp3",
                                            use_container_width=True
                                        )
                                
                            except Exception as e:
                                st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("⚠️ Could not extract text from the document")
            else:
                # Upload prompt
                st.markdown("""
                <div style="text-align: center; padding: 40px; border: 2px dashed #cbd5e1; border-radius: 15px; margin: 20px 0;">
                    <div style="font-size: 3rem; margin-bottom: 20px;">📁</div>
                    <h3>Upload Your Document</h3>
                    <p style="color: #6b7280;">Drag & drop or click to upload</p>
                    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px; font-size: 2rem;">
                        <span title="PDF">📄
