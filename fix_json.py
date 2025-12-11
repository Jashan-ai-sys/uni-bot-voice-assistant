import json
import re

# Read the file
with open('data/navigation/important_links.json', 'r', encoding='utf-8') as f:
    content = f.read()

print("Original file size:", len(content))

# Fix pattern: ": ," should be ": []," or ": {}"
# This handles cases where a value is missing after a colon
fixed = re.sub(r':\s*,', ': [],', content)

# Also fix pattern at end of objects: ": }" should be ": [] }"
fixed = re.sub(r':\s*\}', ': {} }', fixed)

print("After fix size:", len(fixed))

# Validate the fix
try:
    data = json.loads(fixed)
    print("SUCCESS: JSON is now valid!")
    
    # Write the fixed content back
    with open('data/navigation/important_links.json', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print("File has been fixed and saved!")
    
except json.JSONDecodeError as e:
    print(f"Still has errors: {e}")
    print(f"Error at line {e.lineno}, column {e.colno}")
    
    # Show context
    lines = fixed.split('\n')
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
        print(f"{i+1}: {lines[i]}")
