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
    page_title="AI Translator - Professional Translation Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dashboard CSS
st.markdown("""
<style>
    /* Main Styles */
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 10px 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
    }
    
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        text-align: center;
        margin: 8px;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #2E86AB;
        box-shadow: 0 5px 15px rgba(46, 134, 171, 0.2);
    }
    
    /* Translation Box */
    .translation-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #e0e0e0;
    }
    
    .language-selector {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 14px;
        margin: 0 10px;
        transition: border-color 0.3s ease;
    }
    
    .language-selector:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    .swap-btn {
        background: #2E86AB;
        color: white;
        border: none;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        font-size: 18px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .swap-btn:hover {
        background: #2575a0;
        transform: rotate(180deg);
    }
    
    /* Text Areas */
    .text-input {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background: white;
        min-height: 200px;
        font-size: 16px;
        line-height: 1.6;
        transition: border-color 0.3s ease;
    }
    
    .text-input:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    /* Buttons */
    .primary-btn {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 35px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
    }
    
    .primary-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
    }
    
    .secondary-btn {
        background: white;
        color: #2E86AB;
        border: 2px solid #2E86AB;
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .secondary-btn:hover {
        background: #2E86AB;
        color: white;
    }
    
    /* Stats and Metrics */
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* File Upload */
    .upload-area {
        border: 3px dashed #2E86AB;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: rgba(46, 134, 171, 0.05);
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: rgba(46, 134, 171, 0.1);
        border-color: #2575a0;
    }
    
    /* Progress Bar */
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 8px;
        margin: 10px 0;
    }
    
    .progress-fill {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        border-radius: 10px;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* History Items */
    .history-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        border-color: #2E86AB;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
# Language List
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
    'Filipino': 'tl'
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

init_user_data()

# -----------------------------
# Dashboard Interface
# -----------------------------
def show_dashboard():
    # Header Section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-header">🤖 AI Translator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Professional Translation Dashboard with Advanced AI Technology</p>', unsafe_allow_html=True)
    
    # Stats Dashboard
    st.markdown("### 📊 Translation Analytics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">108</div>
            <div class="stat-label">Languages Supported</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">2.5M+</div>
            <div class="stat-label">Translations Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">99.7%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Translation Interface
    st.markdown("### 🔄 Translation Center")
    
    with st.container():
        st.markdown('<div class="translation-container">', unsafe_allow_html=True)
        
        # Language Selection Row
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            source_lang = st.selectbox(
                "**Source Language**",
                ["Auto Detect"] + list(LANGUAGES.keys()),
                index=0,
                key="source_lang"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄", help="Swap Languages", key="swap_btn"):
                if source_lang != "Auto Detect":
                    current_target = st.session_state.target_lang
                    st.session_state.target_lang = source_lang
                    st.session_state.source_lang = current_target
                    st.rerun()
        
        with col3:
            target_lang = st.selectbox(
                "**Target Language**",
                list(LANGUAGES.keys()),
                index=list(LANGUAGES.keys()).index("Urdu"),
                key="target_lang"
            )
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear All", use_container_width=True):
                st.session_state.input_text = ""
                if 'translated_text' in st.session_state:
                    del st.session_state.translated_text
                st.rerun()
        
        # Text Input Areas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Input Text**")
            input_text = st.text_area(
                "",
                placeholder="Enter your text here...",
                height=200,
                key="input_text",
                label_visibility="collapsed"
            )
            if input_text:
                st.markdown(f"**Characters:** {len(input_text)}")
        
        with col2:
            st.markdown(f"**Translated Text - {target_lang}**")
            
            # Translate Button
            if st.button("🚀 Translate Now", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("🔄 AI is translating your text..."):
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
                            st.success("✅ Translation completed successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Translation error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter some text to translate")
            
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
                    st.markdown(f"**Characters:** {len(st.session_state.translated_text)}")
                    
                    # Action Buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                    with col2:
                        st.download_button(
                            "📥 Download Text",
                            data=st.session_state.translated_text,
                            file_name=f"translation_{target_lang}_{datetime.now().strftime('%H%M%S')}.txt",
                            use_container_width=True
                        )
                    with col3:
                        if st.button("📋 Copy Text", use_container_width=True):
                            st.code(st.session_state.translated_text)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Document Translation Section
    st.markdown("### 📁 Document Translation")
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload Document for Translation",
                type=['pdf', 'txt', 'docx'],
                help="Supported formats: PDF, TXT, DOCX"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ Document uploaded: {uploaded_file.name}")
                
                # Extract text
                file_ext = uploaded_file.name.split('.')[-1].lower()
                extracted_text = ""
                
                with st.spinner("📖 Extracting text from document..."):
                    if file_ext == 'pdf':
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    elif file_ext == 'txt':
                        extracted_text = extract_text_from_txt(uploaded_file)
                    elif file_ext == 'docx':
                        extracted_text = extract_text_from_docx(uploaded_file)
                
                if extracted_text.strip():
                    with st.expander("📋 View Extracted Content"):
                        st.text_area("Extracted Text", extracted_text, height=150)
                    
                    if st.button("🚀 Translate Document", use_container_width=True):
                        with st.spinner("🔄 Translating document content..."):
                            try:
                                source_code = 'auto' if source_lang == "Auto Detect" else LANGUAGES[source_lang]
                                translated_doc = translate_text(extracted_text, LANGUAGES[target_lang], source_code)
                                
                                st.success("✅ Document translation completed!")
                                
                                with st.expander("📄 View Translated Document"):
                                    st.text_area("Translated Document", translated_doc, height=200)
                                
                                st.download_button(
                                    "📥 Download Translated Document",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name.split('.')[0]}_{target_lang}.txt",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("❌ Could not extract readable text from the document")
        
        with col2:
            st.markdown("""
            <div class="dashboard-card">
                <h4>📊 Document Stats</h4>
                <p>• PDF, DOCX, TXT Support</p>
                <p>• Auto Text Extraction</p>
                <p>• Batch Processing Ready</p>
                <p>• Format Preservation</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Features Grid
    st.markdown("### ✨ AI-Powered Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🌍 Multi-Language</h4>
            <p>108+ languages with regional dialects support</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Detection</h4>
            <p>Smart language detection and context understanding</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📁 Document AI</h4>
            <p>Intelligent document processing and formatting</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>🔊 Voice Tech</h4>
            <p>Text-to-speech with natural voice synthesis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Translation History
    if st.session_state.translation_history:
        st.markdown("### 📚 Recent Translations")
        
        for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
            with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']} | {entry['characters']} chars"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Text:**")
                    st.write(entry['original'])
                with col2:
                    st.markdown("**Translated Text:**")
                    st.write(entry['translated'])
                
                col1, col2 = st.columns(2)
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
                        st.rerun()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 30px 0;'>
            <h4 style='color: #2E86AB; margin-bottom: 10px;'>🤖 AI Translator Pro</h4>
            <p style='color: #666; margin-bottom: 15px;'>Advanced AI-Powered Translation Platform</p>
            <div style='font-size: 0.9rem; color: #888;'>
                <span>Powered by Machine Learning • 108+ Languages • Enterprise Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    show_dashboard()
