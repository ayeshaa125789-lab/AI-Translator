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
    page_title="AI Translator with Speech",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lightweight CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        color: #1f2937;
    }
    
    .simple-card {
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
    
    .speech-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .speech-section h3 {
        color: white !important;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 5px 0;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 5px;
        color: white;
    }
    
    .stat-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: rgba(255,255,255,0.9);
    }
    
    .language-select {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    }
    
    .audio-player {
        background: #1e293b;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Hide Streamlit elements */
    .css-1lsmgbg { display: none; }
    .stDeployButton { display: none; }
    
    /* Progress indicator */
    .progress-container {
        text-align: center;
        padding: 20px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Complete Language List
# -----------------------------
LANGUAGES = {
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Assamese': 'as',
    'Aymara': 'ay',
    'Azerbaijani': 'az',
    'Bambara': 'bm',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bengali': 'bn',
    'Bhojpuri': 'bho',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Corsican': 'co',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dhivehi': 'dv',
    'Dogri': 'doi',
    'Dutch': 'nl',
    'English': 'en',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Ewe': 'ee',
    'Filipino (Tagalog)': 'tl',
    'Finnish': 'fi',
    'French': 'fr',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'German': 'de',
    'Greek': 'el',
    'Guarani': 'gn',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Ilocano': 'ilo',
    'Indonesian': 'id',
    'Irish': 'ga',
    'Italian': 'it',
    'Japanese': 'ja',
    'Javanese': 'jw',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Kinyarwanda': 'rw',
    'Konkani': 'kok',
    'Korean': 'ko',
    'Krio': 'kri',
    'Kurdish (Kurmanji)': 'ku',
    'Kurdish (Sorani)': 'ckb',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latin': 'la',
    'Latvian': 'lv',
    'Lingala': 'ln',
    'Lithuanian': 'lt',
    'Luganda': 'lg',
    'Luxembourgish': 'lb',
    'Macedonian': 'mk',
    'Maithili': 'mai',
    'Malagasy': 'mg',
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Manipuri (Meiteilon)': 'mni',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mizo': 'lus',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Odia (Oriya)': 'or',
    'Oromo': 'om',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Punjabi': 'pa',
    'Quechua': 'qu',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Samoan': 'sm',
    'Sanskrit': 'sa',
    'Scots Gaelic': 'gd',
    'Sepedi': 'nso',
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
    'Tigrinya': 'ti',
    'Tsonga': 'ts',
    'Turkish': 'tr',
    'Turkmen': 'tk',
    'Twi (Akan)': 'ak',
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
# Session State Management
# -----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "translated_audio" not in st.session_state:
    st.session_state.translated_audio = None

if "show_success" not in st.session_state:
    st.session_state.show_success = False

if "is_translating" not in st.session_state:
    st.session_state.is_translating = False

if "auto_speech" not in st.session_state:
    st.session_state.auto_speech = True  # Auto speech generation ON by default

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
def generate_speech_from_text(text, lang_code, lang_name):
    """Generate speech audio from text"""
    try:
        if not text.strip():
            return None, "No text to convert to speech"
        
        if len(text) > 5000:
            text = text[:5000]  # Limit text for TTS
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes, f"Audio generated in {lang_name}"
    except Exception as e:
        return None, f"Speech generation error: {str(e)}"

def save_audio_file(audio_bytes, lang_name):
    """Save audio to temporary file for download"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"speech_{lang_name}_{timestamp}.mp3"
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(audio_bytes.read())
        temp_file.close()
        
        # Reset pointer
        audio_bytes.seek(0)
        
        return temp_file.name, filename
    except Exception as e:
        return None, f"Error saving audio: {str(e)}"

# -----------------------------
# Translation Function
# -----------------------------
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
# Main Translator Interface
# -----------------------------
def show_translator():
    # Simple Header
    st.markdown('<h1 class="main-header">🌐 AI Translator with Auto Speech</h1>', unsafe_allow_html=True)
    st.caption("Translate text and automatically generate speech in the same language")
    
    # Language Selection
    st.markdown('<div class="language-select">', unsafe_allow_html=True)
    st.markdown("### 🎯 Select Language for Translation & Speech")
    target_lang = st.selectbox(
        "Translate to:",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.target_lang),
        key="target_lang"
    )
    st.markdown(f"**Selected:** {target_lang} | **Code:** {LANGUAGES[target_lang]}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto Speech Toggle
    col_toggle, col_info = st.columns([1, 3])
    with col_toggle:
        auto_speech = st.toggle("Auto Generate Speech", value=st.session_state.auto_speech, 
                               help="Automatically generate speech after translation")
    
    with col_info:
        if auto_speech:
            st.success("✅ Speech will be generated automatically after translation")
        else:
            st.info("ℹ️ Speech generation is disabled")
    
    # Tabs
    tab1, tab2 = st.tabs(["📝 Text Translation", "📁 Document Translation"])
    
    # Tab 1: Text Translation
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
            
            # Handle translation flow
            if translate_clicked:
                if not input_text.strip():
                    st.warning("Please enter some text to translate")
                else:
                    # Set translating state
                    st.session_state.is_translating = True
                    
                    # Show progress
                    progress_placeholder = st.empty()
                    with progress_placeholder.container():
                        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                        st.write("⏳ **Translating...**")
                        st.write("Please wait while we process your text")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    try:
                        # Perform translation
                        translated_text = translate_text(input_text, LANGUAGES[target_lang], 'auto')
                        
                        # Generate speech if enabled
                        speech_audio = None
                        if auto_speech:
                            with st.spinner("🎵 Generating speech..."):
                                speech_audio, speech_msg = generate_speech_from_text(
                                    translated_text, 
                                    LANGUAGES[target_lang], 
                                    target_lang
                                )
                        
                        # Add to history
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "Auto Detected",
                            "target": target_lang,
                            "original": input_text[:500],
                            "translated": translated_text[:500],
                            "characters": len(input_text),
                            "speech_generated": auto_speech
                        }
                        st.session_state.translation_history.append(history_entry)
                        
                        # Update state
                        st.session_state.translated_text = translated_text
                        st.session_state.target_lang = target_lang
                        st.session_state.translated_audio = speech_audio
                        st.session_state.auto_speech = auto_speech
                        st.session_state.is_translating = False
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        st.success("✅ **Translation completed successfully!**")
                        
                        if auto_speech and speech_audio:
                            st.success("🎵 **Speech generated successfully!**")
                        
                        # Show translated text
                        st.text_area(
                            f"Translated text ({target_lang}):",
                            value=translated_text,
                            height=200,
                            key="translated_output"
                        )
                        
                        # Character count
                        st.caption(f"Characters: {len(translated_text)}")
                        
                        # Speech Section (if generated)
                        if auto_speech and speech_audio:
                            st.markdown('<div class="speech-section">', unsafe_allow_html=True)
                            st.markdown("### 🔊 Speech Output")
                            
                            # Audio Player
                            st.audio(speech_audio, format="audio/mp3")
                            
                            # Download buttons
                            col_dl1, col_dl2 = st.columns(2)
                            
                            with col_dl1:
                                st.download_button(
                                    "📥 Download Text",
                                    data=translated_text,
                                    file_name=f"translation_{target_lang}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                            with col_dl2:
                                # Save audio for download
                                temp_file_path, filename = save_audio_file(speech_audio, target_lang)
                                
                                if temp_file_path:
                                    with open(temp_file_path, 'rb') as f:
                                        audio_data = f.read()
                                    
                                    st.download_button(
                                        "🎧 Download Speech",
                                        data=audio_data,
                                        file_name=filename,
                                        mime="audio/mp3",
                                        use_container_width=True
                                    )
                                    
                                    # Clean up temp file
                                    try:
                                        os.unlink(temp_file_path)
                                    except:
                                        pass
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            # Only text download if speech not generated
                            st.download_button(
                                "📥 Download Text",
                                data=translated_text,
                                file_name=f"translation_{target_lang}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        # Clear button
                        if st.button("🗑️ Clear All", use_container_width=True):
                            st.session_state.translated_text = ""
                            st.session_state.translated_audio = None
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
                    height=200,
                    key="existing_translation"
                )
                
                st.caption(f"Characters: {len(st.session_state.translated_text)}")
                
                # Show existing speech if available
                if st.session_state.translated_audio:
                    st.markdown('<div class="speech-section">', unsafe_allow_html=True)
                    st.markdown("### 🔊 Speech Output")
                    
                    # Audio Player
                    st.audio(st.session_state.translated_audio, format="audio/mp3")
                    
                    # Download buttons
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            "📥 Download Text",
                            data=st.session_state.translated_text,
                            file_name=f"translation_{target_lang}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        # Save audio for download
                        temp_file_path, filename = save_audio_file(st.session_state.translated_audio, target_lang)
                        
                        if temp_file_path:
                            with open(temp_file_path, 'rb') as f:
                                audio_data = f.read()
                            
                            st.download_button(
                                "🎧 Download Speech",
                                data=audio_data,
                                file_name=filename,
                                mime="audio/mp3",
                                use_container_width=True
                            )
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_file_path)
                            except:
                                pass
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.download_button(
                        "📥 Download Text",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state.translated_text = ""
                    st.session_state.translated_audio = None
                    st.rerun()
            
            else:
                st.info("✨ **Translation will appear here**\n\n1. Enter text in the left box\n2. Click 'Translate Now' button")
                if auto_speech:
                    st.info("🎵 **Speech will be automatically generated** after translation")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Document Translation
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
                            
                            # Generate speech if enabled
                            doc_speech_audio = None
                            if auto_speech:
                                with st.spinner("🎵 Generating speech..."):
                                    doc_speech_audio, _ = generate_speech_from_text(
                                        translated_doc[:5000],  # Limit for speech
                                        LANGUAGES[target_lang], 
                                        target_lang
                                    )
                            
                            st.success("✅ Document translation completed!")
                            
                            # Show result
                            st.text_area(
                                "Translated Document:",
                                value=translated_doc,
                                height=200
                            )
                            
                            # Speech Section for document
                            if auto_speech and doc_speech_audio:
                                st.markdown('<div class="speech-section">', unsafe_allow_html=True)
                                st.markdown("### 🔊 Document Speech Output")
                                
                                # Audio Player
                                st.audio(doc_speech_audio, format="audio/mp3")
                                
                                # Download options
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "📥 Download Text",
                                        data=translated_doc,
                                        file_name=f"translated_{uploaded_file.name}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                with col2:
                                    # Save audio for download
                                    temp_file_path, filename = save_audio_file(doc_speech_audio, target_lang)
                                    
                                    if temp_file_path:
                                        with open(temp_file_path, 'rb') as f:
                                            audio_data = f.read()
                                        
                                        st.download_button(
                                            "🎧 Download Speech",
                                            data=audio_data,
                                            file_name=filename,
                                            mime="audio/mp3",
                                            use_container_width=True
                                        )
                                        
                                        # Clean up temp file
                                        try:
                                            os.unlink(temp_file_path)
                                        except:
                                            pass
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                # Only text download if speech not generated
                                st.download_button(
                                    "📥 Download Text",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                        except Exception as e:
                            st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("❌ Could not extract text from the document")
            else:
                st.info("Click 'Translate Document' button to start translation")
                if auto_speech:
                    st.info("🎵 Speech will be automatically generated with translation")
        else:
            st.info("Please upload a document to translate")
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("## 🌐 AI Translator")
        st.markdown("---")
        
        # App Info
        st.markdown("""
        ### 🚀 Features
        - **100+ Languages** Support
        - **Auto Speech Generation**
        - **Text & Document** Translation
        - **Real-time** Processing
        - **History** Tracking
        """)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.translated_text = ""
            st.session_state.input_text = ""
            st.session_state.translated_audio = None
            st.rerun()
        
        if st.button("📊 View Full History", use_container_width=True):
            st.session_state.show_history = True
        
        st.markdown("---")
        
        # Recent Translations
        st.markdown("### 📜 Recent Translations")
        
        if st.session_state.translation_history:
            for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
                with st.expander(f"🕒 {entry['timestamp'][-8:]} → {entry['target']}"):
                    st.write(f"**From:** {entry['source']}")
                    st.write(f"**To:** {entry['target']}")
                    st.write(f"**Chars:** {entry.get('characters', 0)}")
                    if entry.get('speech_generated'):
                        st.write("🎵 **Speech:** Generated")
                    
                    if st.button(f"🔁 Load", key=f"load_{i}", use_container_width=True):
                        st.session_state.translated_text = entry['translated']
                        st.session_state.target_lang = entry['target']
                        st.rerun()
        
        # Clear history
        if st.session_state.translation_history:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.translation_history = []
                st.success("History cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Popular Languages
        st.markdown("### 🌍 Popular Languages")
        pop_langs = [
            ("🇺🇸 English", "en"),
            ("🇮🇳 Hindi", "hi"),
            ("🇦🇪 Arabic", "ar"),
            ("🇪🇸 Spanish", "es"),
            ("🇵🇰 Urdu", "ur"),
            ("🇦🇫 Pashto", "ps"),
            ("🇫🇷 French", "fr"),
            ("🇩🇪 German", "de")
        ]
        
        for lang_name, lang_code in pop_langs:
            st.write(f"{lang_name} - `{lang_code}`")

# -----------------------------
# Main App
# -----------------------------
def main():
    show_sidebar()
    show_translator()
    
    # Platform Stats at Bottom
    st.markdown("---")
    st.write("### 📊 Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(LANGUAGES)}+</div>
            <div class="stat-label">Languages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">99.8%</div>
            <div class="stat-label">Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        translations_count = len(st.session_state.translation_history)
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{translations_count}</div>
            <div class="stat-label">Translations</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()s
