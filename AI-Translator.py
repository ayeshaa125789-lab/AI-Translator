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
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import plotly.express as px

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
</style>
""", unsafe_allow_html=True)

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

# -----------------------------
# Enhanced Text-to-Speech Function
# -----------------------------
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

# -----------------------------
# Main Translator Interface
# -----------------------------
def show_translator():
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
    tab1, tab2, tab3 = st.tabs(["🔤 **Text Translator**", "📄 **Document Translator**", "📊 **Analytics**"])
    
    with tab1:
        # Text Translation Interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">📝 Source Text</div>', unsafe_allow_html=True)
            
            # Language detection info
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(67, 233, 123, 0.1), rgba(56, 249, 215, 0.1)); 
                        padding: 10px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #43e97b;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">🤖</span>
                    <div>
                        <strong>Auto-Detection Active</strong><br>
                        <small>AI will automatically detect your input language</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
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
            search_term = st.text_input("🔍 Search Language", placeholder="Type to filter languages...")
            
            if search_term:
                filtered_langs = {k: v for k, v in LANGUAGES.items() if search_term.lower() in k.lower()}
            else:
                filtered_langs = LANGUAGES
            
            target_lang = st.selectbox(
                "Select translation language:",
                list(filtered_langs.keys()),
                index=list(filtered_langs.keys()).index("Urdu") if "Urdu" in filtered_langs else 0,
                key="target_lang"
            )
            
            # Language info card
            st.markdown(f"""
            <div class="glass-card" style="margin-top: 20px; padding: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0;">{target_lang}</h4>
                        <p style="color: #6b7280; margin: 5px 0 0 0;">Code: {LANGUAGES[target_lang]}</p>
                    </div>
                    <div style="font-size: 2rem;">{"🇵🇰" if target_lang == "Urdu" else "🌍"}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Translate button with progress indicator
            if st.button("🚀 **Translate Now**", use_container_width=True, type="primary", key="translate_btn"):
                if input_text.strip():
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        translated_text = translate_text_with_retry(input_text, LANGUAGES[target_lang])
                        
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
                        
                        progress_bar.empty()
                        st.success("✅ **Translation Completed Successfully!**")
                        st.rerun()
                        
                    except Exception as e:
                        progress_bar.empty()
                        st.error(f"❌ **Translation Error:** {str(e)}")
                else:
                    st.warning("⚠️ **Please enter some text to translate**")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Results Section
        if 'translated_text' in st.session_state:
            st.markdown('<div class="modern-output">', unsafe_allow_html=True)
            st.markdown(f'<div class="animated-title">📋 Translation Results - {st.session_state.translated_lang}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Text:**")
                st.text_area("", input_text, height=150, key="original_display", disabled=True)
            
            with col2:
                st.markdown(f"**Translated Text ({st.session_state.translated_lang}):**")
                st.text_area("", st.session_state.translated_text, height=150, key="translated_display", disabled=True)
            
            # Action Buttons Row
            st.markdown("---")
            st.markdown('<div class="animated-title" style="font-size: 1.4rem;">⚡ Actions</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[st.session_state.translated_lang])
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
            
            with col2:
                st.download_button(
                    "💾 Download Text",
                    data=st.session_state.translated_text,
                    file_name=f"translation_{st.session_state.translated_lang}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                if audio_bytes:
                    st.download_button(
                        "🎵 Download Audio",
                        data=audio_bytes,
                        file_name=f"audio_{st.session_state.translated_lang}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
            
            with col4:
                if st.button("🔄 New Translation", use_container_width=True):
                    st.session_state.input_text = ""
                    if 'translated_text' in st.session_state:
                        del st.session_state.translated_text
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Document Translation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">📁 Document Upload</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "**Upload your document**",
                type=['pdf', 'txt', 'docx'],
                help="Supported formats: PDF, TXT, DOCX (Max 200MB)"
            )
            
            if uploaded_file is not None:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
                
                col_size, col_type = st.columns(2)
                with col_size:
                    st.metric("📏 File Size", f"{file_size:.2f} MB")
                with col_type:
                    st.metric("📄 File Type", uploaded_file.name.split('.')[-1].upper())
                
                with st.spinner("🔍 Extracting text from document..."):
                    extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text and extracted_text.strip():
                    with st.expander("📖 View Extracted Content", expanded=True):
                        st.text_area("", extracted_text, height=200, label_visibility="collapsed")
                    
                    if st.button("🚀 Translate Document", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Translating document..."):
                            try:
                                translated_doc = translate_text_with_retry(extracted_text, LANGUAGES[target_lang])
                                
                                st.success("✅ Document translation completed!")
                                
                                # Display translated document
                                st.markdown("**Translated Document:**")
                                st.text_area("", translated_doc, height=200, label_visibility="collapsed")
                                
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
                                    doc_audio = text_to_speech(translated_doc, LANGUAGES[target_lang])
                                    if doc_audio:
                                        st.download_button(
                                            "🎵 Download Audio",
                                            data=doc_audio,
                                            file_name=f"audio_document_{target_lang}.mp3",
                                            mime="audio/mp3",
                                            use_container_width=True
                                        )
                                
                            except Exception as e:
                                st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("⚠️ Could not extract text from the document")
            else:
                st.markdown("""
                <div style="text-align: center; padding: 40px; border: 2px dashed #cbd5e1; border-radius: 15px; margin: 20px 0;">
                    <div style="font-size: 3rem; margin-bottom: 20px;">📁</div>
                    <h3>Upload Document</h3>
                    <p style="color: #6b7280;">Drag & drop or click to upload</p>
                    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px; font-size: 2rem;">
                        <span title="PDF">📄</span>
                        <span title="Text">📝</span>
                        <span title="Word">📘</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="glass-card">
                <div class="animated-title">📋 Supported Formats</div>
                <div style="margin: 15px 0;">
                    <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                        <span style="font-size: 1.5rem;">📄</span>
                        <div>
                            <strong>PDF Documents</strong><br>
                            <small>Extracts text from PDF files</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0; padding: 10px; background: rgba(245, 87, 108, 0.1); border-radius: 10px;">
                        <span style="font-size: 1.5rem;">📝</span>
                        <div>
                            <strong>Text Files</strong><br>
                            <small>Supports .txt format</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0; padding: 10px; background: rgba(79, 172, 254, 0.1); border-radius: 10px;">
                        <span style="font-size: 1.5rem;">📘</span>
                        <div>
                            <strong>Word Documents</strong><br>
                            <small>Supports .docx format</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="glass-card" style="margin-top: 20px;">
                <div class="animated-title">💡 Tips</div>
                <ul style="color: #6b7280;">
                    <li>Ensure documents are readable</li>
                    <li>Max file size: 200MB</li>
                    <li>Use clear text formatting</li>
                    <li>Check extraction preview</li>
                    <li>Save translated files</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # Analytics Dashboard
        st.markdown('<div class="modern-input">', unsafe_allow_html=True)
        st.markdown('<div class="animated-title">📊 Translation Analytics</div>', unsafe_allow_html=True)
        
        if st.session_state.translation_history:
            # Convert history to DataFrame
            df = pd.DataFrame(st.session_state.translation_history)
            
            # Stats Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="gradient-card-1">
                    <div class="glow-number">{}</div>
                    <div class="glow-label">Total Translations</div>
                </div>
                """.format(len(df)), unsafe_allow_html=True)
            
            with col2:
                total_chars = df['characters'].sum() if 'characters' in df.columns else 0
                st.markdown("""
                <div class="gradient-card-2">
                    <div class="glow-number">{}</div>
                    <div class="glow-label">Total Characters</div>
                </div>
                """.format(total_chars), unsafe_allow_html=True)
            
            with col3:
                avg_chars = total_chars // len(df) if len(df) > 0 else 0
                st.markdown("""
                <div class="gradient-card-3">
                    <div class="glow-number">{}</div>
                    <div class="glow-label">Avg. Length</div>
                </div>
                """.format(avg_chars), unsafe_allow_html=True)
            
            with col4:
                most_common_lang = df['target'].mode()[0] if not df['target'].mode().empty else "N/A"
                st.markdown("""
                <div class="gradient-card-4">
                    <div style="font-size: 1.8rem; font-weight: 800;">{}</div>
                    <div class="glow-label">Most Used Language</div>
                </div>
                """.format(most_common_lang), unsafe_allow_html=True)
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                if 'target' in df.columns:
                    lang_counts = df['target'].value_counts().head(10)
                    fig1 = px.bar(
                        lang_counts,
                        title="Top 10 Translated Languages",
                        labels={'value': 'Count', 'index': 'Language'},
                        color=lang_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    fig1.update_layout(showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                if 'timestamp' in df.columns:
                    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                    hour_counts = df['hour'].value_counts().sort_index()
                    fig2 = px.line(
                        hour_counts,
                        title="Translation Activity by Hour",
                        labels={'value': 'Count', 'index': 'Hour'}
                    )
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Recent Translations Table
            st.markdown("**Recent Translations:**")
            st.dataframe(
                df[['timestamp', 'source', 'target', 'characters']].head(10),
                use_container_width=True
            )
            
            # Export Data
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Export as CSV",
                    data=csv,
                    file_name="translation_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_exp2:
                json_data = df.to_json(indent=2, orient='records')
                st.download_button(
                    "📥 Export as JSON",
                    data=json_data,
                    file_name="translation_history.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("📊 **No translation data available yet. Start translating to see analytics!**")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer with Enhanced Stats
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 20px;">
        <h3 style="color: #1f2937; margin-bottom: 10px;">🚀 AI Translator Pro</h3>
        <p style="color: #6b7280; margin-bottom: 20px;">Professional Translation Platform | Powered by Advanced AI Technology</p>
        
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #667eea;">{}</div>
                <div style="font-size: 0.9rem; color: #6b7280;">Languages</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #f5576c;">{}</div>
                <div style="font-size: 0.9rem; color: #6b7280;">Translations</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #4facfe;">24/7</div>
                <div style="font-size: 0.9rem; color: #6b7280;">Availability</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #43e97b;">{}</div>
                <div style="font-size: 0.9rem; color: #6b7280;">Total Chars</div>
            </div>
        </div>
        
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 30px;">© 2024 AI Translator Pro | All Rights Reserved</p>
    </div>
    """.format(len(LANGUAGES), 
               len(st.session_state.translation_history),
               st.session_state.app_stats.get("total_characters", 0)), unsafe_allow_html=True)

# -----------------------------
# Sidebar with Enhanced Features
# -----------------------------
def show_sidebar():
    with st.sidebar:
        # App Logo and Info
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; margin-bottom: 20px; 
                    background: linear-gradient(135deg, #667eea, #764ba2); 
                    border-radius: 15px;'>
            <h2 style='color: white; margin: 0; font-size: 3rem;'>🚀</h2>
            <h3 style='color: white; margin: 10px 0;'>AI Translator Pro</h3>
            <p style='color: rgba(255,255,255,0.9); margin: 0; font-size: 0.8rem;'>
                Version 2.0 | Professional Edition
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Connection Status
        status_color = "#10B981" if st.session_state.connection_status == "online" else "#EF4444"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="font-weight: 600;">Connection Status</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 10px; height: 10px; background-color: {status_color}; 
                                border-radius: 50%; box-shadow: 0 0 10px {status_color};"></div>
                    <span>{st.session_state.connection_status.upper()}</span>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <small>Last checked: {datetime.now().strftime("%H:%M:%S")}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🧭 Navigation**")
        
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("🔤 **Translator**", use_container_width=True, type="primary"):
                st.session_state.current_page = "Translator"
                st.rerun()
        with nav_col2:
            if st.button("📊 **Analytics**", use_container_width=True):
                st.session_state.current_page = "Analytics"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        
        if st.button("🔄 Clear Session", use_container_width=True):
            st.session_state.input_text = ""
            st.session_state.translation_history = []
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            st.success("Session cleared!")
            st.rerun()
        
        if st.button("📥 Export All Data", use_container_width=True):
            if st.session_state.translation_history:
                df = pd.DataFrame(st.session_state.translation_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="all_translations.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # App Statistics
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**📈 App Statistics**")
        
        stats = st.session_state.app_stats
        st.metric("Total Translations", stats.get("total_translations", 0))
        st.metric("Total Characters", stats.get("total_characters", 0))
        st.metric("Last Active", stats.get("last_active", "Never"))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Language Quick Select
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🌍 Quick Language Select**")
        
        popular_langs = ['Urdu', 'English', 'Arabic', 'Hindi', 'Spanish', 'French']
        selected_lang = st.selectbox("Choose language:", popular_langs)
        if selected_lang != st.session_state.target_lang:
            st.session_state.target_lang = selected_lang
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Main App Flow
# -----------------------------
def main():
    # Initialize connection check
    if 'connection_checked' not in st.session_state:
        check_connection()
        st.session_state.connection_checked = True
    
    # Show sidebar
    show_sidebar()
    
    # Show main content based on current page
    if st.session_state.current_page == "Translator":
        show_translator()
    elif st.session_state.current_page == "Analytics":
        # Show analytics in main area
        show_translator()  # This will show the analytics tab

# -----------------------------
# Run the App
# -----------------------------
if __name__ == "__main__":
    main()
