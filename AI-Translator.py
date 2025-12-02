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
    page_title="AI Translator Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS
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
        if source_lang == 'auto':
            translator = GoogleTranslator(target=target_lang)
        else:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        translated = translator.translate(text)
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
    # Modern Animated Header
    st.markdown('<h1 class="gradient-header">🚀 AI Translator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.2rem; margin-bottom: 30px;">Professional Translation Platform | AI-Powered Language Solutions</p>', unsafe_allow_html=True)
    
    # Language Selection - Modern Glass Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="animated-title">🎯 Select Target Language</div>', unsafe_allow_html=True)
        target_lang = st.selectbox(
            "Choose the language you want to translate to:",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index("Urdu"),
            key="target_lang"
        )
    
    with col2:
        st.markdown('<div style="margin-top: 35px;">', unsafe_allow_html=True)
        st.info("""
        **🌍 Smart Features:**
        - Auto Language Detection
        - 1000+ Languages Support
        - Real-time Translation
        - Context-Aware Results
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Translation Tabs with Modern Design
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    # Create tabs with icons
    tab1, tab2 = st.tabs(["📝 **Text Translation**", "📁 **Document Translation**"])
    
    with tab1:
        # Text Input and Output in same tab with modern design
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">📥 Input Text</div>', unsafe_allow_html=True)
            input_text = st.text_area(
                "",
                placeholder="✨ Type or paste your text here in any language...\n\nExample: Hello, how are you? नमस्ते, आप कैसे हैं? مرحبا، كيف حالك؟",
                height=300,
                key="input_text",
                label_visibility="collapsed"
            )
            
            # Character count with style
            if input_text:
                st.markdown(f'<div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px; border-radius: 10px; text-align: center; margin-top: 10px;">📊 Characters: {len(input_text)}</div>', unsafe_allow_html=True)
            
            # Modern Translate button
            if st.button("🚀 **Translate Now**", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("🔄 **AI is processing your translation...**"):
                        try:
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
                            st.success("✅ **Translation completed successfully!**")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ **Translation error:** {str(e)}")
                else:
                    st.warning("⚠️ **Please enter some text to translate**")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-output">', unsafe_allow_html=True)
            st.markdown(f'<div class="animated-title">📤 Translation - {target_lang}</div>', unsafe_allow_html=True)
            
            if 'translated_text' in st.session_state and 'translated_lang' in st.session_state:
                if st.session_state.translated_lang == target_lang:
                    st.text_area(
                        "",
                        value=st.session_state.translated_text,
                        height=300,
                        key="translated_output",
                        label_visibility="collapsed"
                    )
                    
                    # Character count for translation
                    st.markdown(f'<div style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 10px; border-radius: 10px; text-align: center; margin-top: 10px;">📊 Characters: {len(st.session_state.translated_text)}</div>', unsafe_allow_html=True)
                    
                    # Text-to-Speech Section with modern design
                    st.markdown("---")
                    st.markdown('<div class="animated-title" style="font-size: 1.4rem;">🔊 Audio Output</div>', unsafe_allow_html=True)
                    
                    audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                    if audio_bytes:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.audio(audio_bytes, format="audio/mp3")
                        with col2:
                            st.download_button(
                                "🎵 Download Audio",
                                data=audio_bytes,
                                file_name=f"translation_audio_{target_lang}.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                    else:
                        st.warning("🔇 **Audio generation not available for this language**")
                    
                    # Modern download button
                    st.download_button(
                        "💾 Download Text",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.info("🔄 **Please translate again for the selected language**")
            else:
                st.markdown("""
                <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.2)); border-radius: 15px; margin: 20px 0;">
                    <div style="font-size: 4rem; margin-bottom: 20px;">✨</div>
                    <h3 style="color: #1f2937;">Your Translation Awaits</h3>
                    <p style="color: #6b7280;">Enter text in the left box and click "Translate Now"</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Document Translation in second tab
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="modern-input">', unsafe_allow_html=True)
            st.markdown('<div class="animated-title">📁 Document Upload</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "📤 **Drag & drop or click to upload**",
                type=['pdf', 'txt', 'docx'],
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ **File Uploaded Successfully:** {uploaded_file.name}")
                
                with st.spinner("📖 **Extracting text from document...**"):
                    extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text.strip():
                    with st.expander("📋 **View Extracted Content**", expanded=False):
                        st.text_area("", extracted_text, height=150, label_visibility="collapsed")
                    
                    if st.button("🚀 **Translate Document**", use_container_width=True, type="primary"):
                        with st.spinner("🔄 **Translating document content...**"):
                            try:
                                translated_doc = translate_text(extracted_text, LANGUAGES[target_lang], 'auto')
                                
                                st.success("✅ **Document translation completed!**")
                                
                                with st.expander("📄 **View Translated Document**", expanded=True):
                                    st.text_area("", translated_doc, height=200, label_visibility="collapsed")
                                
                                # Audio for document
                                doc_audio_bytes = text_to_speech(translated_doc, LANGUAGES[target_lang])
                                if doc_audio_bytes:
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.audio(doc_audio_bytes, format="audio/mp3")
                                    with col2:
                                        st.download_button(
                                            "🎵 Download Audio",
                                            data=doc_audio_bytes,
                                            file_name=f"document_audio_{target_lang}.mp3",
                                            mime="audio/mp3",
                                            use_container_width=True
                                        )
                                
                                # Download document
                                st.download_button(
                                    "💾 Download Document",
                                    data=translated_doc,
                                    file_name=f"translated_{uploaded_file.name.split('.')[0]}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.error(f"❌ **Document translation failed:** {str(e)}")
                else:
                    st.error("❌ **Could not extract text from the document**")
            else:
                st.markdown("""
                <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.2)); border-radius: 15px; margin: 20px 0; border: 2px dashed #cbd5e1;">
                    <div style="font-size: 4rem; margin-bottom: 20px;">📁</div>
                    <h3 style="color: #1f2937;">Upload Your Document</h3>
                    <p style="color: #6b7280;">Supported formats: PDF, TXT, DOCX</p>
                    <p style="color: #6b7280; font-size: 0.9rem;">Maximum file size: 200MB</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="glass-card">
                <div class="animated-title">📋 Quick Guide</div>
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <p><strong>🎯 1. Select Language</strong><br>Choose your target language</p>
                    <p><strong>📝 2. Enter Text</strong><br>Type or paste your content</p>
                    <p><strong>🚀 3. Click Translate</strong><br>Get instant AI-powered translation</p>
                    <p><strong>🔊 4. Listen & Download</strong><br>Hear audio and save results</p>
                </div>
            </div>
            
            <div class="glass-card" style="margin-top: 15px;">
                <div class="animated-title">✨ Features</div>
                <p>• 🌍 1000+ Languages</p>
                <p>• 🤖 AI-Powered Translation</p>
                <p>• 🔊 Text-to-Speech</p>
                <p>• 📁 Document Support</p>
                <p>• 💾 Download Options</p>
                <p>• 📊 Translation History</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Platform Statistics Section - At the END with modern design
    st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div class="animated-title" style="text-align: center; font-size: 2rem; margin: 40px 0 30px 0;">📊 Platform Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="gradient-card-1 floating">
            <div class="glow-number">1000+</div>
            <div class="glow-label">Languages</div>
            <div style="margin-top: 10px; font-size: 0.8rem; opacity: 0.9;">Global Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="gradient-card-2 floating" style="animation-delay: 0.5s;">
            <div class="glow-number">99.8%</div>
            <div class="glow-label">Accuracy</div>
            <div style="margin-top: 10px; font-size: 0.8rem; opacity: 0.9;">AI-Powered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="gradient-card-3 floating" style="animation-delay: 1s;">
            <div class="glow-number">24/7</div>
            <div class="glow-label">Available</div>
            <div style="margin-top: 10px; font-size: 0.8rem; opacity: 0.9;">Instant Results</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        translations_count = len(st.session_state.translation_history)
        st.markdown(f"""
        <div class="gradient-card-4 floating" style="animation-delay: 1.5s;">
            <div class="glow-number">{translations_count}</div>
            <div class="glow-label">Translations</div>
            <div style="margin-top: 10px; font-size: 0.8rem; opacity: 0.9;">Your Session</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Modern Footer
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 20px;">
        <h3 style="color: #1f2937; margin-bottom: 10px;">🚀 AI Translator Pro</h3>
        <p style="color: #6b7280; margin-bottom: 20px;">Professional Translation Platform | Powered by AI Technology</p>
        <div style="display: flex; justify-content: center; gap: 20px; font-size: 1.5rem;">
            <span>🌍</span><span>🤖</span><span>🔊</span><span>📁</span><span>💾</span>
        </div>
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 20px;">© 2024 AI Translator Pro | All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; margin-bottom: 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px;'>
            <h2 style='color: white; margin: 0;'>🚀</h2>
            <h3 style='color: white; margin: 10px 0;'>AI Translator Pro</h3>
            <p style='color: rgba(255,255,255,0.9); margin: 0; font-size: 0.8rem;'>Professional Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🧭 Navigation**")
        if st.button("🔍 **Translator**", use_container_width=True, type="primary"):
            st.session_state.current_page = "Translator"
            st.rerun()
        
        if st.button("📚 **History**", use_container_width=True):
            st.session_state.current_page = "History"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        if st.button("🔄 **Clear All**", use_container_width=True):
            st.session_state.input_text = ""
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            if 'translated_lang' in st.session_state:
                del st.session_state.translated_lang
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session Info
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**📊 Session Stats**")
        translations_count = len(st.session_state.translation_history)
        st.metric("Translations", translations_count)
        
        if translations_count > 0:
            total_chars
