"""
Georgian Language Learning Automation - Bilingual English/Georgian Content Generator
Creates engaging video content for learning Georgian language
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

# Directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

# Video settings (9:16 vertical)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# English category names (for learners)
CATEGORIES_ENGLISH = [
    "Greetings", "Family", "Food", "Travel", "Numbers",
    "Time", "Colors", "Animals", "Weather", "Emotions",
    "Work", "Health", "Shopping", "Directions", "Home",
    "Nature", "Sports", "Music", "Education", "Friendship",
    "Love", "Success", "Wisdom", "Happiness", "Gratitude"
]

# Georgian translations for categories
CATEGORIES_GEORGIAN = {
    "Greetings": "მისალმება",
    "Family": "ოჯახი",
    "Food": "საკვები",
    "Travel": "მოგზაურობა",
    "Numbers": "რიცხვები",
    "Time": "დრო",
    "Colors": "ფერები",
    "Animals": "ცხოველები",
    "Weather": "ამინდი",
    "Emotions": "ემოციები",
    "Work": "სამუშაო",
    "Health": "ჯანმრთელობა",
    "Shopping": "შოპინგი",
    "Directions": "მიმართულებები",
    "Home": "სახლი",
    "Nature": "ბუნება",
    "Sports": "სპორტი",
    "Music": "მუსიკა",
    "Education": "განათლება",
    "Friendship": "მეგობრობა",
    "Love": "სიყვარული",
    "Success": "წარმატება",
    "Wisdom": "სიბრძნე",
    "Happiness": "ბედნიერება",
    "Gratitude": "მადლიერება"
}

# Edge TTS voices - Georgian native voices available
ENGLISH_VOICE = "en-US-GuyNeural"
GEORGIAN_VOICE = "ka-GE-GiorgiNeural"  # Native Georgian male voice

# AI Model - loaded from environment
AI_MODEL = os.getenv("AI_MODEL")

def mask_key(k):
    return f"{k[:6]}...{k[-4:]}" if k and len(k) > 10 else ("MISSING" if not k else k)

print(f"[config] POLLINATIONS_API_KEY: {mask_key(POLLINATIONS_API_KEY)}")
print(f"[config] AI_MODEL: {AI_MODEL or 'MISSING'}")

if not AI_MODEL:
    print("⚠️  WARNING: AI_MODEL not found in .env file. AI generation will fail.")
if not POLLINATIONS_API_KEY:
    print("⚠️  WARNING: POLLINATIONS_API_KEY not found in .env file. AI generation will fail.")

# Phrase history file
PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"

# Recent categories file (for rotation across runs)
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"


# ============== PHRASE HISTORY MANAGEMENT ==============

def load_phrase_history():
    """Load all previously generated phrases"""
    if PHRASE_HISTORY_FILE.exists():
        try:
            with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[history] Error loading history: {e}")
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    """Save phrase history"""
    data["last_updated"] = datetime.now().isoformat()
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_used_phrases_set():
    """Get a set of all used English phrases for fast lookup"""
    history = load_phrase_history()
    return {p.get("english", "").lower().strip() for p in history.get("phrases", [])}


def is_phrase_used(english_phrase, used_set=None):
    """Check if phrase was already generated"""
    if used_set is None:
        used_set = get_used_phrases_set()
    return english_phrase.lower().strip() in used_set


def add_phrases_to_history(phrases, category):
    """Add new phrases to history"""
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            "georgian": phrase["georgian"],
            "category": category,
            "generated_at": datetime.now().isoformat()
        })
    save_phrase_history(history)
    print(f"[history] Added {len(phrases)} phrases to history (total: {len(history['phrases'])})")


# ============== CATEGORY ROTATION ==============

def load_recent_categories():
    """Load recently used categories to avoid repetition"""
    if RECENT_CATEGORIES_FILE.exists():
        try:
            with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[rotation] Error loading recent categories: {e}")
    return {"date": None, "last_3_days": []}


def save_recent_categories(data):
    """Save recent categories"""
    data["date"] = datetime.now().strftime("%Y-%m-%d")
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_rotation_category():
    """Pick a category not used in the last 3 days, or least recently used"""
    recent = load_recent_categories()
    used_today = recent.get("last_3_days", [])

    # Flatten all recently used categories
    recently_used = set()
    for day_entry in used_today:
        if isinstance(day_entry, dict):
            recently_used.update(day_entry.get("categories", []))
        elif isinstance(day_entry, list):
            recently_used.update(day_entry)

    # Filter available categories
    available = [c for c in CATEGORIES_ENGLISH if c not in recently_used]

    if not available:
        available = list(CATEGORIES_ENGLISH)

    chosen = random.choice(available)

    # Update recent categories
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_entry = None
    for i, entry in enumerate(used_today):
        if isinstance(entry, dict) and entry.get("date") == today_str:
            today_entry = i
            break

    if today_entry is not None:
        if chosen not in used_today[today_entry].get("categories", []):
            used_today[today_entry]["categories"].append(chosen)
    else:
        used_today.append({"date": today_str, "categories": [chosen]})
        # Keep only last 3 days
        if len(used_today) > 3:
            used_today = used_today[-3:]

    recent["last_3_days"] = used_today
    save_recent_categories(recent)

    print(f"[rotation] Chose category: {chosen} (avoiding: {recently_used - {chosen}})")
    return chosen


# ============== GEORGIAN CONTENT GENERATION ==============

def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    """Generate unique English-Georgian phrases via a single AI call."""

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            used_phrases = get_used_phrases_set()
            collected_unique_phrases = []

            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"

            # Try both auth methods: Bearer header and query param
            headers = {
                "Content-Type": "application/json"
            }
            params = {}
            if POLLINATIONS_API_KEY:
                if attempt % 2 == 0:
                    headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"
                else:
                    params["key"] = POLLINATIONS_API_KEY

            request_count = max(num_phrases * 4, 20)
            import random as _rnd
            _seed_words = ["ocean", "mountain", "forest", "desert", "river", "island", "volcano", "valley", "crystal", "thunder", "twilight", "horizon", "eternity", "whisper", "lantern", "compass", "feather", "pearl", "ruby", "sapphire", "bronze", "silver", "arrow", "shield", "crown", "mirror", "temple", "garden", "harbor", "castle", "market", "bridge", "tower", "fountain", "statue", "palace"]
            _seed = _rnd.choice(_seed_words)
            prompt = f"""Generate {request_count} CREATIVE {category_english} phrases for learning Georgian. Theme: {_seed}.
            Each phrase should connect to the theme "{_seed}" in some way (metaphorically, literally, or culturally).

