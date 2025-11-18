import streamlit as st
import requests
import json
import os
from datetime import datetime
import re
import base64
from io import BytesIO

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
        padding: 15px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0px;
    }
    .language-box {
        padding: 10px;
        border-radius: 8px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        margin: 5px 0px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🤖 AI Translator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent Translation with Speech for ALL Languages | پشتو سمیت تمام زبانوں کی آواز</p>', unsafe_allow_html=True)

# -----------------------------
# Complete Language List with Speech Support
# -----------------------------
LANGUAGES = {
    'Auto Detect': 'auto',
    
    # South Asian Languages with Speech
    'Urdu': 'ur',
    'Hindi': 'hi',
    'Pashto': 'ps',  # پشتو - مکمل سپیچ سپورٹ
    'Punjabi': 'pa',
    'Sindhi': 'sd',
    'Balochi': 'bal',  # بلوچی
    'Kashmiri': 'ks',
    'Bengali': 'bn',
    'Nepali': 'ne',
    'Sinhala': 'si',
    'Dhivehi': 'dv',  # مالدیپ کی زبان
    
    # Middle Eastern Languages
    'Arabic': 'ar',
    'Persian (Farsi)': 'fa',
    'Turkish': 'tr',
    'Kurdish': 'ku',
    'Hebrew': 'he',
    
    # European Languages
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Dutch': 'nl',
    'Greek': 'el',
    'Polish': 'pl',
    'Ukrainian': 'uk',
    'Romanian': 'ro',
    'Swedish': 'sv',
    'Norwegian': 'no',
    'Danish': 'da',
    'Finnish': 'fi',
    
    # East Asian Languages
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja',
    'Korean': 'ko',
    
    # Southeast Asian Languages
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Malay': 'ms',
    'Filipino': 'tl',
    'Burmese': 'my',
    
    # African Languages
    'Swahili': 'sw',
    'Afrikaans': 'af',
    'Amharic': 'am',
    'Yoruba': 'yo',
    'Zulu': 'zu',
    'Xhosa': 'xh',
    
    # Other Important Languages
    'Albanian': 'sq',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Estonian': 'et',
    'Georgian': 'ka',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Irish': 'ga',
    'Kazakh': 'kk',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Macedonian': 'mk',
    'Maltese': 'mt',
    'Serbian': 'sr',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Tajik': 'tg',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Turkmen': 'tk',
    'Uzbek': 'uz',
    'Welsh': 'cy'
}

# Languages with guaranteed speech support
SPEECH_SUPPORTED_LANGUAGES = [
    'ur', 'hi', 'ps', 'pa', 'ar', 'fa', 'tr', 'en', 'es', 'fr', 'de', 'it', 
    'pt', 'ru', 'zh-CN', 'ja', 'ko', 'th', 'vi', 'id', 'ms', 'bn', 'nl', 'pl',
    'uk', 'ro', 'sv', 'no', 'da', 'fi', 'el', 'he', 'cs', 'hu', 'sk', 'hr'
]

# -----------------------------
# Enhanced Language Detection
# -----------------------------
def detect_roman_urdu(text):
    """رومن اردو کی بہترین پہچان"""
    roman_urdu_patterns = [
        r'\b(tum|tu|aap|wo|main|hum|mein|mujhe)\b',
        r'\b(mera|tera|hamara|tumhara|uska|unka|apka)\b',
        r'\b(kyun|kaise|kahan|kab|kisne|kisko|kis|kaun)\b',
        r'\b(nahi|nhi|haan|ji|han|jee|jeez|shukriya)\b',
        r'\b(acha|accha|theek|sahi|galat|kharab|behtar)\b',
        r'\b(shukriya|meherbani|mazeed|aage|phir|lekin)\b',
        r'\b(hai|ho|hain|tha|thi|the|raha|rahi|rahe)\b',
        r'\b(lekin|magar|agar|kyunki|warna|toh|phir)\b',
        r'\b(phir|ab|tab|jab|toh|yahi|wahan|yahan)\b',
        r'\b(dikh|sun|kar|dekh|likh|parh|bol|soch)\b',
        r'\b(chahiye|chahta|chahti|karna|karti|karte)\b',
        r'\b(gaya|gayi|gaye|aaya|aayi|aaye|liya|diya)\b'
    ]
    
    text_lower = text.lower()
    pattern_count = 0
    for pattern in roman_urdu_patterns:
        if re.search(pattern, text_lower):
            pattern_count += 1
    
    return pattern_count >= 3

def detect_pashto(text):
    """پشتو کی پہچان"""
    pashto_words = [
        'ستا', 'زما', 'ته', 'زه', 'دی', 'شوی', 'کوي', 'کړي', 'کړل', 'شو', 
        'څه', 'ولې', 'څنگه', 'چېرې', 'کله', 'کوم', 'څوک', 'هلک', 'نجلۍ',
        'مينه', 'کور', 'ورک', 'لوی', 'وړوکی', 'نوی', 'زوړ', 'ښه', 'بد',
        'سپک', 'دروند', 'تيز', 'ورک', 'اوبه', 'دې', 'نه', 'هو', 'مه'
    ]
    
    # Check for Pashto characters
    pashto_chars = set('ښړډږڅځڂېيۍئ')
    text_chars = set(text)
    
    if pashto_chars.intersection(text_chars):
        return True
    
    # Check for common Pashto words
    text_words = text.split()
    pashto_word_count = sum(1 for word in text_words if word in pashto_words)
    
    return pashto_word_count > 2

def detect_english(text):
    """انگریزی کی پہچان"""
    english_words = [
        'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with',
        'for', 'as', 'was', 'on', 'are', 'this', 'by', 'be', 'from',
        'have', 'has', 'had', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'your', 'can', 'said', 'there', 'each', 'which', 'she',
        'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out',
        'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would',
        'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    if len(words) == 0:
        return False
        
    english_word_count = sum(1 for word in words if word in english_words)
    return (english_word_count / len(words)) > 0.3

# -----------------------------
# Translation Function
# -----------------------------
def translate_text(text, target_lang, source_lang='auto'):
    """Translate text using deep-translator"""
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")

# -----------------------------
# Enhanced Text-to-Speech Function
# -----------------------------
def text_to_speech(text, lang, slow=False):
    """Convert text to speech with enhanced support for all languages"""
    try:
        from gtts import gTTS
        from io import BytesIO
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Save to bytes buffer
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes
        
    except Exception as e:
        st.warning(f"Speech not available for {lang}: {str(e)}")
        return None

def has_speech_support(lang_code):
    """Check if language has speech support"""
    return lang_code in SPEECH_SUPPORTED_LANGUAGES

# -----------------------------
# Session State Management
# -----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

# -----------------------------
# Main App Interface
# -----------------------------

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    target_lang = st.selectbox(
        "🎯 Translate to",
        [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
        index=list(LANGUAGES.keys()).index('Pashto')  # Default to Pashto
    )
    
    enable_tts = st.checkbox("🔊 Enable Text-to-Speech", value=True)
    slow_speech = st.checkbox("🐢 Slow Speech (for learning)", value=False)
    
    st.markdown("---")
    st.header("🎯 Popular Languages")
    
    # Quick language buttons
    lang_col1, lang_col2 = st.columns(2)
    
    with lang_col1:
        if st.button("پشتو", use_container_width=True):
            target_lang = 'Pashto'
        if st.button("اردو", use_container_width=True):
            target_lang = 'Urdu'
        if st.button("فارسی", use_container_width=True):
            target_lang = 'Persian (Farsi)'
            
    with lang_col2:
        if st.button("English", use_container_width=True):
            target_lang = 'English'
        if st.button("العربية", use_container_width=True):
            target_lang = 'Arabic'
        if st.button("हिन्दी", use_container_width=True):
            target_lang = 'Hindi'
    
    st.markdown("---")
    st.header("📊 Speech Info")
    
    target_lang_code = LANGUAGES[target_lang]
    if has_speech_support(target_lang_code):
        st.success("✅ Speech: Available")
    else:
        st.warning("⚠️ Speech: Limited")

# Main content
st.success("🎯 **Special Feature: Pashto Speech Support | پشتو بولنے کی خصوصی سہولت**")

# Input section
input_text = st.text_area(
    "📝 Enter text to translate",
    placeholder="Examples:\n• Roman Urdu: 'tum kaisay ho? mera naam Ahmed hai'\n• Pashto: 'ستا نوم څه دی؟'\n• English: 'Hello, how are you?'\n• Any language...",
    height=150
)

# Translate button
translate_btn = st.button("🚀 TRANSLATE NOW", use_container_width=True, type="primary")

# Examples section
st.markdown("### 💡 Try These Examples:")

ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)

with ex_col1:
    if st.button("رومن اردو", use_container_width=True):
        st.session_state.input_text = "salam tum kaisay ho? mera naam Ahmed hai. kya haal hai?"
        st.rerun()

with ex_col2:
    if st.button("پشتو", use_container_width=True):
        st.session_state.input_text = "ستاسو نوم څه دی؟ زما نوم احمد دی۔ تاسو څنګه یاست؟"
        st.rerun()

with ex_col3:
    if st.button("English", use_container_width=True):
        st.session_state.input_text = "Hello, what is your name? My name is Ahmed. How are you?"
        st.rerun()

with ex_col4:
    if st.button("فارسی", use_container_width=True):
        st.session_state.input_text = "سلام نام شما چیست؟ نام من احمد است. حالتان چطور است؟"
        st.rerun()

st.markdown("---")

# -----------------------------
# Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("🔍 Detecting language and translating..."):
            # Enhanced language detection
            detected_language = "Auto-Detected"
            source_lang_code = 'auto'
            
            if detect_pashto(input_text):
                detected_language = "Pashto"
                source_lang_code = 'ps'
                st.success("🎯 **Detected: Pashto** - Translating...")
            elif detect_roman_urdu(input_text):
                detected_language = "Roman Urdu"
                source_lang_code = 'ur'
                st.success("🎯 **Detected: Roman Urdu** - Converting to proper text...")
            elif detect_english(input_text):
                detected_language = "English"
                source_lang_code = 'en'
                st.success("🎯 **Detected: English** - Translating...")
            else:
                st.info("🎯 **Detected: Other Language** - Translating...")
            
            # Perform translation
            translated_text = translate_text(input_text, LANGUAGES[target_lang], source_lang_code)
            
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
                st.caption(f"Detected: {detected_language}")
                
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
            
            # Enhanced Text-to-Speech
            if enable_tts:
                st.subheader("🔊 Audio Output")
                
                target_lang_code = LANGUAGES[target_lang]
                
                if has_speech_support(target_lang_code):
                    audio_bytes = text_to_speech(translated_text, target_lang_code, slow_speech)
                    
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        
                        # Language-specific messages
                        if target_lang_code == 'ps':
                            st.success("🎧 **پشتو آواز**: پشتو زبان میں سنیں")
                        elif target_lang_code == 'ur':
                            st.success("🎧 **اردو آواز**: اردو زبان میں سنیں")
                        elif target_lang_code == 'ar':
                            st.success("🎧 **العربية صوت**: الاستماع باللغة العربية")
                        else:
                            st.success(f"🎧 **{target_lang} Speech**: Listen in {target_lang}")
                    else:
                        st.warning(f"⚠️ Audio generation failed for {target_lang}")
                else:
                    st.info(f"ℹ️ Speech support is limited for {target_lang}. Trying anyway...")
                    audio_bytes = text_to_speech(translated_text, target_lang_code, slow_speech)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.warning(f"❌ Speech not available for {target_lang}")
            
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
            st.success(f"✅ Translation to {target_lang} completed successfully!")

    except Exception as e:
        st.error(f"❌ Translation error: {str(e)}")

elif translate_btn:
    st.warning("⚠️ Please enter some text to translate")

# -----------------------------
# Language Information
# -----------------------------
st.markdown("---")
st.subheader("🌍 Supported Languages with Speech")

# Show languages with speech support
speech_langs = [lang for lang, code in LANGUAGES.items() 
               if code in SPEECH_SUPPORTED_LANGUAGES and lang != 'Auto Detect']

cols = st.columns(4)
for i, lang in enumerate(speech_langs):
    with cols[i % 4]:
        st.markdown(f'<div class="language-box">🔊 {lang}</div>', unsafe_allow_html=True)

# -----------------------------
# Translation History
# -----------------------------
if st.session_state.translation_history:
    st.markdown("---")
    st.subheader("📚 Translation History")
    
    for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
        with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.write(entry['original'])
            with col2:
                st.markdown("**Translated Text:**")
                st.write(entry['translated'])
            
            # Audio replay
            if st.button(f"🔊 Play Audio", key=f"audio_{i}"):
                target_code = LANGUAGES[entry['target']]
                audio_bytes = text_to_speech(entry['translated'], target_code)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center;'>
    <h3>🤖 AI Translator</h3>
    <p><b>Special Pashto Support | پشتو کی خصوصی سہولت</b></p>
    <p><b>Features:</b> Pashto Speech • Roman Urdu • 100+ Languages • Text-to-Speech</p>
    <p>پشتو بولنے کی سہولت • رومن اردو سے اصل اردو • تمام زبانوں کی آواز</p>
</div>
""", unsafe_allow_html=True)

st.caption("© 2024 AI Translator - Complete Speech Support for All Languages")
