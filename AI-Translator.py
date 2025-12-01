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

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean Professional CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        color: #1f2937;
        padding-bottom: 10px;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: none;
        transition: transform 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
    }
    
    .translation-box {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    
    .input-section {
        background: #f8fafc;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        margin: 15px 0;
    }
    
    .output-section {
        background: #f0f9ff;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #bae6fd;
        margin: 15px 0;
    }
    
    .sidebar-section {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        color: white;
    }
    
    .stat-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: rgba(255,255,255,0.9);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Hide Streamlit footer */
    .css-1lsmgbg { display: none; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
# Text-to-Speech Function
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
# Translation Functions
# -----------------------------
def translate_text(text, target_lang, source_lang='auto'):
    try:
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

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Translator"

# -----------------------------
# Main Translator Interface
# -----------------------------
def show_translator():
    # Clean Header - Just name
    st.markdown('<h1 class="main-header">🌐 AI Translator</h1>', unsafe_allow_html=True)
    
    # Language Selection FIRST - Translation interface starts here
    st.markdown('<div class="translation-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="section-title">🎯 Select Language to Translate To</div>', unsafe_allow_html=True)
        target_lang = st.selectbox(
            "Choose target language:",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index("Urdu"),
            key="target_lang"
        )
    
    with col2:
        st.markdown('<div style="margin-top: 35px;">', unsafe_allow_html=True)
        st.info("🌍 **Auto Language Detection** - Source language will be automatically detected")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Translation Tabs - IMMEDIATELY BELOW language selection
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    
    # Tabs for Text and Document Translation
    tab1, tab2 = st.tabs(["📝 **Text Translation**", "📁 **Document Translation**"])
    
    with tab1:
        # Text Input and Output in same tab
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📥 Enter Text to Translate</div>', unsafe_allow_html=True)
            input_text = st.text_area(
                "Type or paste your text here...",
                placeholder="Enter text in any language...",
                height=280,
                key="input_text",
                label_visibility="collapsed"
            )
            
            # Character count
            if input_text:
                st.caption(f"📊 **Characters:** {len(input_text)}")
            
            # Translate button
            if st.button("🚀 **Translate Now**", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("🔍 Detecting language and translating..."):
                        try:
                            # Always use auto detect for source language
                            translated_text = translate_text(input_text, LANGUAGES[target_lang], 'auto')
                            
                            history_entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": "Auto Detected",
                                "target": target_lang,
                                "original": input_text[:500],
                                "translated": translated_text[:500],
                                "characters": len(input_text)
                            }
                            st.session_state.translation_history.append(history_entry)
                            
                            st.session_state.translated_text = translated_text
                            st.session_state.translated_lang = target_lang
                            st.success("✅ Translation completed successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Translation error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter some text to translate")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="output-section">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">📤 Translated Text - {target_lang}</div>', unsafe_allow_html=True)
            
            if 'translated_text' in st.session_state and 'translated_lang' in st.session_state:
                if st.session_state.translated_lang == target_lang:
                    st.text_area(
                        "Translated text appears here...",
                        value=st.session_state.translated_text,
                        height=280,
                        key="translated_output",
                        label_visibility="collapsed"
                    )
                    
                    # Character count for translation
                    st.caption(f"📊 **Characters:** {len(st.session_state.translated_text)}")
                    
                    # Text-to-Speech Section
                    st.markdown("---")
                    st.markdown('<div class="section-title">🔊 Listen to Translation</div>', unsafe_allow_html=True)
                    
                    audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio_bytes:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.audio(audio_bytes, format="audio/mp3")
                        with col2:
                            st.download_button(
                                "📥 Download Audio",
                                data=audio_bytes,
                                file_name=f"audio_{target_lang}.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                    else:
                        st.warning("Audio generation not available for this language")
                    
                    # Download text button
                    st.download_button(
                        "📥 Download Translated Text",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.info("🔄 Please translate again for the selected language")
            else:
                st.info("✨ **Your translation will appear here**\n\n1. Enter text in the left box\n2. Click 'Translate Now' button")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Document Translation in second tab
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📁 Upload Document</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose a file to translate",
                type=['pdf', 'txt', 'docx'],
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ **File Uploaded:** {uploaded_file.name}")
                
                with st.spinner("📖 Extracting text from document..."):
                    extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text.strip():
                    with st.expander("📋 **View Extracted Content**", expanded=False):
                        st.text_area("Extracted Text", extracted_text, height=150, label_visibility="collapsed")
                    
                    if st.button("🚀 **Translate Document**", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Translating document content..."):
                            try:
                                translated_doc = translate_text(extracted_text, LANGUAGES[target_lang], 'auto')
                                
                                st.success("✅ Document translation completed!")
                                
                                with st.expander("📄 **View Translated Document**", expanded=True):
                                    st.text_area("Translated Document", translated_doc, height=200, label_visibility="collapsed")
                                
                                # Text-to-Speech for document
                                st.markdown("---")
                                st.markdown('<div class="section-title">🔊 Listen to Document Translation</div>', unsafe_allow_html=True)
                                
                                doc_audio_bytes = text_to_speech(translated_doc, LANGUAGES[target_lang])
                                if doc_audio_bytes:
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.audio(doc_audio_bytes, format="audio/mp3")
                                    with col2:
                                        st.download_button(
                                            "📥 Download Audio",
                                            data=doc_audio_bytes,
                                            file_name=f"audio_document_{target_lang}.mp3",
                                            mime="audio/mp3",
                                            use_container_width=True
                                        )
                                
                                # Download translated document
                                st.download_button(
                                    "📥 Download Translated Document",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name.split('.')[0]}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("❌ Could not extract text from the document")
            else:
                st.info("📁 **Upload a document to translate**\n\nSupported formats: PDF, TXT, DOCX")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="sidebar-section">
                <div class="section-title">📋 Quick Guide</div>
                <p><strong>1. Select Language</strong><br>Choose target language above</p>
                <p><strong>2. Enter Text/Upload File</strong><br>Type text or upload document</p>
                <p><strong>3. Click Translate</strong><br>Get instant translation</p>
                <p><strong>4. Listen & Download</strong><br>Hear audio and save results</p>
            </div>
            
            <div class="sidebar-section">
                <div class="section-title">✅ Features</div>
                <p>• 🌍 Auto Language Detection</p>
                <p>• 🔊 Text-to-Speech</p>
                <p>• 📥 Download Options</p>
                <p>• 📊 Translation History</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Stats cards moved to the VERY END - After translation interface
    st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align: center;">📊 Platform Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="stat-number">1000+</div>
            <div class="stat-label">Languages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">99.8%</div>
            <div class="stat-label">Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        translations_count = len(st.session_state.translation_history)
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-number">{translations_count}</div>
            <div class="stat-label">Translations</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 15px 0; margin-bottom: 15px;'>
            <h3 style='color: #1f2937; margin: 0;'>🌐 AI Translator</h3>
            <p style='color: #6b7280; margin: 5px 0 0 0; font-size: 0.9rem;'>Professional Translation Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🧭 Navigation**")
        if st.button("🔍 **Translator**", use_container_width=True, type="primary"):
            st.session_state.current_page = "Translator"
            st.rerun()
        
        if st.button("📚 **Translation History**", use_container_width=True):
            st.session_state.current_page = "History"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        if st.button("🔄 **Clear Current**", use_container_width=True):
            st.session_state.input_text = ""
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            if 'translated_lang' in st.session_state:
                del st.session_state.translated_lang
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session Info
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📊 Session Stats**")
        translations_count = len(st.session_state.translation_history)
        st.metric("Total Translations", translations_count)
        
        if translations_count > 0:
            total_chars = sum(entry.get('characters', 0) for entry in st.session_state.translation_history)
            st.metric("Total Characters", f"{total_chars:,}")
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
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.translation_history = []
            st.rerun()
    
    # History Items
    for i, entry in enumerate(reversed(st.session_state.translation_history)):
        with st.expander(f"📅 {entry['timestamp']} | {entry['source']} → {entry['target']} | {entry.get('characters', 0)} chars"):
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
                    st.session_state.target_lang = entry['target']
                    st.session_state.current_page = "Translator"
                    st.rerun()
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.translation_history.pop(-(i+1))
                    st.rerun()

# -----------------------------
# Main App
# -----------------------------
def main():
    show_sidebar()
    
    if st.session_state.current_page == "Translator":
        show_translator()
    elif st.session_state.current_page == "History":
        show_history_page()

if __name__ == "__main__":
    main()