CRITICAL: Each phrase MUST be unique. NEVER repeat the same idea. Be CREATIVE and VARIED.

Rules:
- Short: 3-10 words per language
- Natural commas for pauses
- Authentic Georgian (Mkhedruli script)
- AVOID: hello, how are you, good morning, good evening, goodbye, thank you, please, sorry, yes, no, my name is, nice to meet you (these are overused)

Vary the phrase TYPES: some questions, some statements, some exclamations, some commands.

Return JSON array:
[{{"english": "...", "georgian": "...", "pronunciation": "..."}}]

Return ONLY valid JSON."""

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a creative Georgian language teacher. Produce VARIED, UNIQUE phrases. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.2
            }

            auth_method = "Bearer header" if "Authorization" in headers else "query param"
            print(f"[content] Calling AI (model={AI_MODEL}, auth={auth_method}) for {request_count} candidates...")
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=60)
            if response.status_code == 401 and attempt < max_attempts - 1:
                print(f"[content] Auth failed with {auth_method}, trying alternate method...")
                raise Exception(f"AI API returned {response.status_code}: {response.text[:500]}")
            elif response.status_code != 200:
                raise Exception(f"AI API returned {response.status_code}: {response.text[:500]}")

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            print(f"[content] Response ({len(content)} chars): {content[:400]}...")

            json_content = content
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_content = content.split("```")[1].split("```")[0].strip()
            if not json_content.startswith("["):
                idx = json_content.find("[")
                if idx >= 0:
                    json_content = json_content[idx:]
            if not json_content.endswith("]"):
                idx = json_content.rfind("]")
                if idx >= 0:
                    json_content = json_content[:idx + 1]

            phrases = json.loads(json_content)

            for phrase in phrases:
                if not all(k in phrase for k in ["english", "georgian", "pronunciation"]):
                    continue
                if len(phrase["english"].split()) > 15:
                    continue
                phrase_en = phrase["english"].strip()
                if phrase_en.lower() not in used_phrases:
                    collected_unique_phrases.append(phrase)
                    used_phrases.add(phrase_en.lower())
                if len(collected_unique_phrases) >= num_phrases:
                    break

            print(f"[content] Got {len(collected_unique_phrases)}/{num_phrases} unique phrases from {len(phrases)} candidates")

            if len(collected_unique_phrases) < min(num_phrases, 3):
                raise Exception(
                    f"AI returned only {len(collected_unique_phrases)} valid unique phrases "
                    f"(needed at least {min(num_phrases, 3)}). Got {len(phrases)} JSON entries but most "
                    f"could not be parsed as valid JSON."
                )

            final_phrases = collected_unique_phrases[:num_phrases]
            if len(final_phrases) < num_phrases:
                print(f"[content] ⚠️  Only {len(final_phrases)} unique phrases available (requested {num_phrases}), proceeding with {len(final_phrases)}.")
            add_phrases_to_history(final_phrases, category_english)
            return final_phrases

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} failed: {e}")

    print(f"All attempts failed. Resetting phrase history...")
    Path("output/history/all_generated_phrases.json").write_text('{"phrases":[],"last_updated":null}')
    return generate_phrases(category_english, category_japanese)



# ============== AUDIO GENERATION ==============

async def generate_single_audio(text: str, voice: str, output_path: str):
    """Generate audio using Edge TTS"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


