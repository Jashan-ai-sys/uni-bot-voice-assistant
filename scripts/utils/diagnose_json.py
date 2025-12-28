import json

with open('data/navigation/important_links.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to parse and catch the exact error
try:
    json.loads(content)
    print("JSON is valid!")
except json.JSONDecodeError as e:
    print(f"ERROR: {e.msg}")
    print(f"Position: {e.pos} (line {e.lineno}, column {e.colno})")
    
    # Show exact characters at error position
    start = max(0, e.pos - 200)
    end = min(len(content), e.pos + 200)
    
    context = content[start:end]
    
    # Find where error position is in context
    error_offset = e.pos - start
    
    print("\n" + "="*80)
    print("CONTEXT (200 chars before and after error):")
    print("="*80)
    
    # Split into lines for better visibility
    lines_before = context[:error_offset].split('\n')
    lines_after = context[error_offset:].split('\n')
    
    # Show last 3 lines before error
    for line in lines_before[-3:]:
        print(f"  {line}")
    
    print("  " + "-" * 70 + " ERROR HERE")
    
    # Show first 3 lines after error
    for line in lines_after[:3]:
        print(f"  {line}")
    
    print("="*80)
    
    # Show raw characters
    print("\nRAW CHARACTER SEQUENCE:")
    print(repr(content[e.pos-50:e.pos+50]))
    
    # Find the problematic pattern
    print("\n" + "="*80)
    print("DIAGNOSIS:")
    print("="*80)
    
    problem_area = content[e.pos-20:e.pos+20]
    if '": ,' in problem_area:
        print("Found pattern '\":  ,\" - colon followed by comma (missing value)")
    elif ': }' in problem_area:
        print("Found pattern ': }' - colon followed by closing brace (missing value)")
    elif ',]' in problem_area:
        print("Found trailing comma before array close")
    elif ',}' in problem_area:
        print("Found trailing comma before object close")
    else:
        print("Unclear pattern. Raw:")
        print(repr(problem_area))
