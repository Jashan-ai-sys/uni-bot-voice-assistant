import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_map_info(image_path, output_path="data/map_info.txt"):
    """
    Analyzes a map image using Gemini Vision and saves the description to a text file.
    """
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at {image_path}")
        return False

    print(f"🗺️ Analyzing map: {image_path}...")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        image = Image.open(image_path)
        
        prompt = """
        Analyze this map image in great detail. I need to use this information to answer user questions about locations.
        
        Please provide:
        1. A list of all buildings, blocks, and landmarks visible on the map.
        2. Their relative positions (e.g., "Block A is north of the Library", "The cafeteria is next to the sports complex").
        3. Any specific paths, roads, or gates mentioned.
        4. Key facilities available in each block if identifiable (e.g., "Block 34 contains the School of Computer Science").
        
        Format the output clearly so it can be used as a knowledge base.
        """
        
        response = model.generate_content([prompt, image])
        description = response.text
        
        print("✅ Analysis complete. Saving to file...")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Map Description for {os.path.basename(image_path)}:\n\n")
            f.write(description)
            
        print(f"💾 Map info saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing map: {e}")
        return False

if __name__ == "__main__":
    # Default path, can be changed
    MAP_IMAGE_PATH = "map_lpu.jpg"
    
    if os.path.exists(MAP_IMAGE_PATH):
        extract_map_info(MAP_IMAGE_PATH)
    else:
        print(f"⚠️ {MAP_IMAGE_PATH} not found. Please place the map image in the root directory or update the path.")
