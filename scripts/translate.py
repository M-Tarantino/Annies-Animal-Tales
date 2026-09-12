# scripts/translate.py (KORRIGIERT)
import os
import json
import yaml
import requests
from pathlib import Path
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Korrekte Groq API URL
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

REPO_ROOT = Path(__file__).parent.parent
POSTS_DIR = REPO_ROOT / "docs" / "_posts"
POSTS_EN_DIR = REPO_ROOT / "docs" / "_posts" / "en"
STORIES_DIR = REPO_ROOT / "docs" / "_kindergeschichten"
STORIES_EN_DIR = REPO_ROOT / "docs" / "_kindergeschichten" / "en"

# Create directories if they don't exist
POSTS_EN_DIR.mkdir(parents=True, exist_ok=True)
STORIES_EN_DIR.mkdir(parents=True, exist_ok=True)

def get_translated_text(text: str) -> str:
    """Translate German text to English using Groq API"""
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY nicht gesetzt")
        return text

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein professioneller Übersetzer. Übersetze nur den Text von Deutsch zu Englisch. Antworte nur mit der Übersetzung, keine Erklärungen oder Markdown."
            },
            {
                "role": "user",
                "content": f"Übersetze ins Englische:\n\n{text}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "top_p": 1
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"  → API-Aufruf für {len(text)} Zeichen...")
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 401:
            print(f"❌ Authentifizierungsfehler: API-Key ungültig")
            return text
        elif response.status_code == 404:
            print(f"❌ API-Endpoint nicht gefunden. Verwende Originaltext.")
            return text
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            translated = result["choices"][0]["message"]["content"].strip()
            print(f"  ✓ Übersetzt")
            time.sleep(1)  # Rate limiting
            return translated
        else:
            print(f"❌ Unerwartete API-Antwort: {result}")
            return text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Netzwerkfehler: {e}")
        return text

def process_file(source_file: Path, target_dir: Path) -> bool:
    """Process a single markdown file"""
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split frontmatter and content
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"⚠️ Ungültiges Format: {source_file.name}")
            return False

        frontmatter_str = parts[1].strip()
        markdown_content = parts[2].strip()

        # Parse frontmatter
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            print(f"❌ YAML-Fehler in {source_file.name}: {e}")
            return False

        if not frontmatter:
            frontmatter = {}

        # Check if already translated
        if frontmatter.get("lang") == "en":
            print(f"⏭️  Übersprungen (bereits EN): {source_file.name}")
            return False

        # Mark as German
        frontmatter["lang"] = "de"

        print(f"📝 Übersetze: {source_file.name}")

        # Translate title
        title_en = frontmatter.get("title", "")
        if title_en:
            title_en = get_translated_text(title_en)

        # Translate description
        desc_en = frontmatter.get("description", "")
        if desc_en:
            desc_en = get_translated_text(desc_en)

        # Translate content
        content_en = get_translated_text(markdown_content) if markdown_content else markdown_content

        # Create English frontmatter
        en_frontmatter = frontmatter.copy()
        en_frontmatter["lang"] = "en"
        en_frontmatter["title"] = title_en
        en_frontmatter["description"] = desc_en

        # Generate English filename
        en_filename = target_dir / source_file.name
        
        # Create English markdown file
        en_yaml = yaml.dump(en_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
        en_markdown = f"---\n{en_yaml}---\n\n{content_en}"

        with open(en_filename, "w", encoding="utf-8") as f:
            f.write(en_markdown)

        print(f"✅ Übersetzt → {en_filename.relative_to(REPO_ROOT)}")
        return True

    except Exception as e:
        print(f"❌ Fehler bei {source_file.name}: {e}")
        return False

def main():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY nicht gesetzt - Überspringe Übersetzung")
        return

    translated_count = 0

    # Process Blog Posts
    print("\n📝 Verarbeite Blog-Posts...")
    de_posts = sorted([f for f in POSTS_DIR.glob("*.md") if f.name != ".gitkeep" and not f.name.startswith(".")])
    
    if not de_posts:
        print("ℹ️ Keine Blog-Posts gefunden")
    else:
        for post_file in de_posts:
            en_file = POSTS_EN_DIR / post_file.name
            if en_file.exists():
                print(f"⏭️  Übersprungen (bereits übersetzt): {post_file.name}")
                continue
                
            if process_file(post_file, POSTS_EN_DIR):
                translated_count += 1

    # Process Stories
    print("\n📖 Verarbeite Kindergeschichten...")
    de_stories = sorted([f for f in STORIES_DIR.glob("*.md") if f.name != ".gitkeep" and not f.name.startswith(".")])
    
    if not de_stories:
        print("ℹ️ Keine Kindergeschichten gefunden")
    else:
        for story_file in de_stories:
            en_file = STORIES_EN_DIR / story_file.name
            if en_file.exists():
                print(f"⏭️  Übersprungen (bereits übersetzt): {story_file.name}")
                continue
                
            if process_file(story_file, STORIES_EN_DIR):
                translated_count += 1

    print(f"\n🎉 {translated_count} neue Dateien übersetzt")

if __name__ == "__main__":
    main()