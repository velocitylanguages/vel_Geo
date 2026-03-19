"""
Download Georgian fonts for the project
Handles both local development and GitHub Actions
"""
import os
import sys
import ssl
import urllib.request
from pathlib import Path

# Bypass SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

FONTS_DIR = Path(__file__).parent / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

def download_file(url, destination):
    """Download a file from URL"""
    try:
        print(f"Downloading: {url}")
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': '*/*'
            }
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(destination, 'wb') as out_file:
                out_file.write(response.read())
        
        # Verify TTF header
        with open(destination, 'rb') as f:
            header = f.read(4)
            if header not in [b'\x00\x01\x00\x00', b'ttcf', b'OTTO']:
                print(f"✗ Invalid font file")
                destination.unlink()
                return False
        
        size = destination.stat().st_size / 1024
        print(f"✓ Downloaded: {destination.name} ({size:.0f} KB)")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if destination.exists():
            destination.unlink()
        return False

def install_on_linux():
    """Install fonts on Linux (GitHub Actions)"""
    print("\n🐧 Linux detected - installing system fonts...")
    try:
        import subprocess
        # Install Noto fonts which include Georgian
        subprocess.run(['sudo', 'apt-get', 'update'], check=True, capture_output=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-noto-core'], 
                      check=True, capture_output=True)
        print("✓ System fonts installed")
        
        # Copy to project fonts dir
        system_font_dirs = [
            Path('/usr/share/fonts/truetype/noto'),
            Path('/usr/share/fonts/noto'),
        ]
        
        for font_dir in system_font_dirs:
            if font_dir.exists():
                for font in font_dir.glob('*Georgian*.ttf'):
                    dest = FONTS_DIR / font.name
                    if not dest.exists():
                        import shutil
                        shutil.copy2(font, dest)
                        print(f"✓ Copied: {font.name}")
                return True
    except Exception as e:
        print(f"⚠️  System install failed: {e}")
    return False

def main():
    print("🔤 Georgian Font Installer\n")
    
    georgian_regular = FONTS_DIR / "NotoSansGeorgian-Regular.ttf"
    georgian_bold = FONTS_DIR / "NotoSansGeorgian-Bold.ttf"
    
    # Check if already have fonts
    if georgian_regular.exists() and georgian_bold.exists():
        print("✅ Georgian fonts already installed!")
        return True
    
    # On Linux, try system install first
    if sys.platform.startswith('linux'):
        if install_on_linux():
            # Check if fonts were copied
            if georgian_regular.exists() or georgian_bold.exists():
                print("\n✅ Fonts installed successfully!")
                return True
    
    # Try direct download as fallback
    print("\n📥 Attempting direct download...\n")
    
    # Use reliable mirror
    sources = {
        'regular': "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansGeorgian/NotoSansGeorgian-Regular.ttf",
        'bold': "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansGeorgian/NotoSansGeorgian-Bold.ttf",
    }
    
    downloaded = 0
    for weight, url in sources.items():
        target = FONTS_DIR / f"NotoSansGeorgian-{weight.title()}.ttf"
        if download_file(url, target):
            downloaded += 1
    
    if downloaded >= 1:
        print(f"\n✅ Georgian fonts ready! ({downloaded}/2)")
        return True
    else:
        print("\n⚠️  Could not download fonts")
        if sys.platform.startswith('linux'):
            print("\nFor GitHub Actions, add to workflow:")
            print("  sudo apt-get install -y fonts-noto-core")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
