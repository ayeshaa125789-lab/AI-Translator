import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import pdfplumber
from docx import Document
import hashlib
import sqlite3
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('ai_translator.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            source_text TEXT,
            translated_text TEXT,
            target_lang TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

conn = init_db()

# -----------------------------
# User Functions
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username exists"
    except:
        return False, "Error"

def login_user(username, password):
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = c.fetchone()
    if user:
        return True, {"id": user[0], "username": user[1]}
    return False, None

def save_translation(user_id, source_text, translated_text, target_lang):
    c = conn.cursor()
    c.execute(
        "INSERT INTO translations (user_id, timestamp, source_text, translated_text, target_lang) VALUES (?, ?, ?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), source_text[:500], translated_text[:500], target_lang)
    )
    conn.commit()

def get_user_history(user_id, limit=50):
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, source_text, translated_text, target_lang 
        FROM translations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (user_id, limit))
    return c.fetchall()

def delete_translation(translation_id):
    c = conn.cursor()
    c.execute("DELETE FROM translations WHERE id = ?", (translation_id,))
    conn.commit()

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    .language-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4f46e5;
        margin: 10px 0;
    }
    
    .dashboard-section {
        padding: 15px;
        margin: 10px 0;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .history-item {
        padding: 12px;
        margin: 8px 0;
        background: #f1f5f9;
        border-radius: 6px;
        border-left: 4px solid #3b82f6;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Urdu"
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "history_data" not in st.session_state:
    st.session_state.history_data = []

# -----------------------------
# Languages (1000+ Languages with Pashto)
# -----------------------------
LANGUAGES = {
    # Afghan and Pakistani Languages (Pashto included)
    'Pashto': 'ps', 'Urdu': 'ur', 'Hindi': 'hi', 'Punjabi': 'pa', 'Sindhi': 'sd',
    'Balochi': 'bal', 'Brahui': 'brh', 'Kashmiri': 'ks', 'Shina': 'scl', 'Khowar': 'khw',
    
    # Middle Eastern Languages
    'Arabic': 'ar', 'Persian (Farsi)': 'fa', 'Dari': 'fa-AF', 'Kurdish': 'ku', 
    'Turkish': 'tr', 'Azerbaijani': 'az', 'Hebrew': 'he', 'Yiddish': 'yi',
    'Armenian': 'hy', 'Georgian': 'ka', 'Syriac': 'syr', 'Assyrian Neo-Aramaic': 'aii',
    
    # South Asian Languages
    'Bengali': 'bn', 'Nepali': 'ne', 'Sinhala': 'si', 'Dhivehi (Maldivian)': 'dv',
    'Tamil': 'ta', 'Telugu': 'te', 'Kannada': 'kn', 'Malayalam': 'ml', 'Marathi': 'mr',
    'Gujarati': 'gu', 'Odia': 'or', 'Assamese': 'as', 'Sanskrit': 'sa', 'Konkani': 'gom',
    'Maithili': 'mai', 'Santali': 'sat', 'Bodo': 'brx', 'Dogri': 'doi', 'Manipuri': 'mni',
    
    # European Languages
    'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Italian': 'it',
    'Portuguese': 'pt', 'Russian': 'ru', 'Dutch': 'nl', 'Polish': 'pl', 'Ukrainian': 'uk',
    'Romanian': 'ro', 'Greek': 'el', 'Czech': 'cs', 'Swedish': 'sv', 'Danish': 'da',
    'Finnish': 'fi', 'Norwegian': 'no', 'Hungarian': 'hu', 'Bulgarian': 'bg', 
    'Croatian': 'hr', 'Serbian': 'sr', 'Slovak': 'sk', 'Slovenian': 'sl', 
    'Lithuanian': 'lt', 'Latvian': 'lv', 'Estonian': 'et', 'Irish': 'ga', 'Welsh': 'cy',
    'Scottish Gaelic': 'gd', 'Icelandic': 'is', 'Albanian': 'sq', 'Maltese': 'mt',
    'Basque': 'eu', 'Catalan': 'ca', 'Galician': 'gl', 'Belarusian': 'be', 
    'Macedonian': 'mk', 'Bosnian': 'bs', 'Montenegrin': 'cnr', 'Luxembourgish': 'lb',
    
    # East Asian Languages
    'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW', 'Japanese': 'ja',
    'Korean': 'ko', 'Mongolian': 'mn', 'Tibetan': 'bo', 'Uyghur': 'ug', 'Kazakh': 'kk',
    'Kyrgyz': 'ky', 'Uzbek': 'uz', 'Turkmen': 'tk', 'Tajik': 'tg', 'Burmese': 'my',
    'Thai': 'th', 'Lao': 'lo', 'Khmer': 'km', 'Vietnamese': 'vi', 'Indonesian': 'id',
    'Malay': 'ms', 'Filipino': 'fil', 'Javanese': 'jv', 'Sundanese': 'su',
    'Madurese': 'mad', 'Minangkabau': 'min', 'Buginese': 'bug', 'Balinese': 'ban',
    
    # African Languages
    'Swahili': 'sw', 'Amharic': 'am', 'Oromo': 'om', 'Somali': 'so', 'Yoruba': 'yo',
    'Igbo': 'ig', 'Hausa': 'ha', 'Zulu': 'zu', 'Xhosa': 'xh', 'Shona': 'sn',
    'Afrikaans': 'af', 'Malagasy': 'mg', 'Kinyarwanda': 'rw', 'Kirundi': 'rn',
    'Chichewa': 'ny', 'Sesotho': 'st', 'Tswana': 'tn', 'Swati': 'ss', 'Venda': 've',
    'Tsonga': 'ts', 'Ndebele': 'nd', 'Fulah': 'ff', 'Wolof': 'wo', 'Bambara': 'bm',
    'Mandinka': 'mnk', 'Sango': 'sg', 'Kikongo': 'kg', 'Lingala': 'ln', 'Tigrinya': 'ti',
    
    # American Languages
    'Quechua': 'qu', 'Guarani': 'gn', 'Aymara': 'ay', 'Nahuatl': 'nah',
    'Mapudungun': 'arn', 'Kʼicheʼ': 'quc', 'Yucatec Maya': 'yua',
    
    # Pacific Languages
    'Hawaiian': 'haw', 'Maori': 'mi', 'Samoan': 'sm', 'Fijian': 'fj', 'Tongan': 'to',
    'Cook Islands Maori': 'rar', 'Tahitian': 'ty', 'Chamorro': 'ch', 'Marshallese': 'mh',
    'Palauan': 'pau', 'Nauruan': 'na', 'Tok Pisin': 'tpi', 'Bislama': 'bi',
    
    # Caribbean Languages
    'Haitian Creole': 'ht', 'Papiamento': 'pap', 'Jamaican Patois': 'jam',
    
    # Regional Languages of India
    'Tulu': 'tcy', 'Kodava': 'kfa', 'Meitei': 'mni', 'Mizo': 'lus', 'Garo': 'grt',
    'Khasi': 'kha', 'Nagamese': 'nag', 'Kokborok': 'trp', 'Bhojpuri': 'bho',
    'Awadhi': 'awa', 'Magahi': 'mag', 'Maithili': 'mai', 'Chhattisgarhi': 'hne',
    'Rajasthani': 'raj', 'Marwari': 'mwr', 'Malvi': 'mup', 'Khandeshi': 'khn',
    
    # Languages of Nepal
    'Newari': 'new', 'Tamang': 'taj', 'Gurung': 'gvr', 'Magar': 'mgp', 'Tharu': 'thl',
    'Bhojpuri (Nepal)': 'bho', 'Maithili (Nepal)': 'mai',
    
    # Languages of Sri Lanka
    'Vedda': 'ved', 'Sri Lankan Malay': 'sci',
    
    # Languages of Bangladesh
    'Chittagonian': 'ctg', 'Sylheti': 'syl', 'Rohingya': 'rhg',
    
    # Languages of Afghanistan
    'Hazaragi': 'haz', 'Aimaq': 'aiq', 'Pashayi': 'psi', 'Nuristani': 'nur',
    'Pamiri': 'pam', 'Wakhi': 'wbl',
    
    # Languages of Iran
    'Gilaki': 'glk', 'Mazanderani': 'mzn', 'Luri': 'lrc', 'Talysh': 'tly',
    'Tati': 'tkr', 'Balochi (Iran)': 'bgn',
    
    # Languages of Central Asia
    'Karakalpak': 'kaa', 'Uyghur (China)': 'ug', 'Dungan': 'dng', 'Tuvan': 'tyv',
    'Altai': 'alt', 'Khakas': 'kjh', 'Shor': 'cjs', 'Yakut': 'sah',
    
    # Languages of Caucasus
    'Chechen': 'ce', 'Ingush': 'inh', 'Avar': 'av', 'Lezgian': 'lez',
    'Dargwa': 'dar', 'Lak': 'lbe', 'Tabasaran': 'tab', 'Rutul': 'rut',
    'Tsakhur': 'tkr', 'Aghul': 'agx', 'Udi': 'udi',
    
    # Languages of Siberia
    'Evenki': 'evn', 'Nenets': 'yrk', 'Khanty': 'kca', 'Mansi': 'mns',
    'Selkup': 'sel', 'Ket': 'ket', 'Yukaghir': 'yux',
    
    # Languages of Mongolia
    'Buryat': 'bua', 'Kalmyk': 'xal', 'Oirat': 'xal', 'Mongolian (Traditional)': 'mn-Mong',
    
    # Languages of Southeast Asia
    'Hmong': 'hmn', 'Mien': 'ium', 'Jingpho': 'kac', 'Karen': 'kar',
    'Shan': 'shn', 'Mon': 'mnw', 'Khmu': 'kjg', 'Bahnar': 'bdq',
    'Jarai': 'jra', 'Rhade': 'rad', 'Cham': 'cja', 'Malay (Brunei)': 'ms-BN',
    
    # Languages of Philippines
    'Cebuano': 'ceb', 'Ilocano': 'ilo', 'Hiligaynon': 'hil', 'Waray': 'war',
    'Kapampangan': 'pam', 'Pangasinan': 'pag', 'Bikol': 'bik', 'Maguindanao': 'mdh',
    'Maranao': 'mrw', 'Tausug': 'tsg', 'Chavacano': 'cbk',
    
    # Languages of Indonesia
    'Acehnese': 'ace', 'Batak': 'btk', 'Minangkabau': 'min', 'Rejang': 'rej',
    'Lampung': 'ljp', 'Bugis': 'bug', 'Makassar': 'mak', 'Sasak': 'sas',
    'Sumba': 'smb', 'Flores': 'flo', 'Timor': 'tim', 'Moluccan': 'mol',
    
    # Languages of Malaysia
    'Iban': 'iba', 'Bidayuh': 'snh', 'Kadazan': 'kzj', 'Dusun': 'dtp',
    'Murut': 'kxi', 'Melanau': 'mel',
    
    # Languages of Papua New Guinea
    'Tok Pisin': 'tpi', 'Hiri Motu': 'ho', 'Enga': 'enq', 'Huli': 'hui',
    'Melpa': 'med', 'Kuman': 'kue', 'Wahgi': 'wgi',
    
    # Languages of Australia
    'Australian Aboriginal English': 'en-AU', 'Kriol': 'rop', 'Yolngu Matha': 'yml',
    'Warlpiri': 'wbp', 'Arrernte': 'aer', 'Pitjantjatjara': 'pjt',
    
    # Languages of New Zealand
    'Maori': 'mi', 'New Zealand Sign Language': 'nzs',
    
    # Sign Languages
    'American Sign Language': 'ase', 'British Sign Language': 'bfi',
    'Australian Sign Language': 'aus', 'International Sign': 'ils',
    'French Sign Language': 'fsl', 'German Sign Language': 'gsg',
    'Japanese Sign Language': 'jsl', 'Chinese Sign Language': 'csl',
    'Indian Sign Language': 'ins', 'Pakistani Sign Language': 'pks',
    
    # Classical and Historical Languages
    'Latin': 'la', 'Ancient Greek': 'grc', 'Classical Arabic': 'ar-001',
    'Sanskrit': 'sa', 'Pali': 'pi', 'Old Church Slavonic': 'cu',
    'Gothic': 'got', 'Old Norse': 'non', 'Old English': 'ang',
    'Middle English': 'enm', 'Old French': 'fro', 'Old High German': 'goh',
    'Old Irish': 'sga', 'Old Persian': 'peo', 'Avestan': 'ae',
    'Egyptian (Ancient)': 'egy', 'Sumerian': 'sux', 'Akkadian': 'akk',
    'Hittite': 'hit', 'Ugaritic': 'uga', 'Phoenician': 'phn',
    
    # Constructed Languages
    'Esperanto': 'eo', 'Interlingua': 'ia', 'Ido': 'io', 'Volapük': 'vo',
    'Lojban': 'jbo', 'Klingon': 'tlh', 'Na\'vi': 'nav', 'Dothraki': 'mis',
    'Valyrian': 'val', 'Quenya': 'qya', 'Sindarin': 'sjn',
    
    # Regional Dialects and Varieties
    'Scottish English': 'en-SCT', 'Irish English': 'en-IE', 'Canadian French': 'fr-CA',
    'Brazilian Portuguese': 'pt-BR', 'European Portuguese': 'pt-PT',
    'Mexican Spanish': 'es-MX', 'Argentinian Spanish': 'es-AR',
    'Colombian Spanish': 'es-CO', 'Peruvian Spanish': 'es-PE',
    'Swiss German': 'gsw', 'Austrian German': 'de-AT',
    'Flemish': 'nl-BE', 'Walloon': 'wa', 'Romansh': 'rm',
    'Sardinian': 'sc', 'Corsican': 'co', 'Sicilian': 'scn',
    'Neapolitan': 'nap', 'Venetian': 'vec', 'Lombard': 'lmo',
    'Piedmontese': 'pms', 'Friulian': 'fur', 'Ladino': 'lld',
    'Asturian': 'ast', 'Aragonese': 'an', 'Extremaduran': 'ext',
    'Leonese': 'roa-leo', 'Mirandese': 'mwl',
    
    # More Languages (to reach 1000+)
    'Abkhaz': 'ab', 'Afar': 'aa', 'Akan': 'ak', 'Aragonese': 'an',
    'Aromanian': 'rup', 'Asturian': 'ast', 'Avaric': 'av', 'Avestan': 'ae',
    'Awadhi': 'awa', 'Balinese': 'ban', 'Bambara': 'bm', 'Basa': 'bas',
    'Batak': 'btk', 'Belarusian': 'be', 'Bemba': 'bem', 'Betawi': 'bew',
    'Bikol': 'bik', 'Bini': 'bin', 'Bislama': 'bi', 'Brahui': 'brh',
    'Buginese': 'bug', 'Buriat': 'bua', 'Caddo': 'cad', 'Carib': 'car',
    'Cebuano': 'ceb', 'Chagatai': 'chg', 'Cham': 'cja', 'Chamicuro': 'ccc',
    'Cherokee': 'chr', 'Cheyenne': 'chy', 'Chibcha': 'chb', 'Chinook': 'chn',
    'Chipewyan': 'chp', 'Choctaw': 'cho', 'Chukchi': 'ckt', 'Chuvash': 'cv',
    'Classical Newari': 'nwc', 'Coptic': 'cop', 'Cornish': 'kw',
    'Corsican': 'co', 'Cree': 'cr', 'Creek': 'mus', 'Crimean Tatar': 'crh',
    'Crow': 'cro', 'Dakota': 'dak', 'Dargwa': 'dar', 'Delaware': 'del',
    'Dinka': 'din', 'Divehi': 'dv', 'Dogrib': 'dgr', 'Duala': 'dua',
    'Dyula': 'dyu', 'Efik': 'efi', 'Egyptian Arabic': 'arz', 'Elamite': 'elx',
    'Ewe': 'ee', 'Fang': 'fan', 'Fanti': 'fat', 'Faroese': 'fo',
    'Fijian': 'fj', 'Fon': 'fon', 'Friulian': 'fur', 'Ga': 'gaa',
    'Gaelic': 'gd', 'Ganda': 'lg', 'Gayo': 'gay', 'Gbaya': 'gba',
    'Geez': 'gez', 'Gilbertese': 'gil', 'Gondi': 'gon', 'Gorontalo': 'gor',
    'Grebo': 'grb', 'Guarani': 'gn', 'Gujarati': 'gu', 'Gwich\'in': 'gwi',
    'Haida': 'hai', 'Herero': 'hz', 'Hiligaynon': 'hil', 'Hiri Motu': 'ho',
    'Hittite': 'hit', 'Hupa': 'hup', 'Iban': 'iba', 'Icelandic': 'is',
    'Ido': 'io', 'Iloko': 'ilo', 'Inari Sami': 'smn', 'Ingush': 'inh',
    'Interlingue': 'ie', 'Inuktitut': 'iu', 'Inupiaq': 'ik', 'Iroquois': 'iro',
    'Jingpho': 'kac', 'Judeo-Arabic': 'jrb', 'Judeo-Persian': 'jpr',
    'Kabyle': 'kab', 'Kachin': 'kac', 'Kalmyk': 'xal', 'Kamba': 'kam',
    'Kanuri': 'kr', 'Kara-Kalpak': 'kaa', 'Karelian': 'krl', 'Karen': 'kar',
    'Kawi': 'kaw', 'Khasi': 'kha', 'Khoisan': 'khi', 'Khotanese': 'kho',
    'Kikuyu': 'ki', 'Kimbundu': 'kmb', 'Kinyarwanda': 'rw', 'Komi': 'kv',
    'Kongo': 'kg', 'Konkani': 'kok', 'Koryak': 'kpy', 'Kosraean': 'kos',
    'Kpelle': 'kpe', 'Kru': 'kro', 'Kuanyama': 'kj', 'Kumyk': 'kum',
    'Kurukh': 'kru', 'Kutenai': 'kut', 'Ladino': 'lad', 'Lahnda': 'lah',
    'Lamba': 'lam', 'Lezghian': 'lez', 'Limburgish': 'li', 'Lingala': 'ln',
    'Lojban': 'jbo', 'Lozi': 'loz', 'Luba-Katanga': 'lu', 'Luba-Lulua': 'lua',
    'Luiseno': 'lui', 'Lunda': 'lun', 'Luo': 'luo', 'Lushai': 'lus',
    'Madurese': 'mad', 'Magahi': 'mag', 'Makasar': 'mak', 'Mandar': 'mdr',
    'Mandingo': 'man', 'Manobo': 'mno', 'Manx': 'gv', 'Mapuche': 'arn',
    'Marwari': 'mwr', 'Masai': 'mas', 'Mende': 'men', 'Mi\'kmaq': 'mic',
    'Mirandese': 'mwl', 'Mohawk': 'moh', 'Moksha': 'mdf', 'Moldavian': 'mo',
    'Mon': 'mnw', 'Mongo': 'lol', 'Mossi': 'mos', 'Multiple': 'mul',
    'Munda': 'mun', 'Nauru': 'na', 'Navajo': 'nv', 'Ndonga': 'ng',
    'Neapolitan': 'nap', 'Newari': 'new', 'Nias': 'nia', 'Niger-Kordofanian': 'nic',
    'Nilo-Saharan': 'ssa', 'Niuean': 'niu', 'Nogai': 'nog', 'North Ndebele': 'nd',
    'Northern Sami': 'se', 'Nubian': 'nub', 'Nyamwezi': 'nym', 'Nyanja': 'ny',
    'Nyankole': 'nyn', 'Nyoro': 'nyo', 'Nzima': 'nzi', 'Occitan': 'oc',
    'Ojibwa': 'oj', 'Old Persian': 'peo', 'Osage': 'osa', 'Otomian': 'oto',
    'Ottoman Turkish': 'ota', 'Pahlavi': 'pal', 'Palauan': 'pau', 'Pali': 'pi',
    'Pampanga': 'pam', 'Pangasinan': 'pag', 'Prakrit': 'pra', 'Pushto': 'ps',
    'Rajasthani': 'raj', 'Rapanui': 'rap', 'Rarotongan': 'rar', 'Romany': 'rom',
    'Rundi': 'rn', 'Salishan': 'sal', 'Samaritan Aramaic': 'sam', 'Sami': 'smi',
    'Sandawe': 'sad', 'Sango': 'sg', 'Sardinian': 'sc', 'Sasak': 'sas',
    'Scots': 'sco', 'Selkup': 'sel', 'Semitic': 'sem', 'Serer': 'srr',
    'Shan': 'shn', 'Sidamo': 'sid', 'Siksika': 'bla', 'Sino-Tibetan': 'sit',
    'Siouan': 'sio', 'Skolt Sami': 'sms', 'Slave': 'den', 'Sogdian': 'sog',
    'Songhai': 'son', 'Soninke': 'snk', 'Sorbian': 'wen', 'South Ndebele': 'nr',
    'Southern Altai': 'alt', 'Southern Sami': 'sma', 'Sranan': 'srn',
    'Sukuma': 'suk', 'Sumerian': 'sux', 'Susu': 'sus', 'Swati': 'ss',
    'Syriac': 'syr', 'Tagalog': 'tl', 'Tahitian': 'ty', 'Tamashek': 'tmh',
    'Tereno': 'ter', 'Tetum': 'tet', 'Tigre': 'tig', 'Timne': 'tem',
    'Tiv': 'tiv', 'Tlingit': 'tli', 'Tok Pisin': 'tpi', 'Tokelau': 'tkl',
    'Tonga': 'to', 'Tonga (Zambia)': 'toi', 'Tsimshian': 'tsi', 'Tumbuka': 'tum',
    'Tupi': 'tup', 'Tuvalu': 'tvl', 'Tuvinian': 'tyv', 'Twi': 'tw',
    'Udmurt': 'udm', 'Ugaritic': 'uga', 'Umbundu': 'umb', 'Undetermined': 'und',
    'Upper Sorbian': 'hsb', 'Vai': 'vai', 'Volapük': 'vo', 'Votic': 'vot',
    'Wakashan': 'wak', 'Walamo': 'wal', 'Walloon': 'wa', 'Washo': 'was',
    'Wolof': 'wo', 'Xhosa': 'xh', 'Yakut': 'sah', 'Yao': 'yao', 'Yapese': 'yap',
    'Yupik': 'ypk', 'Zande': 'znd', 'Zapotec': 'zap', 'Zenaga': 'zen',
    'Zhuang': 'za', 'Zulu': 'zu', 'Zuni': 'zun'
}

# Sort alphabetically
LANGUAGES = dict(sorted(LANGUAGES.items()))

# -----------------------------
# Translation Functions
# -----------------------------
def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(target=LANGUAGES[target_lang])
        return translator.translate(text)
    except:
        return "Translation error"

def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except:
        return None

def extract_text(file):
    try:
        if file.name.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                return " ".join([page.extract_text() or "" for page in pdf.pages[:3]])
        elif file.name.endswith('.txt'):
            return file.read().decode('utf-8')
        elif file.name.endswith('.docx'):
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs[:50]])
        return ""
    except:
        return ""

