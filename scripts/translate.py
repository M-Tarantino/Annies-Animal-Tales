# scripts/translate.py (KORRIGIERT)
import os
import yaml
import requests
from pathlib import Path
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

REPO_ROOT = Path(__file__).parent.parent

# DE Quellen
POSTS_DIR = REPO_ROOT / "docs" / "_posts"
STORIES_DIR = REPO_ROOT / "docs" / "_kindergeschichten"

# EN Ziele (in en/ Ordner)
POSTS_EN_DIR = REPO_ROOT / "docs" / "en" / "_posts"
STORIES_EN_DIR = REPO_ROOT / "docs" / "en" / "_kindergeschichten"

POSTS_EN_DIR.mkdir(parents=True, exist_ok=True)
STORIES_EN_DIR.mkdir(parents=True, exist_ok=True)

def get_translated_text(text: str) -> str:
    """Translate German text to English using Groq API"""
    if not GROQ_API_KEY:
        return text

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein professioneller Übersetzer. Übersetze nur den Text von Deutsch zu Englisch. Antworte nur mit der Übersetzung, keine Erklärungen."
            },
            {"role": "user", "content": f"Übersetze ins Englische:\n\n{text}"}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            translated = result["choices"][0]["message"]["content"].strip()
            time.sleep(0.5)
            return translated
        return text
    except Exception as e:
        print(f"  ⚠️  Übersetzung fehlgeschlagen: {e}")
        return text

def extract_slug_from_filename(filename: str) -> str:
    """2026-09-08-willkommen.md → willkommen"""
    parts = filename.replace(".md", "").split("-", 3)
    return parts[3] if len(parts) > 3 else filename.replace(".md", "")

def extract_date_from_filename(filename: str) -> str:
    """2026-09-08-willkommen.md → 2026-09-08"""
    parts = filename.replace(".md", "").split("-", 3)
    return "-".join(parts[:3]) if len(parts) >= 3 else ""

def process_file(source_file: Path, target_dir: Path, content_type: str = "blog") -> bool:
    """
    Übersetzt eine DE-Datei und speichert sie in en/ Ordner
    content_type: "blog" oder "story"
    """
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"  ❌ Ungültiges Format")
            return False

        frontmatter = yaml.safe_load(parts[1].strip()) or {}
        markdown_content = parts[2].strip()

        if frontmatter.get("lang") == "en":
            return False

        frontmatter["lang"] = "de"
        print(f"  → Übersetze: {source_file.name}")

        # Translate
        title_en = get_translated_text(frontmatter.get("title", ""))
        desc_en = get_translated_text(frontmatter.get("description", ""))
        content_en = get_translated_text(markdown_content)

        # Create EN frontmatter
        en_frontmatter = frontmatter.copy()
        en_frontmatter["lang"] = "en"
        en_frontmatter["title"] = title_en
        en_frontmatter["description"] = desc_en

        # Set permalink (mit baseurl)
        slug = extract_slug_from_filename(source_file.name)
        date = extract_date_from_filename(source_file.name)
        
        if content_type == "story":
            en_frontmatter["permalink"] = f"/en/kindergeschichten/{date}/{slug}/"
        else:
            en_frontmatter["permalink"] = f"/en/archive/{date}/{slug}/"

        # Write EN file IN en/ ORDNER
        en_filename = target_dir / source_file.name
        en_yaml = yaml.dump(en_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
        en_markdown = f"---\n{en_yaml}---\n\n{content_en}"

        with open(en_filename, "w", encoding="utf-8") as f:
            f.write(en_markdown)

        print(f"  ✅ {en_filename.relative_to(REPO_ROOT)}")
        return True

    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False

def main():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY nicht gesetzt\n")
        return

    count = 0

    # Blog Posts
    print("📝 Blog-Posts...")
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        if post_file.name.startswith(".") or post_file.name == ".gitkeep":
            continue
        
        en_file = POSTS_EN_DIR / post_file.name
        if en_file.exists():
            print(f"  ⏭️  {post_file.name} (bereits übersetzt)")
            continue
        
        if process_file(post_file, POSTS_EN_DIR, "blog"):
            count += 1

    # Stories
    print("\n📖 Kindergeschichten...")
    for story_file in sorted(STORIES_DIR.glob("*.md")):
        if story_file.name.startswith(".") or story_file.name == ".gitkeep":
            continue
        
        en_file = STORIES_EN_DIR / story_file.name
        if en_file.exists():
            print(f"  ⏭️  {story_file.name} (bereits übersetzt)")
            continue
        
        if process_file(story_file, STORIES_EN_DIR, "story"):
            count += 1

    print(f"\n🎉 {count} neue Dateien übersetzt\n")

if __name__ == "__main__":
    main()