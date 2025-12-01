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
st.set_page_config(page_title="🌍 AI Translator Pro", page_icon="🌐", layout="wide")

st.markdown("""
<h1 style='text-align:center; margin-bottom:5px;'>🌍 AI Translator Pro</h1>
<p style='text-align:center; font-size:18px; margin-top:-10px;'>Translate Anything — Text, Documents, PDFs</p>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("⚙️ App Settings")

    st.markdown("### 🎯 Select Languages")
    source_language = st.selectbox("Source Language", ["auto"] + GoogleTranslator.get_supported_languages(), index=0)
    target_language = st.selectbox("Target Language", GoogleTranslator.get_supported_languages())

    st.markdown("### 🔊 Voice Output")
    voice_enabled = st.checkbox("Enable Voice Output (TTS)", value=False)

    st.markdown("---")
    st.markdown("### 💾 Saved Translations")

    if not os.path.exists("translation_history.json"):
        with open("translation_history.json", "w") as f:
            json.dump([], f)

    with open("translation_history.json", "r") as f:
        history = json.load(f)

    if len(history) > 0:
        for h in history[-5:][::-1]:
            st.markdown(f"**{h['time']}** — {h['source']} → {h['target']}")
    else:
        st.write("No history yet.")

# -----------------------------
# Translation Function
# -----------------------------
def translate_text(text, target_lang, source_lang="auto"):
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    return translator.translate(text)

# -----------------------------
# Save History
# -----------------------------
def save_history(src, tgt):
    new_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": src,
        "target": tgt
    }
    history.append(new_entry)
    with open("translation_history.json", "w") as f:
        json.dump(history, f, indent=4)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📝 Text Translator", "📄 Document Translator", "🎙 Voice Generator"])

# -----------------------------
# TEXT TRANSLATOR
# -----------------------------
with tab1:
    st.subheader("📝 Text Translation")

    text_input = st.text_area("Enter text to translate:", height=180)

    if st.button("Translate Now", icon="🌐"):
        if text_input.strip() == "":
            st.warning("Please enter some text.")
        else:
            try:
                result = translate_text(text_input, target_language, source_language)
                st.success("Translation Complete!")
                st.text_area("Translated Output:", result, height=180)
                save_history(text_input[:20], result[:20])

                if voice_enabled:
                    tts = gTTS(result)
                    audio_file = BytesIO()
                    tts.write_to_fp(audio_file)
                    st.audio(audio_file.getvalue(), format="audio/mp3")
            except Exception as e:
                st.error(f"Translation Error: {e}")

# -----------------------------
# DOCUMENT TRANSLATOR
# -----------------------------
with tab2:
    st.subheader("📄 Document Translator")

    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])

    if uploaded_file:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        extracted_text = ""

        try:
            if file_extension == "pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text() + "\n"

            elif file_extension == "docx":
                doc = Document(uploaded_file)
                extracted_text = "\n".join([para.text for para in doc.paragraphs])

            elif file_extension == "txt":
                extracted_text = uploaded_file.read().decode("utf-8")

            st.info("File extracted successfully!")
            st.text_area("Extracted Text:", extracted_text, height=200)

            if st.button("Translate Document"):
                translated_doc = translate_text(extracted_text, target_language)
                st.success("Document Translated!")

                st.text_area("Translated Document:", translated_doc, height=200)

                save_history("Document", "Translated Document")

        except Exception as e:
            st.error(f"Error reading file: {e}")

# -----------------------------
# VOICE GENERATOR
# -----------------------------
with tab3:
    st.subheader("🎙 Generate Voice from Text")

    voice_text = st.text_area("Enter text to convert to voice:", height=150)

    if st.button("Generate Voice", icon="🎧"):
        if voice_text.strip() == "":
            st.warning("Please enter some text.")
        else:
            tts = gTTS(voice_text)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)

            st.audio(audio_file.getvalue(), format="audio/mp3")

# -----------------------------
# Footer (NO STATS ADDED)
# -----------------------------
st.markdown("""
<div style='text-align: center; padding: 20px; margin-top: 40px; font-size: 14px; opacity: 0.6;'>
AI Translator Pro — Powered by Google AI Translation
</div>
""", unsafe_allow_html=True)
