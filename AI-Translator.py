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

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="🤖 AI Translator Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .feature-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        margin: 10px 0px;
    }
    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🤖 AI Translator Pro</h1>', unsafe_allow_html=True)
st.markdown("### 🚀 Intelligent Translation with PDF Support & Text-to-Speech")

# -----------------------------
# Language List
# -----------------------------
LANGUAGES = {
    'Auto Detect': 'auto',
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
    """Extract text from PDF file"""
    try:
        text = ""
        # Method 1: Using pdfplumber (better for text extraction)
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text.strip()
        
        # Method 2: Using PyPDF2 as fallback
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
        # Using gTTS for better language support
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        # Fallback to pyttsx3
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
        # Handle Roman Urdu detection
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

# -----------------------------
# Main App Interface
# -----------------------------

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Features")
    
    # Translation Settings
    st.subheader("🔤 Translation")
    source_lang = st.selectbox(
        "From Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index("English")
    )
    
    target_lang = st.selectbox(
        "To Language",
        [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
        index=list(LANGUAGES.keys()).index("Urdu")
    )
    
    # Speech Settings
    st.subheader("🔊 Speech")
    enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
    slow_speech = st.checkbox("Slow Speech", value=False)
    
    # File Settings
    st.subheader("📁 File Support")
    st.info("""
    Supported formats:
    - 📄 PDF Documents
    - 📝 Text Files (.txt)
    - 📋 Word Documents (.docx)
    """)
    
    st.markdown("---")
    st.subheader("🎯 Quick Actions")
    
    if st.button("Clear All", use_container_width=True):
        st.session_state.input_text = ""
        st.rerun()
    
    if st.button("Show History", use_container_width=True):
        st.session_state.show_history = True

# Main Content Area
st.markdown("### 📝 Text Translation")

# Input Methods Tabs
tab1, tab2 = st.tabs(["✏️ Type Text", "📁 Upload File"])

with tab1:
    input_text = st.text_area(
        "Enter text to translate:",
        placeholder="Type or paste your text here...\nExamples:\n• English: Hello, how are you?\n• Roman Urdu: tum kaisay ho?\n• Any other language...",
        height=150,
        key="text_input"
    )

with tab2:
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'docx'],
        help="Upload PDF, TXT, or DOCX files for translation"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Extract text based on file type
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
            st.text_area("Extracted Text", extracted_text, height=150)
            input_text = extracted_text
        else:
            st.error("Could not extract text from the file")

# Translate Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    translate_btn = st.button("🚀 TRANSLATE NOW", use_container_width=True, type="primary")

st.markdown("---")

# -----------------------------
# Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("🔄 Translating..."):
            # Perform translation
            if source_lang == 'Auto Detect':
                # Auto-detection with Roman Urdu support
                if detect_roman_urdu(input_text):
                    detected_source = "Roman Urdu"
                    source_code = 'ur'
                else:
                    detected_source = "Auto-Detected"
                    source_code = 'auto'
            else:
                detected_source = source_lang
                source_code = LANGUAGES[source_lang]
            
            translated_text = translate_text(input_text, LANGUAGES[target_lang], source_code)
            
            # Display Results
            st.subheader("🎉 Translation Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📥 Original Text ({detected_source})**")
                st.text_area(
                    "Original Text",
                    input_text,
                    height=200,
                    key="original_output",
                    label_visibility="collapsed"
                )
                st.caption(f"Source: {detected_source} | Characters: {len(input_text)}")
                
            with col2:
                st.markdown(f"**📤 Translated Text ({target_lang})**")
                st.text_area(
                    "Translated Text",
                    translated_text,
                    height=200,
                    key="translated_output",
                    label_visibility="collapsed"
                )
                st.caption(f"Target: {target_lang} | Characters: {len(translated_text)}")
            
            # Text-to-Speech Section
            if enable_tts:
                st.subheader("🔊 Audio Output")
                
                audio_bytes = text_to_speech_enhanced(translated_text, LANGUAGES[target_lang], slow_speech)
                
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download audio button
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_bytes,
                        file_name=f"translation_{target_lang}_{datetime.now().strftime('%H%M%S')}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                    
                    st.success(f"🎧 Listen to the {target_lang} translation")
                else:
                    st.warning("Audio generation failed for this language")
            
            # Save to translation history
            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": detected_source,
                "target": target_lang,
                "original": input_text,
                "translated": translated_text
            }
            st.session_state.translation_history.append(history_entry)
            
            # Success message
            st.balloons()
            st.success("✅ Translation completed successfully!")

    except Exception as e:
        st.error(f"❌ Translation error: {str(e)}")

elif translate_btn:
    st.warning("⚠️ Please enter some text or upload a file to translate")

# -----------------------------
# Translation History
# -----------------------------
if st.session_state.translation_history:
    st.markdown("---")
    st.subheader("📚 Translation History")
    
    # Show last 5 translations
    for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
        with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.write(entry['original'])
            with col2:
                st.markdown("**Translated Text:**")
                st.write(entry['translated'])
            
            # Audio replay and actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🔊 Play Audio", key=f"audio_{i}"):
                    audio_bytes = text_to_speech_enhanced(entry['translated'], LANGUAGES[entry['target']])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
            with col2:
                st.download_button(
                    label="📥 Download Text",
                    data=entry['translated'],
                    file_name=f"translation_{entry['target']}_{i}.txt",
                    key=f"download_{i}"
                )
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.translation_history.pop(-(i+1))
                    st.rerun()

# -----------------------------
# Features Section
# -----------------------------
st.markdown("---")
st.subheader("✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-box">' +
                '<h4>🔤 100+ Languages</h4>' +
                '<p>Support for all major languages including Pashto, Urdu, Arabic, and more</p>' +
                '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box">' +
                '<h4>📁 PDF Support</h4>' +
                '<p>Upload and translate PDF, TXT, and DOCX files with text extraction</p>' +
                '</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-box">' +
                '<h4>🔊 Text-to-Speech</h4>' +
                '<p>Listen to translations with high-quality audio output</p>' +
                '</div>', unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center;'>
    <h4>🤖 AI Translator Pro</h4>
    <p>Professional Translation Tool with PDF Support & Text-to-Speech</p>
    <p><b>Powered by:</b> Streamlit • Google Translate • gTTS • PyPDF2</p>
</div>
""", unsafe_allow_html=True)

st.caption("© 2024 AI Translator Pro - All rights reserved")
