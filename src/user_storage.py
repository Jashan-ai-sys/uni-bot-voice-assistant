import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

USER_DATA_DIR = "./data/users"

def ensure_user_dir(student_id: str) -> str:
    """Create user directory if it doesn't exist"""
    user_path = os.path.join(USER_DATA_DIR, student_id)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def save_user_profile(student_id: str, name: str, program: str, semester: int) -> Dict[str, Any]:
    """Save user profile"""
    ensure_user_dir(student_id)
    
    profile = {
        "student_id": student_id,
        "name": name,
        "program": program,
        "semester": semester,
        "timetable_uploaded": False,
        "created_at": datetime.now().isoformat()
    }
    
    profile_path = os.path.join(USER_DATA_DIR, student_id, "profile.json")
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    return profile

def get_user_profile(student_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile"""
    profile_path = os.path.join(USER_DATA_DIR, student_id, "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    return None

def save_user_timetable(student_id: str, timetable_data: Dict[str, Any], pdf_path: str) -> bool:
    """Save user timetable data"""
    ensure_user_dir(student_id)
    
    # Save JSON data
    timetable_path = os.path.join(USER_DATA_DIR, student_id, "timetable.json")
    with open(timetable_path, 'w') as f:
        json.dump(timetable_data, f, indent=2)
    
    # Update profile
    profile = get_user_profile(student_id)
    if profile:
        profile["timetable_uploaded"] = True
        profile["timetable_updated_at"] = datetime.now().isoformat()
        save_user_profile(profile["student_id"], profile["name"], profile["program"], profile["semester"])
    
    return True

def get_user_timetable(student_id: str) -> Optional[Dict[str, Any]]:
    """Get user timetable data"""
    timetable_path = os.path.join(USER_DATA_DIR, student_id, "timetable.json")
    if os.path.exists(timetable_path):
        with open(timetable_path, 'r') as f:
            return json.load(f)
    return None

def save_user_timetable_pdf(student_id: str, pdf_content: bytes) -> str:
    """Save user timetable PDF"""
    user_dir = ensure_user_dir(student_id)
    pdf_path = os.path.join(user_dir, "timetable.pdf")
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    
    return pdf_path
