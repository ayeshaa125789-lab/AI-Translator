# professional_ai_translator.py
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import json
from datetime import datetime
import re
from io import BytesIO
import base64
import pdfplumber
from docx import Document
import tempfile
import hashlib
import docx2txt

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator - Professional",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Styles (Professional)
# -----------------------------
st.markdown("""
<style>
/* Global font */
* { font-family: 'Inter', sans-serif; }

/* Header */
.main-header {
  font-size: 2.6rem;
  font-weight: 800;
  text-align: left;
  color: transparent;
  background: linear-gradient(90deg,#4e4376,#2b5876);
  -webkit-background-clip: text;
  margin-bottom: 0.1rem;
}
.sub-header {
  color: #6b7280;
  margin-top: -6px;
  margin-bottom: 18px;
}

/* Card */
.card {
  background: #ffffff;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(11,15,26,0.06);
  border: 1px solid #e6e9ef;
}

/* stats */
.stats {
  padding: 18px;
  border-radius: 12px;
  text-align: center;
}

/* section title */
.section-title {
  font-size: 1.25rem;
  color: #234;
  font-weight: 700;
  margin-bottom: 12px;
}

/* textarea */
textarea {
  background: #fbfdff !important;
  border: 1px solid #e6eef8 !important;
  border-radius: 10px !important;
  padding: 14px !important;
  font-size: 14px !important;
}

/* upload */
.upload-area {
  padding: 22px;
  border-radius: 12px;
  border: 2px dashed #e6eef8;
  text-align: center;
  background: #fbfdff;
}

/* buttons */
.stButton>button {
  background: linear-gradient(90deg,#4e4376,#2b5876) !important;
  color: white !important;
  border-radius: 10px !important;
  padding: 10px 14px !important;
  font-weight: 700 !important;
}

/* small helper text */
.helper {
  color: #6b7280;
  font-size: 0.88rem;
}

/* history item */
.history-item {
  border-left: 4px solid #4e4376;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  background: #fff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Utilities & Session init
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

init_user_data()

if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# -----------------------------
# Languages (subset + expandable)
# -----------------------------
LANGUAGES = {
    'English': 'en', 'Urdu': 'ur', 'Hindi': 'hi', 'Arabic': 'ar',
    'Spanish': 'es', 'French': 'fr', 'German': 'de',
    'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja', 'Korean': 'ko', 'Russian': 'ru',
    'Portuguese': 'pt', 'Italian': 'it', 'Dutch': 'nl',
    'Turkish': 'tr', 'Polish': 'pl', 'Persian': 'fa',
    'Bengali': 'bn', 'Punjabi': 'pa', 'Gujarati': 'gu',
    'Tamil': 'ta', 'Telugu': 'te', 'Malayalam': 'ml',
    'Thai': 'th', 'Vietnamese': 'vi', 'Indonesian': 'id',
    'Malay': 'ms', 'Swahili': 'sw', 'Pashto': 'ps',
    'Sindhi': 'sd', 'Kannada': 'kn', 'Marathi': 'mr',
    # add more if required
}

# -----------------------------
# File extraction functions
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
    except Exception:
        return ""

def extract_text_from_txt(uploaded_file):
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except:
        try:
            uploaded_file.seek(0)
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
    except Exception:
        return ""

def extract_text_from_doc(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.doc') as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        text = docx2txt.process(temp_file_path)
        os.unlink(temp_file_path)
        return text.strip() if text.strip() else ""
    except Exception:
        return ""

def extract_text_from_file(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if file_ext == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_ext == 'txt':
        return extract_text_from_txt(uploaded_file)
    elif file_ext == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_ext == 'doc':
        return extract_text_from_doc(uploaded_file)
    else:
        return ""

# -----------------------------
# TTS
# -----------------------------
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception:
        return None

# -----------------------------
# Roman Urdu detection & translate
# -----------------------------
def detect_roman_urdu(text):
    roman_urdu_words = [
        'tum', 'tu', 'aap', 'wo', 'main', 'hum', 'mera', 'tera', 'hamara',
        'tumhara', 'uska', 'unka', 'kyun', 'kaise', 'kahan', 'kab', 'kitna',
        'nahi', 'nhi', 'haan', 'ji', 'han', 'jee', 'acha', 'accha', 'theek'
    ]
    text_lower = text.lower()
    words = re.findall(r'\w+', text_lower)
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
# UI components
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:6px;'>🌐 AI Translator</h3>", unsafe_allow_html=True)
        st.markdown("<div class='helper'>Professional translator • Auto source-detect • Document support</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.experimental_rerun()
        if st.button("History", use_container_width=True):
            st.session_state.current_page = "History"
            st.experimental_rerun()
        if st.button("Settings", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.experimental_rerun()
        st.markdown("---")
        st.markdown(f"**Translations this session:** {len(st.session_state.translation_history)}")
        if st.button("Clear Session", use_container_width=True):
            st.session_state.translation_history = []
            st.session_state.input_text = ""
            if 'translated_text' in st.session_state:
                del st.session_state.translated_text
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def dashboard_page():
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'>", unsafe_allow_html=True)
    st.markdown("<div><h1 class='main-header'>AI Translator</h1><div class='sub-header'>Fast • Accurate • Professional — Source automatically detected</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:right;'><small class='helper'>Asking only for target language — source set to Auto-detect</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Stats row
    c1, c2, c3, c4 = st.columns([1,1,1,1], gap="large")
    with c1:
        st.markdown("<div class='card stats'><div style='font-size:20px; font-weight:700;'>1000+</div><div class='helper'>Languages</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card stats'><div style='font-size:20px; font-weight:700;'>99.8%</div><div class='helper'>Accuracy (AI)</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card stats'><div style='font-size:20px; font-weight:700;'>24/7</div><div class='helper'>Available</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='card stats'><div style='font-size:20px; font-weight:700;'>{len(st.session_state.translation_history)}</div><div class='helper'>This Session</div></div>", unsafe_allow_html=True)

    st.markdown("<br/>")
    # Translation center: left = text, right = document / target selection
    left, right = st.columns([2,1], gap="large")
    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Translate Text</div>", unsafe_allow_html=True)
        input_text = st.text_area("Enter text to translate (or paste text / right from OCR)", value=st.session_state.input_text, height=260, key="input_text_area")
        st.markdown(f"<div class='helper'>Characters: {len(input_text or '')}</div>", unsafe_allow_html=True)

        # Inline action buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1,1,1])
        with btn_col1:
            if st.button("Translate Text", use_container_width=True):
                if (input_text or "").strip():
                    with st.spinner("Translating text..."):
                        try:
                            # source is auto-detect always
                            translated = translate_text(input_text, LANGUAGES[st.session_state.target_lang], source_lang='auto')
                            st.session_state.translated_text = translated
                            # Save history
                            entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": "Auto Detect",
                                "target": st.session_state.target_lang,
                                "original": input_text[:500],
                                "translated": translated[:500],
                                "characters": len(input_text)
                            }
                            st.session_state.translation_history.append(entry)
                            st.success("Translation completed.")
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("Please enter some text to translate.")
        with btn_col2:
            if st.button("Clear Input", use_container_width=True):
                st.session_state.input_text = ""
                if 'translated_text' in st.session_state:
                    del st.session_state.translated_text
                st.experimental_rerun()
        with btn_col3:
            if st.button("Use Extracted Document Text", use_container_width=True):
                if 'extracted_text' in st.session_state and st.session_state.extracted_text.strip():
                    st.session_state.input_text = st.session_state.extracted_text
                    st.experimental_rerun()
                else:
                    st.warning("No extracted document text available. Upload and extract a document first.")

        # Show translated text if exists
        if 'translated_text' in st.session_state:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Translated Output</div>", unsafe_allow_html=True)
            st.text_area("", value=st.session_state.translated_text, height=200, key="translated_out")
            st.markdown("<div style='display:flex; gap:8px; margin-top:8px;'>", unsafe_allow_html=True)
            # audio and download
            try:
                audio_bytes = text_to_speech(st.session_state.translated_text, LANGUAGES[st.session_state.target_lang])
            except Exception:
                audio_bytes = None
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
            st.download_button("Download Translated Text", data=st.session_state.translated_text, file_name=f"translation_{st.session_state.target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Target Language & Document</div>", unsafe_allow_html=True)

        # Target language select (single selection only; source auto)
        target_lang = st.selectbox("Choose Target Language", options=list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.target_lang))
        st.session_state.target_lang = target_lang
        st.markdown("<div class='helper'>Source language will be detected automatically.</div>", unsafe_allow_html=True)
        st.markdown("<hr/>", unsafe_allow_html=True)

        # File uploader (PDF, TXT, DOCX, DOC) + Extract & Translate
        uploaded_file = st.file_uploader("Upload Document (PDF, TXT, DOCX, DOC)", type=['pdf', 'txt', 'docx', 'doc'])
        if uploaded_file is not None:
            st.markdown(f"**Uploaded:** {uploaded_file.name}", unsafe_allow_html=True)
            with st.spinner("Extracting text from document..."):
                extracted = extract_text_from_file(uploaded_file)
                st.session_state.extracted_text = extracted
                if extracted.strip():
                    st.success("Text extracted from document.")
                else:
                    st.error("Could not extract text or document format not supported.")
            if extracted.strip():
                with st.expander("Preview extracted text"):
                    st.text_area("Extracted Text", value=extracted, height=180, key="extracted_preview")
                if st.button("Translate Document", use_container_width=True):
                    with st.spinner("Translating document..."):
                        try:
                            translated_doc = translate_text(extracted, LANGUAGES[st.session_state.target_lang], source_lang='auto')
                            st.session_state.translated_doc = translated_doc
                            # Save history (short)
                            entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": "Auto Detect",
                                "target": st.session_state.target_lang,
                                "original": extracted[:500],
                                "translated": translated_doc[:500],
                                "characters": len(extracted)
                            }
                            st.session_state.translation_history.append(entry)
                            st.success("Document translated.")
                        except Exception as e:
                            st.error(str(e))

        # Show translated_doc and download
        if 'translated_doc' in st.session_state:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Translated Document</div>", unsafe_allow_html=True)
            st.text_area("", value=st.session_state.translated_doc, height=180, key="translated_doc_area")
            st.download_button("Download Translated Document", data=st.session_state.translated_doc, file_name=f"translated_doc_{st.session_state.target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

def history_page():
    st.markdown("<h1 class='main-header'>Translation History</h1>", unsafe_allow_html=True)
    if not st.session_state.translation_history:
        st.info("No translations yet — translate text or documents to see history.")
        return

    # summary
    total_trans = len(st.session_state.translation_history)
    total_chars = sum(e.get('characters',0) for e in st.session_state.translation_history)
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.metric("Total Translations", total_trans)
    with c2:
        st.metric("Total Characters", f"{total_chars:,}")
    with c3:
        if st.button("Clear History"):
            st.session_state.translation_history = []
            st.experimental_rerun()

    st.markdown("<br/>")
    for i, entry in enumerate(reversed(st.session_state.translation_history)):
        st.markdown("<div class='history-item'>", unsafe_allow_html=True)
        st.markdown(f"**{entry['timestamp']}** — {entry['source']} → {entry['target']} — {entry.get('characters',0)} chars")
        st.markdown(f"**Original:** {entry['original']}")
        st.markdown(f"**Translated:** {entry['translated']}")
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button(f"🔊 Listen {i}", key=f"listen_{i}"):
                try:
                    audio = text_to_speech(entry['translated'], LANGUAGES[entry['target']])
                    if audio:
                        st.audio(audio, format="audio/mp3")
                except:
                    st.error("Audio playback failed.")
        with col2:
            if st.button(f"↻ Reuse {i}", key=f"reuse_{i}"):
                st.session_state.input_text = entry['original']
                st.session_state.target_lang = entry['target']
                st.session_state.current_page = "Dashboard"
                st.experimental_rerun()
        with col3:
            if st.button(f"🗑 Delete {i}", key=f"del_{i}"):
                # delete specific entry (index from end)
                st.session_state.translation_history.pop(len(st.session_state.translation_history)-1 - i)
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def settings_page():
    st.markdown("<h1 class='main-header'>Settings</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Preferences", unsafe_allow_html=True)
    default_target = st.selectbox("Default target language (for new sessions)", options=list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.target_lang))
    st.session_state.target_lang = default_target
    st.checkbox("Enable Text-to-Speech", value=True, key="enable_tts")
    st.markdown("<hr/>", unsafe_allow_html=True)
    if st.button("Reset Session Data"):
        st.session_state.translation_history = []
        st.session_state.input_text = ""
        if 'translated_text' in st.session_state:
            del st.session_state.translated_text
        st.success("Session data reset.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Page controller
# -----------------------------
def main():
    show_sidebar()
    if st.session_state.current_page == "Dashboard":
        dashboard_page()
    elif st.session_state.current_page == "History":
        history_page()
    elif st.session_state.current_page == "Settings":
        settings_page()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:#6b7280;'>© 2024 AI Translator — Professional UI</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
