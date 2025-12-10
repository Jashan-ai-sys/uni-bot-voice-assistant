import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, List, Any
import time
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_timetable_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract timetable data from PDF using Gemini Vision API with two-step approach
    """
    print(f"📤 Uploading timetable PDF: {pdf_path}")
    
    # Upload PDF to Gemini
    uploaded_file = genai.upload_file(path=pdf_path, display_name="Timetable")
    print(f"✅ Uploaded: {uploaded_file.name}")
    
    # Wait for processing
    while uploaded_file.state.name == "PROCESSING":
        print("⏳ Processing...")
        time.sleep(2)
        uploaded_file = genai.get_file(uploaded_file.name)
    
    if uploaded_file.state.name == "FAILED":
        raise Exception("PDF processing failed")
    
    # Step 1: Extract the table as structured text (simplified prompt)
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    # Use a simpler, clearer prompt focusing on table structure
    prompt = """
    Extract the class schedule from this timetable image into a simple table format.
    
    For EACH cell in the timetable that contains a class (not empty or "Project Work"):
    - List the DAY (from column header)
    - List the TIME (from the leftmost "Timing" column)
    - Extract the TYPE (Lecture/Tutorial/Practical)
    - Extract COURSE CODE after "C:" (e.g., C:PEAS05 -> PEAS05)
    - Extract ROOM after "R:" (e.g., R: 34-103 -> 34-103)
    - Extract SECTION after "S:" (e.g., S:9R915 -> 9R915)
    
    Format each class as ONE LINE:
    DAY | TIME | TYPE | COURSE | ROOM | SECTION
    
    Example:
    Thursday | 10-11 AM | Lecture | PEAS05 | 34-103 | 9R915
    Thursday | 11-12 AM | Lecture | PEAS05 | 34-103 | 9R915
    
    List ALL classes from the entire timetable, one per line.
    Skip empty cells and "Project Work" cells.
    """
    
    try:
        response = model.generate_content([prompt, uploaded_file])
        raw_text = response.text.strip()
        print(f"📝 Extracted table text")
        
        # Step 2: Parse the structured text into JSON
        schedule = []
        lines = raw_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '|' not in line or line.startswith('DAY'):
                continue
                
            try:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    schedule.append({
                        "day": parts[0],
                        "time": parts[1],
                        "type": parts[2],
                        "course_code": parts[3],
                        "room": parts[4],
                        "section": parts[5]
                    })
            except Exception as e:
                print(f"⚠️ Skipping malformed line: {line}")
                continue
        
        if not schedule:
            print("⚠️ No classes parsed, falling back to JSON extraction")
            # Fallback: try direct JSON extraction
            json_prompt = """
            Extract all classes as JSON array. For each class provide:
            {"day": "Day", "time": "Time", "type": "Type", "course_code": "Code", "room": "Room", "section": "Section"}
            Return ONLY valid JSON array, no markdown.
            """
            response = model.generate_content([json_prompt, uploaded_file])
            import json
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1].replace("json", "").strip()
            schedule = json.loads(response_text)
        
        print(f"✅ Extracted {len(schedule)} classes")
        return {"schedule": schedule}
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return {"schedule": [], "error": str(e)}

def search_timetable(timetable_data: Dict[str, Any], query: str) -> str:
    """
    Search timetable using LLM for intelligent query understanding
    """
    if not timetable_data or "schedule" not in timetable_data:
        return "No timetable data available."
    
    schedule = timetable_data["schedule"]
    
    if not schedule:
        return "Your timetable appears to be empty."
    
    # Convert schedule to readable text context for LLM
    schedule_context = "Student's Class Schedule:\n\n"
    for entry in schedule:
        schedule_context += (
            f"- {entry['day']} at {entry['time']}: "
            f"{entry.get('type', 'Class')} {entry.get('course_code', 'N/A')} "
            f"in Room {entry.get('room', 'N/A')} "
            f"(Section: {entry.get('section', 'N/A')})\n"
        )
    
    # Use Gemini to intelligently answer the query
    try:
        print(f"🤖 Using LLM to answer timetable query: {query}")
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite-preview-02-05')
        
        system_prompt = f"""You are a helpful assistant that answers questions about a student's class timetable.

{schedule_context}

User Question: {query}

Instructions:
1. Answer the question directly and concisely
2. Only include relevant information from the schedule
3. If asking for "next class" or "upcoming", determine what day/time it currently is and show the immediately next class
4. Format your answer clearly with emojis and structure
5. If the question is about a specific class, only show that class
6. If no specific match, explain what you found

Answer the user's question now:"""
        
        response = model.generate_content(system_prompt)
        print(f"✅ LLM response received")
        return response.text
        
    except Exception as e:
        print(f"❌ LLM query error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to basic search
        return fallback_search(schedule, query)

def fallback_search(schedule: List[Dict[str, Any]], query: str) -> str:
    """Fallback keyword-based search if LLM fails"""
    query_lower = query.lower()
    results = []
    
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # Check for specific day
    for day in days:
        if day in query_lower:
            for entry in schedule:
                if entry["day"].lower() == day:
                    results.append(entry)
            if results:
                return f"📅 **Your {day.capitalize()} Schedule:**\n\n" + format_schedule(results)
    
    # Check for course code
    for entry in schedule:
        course_code = entry.get("course_code", "").lower()
        if course_code in query_lower:
            results.append(entry)
    
    if results:
        return format_schedule(results)
    
    # Default: show upcoming classes
    return "Here are your upcoming classes:\n\n" + format_schedule(schedule[:5])

def format_schedule(schedule: List[Dict[str, Any]]) -> str:
    """Format schedule entries into readable text"""
    if not schedule:
        return "No matching classes found."
    
    formatted = []
    for entry in schedule:
        # Handle both old format (with teacher) and new format (with course code)
        if 'course_code' in entry and entry['course_code'] != 'N/A':
            formatted.append(
                f"📚 **{entry.get('type', 'Class')}** - {entry['course_code']}\n"
                f"   🕐 {entry['day']} at {entry['time']}\n"
                f"   🚪 Room: {entry.get('room', 'N/A')}\n"
                f"   📋 Section: {entry.get('section', 'N/A')}"
            )
        else:
            # Fallback to old format
            formatted.append(
                f"📚 **{entry.get('subject', 'Class')}** ({entry.get('course_code', 'N/A')})\n"
                f"   🕐 {entry['day']} at {entry['time']}\n"
                f"   👨‍🏫 Teacher: {entry.get('teacher', 'N/A')}\n"
                f"   🚪 Room: {entry.get('room', 'N/A')}"
            )
    
    return "\n\n".join(formatted)
