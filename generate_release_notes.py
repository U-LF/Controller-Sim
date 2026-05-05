import subprocess
import datetime
import re

def get_last_tag():
    try:
        # We look for the latest tag reachable from the parent of the current commit.
        # This ensures that if we are currently at a tag (e.g. v1.1.0), 
        # we find the one BEFORE it (e.g. v1.0.0).
        return subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0', 'HEAD^'], stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_commits(since_tag):
    # Format: [Date] [Time] [Message]
    git_cmd = ['git', 'log', f'{since_tag}..HEAD', '--pretty=format:%ad|%s', '--date=format:%Y-%m-%d %H:%M']
    if not since_tag:
        git_cmd = ['git', 'log', '--pretty=format:%ad|%s', '--date=format:%Y-%m-%d %H:%M']
    
    output = subprocess.check_output(git_cmd).decode().strip()
    if not output:
        return []
    return [line.split('|') for line in output.split('\n')]

def generate_notes():
    last_tag = get_last_tag()
    commits = get_commits(last_tag)
    
    if not commits:
        return "No changes since last release."

    categories = {
        "🚀 Features": [],
        "🐞 Bug Fixes": [],
        "🛠️ Refactors": [],
        "📝 Documentation": [],
        "📦 Other": []
    }

    # Conventional Commit mapping
    mappings = {
        'feat': "🚀 Features",
        'fix': "🐞 Bug Fixes",
        'refactor': "🛠️ Refactors",
        'docs': "📝 Documentation"
    }

    for timestamp, message in commits:
        # Skip merge commits
        if message.startswith("Merge "):
            continue
            
        # Try to categorize
        match = re.match(r'^(\w+)(\(.*\))?!?: (.*)$', message)
        if match:
            prefix = match.group(1).lower()
            clean_msg = match.group(3)
            category = mappings.get(prefix, "📦 Other")
            categories[category].append(f"_{timestamp}_ - {clean_msg}")
        else:
            categories["📦 Other"].append(f"_{timestamp}_ - {message}")

    # Build Markdown
    release_body = f"## 📦 Release Notes ({datetime.datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    for cat, items in categories.items():
        if items:
            release_body += f"### {cat}\n"
            for item in items:
                release_body += f"- {item}\n"
            release_body += "\n"

    return release_body

if __name__ == "__main__":
    notes = generate_notes()
    with open("RELEASE_NOTES.md", "w", encoding="utf-8") as f:
        f.write(notes)
    print("Release notes generated in RELEASE_NOTES.md")
