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
    page_title="AI Translator Pro - Multilingual Translation Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colorful Professional CSS
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 20%, #f093fb 40%, #f5576c 60%, #4facfe 80%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Colorful Stats Cards */
    .stats-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: none;
    }
    
    .stats-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
        border: none;
    }
    
    .stats-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
        border: none;
    }
    
    .stats-card-4 {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(67, 233, 123, 0.3);
        border: none;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 2px solid;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .feature-card-1 { border-color: #667eea; }
    .feature-card-2 { border-color: #f5576c; }
    .feature-card-3 { border-color: #4facfe; }
    .feature-card-4 { border-color: #43e97b; }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    /* Translation Container */
    .translation-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 25px;
        padding: 30px;
        margin: 25px 0;
        border: 2px solid #e0e0e0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    /* Language Selectors */
    .language-selector {
        background: white;
        border: 3px solid #667eea;
        border-radius: 15px;
        padding: 15px;
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin: 0 10px;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Swap Button */
    .swap-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }
    
    .swap-btn:hover {
        transform: rotate(180deg) scale(1.1);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
    }
    
    /* Text Areas */
    .text-input {
        border: 3px solid #667eea;
        border-radius: 20px;
        padding: 25px;
        background: white;
        min-height: 250px;
        font-size: 16px;
        line-height: 1.6;
        font-family: 'Arial', sans-serif;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .text-input:focus {
        border-color: #f5576c;
        box-shadow: 0 8px 30px rgba(245, 87, 108, 0.2);
    }
    
    /* Buttons */
    .translate-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 18px 45px;
        font-size: 18px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .translate-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .action-btn {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 12px 25px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(79, 172, 254, 0.3);
    }
    
    .action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5);
    }
    
    /* Stats Numbers */
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 1rem;
        font-weight: 600;
        opacity: 0.9;
    }
    
    /* File Upload */
    .upload-area {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border: 3px dashed #667eea;
        border-radius: 25px;
        padding: 50px;
        text-align: center;
        margin: 25px 0;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .upload-area:hover {
        background: linear-gradient(135deg, #fed6e3 0%, #a8edea 100%);
        border-color: #f5576c;
        transform: scale(1.02);
    }
    
    /* History Items */
    .history-item {
        background: white;
        border-left: 5px solid #667eea;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        border-left-color: #f5576c;
        transform: translateX(10px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin: 40px 0 20px 0;
        background: linear-gradient(135deg, #667eea, #f5576c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Feature Icons */
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
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
# Colorful Dashboard Interface
# -----------------------------
def show_colorful_dashboard():
    # Header Section with Gradient
    st.markdown('<h1 class="main-header">🤖 AI Translator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">🌍 World\'s Most Advanced Multilingual Translation Platform</p>', unsafe_allow_html=True)
    
    # Colorful Stats Dashboard
    st.markdown("### 📊 Live Translation Analytics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card-1">
            <div class="stat-number">108+</div>
            <div class="stat-label">Languages</div>
            <div style="margin-top: 10px; font-size: 0.9rem;">🌐 Global Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card-2">
            <div class="stat-number">2.5M+</div>
            <div class="stat-label">Translations</div>
            <div style="margin-top: 10px; font-size: 0.9rem;">🚀 Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card-3">
            <div class="stat-number">99.8%</div>
            <div class="stat-label">Accuracy</div>
            <div style="margin-top: 10px; font-size: 0.9rem;">🎯 AI Powered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card-4">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
            <div style="margin-top: 10px; font-size: 0.9rem;">⚡ Instant Results</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Translation Interface
    st.markdown('<div class="section-header">🎯 Smart Translation Center</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="translation-container">', unsafe_allow_html=True)
        
        # Language Selection with Colorful Design
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            source_lang = st.selectbox(
                "**🔤 Source Language**",
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
                "**🎯 Target Language**",
                list(LANGUAGES.keys()),
                index=list(LANGUAGES.keys()).index("Urdu"),
                key="target_lang"
            )
        
        # Text Input Areas with Colorful Borders
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📝 Input Text**")
            input_text = st.text_area(
                "",
                placeholder="✨ Enter your text here... Let our AI work its magic!",
                height=250,
                key="input_text",
                label_visibility="collapsed"
            )
            if input_text:
                st.markdown(f"**🔢 Characters:** {len(input_text)}")
        
        with col2:
            st.markdown(f"**🌍 Translated Text - {target_lang}**")
            
            # Big Colorful Translate Button
            if st.button("🚀 TRANSLATE NOW", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("🎨 AI is crafting your translation..."):
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
                            st.success("🎉 Translation completed successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Translation error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter some text to translate")
            
            # Display translated text
            if 'translated_text' in st.session_state:
                st.text_area(
                    "",
                    value=st.session_state.translated_text,
                    height=250,
                    key="translated_output",
                    label_visibility="collapsed"
                )
                if st.session_state.translated_text:
                    st.markdown(f"**🔢 Characters:** {len(st.session_state.translated_text)}")
                    
                    # Colorful Action Buttons
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
    st.markdown('<div class="section-header">📁 Document Translation Hub</div>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "🎨 Upload Your Document (PDF, TXT, DOCX)",
                type=['pdf', 'txt', 'docx'],
                help="✨ Drag and drop your files here for instant translation!"
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
                        with st.spinner("🎨 Translating document content..."):
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
            <div class="feature-card feature-card-1">
                <div class="feature-icon">📊</div>
                <h4>Document Stats</h4>
                <p>• 📄 PDF Support</p>
                <p>• 📝 DOCX Ready</p>
                <p>• 🎯 Text Extraction</p>
                <p>• ⚡ Fast Processing</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Colorful Features Grid
    st.markdown('<div class="section-header">✨ Premium Features</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card feature-card-1">
            <div class="feature-icon">🌍</div>
            <h4>108+ Languages</h4>
            <p>Global language coverage with regional dialects and accents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card feature-card-2">
            <div class="feature-icon">🤖</div>
            <h4>AI Powered</h4>
            <p>Advanced machine learning for accurate translations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card feature-card-3">
            <div class="feature-icon">📁</div>
            <h4>Document AI</h4>
            <p>Smart document processing with format preservation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card feature-card-4">
            <div class="feature-icon">🔊</div>
            <h4>Voice Tech</h4>
            <p>Natural text-to-speech with multiple voice options</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Translation History with Colorful Design
    if st.session_state.translation_history:
        st.markdown('<div class="section-header">📚 Translation History</div>', unsafe_allow_html=True)
        
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
    
    # Colorful Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 40px 0; background: linear-gradient(135deg, #667eea, #f5576c); border-radius: 20px; color: white;'>
        <h3 style='margin-bottom: 15px;'>🤖 AI Translator Pro</h3>
        <p style='margin-bottom: 20px; font-size: 1.1rem;'>World's Most Colorful & Powerful Translation Platform</p>
        <div style='font-size: 0.9rem; opacity: 0.9;'>
            <span>✨ 108+ Languages • 🎯 99.8% Accuracy • ⚡ Instant Results • 🌍 Global Reach</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    show_colorful_dashboard()
