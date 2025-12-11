import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read the file
with open('data/navigation/important_links.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original file size: {len(content)} characters")

# Apply multiple fixes
fixes_applied = []

# Fix 1: ": ," → ": [],"
if ': ,' in content:
    content = content.replace(': ,', ': [],')
    fixes_applied.append("Replaced ': ,' with ': [],'")

# Fix 2: ": }" → ": []}"
if ': }' in content:
    content = content.replace(': }', ': []}')
    fixes_applied.append("Replaced ': }' with ': []}'")

# Fix 3: trailing comma before }
import re
content = re.sub(r',(\s*\})', r'\1', content)
fixes_applied.append("Removed trailing commas before }")

# Fix 4: trailing comma before ]
content = re.sub(r',(\s*\])', r'\1', content)
fixes_applied.append("Removed trailing commas before ]")

print(f"\nFixes applied: {len(fixes_applied)}")
for fix in fixes_applied:
    print(f"  - {fix}")

# Validate
try:
    data = json.loads(content)
    print("\n✓ SUCCESS: JSON is now valid!")
    
    # Write back
    with open('data/navigation/important_links.json', 'w', encoding='utf-8') as f:
        # Pretty print for better readability
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✓ File has been fixed and reformatted!")
    
except json.JSONDecodeError as e:
    print(f"\n✗ ERROR: {e.msg}")
    print(f"  Line: {e.lineno}, Column: {e.colno}, Position: {e.pos}")
    
    # Show context with line numbers
    lines = content.split('\n')
    start = max(0, e.lineno - 4)
    end = min(len(lines), e.lineno + 3)
    
    print(f"\nContext (lines {start+1}-{end}):")
    for i in range(start, end):
        marker = ">>> " if i == e.lineno - 1 else "    "
        line_content = lines[i][:200]  # Truncate very long lines
        print(f"{marker}{i+1:4d}: {line_content}")
    
    # Show character context
    if e.pos:
        char_start = max(0, e.pos - 100)
        char_end = min(len(content), e.pos + 100)
        print(f"\nCharacter context around position {e.pos}:")
        print(repr(content[char_start:char_end]))
