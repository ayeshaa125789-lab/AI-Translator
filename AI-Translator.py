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
    page_title="Translate - Professional AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Google Translate Style
st.markdown("""
<style>
    /* Main Container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header */
    .header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #e8eaed;
        margin-bottom: 30px;
    }
    
    .logo {
        font-size: 32px;
        font-weight: 500;
        color: #1a73e8;
        margin-bottom: 8px;
    }
    
    .tagline {
        font-size: 16px;
        color: #5f6368;
        margin-bottom: 20px;
    }
    
    /* Translation Box */
    .translation-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #dadce0;
    }
    
    .language-selector {
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        margin: 0 8px;
    }
    
    .swap-button {
        background: #f8f9fa;
        border: 1px solid #dadce0;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin: 0 12px;
    }
    
    .swap-button:hover {
        background: #e8f0fe;
        border-color: #1a73e8;
    }
    
    /* Text Areas */
    .text-area {
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 16px;
        background: white;
        min-height: 200px;
        font-size: 16px;
        line-height: 1.5;
    }
    
    .text-area:focus {
        border-color: #1a73e8;
        box-shadow: 0 0 0 2px #e8f0fe;
    }
    
    /* Buttons */
    .translate-btn {
        background: #1a73e8;
        color: white;
        border: none;
        border-radius: 24px;
        padding: 12px 32px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .translate-btn:hover {
        background: #1669d6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    .secondary-btn {
        background: white;
        color: #1a73e8;
        border: 1px solid #dadce0;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        cursor: pointer;
        margin: 0 4px;
    }
    
    .secondary-btn:hover {
        background: #f8f9fa;
    }
    
    /* Stats */
    .stats {
        font-size: 12px;
        color: #5f6368;
        text-align: right;
        margin-top: 8px;
    }
    
    /* Features */
    .feature-card {
        background: white;
        border: 1px solid #dadce0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 8px;
    }
    
    .feature-icon {
        font-size: 24px;
        margin-bottom: 12px;
    }
    
    /* Language Badge */
    .language-badge {
        background: #e8f0fe;
        color: #1a73e8;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 500;
        margin: 0 4px;
    }
    
    /* File Upload */
    .upload-area {
        border: 2px dashed #dadce0;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #f8f9fa;
        margin: 16px 0;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #1a73e8;
        background: #f0f7ff;
    }
    
    /* History Item */
    .history-item {
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background: white;
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
    st.session_state.source_lang = "Detect language"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

init_user_data()

# -----------------------------
# Main App Interface
# -----------------------------
def main():
    # Header
    st.markdown("""
    <div class="main-container">
        <div class="header">
            <div class="logo">Translate</div>
            <div class="tagline">Professional translation service supporting 100+ languages</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Translation Interface
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        source_lang = st.selectbox(
            "",
            ["Detect language"] + list(LANGUAGES.keys()),
            index=0,
            key="source_lang"
        )
    
    with col2:
        st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 60px;'>", unsafe_allow_html=True)
        if st.button("⇄", help="Swap languages"):
            if source_lang != "Detect language":
                current_target = st.session_state.target_lang
                st.session_state.target_lang = source_lang
                st.session_state.source_lang = current_target
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        target_lang = st.selectbox(
            "",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index("Urdu"),
            key="target_lang"
        )
    
    # Text Input Areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Source text**")
        input_text = st.text_area(
            "",
            placeholder="Enter text...",
            height=200,
            key="input_text",
            label_visibility="collapsed"
        )
        if input_text:
            st.markdown(f'<div class="stats">{len(input_text)} characters</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Translation - {target_lang}**")
        
        # Translate Button
        if st.button("Translate", use_container_width=True, type="primary"):
            if input_text.strip():
                with st.spinner("Translating..."):
                    try:
                        source_code = 'auto' if source_lang == "Detect language" else LANGUAGES[source_lang]
                        translated_text = translate_text(input_text, LANGUAGES[target_lang], source_code)
                        
                        # Save to history
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": source_lang,
                            "target": target_lang,
                            "original": input_text[:300],
                            "translated": translated_text[:300]
                        }
                        st.session_state.translation_history.append(history_entry)
                        
                        st.session_state.translated_text = translated_text
                        st.success("Translation completed")
                        
                    except Exception as e:
                        st.error(f"Translation error: {str(e)}")
            else:
                st.warning("Please enter text to translate")
        
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
                st.markdown(f'<div class="stats">{len(st.session_state.translated_text)} characters</div>', unsafe_allow_html=True)
                
                # Audio and Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                with col2:
                    st.download_button(
                        "Download translation",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        use_container_width=True
                    )
    
    # File Upload Section
    st.markdown("---")
    st.markdown("### Document Translation")
    
    uploaded_file = st.file_uploader(
        "Upload document for translation",
        type=['pdf', 'txt', 'docx'],
        help="Supported formats: PDF, TXT, DOCX"
    )
    
    if uploaded_file is not None:
        st.info(f"File uploaded: {uploaded_file.name}")
        
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
            st.text_area("Extracted content", extracted_text, height=150)
            
            if st.button("Translate Document", use_container_width=True):
                with st.spinner("Translating document..."):
                    try:
                        source_code = 'auto' if source_lang == "Detect language" else LANGUAGES[source_lang]
                        translated_doc = translate_text(extracted_text, LANGUAGES[target_lang], source_code)
                        
                        st.text_area("Translated document", translated_doc, height=200)
                        
                        st.download_button(
                            "Download translated document",
                            data=translated_doc,
                            file_name=f"translated_{uploaded_file.name.split('.')[0]}_{target_lang}.txt",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Document translation failed: {str(e)}")
        else:
            st.error("Could not extract text from the document")
    
    # Features Section
    st.markdown("---")
    st.markdown("### Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <h4>100+ Languages</h4>
            <p>Support for major world languages and regional dialects</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h4>Auto Detection</h4>
            <p>Automatically detect source language</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📁</div>
            <h4>Document Support</h4>
            <p>Translate PDF, Word, and text files</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔊</div>
            <h4>Text-to-Speech</h4>
            <p>Listen to translations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Translation History
    if st.session_state.translation_history:
        st.markdown("---")
        st.markdown("### Recent Translations")
        
        for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
            with st.expander(f"{entry['timestamp']} | {entry['source']} → {entry['target']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area(f"Original {i}", entry['original'], height=100, key=f"orig_{i}")
                with col2:
                    st.text_area(f"Translated {i}", entry['translated'], height=100, key=f"trans_{i}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 40px 0; color: #5f6368;'>
        <h4 style='color: #1a73e8; margin-bottom: 8px;'>Translate</h4>
        <p style='margin-bottom: 16px;'>Professional translation service</p>
        <div style='font-size: 12px;'>
            <span>Supporting 100+ languages • Accurate translations • Secure processing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()