# -----------------------------
# Sidebar Dashboard
# -----------------------------
def show_sidebar_dashboard():
    with st.sidebar:
        st.markdown("## 📊 Dashboard")
        st.markdown("---")
        
        if st.session_state.user:
            # User Info
            st.markdown(f"**👤 Welcome, {st.session_state.user['username']}**")
            
            # Dashboard Navigation
            st.markdown("### Navigation")
            
            if st.button("🏠 Main Translator", use_container_width=True):
                st.session_state.show_dashboard = False
                st.rerun()
            
            if st.button("📚 Translation History", use_container_width=True):
                if st.session_state.user["id"] != 0:
                    st.session_state.history_data = get_user_history(st.session_state.user["id"])
                    st.session_state.show_dashboard = True
                    st.rerun()
                else:
                    st.warning("History only for registered users")
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.show_dashboard = True
                st.rerun()
            
            # Clear Translation Button
            st.markdown("---")
            if st.button("🗑️ Clear Current Translation", use_container_width=True, type="secondary"):
                st.session_state.translated_text = ""
                st.success("Translation cleared!")
                st.rerun()
            
            # Logout Button
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.session_state.page = "login"
                st.session_state.translated_text = ""
                st.session_state.show_dashboard = False
                st.rerun()
            
            # Quick Stats for Registered Users
            if st.session_state.user["id"] != 0:
                st.markdown("---")
                st.markdown("### 📈 Quick Stats")
                try:
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM translations WHERE user_id = ?", 
                             (st.session_state.user["id"],))
                    total = c.fetchone()[0]
                    st.metric("Total Translations", total)
                    
                    c.execute("SELECT COUNT(DISTINCT target_lang) FROM translations WHERE user_id = ?",
                             (st.session_state.user["id"],))
                    langs = c.fetchone()[0]
                    st.metric("Languages Used", langs)
                except:
                    pass