def generate_all_audio(phrases: list, output_dir: str):
    """Generate audio for all phrases with proper timing"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        georgian_file = output_dir / f"georgian_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    GE: {phrase['georgian']}")

        # Generate English audio
        en_success = asyncio.run(generate_single_audio(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    ✓ English: {english_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        # Generate Georgian audio (use Russian voice as fallback)
        ge_success = asyncio.run(generate_single_audio(phrase["georgian"], GEORGIAN_VOICE, str(georgian_file)))
        if ge_success:
            print(f"    ✓ Georgian: {georgian_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(georgian_file)]
            subprocess.run(cmd, capture_output=True)

        # Get ACTUAL durations
        en_duration = get_audio_duration(str(english_file))
        ge_duration = get_audio_duration(str(georgian_file))

        # Add pause between English and Georgian
        pause_between = 0.5
        total_duration = en_duration + pause_between + ge_duration

        print(f"    ⏱️  Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + GE: {ge_duration:.2f}s)")

        # Combine audio files
        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(georgian_file),
            "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{georgian_file.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    ✓ Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "georgian": str(georgian_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "ge_duration": ge_duration
        })

    print(f"\n[audio] ✓ Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    """Get audio duration in seconds"""
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    """Combine all audio files"""
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")

    concat_file = Path(output_file).parent / "narration_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if concat_file.exists():
        concat_file.unlink()

    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] ✓ Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True

    return False


# ============== IMAGE GENERATION ==============

def create_impressive_background(category_english: str):
    """Create stunning gradient background with geometric patterns and glow"""
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    # HIGH CONTRAST gradients for ALL 25 categories
    category_colors = {
        "Greetings": [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)],
        "Family": [(255, 0, 100), (139, 0, 0), (255, 105, 180), (255, 192, 203)],
        "Food": [(255, 215, 0), (0, 100, 0), (255, 140, 0), (34, 139, 34)],
        "Travel": [(0, 0, 139), (255, 215, 0), (70, 130, 180), (255, 255, 0)],
        "Numbers": [(255, 255, 0), (255, 0, 255), (255, 165, 0), (147, 112, 219)],
        "Time": [(0, 128, 0), (255, 215, 0), (0, 255, 0), (255, 140, 0)],
        "Colors": [(255, 127, 80), (75, 0, 130), (255, 160, 122), (138, 43, 226)],
        "Animals": [(255, 192, 203), (0, 100, 80), (255, 105, 180), (0, 200, 160)],
        "Weather": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Emotions": [(255, 0, 127), (0, 0, 139), (255, 20, 147), (75, 0, 130)],
        "Work": [(135, 206, 235), (0, 0, 100), (176, 224, 230), (75, 0, 130)],
        "Health": [(255, 69, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],
        "Shopping": [(139, 69, 19), (255, 215, 0), (160, 82, 45), (255, 140, 0)],
        "Directions": [(255, 0, 255), (75, 0, 130), (255, 20, 147), (0, 0, 139)],
        "Home": [(50, 205, 50), (255, 0, 127), (144, 238, 144), (255, 20, 147)],
        "Nature": [(178, 34, 34), (255, 215, 0), (220, 20, 60), (255, 140, 0)],
        "Sports": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],
        "Music": [(34, 139, 34), (255, 255, 0), (60, 179, 113), (255, 215, 0)],
        "Education": [(230, 230, 250), (75, 0, 130), (216, 191, 216), (138, 43, 226)],
        "Friendship": [(100, 100, 100), (255, 69, 0), (150, 150, 150), (255, 140, 0)],
        "Love": [(255, 255, 0), (255, 0, 127), (255, 215, 0), (147, 112, 219)],
        "Success": [(60, 179, 113), (138, 43, 226), (152, 251, 152), (75, 0, 130)],
        "Wisdom": [(0, 100, 0), (255, 215, 0), (34, 139, 34), (255, 140, 0)],
        "Happiness": [(75, 0, 130), (255, 215, 0), (138, 43, 226), (255, 140, 0)],
        "Gratitude": [(210, 180, 140), (75, 0, 130), (245, 245, 220), (138, 43, 226)],
    }

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    # Create smooth multi-stop gradient
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    # Add subtle geometric pattern for depth (circles)
    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    # Add radial glow effect from center
    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    # Composite glow over background
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)

    return img


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str):
    """Generate image with impressive background and Georgian font support"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    # Font paths - Georgian compatible
    # Priority: 1) Project fonts dir, 2) Windows fonts, 3) Linux fonts, 4) Default
    font_dirs = [
        Path(__file__).parent / "fonts",  # Project fonts
        Path("C:/Windows/Fonts"),  # Windows
        Path("/usr/share/fonts/truetype/noto"),  # Linux (Ubuntu/Debian)
        Path("/usr/share/fonts"),  # Linux generic
    ]
    
    font_files = {
        "bold": ["NotoSansGeorgian-Bold.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"],
        "regular": ["NotoSansGeorgian-Regular.ttf", "arial.ttf", "DejaVuSans.ttf"],
    }
    
    def find_font(weight):
        """Find font file in priority order"""
        for font_dir in font_dirs:
            for font_name in font_files.get(weight, []):
                font_path = font_dir / font_name
                if font_path.exists():
                    return str(font_path)
        return None
    
    # Load fonts with Georgian support
    font_category_size = 60
    font_large_size = 85
    font_pronunciation_size = 42
    font_branding_size = 52
    
    try:
        bold_font = find_font("bold")
        regular_font = find_font("regular")
        
        if bold_font and regular_font:
            font_category = ImageFont.truetype(bold_font, font_category_size)
            font_large = ImageFont.truetype(bold_font, font_large_size)
            font_pronunciation = ImageFont.truetype(regular_font, font_pronunciation_size)
            font_branding = ImageFont.truetype(bold_font, font_branding_size)
            print(f"  ✓ Using fonts: {bold_font}")
        else:
            raise FileNotFoundError("Georgian fonts not found")
    except Exception as e:
        print(f"  ⚠️  Font warning: {e}")
        print("  Using default fonts (Georgian may not render correctly)")
        font_category = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_pronunciation = ImageFont.load_default()
        font_branding = ImageFont.load_default()

    english = phrase_data.get("english", "")
    georgian = phrase_data.get("georgian", "")
    pronunciation = phrase_data.get("pronunciation", "")

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    # Category at top
    category_text = category_english.upper()
    category_bbox = draw.textbbox((VIDEO_WIDTH // 2, 140), category_text, font=font_category, anchor="mm")
    padding = 25
    draw.rectangle(
        [(category_bbox[0] - padding, category_bbox[1] - padding),
         (category_bbox[2] + padding, category_bbox[3] + padding)],
        fill=(0, 0, 0, 200)
    )
    draw.text(
        (VIDEO_WIDTH // 2, 140),
        category_text,
        fill=(255, 255, 255),
        font=font_category,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # English text
    english_y = 470
    english_lines = wrap_text(english, font_large, VIDEO_WIDTH - 140)
    total_height = len(english_lines) * 95

    draw.rectangle(
        [(60, english_y - 55), (VIDEO_WIDTH - 60, english_y + total_height + 15)],
        fill=(20, 30, 80, 220)
    )

    for i, line in enumerate(english_lines):
        y_pos = english_y + (i * 95)
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # Georgian text
    georgian_y = english_y + total_height + 110
    georgian_lines = wrap_text(georgian, font_large, VIDEO_WIDTH - 140)
    total_height = len(georgian_lines) * 95

    draw.rectangle(
        [(60, georgian_y - 55), (VIDEO_WIDTH - 60, georgian_y + total_height + 15)],
        fill=(80, 30, 30, 220)
    )

    for i, line in enumerate(georgian_lines):
        y_pos = georgian_y + (i * 95)
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 0),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # Pronunciation with FILLED BOX
    pronunciation_y = georgian_y + total_height + 90
    pronunciation_text = f"[{pronunciation}]"
    pron_lines = wrap_text(pronunciation_text, font_pronunciation, VIDEO_WIDTH - 160)

    if pron_lines:
        pron_total_height = len(pron_lines) * 42
        draw.rectangle(
            [(70, pronunciation_y - 20), (VIDEO_WIDTH - 70, pronunciation_y + pron_total_height + 10)],
            fill=(40, 40, 40, 230)
        )

        for i, pron_line in enumerate(pron_lines):
            y_pos = pronunciation_y + (i * 42)
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                pron_line,
                fill=(240, 240, 240),
                font=font_pronunciation,
                anchor="mm",
                stroke_width=1,
                stroke_fill=(20, 20, 20, 200)
            )

    # Branding
    branding_y = VIDEO_HEIGHT - 100
    draw.rectangle(
        [(0, branding_y - 30), (VIDEO_WIDTH, branding_y + 50)],
        fill=(0, 0, 0, 180)
    )
    draw.text(
        (VIDEO_WIDTH // 2, branding_y),
        "VELOCITY GEORGIAN",
        fill=(255, 255, 255),
        font=font_branding,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  ✓ Image: {Path(output_path).name}")
    return output_path


# ============== VIDEO CREATION ==============

def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    """Create video from images and audio with PERFECT synchronization"""

    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_info, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"[video] Clip {i+1}/{len(image_files)}: {duration:.2f}s")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        # Create video clip from image with exact duration
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_info['image']),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    # Create concat file
    concat_file = Path(output_file).parent / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve()}'\n")

    # Concatenate clips
    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(temp_video)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    # Add audio
    print("[video] Adding audio...")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    print(f"[video] ✓ Video created: {output_file}")

    # Cleanup
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()

    return output_file


# ============== MAIN WORKFLOW ==============

def create_georgian_reel(category: str = None, num_phrases: int = 5):
    """Create complete Georgian learning reel"""

    if category is None:
        category = get_rotation_category()

    print("\n" + "="*80)
    print("🇬🇪 VELOCITY GEORGIAN - LANGUAGE LEARNING REEL 🇬🇪")
    print("="*80)
    print(f"Category: {category}")
    print(f"Georgian: {CATEGORIES_GEORGIAN.get(category, 'N/A')}")
    print(f"Phrases: {num_phrases}")
    print("="*80)

    # Generate phrases
    print("\n[content] Generating Georgian phrases...")
    phrases = generate_phrases(category, num_phrases)

    for i, phrase in enumerate(phrases, 1):
        print(f"\n  {i}. {phrase['english']}")
        print(f"     Georgian: {phrase['georgian']}")
        print(f"     Pronunciation: {phrase['pronunciation']}")

    # Generate images
    print("\n[image] Generating images...")
    image_files = []
    for i, phrase in enumerate(phrases):
        image_path = IMAGES_DIR / f"image_{i:02d}.jpg"
        img_result = generate_complete_image(phrase, category, str(image_path))
        if img_result:
            image_files.append({"index": i, "image": img_result})

    # Generate audio
    print("\n[audio] Generating audio...")
    audio_files = generate_all_audio(phrases, str(AUDIO_DIR))

    # Create combined narration
    combined_audio = AUDIO_DIR / "combined_narration.mp3"
    create_final_narration(audio_files, str(combined_audio))

    # Create video
    print("\n[video] Creating final video...")
    output_video = VIDEO_DIR / f"georgian_{category.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" / "final_reel.mp4"
    output_video.parent.mkdir(parents=True, exist_ok=True)

    create_video_from_images_audio(image_files, audio_files, str(combined_audio), str(output_video))

    # Save metadata
    metadata = {
        "category_english": category,
        "category_georgian": CATEGORIES_GEORGIAN.get(category, ""),
        "phrases": phrases,
        "created_at": datetime.now().isoformat(),
        "video_path": str(output_video)
    }

    metadata_file = output_video.parent / "metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[complete] ✓ Reel created successfully!")
    print(f"[complete] Video: {output_video}")
    print(f"[complete] Metadata: {metadata_file}")
    print("="*80)

    return str(output_video)


if __name__ == "__main__":
    # Create a Georgian learning reel
    import argparse

    parser = argparse.ArgumentParser(description="Create Georgian language learning reels")
    parser.add_argument("--category", "-c", choices=CATEGORIES_ENGLISH, help="Learning category")
    parser.add_argument("--phrases", "-p", type=int, default=5, help="Number of phrases")

    args = parser.parse_args()

    create_georgian_reel(category=args.category, num_phrases=args.phrases)
