import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-2.5-flash")

files_to_fix = [
    r"data/navigation/navi.json",
    r"data/navigation/important_links.json"
]

print("🚀 Starting JSON repair...")

for file_path in files_to_fix:
    print(f"📄 Processing {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        prompt = f"""
        The following JSON file is corrupted/malformed. Fix the syntax errors and return ONLY the valid JSON. 
        Do not add Markdown formatting code blocks. Just raw JSON.
        Make sure to close all brackets and quotes correctly.
        
        File Content:
        {content}
        """
        
        response = model.generate_content(prompt)
        fixed_content = response.text.strip()
        
        # Remove markdown code blocks if present (despite prompt)
        if fixed_content.startswith("```json"):
            fixed_content = fixed_content[7:]
        if fixed_content.startswith("```"):
            fixed_content = fixed_content[3:]
        if fixed_content.endswith("```"):
            fixed_content = fixed_content[:-3]
            
        fixed_content = fixed_content.strip()
        
        # Validate
        json.loads(fixed_content)
        
        # Save
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
            
        print(f"✅ Fixed and saved {file_path}")
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

print("Done.")
