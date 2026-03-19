# Velocity Georgian - Georgian Language Learning Bot

🇬🇪 Automated Georgian language learning content generator for social media

## Overview

Velocity Georgian creates engaging short-form video content for teaching Georgian (Kartuli) language to English speakers. Each video features:

- **Bilingual phrases**: English + Georgian (with Mkhedruli script)
- **Phonetic pronunciation**: Easy-to-read pronunciation guides
- **Beautiful visuals**: Category-specific gradient backgrounds
- **Audio narration**: English + Georgian voice-over
- **Optimized for social media**: 9:16 vertical format for Reels/Shorts/TikTok

## Features

- **25 Learning Categories**: Greetings, Family, Food, Travel, Numbers, Time, Colors, Animals, Weather, Emotions, Work, Health, Shopping, Directions, Home, Nature, Sports, Music, Education, Friendship, Love, Success, Wisdom, Happiness, Gratitude
- **Phrase History**: Never repeats phrases across runs
- **Georgian Font Support**: Noto Sans Georgian for proper script rendering
- **Multi-platform Upload**: Facebook, Instagram, YouTube, TikTok, Twitter/X, VK, Telegram
- **GitHub Actions Ready**: Automated daily posting (4x per day)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Georgian Fonts

```bash
python download_fonts.py
```

### 3. Set Up Environment

Create a `.env` file with your API keys:

```env
POLLINATIONS_API_KEY=your_key_here

# YouTube
YT_CLIENT_ID=your_client_id
YT_CLIENT_SECRET=your_secret
YT_REFRESH_TOKEN=your_token

# Instagram
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id

# Facebook
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id

# Other platforms...
```

### 4. Generate a Video

```bash
# Random category
python georgian_reels_automation.py

# Specific category
python georgian_reels_automation.py --category Love --phrases 5

# Available categories: Greetings, Family, Food, Travel, Numbers, Time, Colors, Animals, Weather, Emotions, Work, Health, Shopping, Directions, Home, Nature, Sports, Music, Education, Friendship, Love, Success, Wisdom, Happiness, Gratitude
```

### 5. Upload to Social Media

```bash
python upload_all_platforms.py
```

## Project Structure

```
Velocity Georgian/
├── georgian_reels_automation.py    # Main content generator
├── upload_all_platforms.py          # Multi-platform uploader
├── download_fonts.py                # Georgian font installer
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (create this)
├── fonts/                          # Georgian fonts (auto-downloaded)
│   ├── NotoSansGeorgian-Regular.ttf
│   └── NotoSansGeorgian-Bold.ttf
├── output/                         # Generated content
│   ├── images/                     # Generated images
│   ├── audio/                      # Generated audio
│   ├── video/                      # Final videos
│   └── history/                    # Phrase history (prevents repeats)
└── .github/workflows/
    └── daily_georgian_upload.yml   # GitHub Actions workflow
```

## GitHub Actions Setup

The project includes a pre-configured workflow for automated posting:

1. **Add Secrets** to your GitHub repository:
   - `POLLINATIONS_API_KEY`
   - `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
   - `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`
   - `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`
   - etc.

2. **Enable Workflows**: The workflow runs 4x daily (9AM, 12PM, 3PM, 7PM EST)

3. **Phrase Persistence**: History is committed to the repo to prevent repeats

## Georgian Language Support

### Fonts
- **Noto Sans Georgian**: Open-source font supporting Mkhedruli script
- Auto-downloaded on first run or GitHub Actions
- Also installed via `fonts-noto-core` on Linux

### Text-to-Speech
- English: `en-US-GuyNeural` (Edge TTS)
- Georgian: Uses closest available voice (Georgian TTS is limited)

### Categories (English → Georgian)
| English | Georgian |
|---------|----------|
| Greetings | მისალმება |
| Family | ოჯახი |
| Food | საკვები |
| Travel | მოგზაურობა |
| Numbers | რიცხვები |
| Time | დრო |
| Colors | ფერები |
| Animals | ცხოველები |
| Weather | ამინდი |
| Emotions | ემოციები |
| Work | სამუშაო |
| Health | ჯანმრთელობა |
| Shopping | შოპინგი |
| Directions | მიმართულებები |
| Home | სახლი |
| Nature | ბუნება |
| Sports | სპორტი |
| Music | მუსიკა |
| Education | განათლება |
| Friendship | მეგობრობა |
| Love | სიყვარული |
| Success | წარმატება |
| Wisdom | სიბრძნე |
| Happiness | ბედნიერება |
| Gratitude | მადლიერება |

## Sample Output

Each video contains:
1. Category title (English + Georgian)
2. 3-5 phrases with:
   - English text
   - Georgian text (Mkhedruli script)
   - Phonetic pronunciation
3. "VELOCITY GEORGIAN" branding

## Troubleshooting

### Georgian Text Not Showing
1. Run: `python download_fonts.py`
2. Check `fonts/` directory for `.ttf` files
3. On Linux: `sudo apt-get install fonts-noto-core`

### Audio Generation Fails
- Edge TTS may have rate limits
- Check internet connection
- Verify API keys

### Upload Fails
- Verify platform credentials in `.env`
- Check platform API limits
- Review error logs in `output/`

## License

This project uses:
- **Noto Sans Georgian**: SIL Open Font License
- **Generated content**: Your ownership (API terms apply)

## Contributing

Contributions welcome! Areas for improvement:
- Better Georgian TTS voices
- More learning categories
- Improved pronunciation guides
- Additional platform support

---

**Made with ❤️ for Georgian language learners worldwide**

🇬🇪 **შეისწავლე ქართული!** (Learn Georgian!)