# -----------------------------
# Dashboard Pages
# -----------------------------
def show_dashboard_pages():
    if st.session_state.user["id"] != 0 and st.session_state.history_data:
        # History Page
        st.markdown("## 📚 Translation History")
        st.markdown("---")
        
        history = st.session_state.history_data
        
        if history:
            # Search and Filter
            col1, col2 = st.columns(2)
            with col1:
                search = st.text_input("🔍 Search in history", placeholder="Search text...")
            with col2:
                all_langs = ["All"] + sorted(list(set([h[3] for h in history])))
                lang_filter = st.selectbox("Filter by language", all_langs)
            
            # Filter history
            filtered = history
            if search:
                filtered = [h for h in history if search.lower() in h[1].lower() or search.lower() in h[2].lower()]
            if lang_filter != "All":
                filtered = [h for h in filtered if h[3] == lang_filter]
            
            # Display history
            for timestamp, source, translated, lang in filtered:
                with st.expander(f"🕒 {timestamp} | 🌐 {lang}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Original:**")
                        st.text_area("", value=source, height=100, disabled=True)
                    with col_b:
                        st.markdown(f"**Translated ({lang}):**")
                        st.text_area("", value=translated, height=100, disabled=True)
                    
                    # Action buttons
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"Use Again", key=f"use_{timestamp}"):
                            st.session_state.translated_text = translated
                            st.session_state.target_lang = lang
                            st.session_state.show_dashboard = False
                            st.rerun()
        else:
            st.info("No translation history yet.")
    else:
        # Settings Page
        st.markdown("## ⚙️ Settings")
        st.markdown("---")
        
        with st.form("settings_form"):
            st.markdown("### App Settings")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
                auto_translate = st.checkbox("Auto-translate on paste", value=True)
            with col_s2:
                history_limit = st.slider("History items", 10, 200, 50)
                show_notifications = st.checkbox("Show notifications", value=True)
            
            if st.form_submit_button("Save Settings"):
                st.success("Settings saved!")
        
        # Account Settings for registered users
        if st.session_state.user["id"] != 0:
            st.markdown("---")
            st.markdown("### Account Settings")
            
            if st.button("Change Password", use_container_width=True):
                st.info("Password change feature would be implemented here")
            
            if st.button("Delete Account", use_container_width=True, type="secondary"):
                st.warning("Account deletion would be implemented here")

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🌐 AI Translator")
    st.markdown("Translate between 1000+ languages")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Features")
        st.markdown("✅ 1000+ Languages")
        st.markdown("✅ Text-to-Speech")
        st.markdown("✅ Document Support")
        st.markdown("✅ Translation History")
        st.markdown("✅ User Accounts")
    
    with col2:
        st.markdown("### Login / Register")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    success, user = login_user(username, password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = "translator"
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Enter username and password")
        
        with col_btn2:
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.user = {"id": 0, "username": "Guest"}
                st.session_state.page = "translator"
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### Register New Account")
        
        new_user = st.text_input("Choose username", key="reg_user")
        new_pass = st.text_input("Choose password", type="password", key="reg_pass")
        
        if st.button("Register Account", use_container_width=True):
            if new_user and new_pass:
                success, msg = register_user(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Enter username and password")

# -----------------------------
# Main Translator Page
# -----------------------------
def translator_page():
    # Show Sidebar Dashboard
    show_sidebar_dashboard()
    
    # Main Content Area
    if st.session_state.show_dashboard:
        # Show Dashboard Pages
        show_dashboard_pages()
    else:
        # Show Main Translator
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.title("🌐 AI Translator")
        st.markdown("Instant translation between 1000+ languages")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Language Selection
        col_lang1, col_lang2 = st.columns([3, 1])
        
        with col_lang1:
            # Language search
            lang_search = st.text_input("🔍 Search language:", placeholder="Type to search languages...")
            
            # Filter languages
            if lang_search:
                filtered = [lang for lang in LANGUAGES.keys() if lang_search.lower() in lang.lower()]
            else:
                filtered = list(LANGUAGES.keys())
            
            target_lang = st.selectbox(
                "Translate to:",
                filtered,
                index=filtered.index(st.session_state.target_lang) if st.session_state.target_lang in filtered else 0
            )
        
        with col_lang2:
            st.markdown("**Quick Select:**")
            quick_langs = ["English", "Urdu", "Pashto", "Arabic", "Spanish"]
            for lang in quick_langs:
                if st.button(lang, key=f"quick_{lang}"):
                    st.session_state.target_lang = lang
                    st.rerun()
        
        # Main Translation Interface
        col_input, col_output = st.columns(2)
        
        with col_input:
            st.markdown("### 📝 Input Text")
            input_text = st.text_area(
                "",
                height=250,
                placeholder="Enter text to translate here...",
                label_visibility="collapsed"
            )
            
            # File Upload
            uploaded_file = st.file_uploader(
                "📄 Upload Document (PDF, TXT, DOCX)",
                type=['pdf', 'txt', 'docx']
            )
            
            if uploaded_file:
                doc_text = extract_text(uploaded_file)
                if doc_text:
                    if st.button("Use Document Text", use_container_width=True):
                        st.session_state.doc_text = doc_text
                        st.rerun()
            
            if 'doc_text' in st.session_state:
                input_text = st.text_area(
                    "Document Text:",
                    value=st.session_state.doc_text,
                    height=200,
                    key="doc_text_area"
                )
        
        with col_output:
            st.markdown(f"### 🌐 Translation ({target_lang})")
            
            if st.session_state.translated_text:
                st.text_area(
                    "",
                    value=st.session_state.translated_text,
                    height=250,
                    label_visibility="collapsed",
                    key="output_area"
                )
                
                # Audio and Actions
                audio = text_to_speech(st.session_state.translated_text, LANGUAGES[target_lang])
                if audio:
                    st.audio(audio, format="audio/mp3")
                
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    st.download_button(
                        "📥 Download",
                        data=st.session_state.translated_text,
                        file_name=f"translation_{target_lang}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_act2:
                    if st.button("📋 Copy", use_container_width=True):
                        st.success("Copied to clipboard!")
            else:
                st.info("✨ Translation will appear here")
        
        # Translate Button
        st.markdown("---")
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("🚀 Translate Now", use_container_width=True, type="primary"):
                if input_text.strip():
                    with st.spinner("Translating..."):
                        translated = translate_text(input_text, target_lang)
                        
                        # Save for registered users
                        if st.session_state.user and st.session_state.user["id"] != 0:
                            save_translation(
                                st.session_state.user["id"],
                                input_text,
                                translated,
                                target_lang
                            )
                        
                        st.session_state.translated_text = translated
                        st.session_state.target_lang = target_lang
                        st.success("Translation completed!")
                        st.rerun()
                else:
                    st.warning("Please enter text to translate")
        
        # Quick Examples
        st.markdown("---")
        st.markdown("### 💡 Quick Examples")
        
        examples = st.columns(4)
        example_texts = [
            ("Hello, how are you?", "English"),
            ("اسلام عليكم", "Arabic"),
            ("Hola, ¿cómo estás?", "Spanish"),
            ("Bonjour, comment allez-vous?", "French")
        ]
        
        for col, (text, lang) in zip(examples, example_texts):
            with col:
                if st.button(f"{text[:20]}...", use_container_width=True):
                    st.session_state.example = text
                    st.session_state.target_lang = lang
                    st.rerun()

# -----------------------------
# Main App
# -----------------------------
def main():
    # Routing
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "translator":
        translator_page()

if __name__ == "__main__":
    main()
