import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os, json
from datetime import datetime
import re

# -----------------------------
# App Config - AI Translator
# -----------------------------
st.set_page_config(
    page_title="🤖 AI Translator", 
    page_icon="🤖", 
    layout="wide"
)

# AI Translator ہیڈر
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
    </style>
    <h1 class="main-header">🤖 AI Translator</h1>
    <p class="sub-header">Intelligent Translation in 100+ Languages | رومن اردو سے اصل اردو میں ترجمہ</p>
""", unsafe_allow_html=True)

# -----------------------------
# Complete Language List with Full Names
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
    'Fijian': 'fj',
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
# Roman Urdu to Urdu Detection
# -----------------------------
def detect_roman_urdu(text):
    """رومن اردو کی پہچان کے لیے بہتر فنکشن"""
    roman_urdu_patterns = [
        r'\b(tum|tu|aap|wo|main|hum)\b',
        r'\b(mera|tera|hamara|tumhara|uska|unka)\b',
        r'\b(kyun|kaise|kahan|kab|kitna)\b',
        r'\b(nahi|nhi|haan|ji|han|jee)\b',
        r'\b(acha|accha|theek|sahi|galat)\b',
        r'\b(shukriya|meherbani|mazeed)\b',
        r'\b(hai|ho|hain|tha|thi|the)\b',
        r'\b(lekin|magar|agar|kyunki)\b',
        r'\b(phir|ab|tab|jab|toh)\b',
        r'\b(dikh|sun|kar|dekh|likh)\b'
    ]
    
    text_lower = text.lower()
    
    # Count Roman Urdu patterns
    pattern_count = 0
    for pattern in roman_urdu_patterns:
        if re.search(pattern, text_lower):
            pattern_count += 1
    
    # If more than 2 patterns found, consider it Roman Urdu
    return pattern_count >= 2

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
        'people', 'my', 'than', 'first', 'water', 'been', 'call',
        'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day',
        'did', 'get', 'come', 'made', 'may', 'part', 'over', 'new'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    english_word_count = sum(1 for word in words if word in english_words)
    
    # If more than 30% words are English, consider it English
    return len(words) > 0 and (english_word_count / len(words)) > 0.3

# -----------------------------
# File Management
# -----------------------------
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

users = load_json(USER_FILE)
history = load_json(HISTORY_FILE)

# -----------------------------
# Session Management
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = "Guest"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

# -----------------------------
# Main Translator Interface
# -----------------------------
st.success(f"🤖 Welcome to AI Translator!")

# Automatic language detection
st.markdown("### 🌍 Smart Language Detection")
st.info("💡 **Just type your text - AI will automatically detect Roman Urdu, English, or any other language!**")

col1, col2 = st.columns([2, 1])

with col1:
    input_text = st.text_area(
        "📝 Enter text to translate", 
        placeholder="Type Roman Urdu, English, or any language text...\nمثال: 'tum kaisay ho' یا 'How are you'",
        height=150
    )

with col2:
    st.markdown("#### 🎯 Translate to:")
    target_lang = st.selectbox(
        "Select target language",
        [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
        index=list(LANGUAGES.keys()).index('Urdu')
    )
    
    # Translation options
    st.markdown("#### ⚙️ Settings")
    enable_tts = st.checkbox("🔊 Enable Text-to-Speech", value=True)
    show_detection = st.checkbox("🔍 Show Language Detection", value=True)

translate_btn = st.button("🚀 TRANSLATE NOW", type="primary", use_container_width=True)

st.markdown("---")

# -----------------------------
# Enhanced Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("🔍 AI is detecting language and translating..."):
            # Smart language detection
            detected_language = "Auto"
            source_lang_code = 'auto'
            
            if detect_roman_urdu(input_text):
                detected_language = "Roman Urdu"
                source_lang_code = 'ur'
                st.success("🎯 **Detected: Roman Urdu** → Converting to proper Urdu...")
                
            elif detect_english(input_text):
                detected_language = "English" 
                source_lang_code = 'en'
                st.success("🎯 **Detected: English** → Translating...")
                
            else:
                detected_language = "Auto-Detected"
                source_lang_code = 'auto'
                st.info("🎯 **Detected: Other Language** → Translating...")
            
            # Perform translation
            if source_lang_code == 'auto':
                translated_text = GoogleTranslator(source='auto', target=LANGUAGES[target_lang]).translate(input_text)
            else:
                translated_text = GoogleTranslator(source=source_lang_code, target=LANGUAGES[target_lang]).translate(input_text)
            
            # Display Results
            st.subheader("🎉 Translation Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📥 Original Text ({detected_language})**")
                st.info(input_text)
                if show_detection:
                    st.caption(f"Detected as: {detected_language}")
                
            with col2:
                st.markdown(f"**📤 Translated Text ({target_lang})**")
                st.success(translated_text)
                st.caption(f"Translated to: {target_lang}")
            
            # Text-to-Speech for ALL languages
            if enable_tts:
                st.subheader("🔊 Audio Output")
                
                try:
                    # For translated text
                    tts = gTTS(translated_text, lang=LANGUAGES[target_lang])
                    translated_audio_file = f"translated_{LANGUAGES[target_lang]}.mp3"
                    tts.save(translated_audio_file)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🎧 Listen to {target_lang} Translation**")
                        st.audio(translated_audio_file, format="audio/mp3")
                        st.caption(f"Audio in {target_lang}")
                    
                    # Try to create audio for original text
                    try:
                        if detected_language == "Roman Urdu":
                            orig_lang_code = 'ur'
                        elif detected_language == "English":
                            orig_lang_code = 'en'
                        else:
                            orig_lang_code = 'en'  # fallback
                            
                        tts_original = gTTS(input_text, lang=orig_lang_code)
                        original_audio_file = "original_audio.mp3"
                        tts_original.save(original_audio_file)
                        
                        with col2:
                            st.markdown(f"**🎧 Listen to Original ({detected_language})**")
                            st.audio(original_audio_file, format="audio/mp3")
                            st.caption(f"Audio in {detected_language}")
                    except Exception as e:
                        st.warning(f"Original audio not available: {e}")
                    
                    # Cleanup audio files
                    for file in [translated_audio_file, "original_audio.mp3"]:
                        if os.path.exists(file):
                            os.remove(file)
                            
                except Exception as e:
                    st.warning(f"⚠️ Audio generation issue: {str(e)}")
                    # Fallback to pyttsx3
                    try:
                        engine = pyttsx3.init()
                        engine.save_to_file(translated_text, "fallback_audio.wav")
                        engine.runAndWait()
                        st.audio("fallback_audio.wav", format="audio/wav")
                        if os.path.exists("fallback_audio.wav"):
                            os.remove("fallback_audio.wav")
                    except:
                        st.error("❌ Audio not available for this language")
            
            # Save to history
            user = st.session_state.user
            if user not in history:
                history[user] = []
            
            history[user].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": detected_language,
                "target": target_lang,
                "original": input_text,
                "translated": translated_text
            })
            save_json(HISTORY_FILE, history)
            
            st.balloons()
            st.success("✅ Translation completed successfully!")

    except Exception as e:
        st.error(f"❌ Translation error: {str(e)}")
        st.info("💡 Please check your internet connection and try again.")

elif translate_btn:
    st.warning("⚠️ Please enter some text to translate")

# -----------------------------
# Examples Section
# -----------------------------
st.markdown("---")
st.subheader("💡 Examples to Try")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**رومن اردو سے اردو**")
    st.code("tum kaisay ho?\nmera naam Ahmed hai\nshukriya bahut acha")
    if st.button("Try Example 1", key="ex1"):
        st.session_state.input_text = "tum kaisay ho? mera naam Ahmed hai"

with col2:
    st.markdown("**English to Urdu**")
    st.code("Hello, how are you?\nMy name is Ahmed\nThank you very much")
    if st.button("Try Example 2", key="ex2"):
        st.session_state.input_text = "Hello, how are you? My name is Ahmed"

with col3:
    st.markdown("**English to Hindi**")
    st.code("What is your name?\nI am from Pakistan\nNice to meet you")
    if st.button("Try Example 3", key="ex3"):
        st.session_state.input_text = "What is your name? I am from Pakistan"

# Set example text if button clicked
if 'input_text' in st.session_state:
    input_text = st.session_state.input_text

# -----------------------------
# Translation History
# -----------------------------
st.markdown("---")
st.subheader("📚 Translation History")

if st.session_state.user in history and history[st.session_state.user]:
    user_history = history[st.session_state.user]
    
    # Show recent translations
    for i, entry in enumerate(reversed(user_history[-5:])):
        with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.write(entry['original'])
                st.caption(f"Source: {entry['source']}")
            with col2:
                st.markdown("**Translated:**")
                st.write(entry['translated'])
                st.caption(f"Target: {entry['target']}")
            
            # Quick audio replay
            if st.button(f"🔊 Play Audio", key=f"audio_{i}"):
                try:
                    tts = gTTS(entry['translated'], lang=LANGUAGES[entry['target']])
                    tts.save(f"history_{i}.mp3")
                    st.audio(f"history_{i}.mp3", format="audio/mp3")
                    if os.path.exists(f"history_{i}.mp3"):
                        os.remove(f"history_{i}.mp3")
                except:
                    st.warning("Audio not available")
else:
    st.info("No translation history yet. Start translating to build your history!")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <h3>🤖 AI Translator</h3>
        <p><b>Special Features:</b> Roman Urdu Detection • English to Urdu • 100+ Languages • Text-to-Speech</p>
        <p>رومن اردو سے اصل اردو | انگریزی سے اردو ترجمہ | ہر زبان کے لیے آڈیو</p>
    </div>
""", unsafe_allow_html=True)

st.caption("© 2024 AI Translator - Intelligent Translation for Everyone | ہر کسی کے لیے ذہین ترجمہ")
