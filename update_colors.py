import os
import re
from pathlib import Path

# Color replacements
replacements = {
    '#0078d4': '#C9A961',  # primary blue -> matte gold
    '#106ebe': '#B8954D',  # dark blue -> dark gold
    '#005a9e': '#B8954D',  # darker blue -> dark gold
    '#0086f0': '#D4B76E',  # light blue -> light gold
    'background: white': 'background: #222222',  # white cards -> dark cards
    'background-color: white': 'background-color: #222222',
    '#faf9f8': '#0f0f0f',  # light bg -> black
    '#f3f2f1': '#1a1a1a',  # lighter bg -> dark black
    '#edebe9': '#3a3a3a',  # borders -> dark borders
    '#323130': '#e8e8e8',  # dark text -> light text
    '#605e5c': '#b8b8b8',  # secondary text -> light secondary
    '#8a8886': '#888888',  # tertiary -> gray
    '#a19f9d': '#888888',  # tertiary -> gray
    '#107c10': '#4CAF50',  # green -> new green
    '#a80000': '#f44336',  # red -> new red
    '#a4262c': '#f44336',  # red -> new red
    '#d83b01': '#C9A961',  # orange -> gold
}

print("🎨 Updating color scheme to Matte Gold & Black...")
print()

count = 0
templates_dir = Path('templates')

for html_file in templates_dir.rglob('*.html'):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_color, new_color in replacements.items():
            content = content.replace(old_color, new_color)
        
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            print(f"✓ Updated: {html_file.name}")
    
    except Exception as e:
        print(f"✗ Error updating {html_file.name}: {e}")

print()
print("✅ Color scheme update complete!")
print(f"📊 Files modified: {count}")
print()
print("🎨 Color Palette:")
print("   Primary: Matte Gold #C9A961")
print("   Background: Matte Black #0f0f0f")
print("   Cards: Dark #222222")
print("   Text: Light #e8e8e8")
print()
print("⚠️  Restart Flask server to see changes!")
