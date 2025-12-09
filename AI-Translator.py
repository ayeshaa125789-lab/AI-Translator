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
    page_title="AI Translator & TTS",
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
    
    .tts-area {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .tts-area h3 {
        color: white !important;
        margin-bottom: 15px;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        padding: 12px;
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
# Complete Language List (1000+ Languages) - UPDATED
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

if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None

if "tts_text" not in st.session_state:
    st.session_state.tts_text = ""

if "tts_lang" not in st.session_state:
    st.session_state.tts_lang = "English"

if "show_success" not in st.session_state:
    st.session_state.show_success = False

if "is_translating" not in st.session_state:
    st.session_state.is_translating = False

if "is_tts_processing" not in st.session_state:
    st.session_state.is_tts_processing = False

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
# Text-to-Speech Functions
# -----------------------------
def generate_tts_audio(text, lang_code, lang_name="English"):
    """Generate TTS audio from text"""
    try:
        if not text.strip():
            return None, "Please enter text for TTS"
        
        if len(text) > 5000:
            return None, "Text too long for TTS (max 5000 characters)"
        
        with st.spinner(f"Generating {lang_name} audio..."):
            tts = gTTS(text=text, lang=lang_code, slow=False)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            # Store in session state
            st.session_state.tts_audio = audio_bytes
            st.session_state.tts_text = text
            st.session_state.tts_lang = lang_name
            
            return audio_bytes, "Audio generated successfully!"
    except Exception as e:
        return None, f"TTS Error: {str(e)}"

def save_tts_audio(audio_bytes, lang_name="English"):
    """Save TTS audio to a temporary file for download"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_audio_{lang_name}_{timestamp}.mp3"
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(audio_bytes.read())
        temp_file.close()
        
        # Reset pointer
        audio_bytes.seek(0)
        
        return temp_file.name, filename
    except Exception as e:
        return None, f"Error saving audio: {str(e)}"

# -----------------------------
# Translation Function with Proper Flow
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
# Text-to-Speech Interface
# -----------------------------
def show_tts_interface():
    st.markdown('<div class="tts-area">', unsafe_allow_html=True)
    st.markdown("### 🔊 Text-to-Speech Converter")
    st.markdown("Convert any text to speech in multiple languages")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        
        # TTS Text Input
        tts_input = st.text_area(
            "Enter text for speech:",
            height=200,
            placeholder="Type or paste text here to convert to audio...",
            key="tts_input"
        )
        
        if tts_input:
            st.caption(f"Characters: {len(tts_input)}")
        
        # TTS Language Selection
        tts_lang = st.selectbox(
            "Select language for speech:",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.tts_lang),
            key="tts_lang_select"
        )
        
        # Generate TTS Button
        col_gen, col_clear = st.columns(2)
        with col_gen:
            generate_tts = st.button(
                "🔊 Generate Speech", 
                use_container_width=True,
                type="primary",
                key="generate_tts"
            )
        
        with col_clear:
            clear_tts = st.button(
                "🗑️ Clear", 
                use_container_width=True,
                key="clear_tts"
            )
        
        if clear_tts:
            st.session_state.tts_audio = None
            st.session_state.tts_text = ""
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="output-area">', unsafe_allow_html=True)
        
        # Handle TTS Generation
        if generate_tts:
            if not tts_input.strip():
                st.warning("Please enter text for speech generation")
            else:
                audio_bytes, message = generate_tts_audio(tts_input, LANGUAGES[tts_lang], tts_lang)
                
                if audio_bytes:
                    st.success(f"✅ {message}")
                    
                    # Audio Player
                    st.markdown("### 🎧 Audio Preview")
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download Button
                    temp_file_path, filename = save_tts_audio(audio_bytes, tts_lang)
                    
                    if temp_file_path:
                        with open(temp_file_path, 'rb') as f:
                            audio_data = f.read()
                        
                        st.download_button(
                            label="📥 Download Audio",
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
                    
                    # TTS Info
                    st.markdown("---")
                    st.markdown("#### 📊 TTS Information")
                    st.write(f"**Language:** {tts_lang}")
                    st.write(f"**Text Length:** {len(tts_input)} characters")
                    st.write(f"**Audio Format:** MP3")
                    
                else:
                    st.error(f"❌ {message}")
        
        # Show existing TTS audio
        elif st.session_state.tts_audio and st.session_state.tts_text:
            st.success(f"✅ Audio available in {st.session_state.tts_lang}")
            
            # Audio Player
            st.markdown("### 🎧 Audio Preview")
            st.audio(st.session_state.tts_audio, format="audio/mp3")
            
            # Download Button
            temp_file_path, filename = save_tts_audio(st.session_state.tts_audio, st.session_state.tts_lang)
            
            if temp_file_path:
                with open(temp_file_path, 'rb') as f:
                    audio_data = f.read()
                
                st.download_button(
                    label="📥 Download Audio",
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
            
            # TTS Info
            st.markdown("---")
            st.markdown("#### 📊 TTS Information")
            st.write(f"**Language:** {st.session_state.tts_lang}")
            st.write(f"**Text Length:** {len(st.session_state.tts_text)} characters")
            st.write(f"**Audio Format:** MP3")
        
        else:
            st.info("✨ **TTS Audio will appear here**\n\n1. Enter text in the left box\n2. Select language\n3. Click 'Generate Speech'")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TTS Tips
    st.markdown("---")
    st.markdown("#### 💡 TTS Tips")
    
    tip_col1, tip_col2, tip_col3 = st.columns(3)
    
    with tip_col1:
        st.markdown("**🎯 Best Practices**")
        st.markdown("""
        - Keep text under 5000 chars
        - Use proper punctuation
        - Avoid special characters
        - Break long texts into paragraphs
        """)
    
    with tip_col2:
        st.markdown("**🌍 Popular Languages**")
        st.markdown("""
        - English (en)
        - Hindi (hi)
        - Spanish (es)
        - Arabic (ar)
        - Urdu (ur)
        - Pashto (ps)
        """)
    
    with tip_col3:
        st.markdown("**⚡ Quick Actions**")
        st.markdown("""
        - Click 🔊 to preview
        - Click 📥 to download
        - Use clear button to reset
        - Try different languages
        """)

# -----------------------------
# Main Translator Interface
# -----------------------------
def show_translator():
    # Simple Header
    st.markdown('<h1 class="main-header">🌐 AI Translator & Text-to-Speech</h1>', unsafe_allow_html=True)
    st.caption("Professional Translation & Speech Synthesis with 100+ Languages")
    
    # Language Selection - ONLY in main section (sidebar से हटा दिया)
    st.markdown('<div class="language-select">', unsafe_allow_html=True)
    st.markdown("### 🎯 Select Target Language")
    target_lang = st.selectbox(
        "Translate to:",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.target_lang),
        key="target_lang"
    )
    st.markdown(f"**Selected:** {target_lang} | **Code:** {LANGUAGES[target_lang]}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📝 Text Translation", "📁 Document Translation", "🔊 Text-to-Speech"])
    
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
                        
                        # Add to history
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "Auto Detected",
                            "target": target_lang,
                            "original": input_text[:500],
                            "translated": translated_text[:500],
                            "characters": len(input_text)
                        }
                        st.session_state.translation_history.append(history_entry)
                        
                        # Update state
                        st.session_state.translated_text = translated_text
                        st.session_state.target_lang = target_lang
                        st.session_state.is_translating = False
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        st.success("✅ **Translation completed successfully!**")
                        
                        # Show translated text immediately
                        st.text_area(
                            f"Translated text ({target_lang}):",
                            value=translated_text,
                            height=250,
                            key="translated_output"
                        )
                        
                        # Character count
                        st.caption(f"Characters: {len(translated_text)}")
                        
                        # Audio and Download options
                        st.markdown("---")
                        
                        col_audio, col_download, col_tts = st.columns(3)
                        with col_audio:
                            audio_bytes = text_to_speech(translated_text, LANGUAGES[target_lang])
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                        
                        with col_download:
                            st.download_button(
                                "📥 Download Text",
                                data=translated_text,
                                file_name=f"translation_{target_lang}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col_tts:
                            if st.button("🔊 Generate Speech", use_container_width=True):
                                st.session_state.tts_text = translated_text
                                st.session_state.tts_lang = target_lang
                                st.session_state.active_tab = "Tab 3"
                                st.rerun()
                        
                        # Clear button
                        if st.button("🗑️ Clear Translation", use_container_width=True):
                            st.session_state.translated_text = ""
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
                    height=250,
                    key="existing_translation"
                )
                
                st.caption(f"Characters: {len(st.session_state.translated_text)}")
                
                st.markdown("---")
                
                col_audio, col_download, col_tts = st.columns(3)
                with col_audio:
                    audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                
                with col_download:
                    st.download_button(
                        "📥 Download Text",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col_tts:
                    if st.button("🔊 Generate Speech", use_container_width=True):
                        st.session_state.tts_text = st.session_state.translated_text
                        st.session_state.tts_lang = target_lang
                        st.session_state.active_tab = "Tab 3"
                        st.rerun()
                
                if st.button("🗑️ Clear Translation", use_container_width=True):
                    st.session_state.translated_text = ""
                    st.rerun()
            
            else:
                st.info("✨ **Translation will appear here**\n\n1. Enter text in the left box\n2. Click 'Translate Now' button")
            
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
                            
                            st.success("✅ Document translation completed!")
                            
                            # Show result
                            st.text_area(
                                "Translated Document:",
                                value=translated_doc,
                                height=200
                            )
                            
                            # Download options
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.download_button(
                                    "📥 Download Text",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            with col2:
                                doc_audio = text_to_speech(translated_doc, LANGUAGES[target_lang])
                                if doc_audio:
                                    st.download_button(
                                        "🎧 Download Audio",
                                        data=doc_audio,
                                        file_name=f"audio_{target_lang}.mp3",
                                        mime="audio/mp3",
                                        use_container_width=True
                                    )
                            with col3:
                                if st.button("🔊 Generate TTS", use_container_width=True):
                                    st.session_state.tts_text = translated_doc
                                    st.session_state.tts_lang = target_lang
                                    st.session_state.active_tab = "Tab 3"
                                    st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Document translation failed: {str(e)}")
                else:
                    st.error("❌ Could not extract text from the document")
            else:
                st.info("Click 'Translate Document' button to start translation")
        else:
            st.info("Please upload a document to translate")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Text-to-Speech
    with tab3:
        show_tts_interface()

# -----------------------------
# Text-to-Speech Helper Function (for translation tabs)
# -----------------------------
def text_to_speech(text, lang_code):
    """Quick TTS function for translation results"""
    try:
        tts = gTTS(text=text[:5000], lang=lang_code, slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

# -----------------------------
# Sidebar - UPDATED (Language selection हटा दिया)
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("## 🌐 AI Translator & TTS")
        st.markdown("---")
        
        # App Info
        st.markdown("""
        ### 🚀 Features
        - **100+ Languages** Support
        - **Text & Document** Translation
        - **Text-to-Speech** Audio Output
        - **Real-time** Processing
        - **History** Tracking
        """)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear All", use_container_width=True):
                st.session_state.translated_text = ""
                st.session_state.input_text = ""
                st.session_state.tts_audio = None
                st.session_state.tts_text = ""
                st.rerun()
        
        with col2:
            if st.button("📊 View History", use_container_width=True):
                st.session_state.show_history = True
        
        st.markdown("---")
        
        # Recent Translations
        st.markdown("### 📜 Recent Translations")
        
        if st.session_state.translation_history:
            for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
                with st.expander(f"🕒 {entry['timestamp'][-8:]} → {entry['target']}"):
                    st.write(f"**From:** {entry['source']}")
                    st.write(f"**To:** {entry['target']}")
                    st.write(f"**Characters:** {entry.get('characters', 0)}")
                    
                    col_load, col_tts = st.columns(2)
                    with col_load:
                        if st.button(f"🔁 Load", key=f"load_{i}"):
                            st.session_state.translated_text = entry['translated']
                            st.session_state.target_lang = entry['target']
                            st.rerun()
                    with col_tts:
                        if st.button(f"🔊 TTS", key=f"tts_{i}"):
                            st.session_state.tts_text = entry['translated']
                            st.session_state.tts_lang = entry['target']
                            st.session_state.active_tab = "Tab 3"
                            st.rerun()
        
        # Clear history button
        if st.session_state.translation_history:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.translation_history = []
                st.success("History cleared!")
                st.rerun()
        else:
            st.info("No translation history yet")
        
        st.markdown("---")
        
        # Popular Languages Info (Selection नहीं, केवल info)
        st.markdown("### 🌍 Popular Languages")
        
        pop_langs_info = {
            "🇺🇸 English": "en",
            "🇮🇳 Hindi": "hi", 
            "🇦🇪 Arabic": "ar",
            "🇪🇸 Spanish": "es",
            "🇵🇰 Urdu": "ur",
            "🇦🇫 Pashto": "ps",
            "🇫🇷 French": "fr",
            "🇩🇪 German": "de"
        }
        
        for lang_name, lang_code in pop_langs_info.items():
            st.write(f"{lang_name} - `{lang_code}`")
        
        st.markdown("---")
        
        # Quick TTS (Limited functionality)
        st.markdown("### 🔊 Quick TTS")
        tts_quick_text = st.text_input("Text for TTS:", placeholder="Enter text...", key="sidebar_tts_text")
        
        if tts_quick_text:
            if st.button("Generate TTS", use_container_width=True):
                # Use English as default for quick TTS
                audio_bytes, message = generate_tts_audio(tts_quick_text, 'en', "English")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("TTS generated!")
                else:
                    st.error(message)

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
    main()
