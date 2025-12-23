import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

file_path = r"c:\Users\WIN11\lpu bot RAG\uni-bot\data\hostel\emeergency_numbers.pdf"
output_path = r"c:\Users\WIN11\lpu bot RAG\uni-bot\data\hostel\emeergency_numbers_extracted.txt"

def extract_text_with_gemini():
    print(f"📤 Uploading {file_path} to Gemini...")
    
    # Upload file
    sample_file = genai.upload_file(path=file_path, display_name="Emergency Numbers")
    print(f"✅ Uploaded file: {sample_file.name}")
    
    # Wait for processing
    while sample_file.state.name == "PROCESSING":
        print("⏳ Waiting for file processing...")
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)
        
    if sample_file.state.name == "FAILED":
        print("❌ File processing failed")
        return

    print("🧠 Extracting text...")
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    response = model.generate_content([
        "Extract all text from this document exactly as it appears. Preserve phone numbers and names.",
        sample_file
    ])
    
    text = response.text
    print(f"✅ Extracted {len(text)} characters")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    print(f"💾 Saved extracted text to {output_path}")

if __name__ == "__main__":
    extract_text_with_gemini()
