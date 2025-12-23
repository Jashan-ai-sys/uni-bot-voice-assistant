lines = open('data/navigation/important_links.json', 'r', encoding='utf-8').readlines()
with open('lines_648_655.txt', 'w', encoding='utf-8') as f:
    for i in range(645, min(656, len(lines))):
        f.write(f"{i+1}: {lines[i]}")
print("Lines written to lines_648_655.txt")
