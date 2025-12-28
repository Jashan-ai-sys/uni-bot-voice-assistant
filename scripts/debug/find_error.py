with open('data/navigation/important_links.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Find line number and context
error_pos = 34159
lines = content.split('\n')

# Calculate which line contains the error
char_count = 0
error_line = 0
for i, line in enumerate(lines):
    if char_count + len(line) + 1 >= error_pos:  # +1 for newline
        error_line = i + 1
        break
    char_count += len(line) + 1

print(f"Error at line {error_line}")
print(f"\nContext around error position (lines {max(1, error_line-5)} to {error_line+5}):\n")

for i in range(max(0, error_line-6), min(len(lines), error_line+5)):
    marker = ">>> " if i == error_line-1 else "    "
    print(f"{marker}{i+1}: {lines[i]}")

# Also show exact character range
print(f"\n\nExact characters at error position:")
print(repr(content[error_pos-50:error_pos+50]))
