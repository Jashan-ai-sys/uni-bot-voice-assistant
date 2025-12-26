import base64
import re

# Read the image
image_path = r'C:/Users/V/.gemini/antigravity/brain/790a633d-bcc1-40bb-9b52-29ad1090480a/uploaded_image_1_1764867752679.png'
with open(image_path, 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')

# Read web_app.py
file_path = 'web_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old HTML block pattern (using regex to be safe with whitespace)
# We look for the input-wrapper and its children
pattern = r'<div class="input-wrapper">\s*<div class="input-icon">🔍</div>\s*<input type="text" class="chat-input" id="chatInput"[^>]*>\s*<div class="input-icon">📎</div>\s*<div class="input-icon">😊</div>\s*<div class="input-icon">🎤</div>\s*<div class="input-icon" onclick="sendMessage\(\)">➤</div>\s*</div>'

# Construct the new HTML block
# Removing search (🔍) and attach (📎)
# Replacing mic (🎤) with image
new_html = f'''<div class="input-wrapper">
                    <input type="text" class="chat-input" id="chatInput"
                        placeholder="Ask anything. Type @ for mentions and / for shortcuts."
                        onkeypress="handleKeyPress(event)">
                    <div class="input-icon">😊</div>
                    <div class="input-icon" onclick="toggleVoice()">
                        <img src="data:image/png;base64,{b64_string}" style="width: 20px; height: 20px; object-fit: contain;">
                    </div>
                    <div class="input-icon" onclick="sendMessage()">➤</div>
                </div>'''

# We need to be careful with regex matching multiline
# Let's try to find the exact string first without regex if possible, or use a simplified regex
# The previous view_file showed:
# <div class="input-wrapper">
#     <div class="input-icon">🔍</div>
#     <input type="text" class="chat-input" id="chatInput"
#         placeholder="Ask anything. Type @ for mentions and / for shortcuts."
#         onkeypress="handleKeyPress(event)">
#     <div class="input-icon">📎</div>
#     <div class="input-icon">😊</div>
#     <div class="input-icon">🎤</div>
#     <div class="input-icon" onclick="sendMessage()">➤</div>
# </div>

# Let's try to locate the start and end of the block in the file content
start_marker = '<div class="input-wrapper">'
end_marker = '<div class="input-icon" onclick="sendMessage()">➤</div>'

start_idx = content.find(start_marker)
if start_idx != -1:
    # Find the end of the div
    # We can look for the closing </div> after the send button
    end_btn_idx = content.find(end_marker, start_idx)
    if end_btn_idx != -1:
        div_end_idx = content.find('</div>', end_btn_idx) + 6
        
        old_block = content[start_idx:div_end_idx]
        print("Found block:")
        print(old_block)
        
        # Replace
        new_content = content.replace(old_block, new_html)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully updated icons!")
    else:
        print("❌ Could not find end marker")
else:
    print("❌ Could not find start marker")
