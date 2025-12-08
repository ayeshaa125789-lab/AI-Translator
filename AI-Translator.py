import streamlit as st
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from io import BytesIO
import sqlite3
import hashlib
import time
import pdfplumber
from docx import Document
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('ai_translator.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Translations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            source_text TEXT,
            translated_text TEXT,
            source_lang TEXT,
            target_lang TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            characters INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_db()

# -----------------------------
# Authentication Functions
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=""):
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_user(username, password):
    c = conn.cursor()
    password_hash = hash_password(password)
    
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    user = c.fetchone()
    
    if user:
        return True, user
    return False, None

def save_translation(user_id, source_text, translated_text, source_lang, target_lang, characters):
    c = conn.cursor()
    c.execute(
        """INSERT INTO translations 
           (user_id, source_text, translated_text, source_lang, target_lang, characters) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, source_text, translated_text, source_lang, target_lang, characters)
    )
    conn.commit()

def get_user_translations(user_id, limit=50):
    c = conn.cursor()
    c.execute(
        """SELECT * FROM translations 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    )
    return c.fetchall()

def get_user_stats(user_id):
    c = conn.cursor()
    
    # Total translations
    c.execute("SELECT COUNT(*) FROM translations WHERE user_id = ?", (user_id,))
    total_translations = c.fetchone()[0]
    
    # Total characters
    c.execute("SELECT SUM(characters) FROM translations WHERE user_id = ?", (user_id,))
    total_chars = c.fetchone()[0] or 0
    
    # Top languages
    c.execute("""
        SELECT target_lang, COUNT(*) as count 
        FROM translations 
        WHERE user_id = ? 
        GROUP BY target_lang 
        ORDER BY count DESC 
        LIMIT 5
    """, (user_id,))
    top_langs = c.fetchall()
    
    return {
        "total_translations": total_translations,
        "total_chars": total_chars,
        "top_languages": top_langs
    }

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton { display: none; }
    
    /* Main container */
    .main-container {
        background: white;
        min-height: 100vh;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
    }
    
    /* Cards */
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin: 10px 0;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f3f4f6;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* User badge */
    .user-badge {
        background: white;
        color: #667eea;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Metrics */
    .metric-box {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f6f8ff 0%, #f9f5ff 100%);
        border-radius: 15px;
        margin: 10px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State Management
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "English"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "dashboard_tab" not in st.session_state:
    st.session_state.dashboard_tab = "translate"

# -----------------------------
# Language Functions
# -----------------------------
@st.cache_data(ttl=3600)
def get_language_list():
    """Get all supported languages"""
    lang_dict = {}
    for code, name in LANGUAGES.items():
        lang_dict[name.title()] = code
    return lang_dict

LANGUAGE_DICT = get_language_list()

# -----------------------------
# Translation Functions
# -----------------------------
@st.cache_data(ttl=300, max_entries=100)
def cached_translate(text, dest_lang_code):
    """Cached translation"""
    try:
        translator = Translator()
        result = translator.translate(text, dest=dest_lang_code)
        return result.text
    except Exception as e:
        return f"Error: {str(e)[:100]}"

def fast_translate(text, target_lang_name):
    """Fast translation"""
    if not text or not text.strip():
        return ""
    
    lang_code = LANGUAGE_DICT.get(target_lang_name, 'en')
    
    if len(text) > 1000:
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        translated_chunks = []
        for chunk in chunks:
            translated = cached_translate(chunk, lang_code)
            translated_chunks.append(translated)
        return " ".join(translated_chunks)
    else:
        return cached_translate(text, lang_code)

@st.cache_data(ttl=600)
def fast_extract_text(file_bytes, file_type):
    """Extract text from files"""
    try:
        from io import BytesIO
        
        if file_type == 'pdf':
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages[:10]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text[:15000]
        
        elif file_type == 'txt':
            return file_bytes.decode('utf-8', errors='ignore')[:15000]
        
        elif file_type == 'docx':
            doc = Document(BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs[:200]])
            return text[:15000]
        
        return ""
    except Exception as e:
        return f"Error: {str(e)[:100]}"

def text_to_speech_fast(text, lang_code):
    """Generate speech"""
    try:
        tts = gTTS(text=text[:500], lang=lang_code, slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

# -----------------------------
# Auth Page
# -----------------------------
def show_auth_page():
    """Login/Register page"""
    st.markdown("""
    <div class='header'>
        <h1 style='font-size: 42px; margin-bottom: 10px;'>AI Translator</h1>
        <p style='font-size: 16px; opacity: 0.9;'>
            Advanced Translation Platform with Real-time Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Login")
        
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                with st.spinner("Signing in..."):
                    success, user = authenticate_user(username, password)
                    if success:
                        st.session_state.user = {
                            "id": user[0], 
                            "username": user[1]
                        }
                        st.session_state.page = "dashboard"
                        st.success("✅ Welcome!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            else:
                st.warning("Please enter username and password")
        
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.user = {"id": 0, "username": "Guest"}
            st.session_state.page = "dashboard"
            st.rerun()
    
    with col2:
        st.markdown("### 📝 Register")
        
        new_user = st.text_input("Choose Username", key="reg_user")
        new_email = st.text_input("Email (optional)", key="reg_email")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", type="primary", use_container_width=True):
            if not new_user or not new_pass:
                st.warning("Username and password required")
            elif new_pass != confirm_pass:
                st.error("Passwords don't match")
            else:
                with st.spinner("Creating account..."):
                    success, msg = register_user(new_user, new_pass, new_email)
                    if success:
                        st.success("✅ Account created! Please login")
                    else:
                        st.error(f"❌ {msg}")

# -----------------------------
# Dashboard Header
# -----------------------------
def show_dashboard_header():
    """Dashboard header"""
    col1, col2, col3 = st.columns([4, 2, 1])
    
    with col1:
        st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 15px;'>
                <h1 style='color: #667eea; margin: 0;'>AI Translator</h1>
                <span style='font-size: 14px; color: #666;'>
                    Professional Translation Platform
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.user:
            st.markdown(f"""
                <div class='user-badge'>
                    👤 {st.session_state.user['username']}
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown("---")

# -----------------------------
# Dashboard Navigation
# -----------------------------
def show_dashboard_nav():
    """Dashboard navigation tabs"""
    tabs = ["Translate", "History", "Analytics", "Settings"]
    
    cols = st.columns(len(tabs))
    for idx, tab in enumerate(tabs):
        with cols[idx]:
            if st.button(tab, use_container_width=True, 
                        type="primary" if st.session_state.dashboard_tab == tab.lower() else "secondary"):
                st.session_state.dashboard_tab = tab.lower()
                st.rerun()
    
    st.markdown("---")

# -----------------------------
# Translate Page
# -----------------------------
def show_translate_page():
    """Main translation interface"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Source Text")
        
        input_text = st.text_area(
            "Enter text:",
            height=200,
            placeholder="Type or paste text here...",
            value=st.session_state.input_text,
            key="translate_input"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Or upload file:",
            type=['pdf', 'txt', 'docx'],
            key="file_upload"
        )
        
        if uploaded_file:
            with st.spinner("Extracting text..."):
                file_bytes = uploaded_file.getvalue()
                file_ext = uploaded_file.name.split('.')[-1].lower()
                extracted = fast_extract_text(file_bytes, file_ext)
                if extracted and not extracted.startswith("Error"):
                    input_text = extracted
                    st.success(f"✅ Extracted {len(extracted)} characters")
        
        st.session_state.input_text = input_text
    
    with col2:
        st.markdown("### 🌍 Translation Settings")
        
        # Language selection
        target_lang = st.selectbox(
            "Translate to:",
            sorted(LANGUAGE_DICT.keys()),
            index=list(sorted(LANGUAGE_DICT.keys())).index("Urdu") 
            if "Urdu" in LANGUAGE_DICT else 0,
            key="target_lang_select"
        )
        
        st.session_state.target_lang = target_lang
        
        # Translation options
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            auto_detect = st.checkbox("Auto-detect language", value=True)
        with col_opt2:
            preserve_format = st.checkbox("Keep formatting", value=True)
    
    # Translate button
    if st.button("🚀 Translate Now", type="primary", use_container_width=True):
        if input_text and input_text.strip():
            with st.spinner("Translating..."):
                translated = fast_translate(input_text, target_lang)
                st.session_state.translated_text = translated
                
                # Save to history
                if st.session_state.user and st.session_state.user["id"] != 0:
                    save_translation(
                        st.session_state.user["id"],
                        input_text[:500],
                        translated[:500],
                        "auto",
                        target_lang,
                        len(input_text)
                    )
                
                st.success("✅ Translation complete!")
    
    # Show result
    if st.session_state.translated_text:
        st.markdown("### 📄 Translation Result")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("**Original Text:**")
            st.text_area("", value=input_text[:500], height=150, disabled=True)
        
        with col_res2:
            st.markdown(f"**Translated ({target_lang}):**")
            st.text_area("", value=st.session_state.translated_text, height=150, disabled=True)
        
        # Actions
        st.markdown("### ⚡ Actions")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            # Text to Speech
            lang_code = LANGUAGE_DICT.get(target_lang, 'en')
            audio = text_to_speech_fast(st.session_state.translated_text, lang_code)
            if audio:
                st.audio(audio, format="audio/mp3")
        
        with col_act2:
            # Download
            st.download_button(
                "📥 Download",
                data=st.session_state.translated_text,
                file_name=f"translation_{target_lang}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_act3:
            # Copy
            if st.button("📋 Copy Text", use_container_width=True):
                st.success("Copied to clipboard!")

# -----------------------------
# History Page
# -----------------------------
def show_history_page():
    """Translation history"""
    st.markdown("## 📚 Translation History")
    
    if st.session_state.user and st.session_state.user["id"] != 0:
        translations = get_user_translations(st.session_state.user["id"], limit=50)
        
        if translations:
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                    <div class='metric-box'>
                        <div class='metric-value'>{len(translations)}</div>
                        <div class='metric-label'>Total Translations</div>
                    </div>
                """, unsafe_allow_html=True)
            
            total_chars = sum(t[7] for t in translations)
            with col2:
                st.markdown(f"""
                    <div class='metric-box'>
                        <div class='metric-value'>{total_chars:,}</div>
                        <div class='metric-label'>Characters</div>
                    </div>
                """, unsafe_allow_html=True)
            
            unique_langs = len(set(t[5] for t in translations))
            with col3:
                st.markdown(f"""
                    <div class='metric-box'>
                        <div class='metric-value'>{unique_langs}</div>
                        <div class='metric-label'>Languages</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Search
            search = st.text_input("🔍 Search in translations...")
            
            # Display translations
            for trans in translations:
                if search and search.lower() not in trans[2].lower() and search.lower() not in trans[3].lower():
                    continue
                
                with st.expander(f"{trans[6]} | {trans[5]} | {trans[7]} chars", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Source Text:**")
                        st.text(trans[2][:200] + "..." if len(trans[2]) > 200 else trans[2])
                    with col2:
                        st.markdown(f"**Translated ({trans[5]}):**")
                        st.text(trans[3][:200] + "..." if len(trans[3]) > 200 else trans[3])
                    
                    if st.button(f"Use This", key=f"use_{trans[0]}"):
                        st.session_state.translated_text = trans[3]
                        st.session_state.target_lang = trans[5]
                        st.session_state.dashboard_tab = "translate"
                        st.rerun()
        else:
            st.info("No translation history yet")
    else:
        st.info("Guest mode - History not saved")

# -----------------------------
# Analytics Page
# -----------------------------
def show_analytics_page():
    """Analytics dashboard"""
    st.markdown("## 📊 Analytics Dashboard")
    
    if st.session_state.user and st.session_state.user["id"] != 0:
        stats = get_user_stats(st.session_state.user["id"])
        
        # Top metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div class='stats-card'>
                    <h3>Total Translations</h3>
                    <h1 style='color: #667eea;'>{stats['total_translations']}</h1>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='stats-card'>
                    <h3>Characters Translated</h3>
                    <h1 style='color: #667eea;'>{stats['total_chars']:,}</h1>
                </div>
            """, unsafe_allow_html=True)
        
        # Language distribution
        st.markdown("### 🌍 Language Distribution")
        
        if stats['top_languages']:
            df = pd.DataFrame(stats['top_languages'], columns=['Language', 'Count'])
            fig = px.pie(df, values='Count', names='Language', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
            # Bar chart
            fig2 = px.bar(df, x='Language', y='Count', color='Language')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No translation data yet")
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        translations = get_user_translations(st.session_state.user["id"], limit=10)
        
        if translations:
            data = []
            for trans in translations:
                data.append({
                    'Date': trans[6],
                    'Language': trans[5],
                    'Characters': trans[7]
                })
            
            df_activity = pd.DataFrame(data)
            st.dataframe(df_activity, use_container_width=True)
    else:
        st.info("Guest mode - Analytics not available")

# -----------------------------
# Settings Page
# -----------------------------
def show_settings_page():
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    if st.session_state.user:
        tab1, tab2 = st.tabs(["Preferences", "Account"])
        
        with tab1:
            st.markdown("### Translation Preferences")
            
            default_lang = st.selectbox(
                "Default Language",
                sorted(LANGUAGE_DICT.keys()),
                index=list(sorted(LANGUAGE_DICT.keys())).index("Urdu") 
                if "Urdu" in LANGUAGE_DICT else 0
            )
            
            col1, col2 = st.columns(2)
            with col1:
                auto_save = st.checkbox("Auto-save translations", value=True)
                auto_detect = st.checkbox("Auto-detect language", value=True)
            with col2:
                show_stats = st.checkbox("Show statistics", value=True)
                dark_mode = st.checkbox("Dark mode", value=False)
            
            if st.button("Save Preferences", type="primary"):
                st.success("Preferences saved!")
        
        with tab2:
            st.markdown("### Account Settings")
            
            col1, col2 = st.columns(2)
            with col1:
                current_user = st.text_input("Username", value=st.session_state.user["username"])
            with col2:
                current_email = st.text_input("Email", value="user@example.com")
            
            st.markdown("### Change Password")
            col1, col2 = st.columns(2)
            with col1:
                old_pass = st.text_input("Current Password", type="password")
                new_pass = st.text_input("New Password", type="password")
            with col2:
                confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.button("Update Account", type="primary"):
                st.success("Account updated!")
            
            st.markdown("---")
            
            if st.button("Delete Account", type="secondary"):
                st.warning("This action cannot be undone!")
    else:
        st.info("Please login to access settings")

# -----------------------------
# Main Dashboard
# -----------------------------
def show_dashboard():
    """Main dashboard"""
    # Header
    show_dashboard_header()
    
    # Navigation
    show_dashboard_nav()
    
    # Content based on selected tab
    if st.session_state.dashboard_tab == "translate":
        show_translate_page()
    
    elif st.session_state.dashboard_tab == "history":
        show_history_page()
    
    elif st.session_state.dashboard_tab == "analytics":
        show_analytics_page()
    
    elif st.session_state.dashboard_tab == "settings":
        show_settings_page()

# -----------------------------
# Main App
# -----------------------------
def main():
    """Main app router"""
    if st.session_state.page == "login":
        show_auth_page()
    elif st.session_state.page == "dashboard":
        show_dashboard()

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()s
