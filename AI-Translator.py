import streamlit as st
import os
import json
from datetime import datetime
import re

# First try to import required packages
try:
    from deep_translator import GoogleTranslator
except ImportError:
    st.error("❌ deep-translator package is not installed. Please add it to requirements.txt")
    st.stop()

try:
    from gtts import gTTS
except ImportError:
    st.warning("⚠️ gTTS is not available. Audio features will be limited.")

try:
    import pyttsx3
except ImportError:
    st.warning("⚠️ pyttsx3 is not available. Backup audio features disabled.")

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="🤖 AI Translator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    .sub-header {
        font-size: 1.5rem;
        color: #0068C9;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🤖 AI Translator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent Translation in 100+ Languages | رومن اردو سے اصل اردو میں ترجمہ</p>', unsafe_allow_html=True)

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
    'Pashto': 'ps',
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
# Language Detection Functions
# -----------------------------
def detect_roman_urdu(text):
    """رومن اردو کی پہچان"""
    roman_urdu_words = [
        'tum', 'tu', 'aap', 'wo', 'main', 'hum', 'mera', 'tera', 'hamara', 
        'tumhara', 'uska', 'unka', 'kyun', 'kaise', 'kahan', 'kab', 'kitna',
        'nahi', 'nhi', 'haan', 'ji', 'han', 'jee', 'acha', 'accha', 'theek',
        'sahi', 'galat', 'shukriya', 'meherbani', 'mazeed', 'hai', 'ho',
        'hain', 'tha', 'thi', 'the', 'lekin', 'magar', 'agar', 'kyunki',
        'phir', 'ab', 'tab', 'jab', 'toh', 'dikh', 'sun', 'kar', 'dekh', 'likh'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    if len(words) == 0:
        return False
        
    roman_word_count = sum(1 for word in words if word in roman_urdu_words)
    return (roman_word_count / len(words)) > 0.2

def detect_english(text):
    """انگریزی کی پہچان"""
    english_words = [
        'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with',
        'for', 'as', 'was', 'on', 'are', 'this', 'by', 'be', 'from',
        'have', 'has', 'had', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'your', 'can', 'said', 'there', 'each', 'which', 'she',
        'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out',
        'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would',
        'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two',
        'more', 'write', 'go', 'see', 'number', 'no', 'way', 'could',
        'people', 'my', 'than', 'first', 'water', 'been', 'call'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    if len(words) == 0:
        return False
        
    english_word_count = sum(1 for word in words if word in english_words)
    return (english_word_count / len(words)) > 0.3

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
    st.header("⚙️ Settings")
    
    target_lang = st.selectbox(
        "🎯 Translate to",
        [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
        index=list(LANGUAGES.keys()).index('Urdu')
    )
    
    enable_tts = st.checkbox("🔊 Enable Text-to-Speech", value=True)
    show_examples = st.checkbox("💡 Show Examples", value=True)
    
    st.markdown("---")
    st.header("📊 App Info")
    st.info("""
    **Features:**
    - 🤖 Auto Language Detection
    - 📝 Roman Urdu to Urdu
    - 🌍 100+ Languages
    - 🔊 Text-to-Speech
    - ⚡ Fast Translation
    """)

# Main content
st.success("🚀 **Simply type your text - AI will automatically detect the language and translate!**")

# Input section
input_text = st.text_area(
    "📝 Enter text to translate",
    placeholder="Examples:\n• Roman Urdu: 'tum kaisay ho? mera naam Ahmed hai'\n• English: 'Hello, how are you? My name is Ahmed'\n• Any other language...",
    height=150,
    key="input_text_area"
)

# Translate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    translate_btn = st.button("🚀 TRANSLATE NOW", use_container_width=True, type="primary")

# Examples section
if show_examples:
    st.markdown("### 💡 Quick Examples:")
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    
    with ex_col1:
        if st.button("رومن اردو", use_container_width=True):
            st.session_state.input_text = "tum kaisay ho? mera naam Ahmed hai. shukriya bahut acha."
            st.rerun()
    
    with ex_col2:
        if st.button("English", use_container_width=True):
            st.session_state.input_text = "Hello, how are you? My name is Ahmed. Thank you very much."
            st.rerun()
    
    with ex_col3:
        if st.button("Mixed Text", use_container_width=True):
            st.session_state.input_text = "Hello! tum kaisay ho? How are you doing today?"
            st.rerun()

st.markdown("---")

# -----------------------------
# Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("🔍 AI is detecting language and translating..."):
            # Language detection
            detected_language = "Auto-Detected"
            source_lang_code = 'auto'
            
            if detect_roman_urdu(input_text):
                detected_language = "Roman Urdu"
                source_lang_code = 'ur'
                st.success(f"🎯 **Detected: Roman Urdu** - Converting to proper {target_lang}...")
            elif detect_english(input_text):
                detected_language = "English" 
                source_lang_code = 'en'
                st.success(f"🎯 **Detected: English** - Translating to {target_lang}...")
            else:
                st.info("🎯 **Detected: Other Language** - Translating...")
            
            # Perform translation
            translated_text = GoogleTranslator(
                source=source_lang_code, 
                target=LANGUAGES[target_lang]
            ).translate(input_text)
            
            # Display results
            st.subheader("🎉 Translation Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📥 Original Text**")
                st.text_area(
                    "Original", 
                    input_text, 
                    height=150, 
                    key="original_display",
                    label_visibility="collapsed"
                )
                st.caption(f"Language: {detected_language}")
                
            with col2:
                st.markdown(f"**📤 Translated Text ({target_lang})**")
                st.text_area(
                    "Translated", 
                    translated_text, 
                    height=150, 
                    key="translated_display",
                    label_visibility="collapsed"
                )
                st.caption(f"Translated to: {target_lang}")
            
            # Text-to-Speech
            if enable_tts:
                st.subheader("🔊 Audio Output")
                
                try:
                    # Create audio for translated text
                    tts = gTTS(translated_text, lang=LANGUAGES[target_lang])
                    audio_file = f"output_{datetime.now().strftime('%H%M%S')}.mp3"
                    tts.save(audio_file)
                    
                    # Display audio player
                    st.audio(audio_file, format="audio/mp3")
                    st.caption(f"🎧 Listen to the {target_lang} translation")
                    
                    # Clean up audio file
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        
                except Exception as e:
                    st.warning(f"⚠️ Text-to-speech not available: {str(e)}")
                    # Fallback to pyttsx3
                    try:
                        engine = pyttsx3.init()
                        fallback_file = f"fallback_{datetime.now().strftime('%H%M%S')}.wav"
                        engine.save_to_file(translated_text, fallback_file)
                        engine.runAndWait()
                        st.audio(fallback_file, format="audio/wav")
                        if os.path.exists(fallback_file):
                            os.remove(fallback_file)
                    except:
                        st.error("❌ Audio generation failed for this language")
            
            # Save to history
            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": detected_language,
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
        st.info("💡 Please check your internet connection and try again.")

elif translate_btn:
    st.warning("⚠️ Please enter some text to translate")

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
            
            # Audio replay button
            if st.button(f"🔊 Play Audio", key=f"audio_{i}"):
                try:
                    tts = gTTS(entry['translated'], lang=LANGUAGES[entry['target']])
                    audio_file = f"history_{i}.mp3"
                    tts.save(audio_file)
                    st.audio(audio_file, format="audio/mp3")
                    # Cleanup will happen on next run
                except:
                    st.warning("Audio not available for this entry")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center;'>
    <h3>🤖 AI Translator</h3>
    <p><b>Powered by:</b> Streamlit • Google Translate • gTTS</p>
    <p><b>Special Features:</b> Roman Urdu Detection • Auto Language Detection • Text-to-Speech • 100+ Languages</p>
    <p>رومن اردو سے اصل اردو | انگریزی سے اردو ترجمہ | ہر زبان کے لیے آڈیو</p>
</div>
""", unsafe_allow_html=True)

st.caption("© 2024 AI Translator - Built with Streamlit | Deployed on Streamlit Cloud")
