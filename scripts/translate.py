# scripts/translate.py
import os
import json
import yaml
import requests
from pathlib import Path

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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
                "content": "Du bist ein professioneller Übersetzer. Übersetze nur den Text von Deutsch zu Englisch. Antworte nur mit der Übersetzung, keine Erklärungen."
            },
            {
                "role": "user",
                "content": f"Übersetze ins Englische:\n\n{text}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            translated = result["choices"][0]["message"]["content"].strip()
            return translated
        else:
            print(f"❌ Unerwartete API-Antwort: {result}")
            return text
    except requests.exceptions.RequestException as e:
        print(f"❌ API-Fehler: {e}")
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
        if "title" in frontmatter:
            frontmatter["title_en"] = get_translated_text(frontmatter["title"])

        # Translate description
        if "description" in frontmatter:
            frontmatter["description_en"] = get_translated_text(frontmatter["description"])

        # Translate content
        translated_content = get_translated_text(markdown_content)

        # Create English frontmatter
        en_frontmatter = frontmatter.copy()
        en_frontmatter["lang"] = "en"
        en_frontmatter["title"] = en_frontmatter.pop("title_en", frontmatter.get("title", ""))
        en_frontmatter["description"] = en_frontmatter.pop("description_en", frontmatter.get("description", ""))

        # Generate English filename
        en_filename = target_dir / source_file.name
        
        # Create English markdown file
        en_yaml = yaml.dump(en_frontmatter, default_flow_style=False, allow_unicode=True)
        en_markdown = f"---\n{en_yaml}---\n\n{translated_content}"

        with open(en_filename, "w", encoding="utf-8") as f:
            f.write(en_markdown)

        print(f"✅ Übersetzt → {en_filename.relative_to(REPO_ROOT)}")
        return True

    except Exception as e:
        print(f"❌ Fehler bei {source_file.name}: {e}")
        return False

def main():
    translated_count = 0

    # Process Blog Posts
    print("\n📝 Verarbeite Blog-Posts...")
    de_posts = sorted([f for f in POSTS_DIR.glob("*.md") if f.name != ".gitkeep"])
    
    for post_file in de_posts:
        # Check if EN version exists
        en_file = POSTS_EN_DIR / post_file.name
        if en_file.exists():
            print(f"⏭️  Übersprungen (bereits übersetzt): {post_file.name}")
            continue
            
        if process_file(post_file, POSTS_EN_DIR):
            translated_count += 1

    # Process Stories
    print("\n📖 Verarbeite Kindergeschichten...")
    de_stories = sorted([f for f in STORIES_DIR.glob("*.md") if f.name != ".gitkeep"])
    
    for story_file in de_stories:
        # Check if EN version exists
        en_file = STORIES_EN_DIR / story_file.name
        if en_file.exists():
            print(f"⏭️  Übersprungen (bereits übersetzt): {story_file.name}")
            continue
            
        if process_file(story_file, STORIES_EN_DIR):
            translated_count += 1

    print(f"\n🎉 {translated_count} neue Dateien übersetzt")

if __name__ == "__main__":
    main()