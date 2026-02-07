import os
from pathlib import Path

# NEW VIBRANT COLOR REPLACEMENTS - Realistic Gold, Charcoal, White & Steel
replacements = {
    # OLD MUTED GOLD -> NEW VIBRANT GOLD
    '#C9A961': '#DAA520',  # Goldenrod - vibrant, realistic gold
    '#B8954D': '#B8860B',  # Dark goldenrod
    '#D4B76E': '#FFD700',  # Bright gold
    
    # OLD DARK BACKGROUNDS -> NEW CHARCOAL
    '#0f0f0f': '#1C1C1C',  # Softer charcoal background
    '#1a1a1a': '#2C2C2C',  # Medium charcoal
    '#222222': '#353535',  # Card background - lighter for visibility
    
    # OLD BORDERS -> NEW STEEL GRAY
    '#3a3a3a': '#4A4A4A',  # Steel gray borders
    '#2d2d2d': '#3A3A3A',  # Darker steel
    
    # OLD MUTED TEXT -> NEW WHITE/SILVER
    '#e8e8e8': '#FFFFFF',  # Pure white text
    '#b8b8b8': '#C0C0C0',  # Silver text
    '#888888': '#808080',  # Steel gray muted text
}

print("🎨 Upgrading to VIBRANT Gold, Charcoal & Steel...")
print()
print("NEW PALETTE:")
print("  Gold: Goldenrod #DAA520 (vibrant & realistic)")
print("  Background: Charcoal #1C1C1C (softer black)")
print("  Text: Pure White #FFFFFF")
print("  Accents: Steel Gray #C0C0C0")
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
print("✅ VIBRANT color upgrade complete!")
print(f"📊 Files modified: {count}")
print()
print("🎨 NEW COLOR PALETTE:")
print("   Gold: #DAA520 (Goldenrod - vibrant & luxurious)")
print("   Light Gold: #FFD700 (Bright gold highlights)")
print("   Dark Gold: #B8860B (Rich dark gold)")
print()
print("   Charcoal: #1C1C1C (Softer than pure black)")
print("   Medium Charcoal: #2C2C2C")
print("   Card Background: #353535 (Better visibility)")
print()
print("   Text: #FFFFFF (Pure white - maximum contrast)")
print("   Secondary Text: #C0C0C0 (Silver)")
print("   Muted Text: #808080 (Steel gray)")
print()
print("   Borders: #4A4A4A (Steel gray - clearly visible)")
print()
print("⚠️  Restart Flask & refresh browser (Ctrl+Shift+R)!")
