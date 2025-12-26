import base64
import re

# Read the new image
image_path = r'C:/Users/V/.gemini/antigravity/brain/790a633d-bcc1-40bb-9b52-29ad1090480a/uploaded_image_1764868533701.png'
with open(image_path, 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')

# Read web_app.py
file_path = 'web_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the input-wrapper block again.
# Since we modified it before, the regex/string match needs to match the CURRENT state.
# Current state has the smiley and the OLD base64 image.

# Instead of matching the exact base64 string (which is huge), let's match the structure using regex.
# We look for <div class="input-wrapper"> ... </div>
# And replace the inner content.

start_marker = '<div class="input-wrapper">'
end_marker = '<div class="input-icon" onclick="sendMessage()">➤</div>'

start_idx = content.find(start_marker)
if start_idx != -1:
    # Find the end of the div (closing div of input-wrapper)
    # It should be after the send button
    end_btn_idx = content.find(end_marker, start_idx)
    if end_btn_idx != -1:
        div_end_idx = content.find('</div>', end_btn_idx) + 6
        
        # New content
        # Removed smiley
        # Updated mic image
        new_html = f'''<div class="input-wrapper">
                    <input type="text" class="chat-input" id="chatInput"
                        placeholder="Ask anything. Type @ for mentions and / for shortcuts."
                        onkeypress="handleKeyPress(event)">
                    <div class="input-icon" onclick="toggleVoice()">
                        <img src="data:image/png;base64,{b64_string}" style="width: 24px; height: 24px; object-fit: contain;">
                    </div>
                    <div class="input-icon" onclick="sendMessage()">➤</div>
                </div>'''
        
        # We replace the chunk from start_idx to div_end_idx
        new_content = content[:start_idx] + new_html + content[div_end_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully updated icons (removed smiley, updated mic)!")
    else:
        print("❌ Could not find end marker")
else:
    print("❌ Could not find start marker")
