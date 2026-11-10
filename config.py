"""VELOCITY GEORGIAN - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY GEORGIAN"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "GEORGIAN"
HANDLE = "@velocitygeorgian"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "ka",
    "name": "Georgian",
    "native_name": "ქართული",
    "history_key": "georgian",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "ka-GE-GiorgiNeural",
    "native_fallback_voice": "ka-GE-EkaNeural",
    "native_engine": "edge",
    "native_lang_code": "ka",
    "english_rate": "-2%",
    "native_rate": "-6%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "ქართული",
    "translit_label": "SAY IT LIKE",
    "greeting": "გამარჯობა!",
    "encouragement": "შესანიშნავია!",
    "rtl": False,
    "char_tiles": False,
    "script_font": "NotoSansGeorgian-Bold.ttf",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "მისალმება", "hand", "#1CB0F6"),
    ("Family", "ოჯახი", "users", "#FF4B4B"),
    ("Food", "საკვები", "fork", "#FF7A00"),
    ("Travel", "მოგზაურობა", "plane", "#1CB0F6"),
    ("Numbers", "რიცხვები", "hash", "#A560E8"),
    ("Time", "დრო", "clock", "#00A889"),
    ("Colors", "ფერები", "palette", "#E056A0"),
    ("Animals", "ცხოველები", "paw", "#FF7A00"),
    ("Weather", "ამინდი", "cloud", "#1CB0F6"),
    ("Emotions", "ემოციები", "smile", "#CE82FF"),
    ("Work", "სამუშაო", "briefcase", "#1CB0F6"),
    ("Health", "ჯანმრთელობა", "heart", "#58CC02"),
    ("Shopping", "შოპინგი", "bag", "#E056A0"),
    ("Directions", "მიმართულებები", "compass", "#1CB0F6"),
    ("Home", "სახლი", "sun", "#FFC800"),
    ("Nature", "ბუნება", "leaf", "#58CC02"),
    ("Sports", "სპორტი", "ball", "#FF7A00"),
    ("Music", "მუსიკა", "music", "#A560E8"),
    ("Education", "განათლება", "book", "#1CB0F6"),
    ("Friendship", "მეგობრობა", "users", "#00A889"),
    ("Love", "სიყვარული", "heart", "#FF4B4B"),
    ("Success", "წარმატება", "trophy", "#F5A700"),
    ("Wisdom", "სიბრძნე", "book", "#A560E8"),
    ("Happiness", "ბედნიერება", "smile", "#F5A700"),
    ("Gratitude", "მადლიერება", "heart", "#FF7A00"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learngeorgian",
    "#georgianlessons",
    "#georgianforbeginners",
    "#languagelearning",
    "#georgianvocabulary",
    "#velocitygeorgian",
    "#dailygeorgian",
    "#georgian",
    "#learnlanguages",
    "#speakgeorgian",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====
