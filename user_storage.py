import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

USER_DATA_DIR = "./data/users"

def ensure_user_dir(student_id: str) -> str:
    """Create user directory if it doesn't exist"""
    user_dir = os.path.join(USER_DATA_DIR, student_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def save_user_profile(student_id: str, name: str, program: str, semester: int) -> Dict[str, Any]:
    """Save or update user profile"""
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
    
    if not os.path.exists(profile_path):
        return None
    
    with open(profile_path, 'r') as f:
        return json.load(f)

def save_timetable_data(student_id: str, timetable_data: Dict[str, Any]) -> bool:
    """Save extracted timetable data"""
    user_dir = ensure_user_dir(student_id)
    
    timetable_path = os.path.join(user_dir, "timetable.json")
    with open(timetable_path, 'w') as f:
        json.dump(timetable_data, f, indent=2)
    
    # Update profile to mark timetable as uploaded
    profile = get_user_profile(student_id)
    if profile:
        profile["timetable_uploaded"] = True
        profile["upload_date"] = datetime.now().isoformat()
        profile_path = os.path.join(user_dir, "profile.json")
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
    
    return True

def get_timetable_data(student_id: str) -> Optional[Dict[str, Any]]:
    """Get user's timetable data"""
    timetable_path = os.path.join(USER_DATA_DIR, student_id, "timetable.json")
    
    if not os.path.exists(timetable_path):
        return None
    
    with open(timetable_path, 'r') as f:
        return json.load(f)

def save_timetable_pdf(student_id: str, pdf_content: bytes) -> str:
    """Save uploaded PDF"""
    user_dir = ensure_user_dir(student_id)
    pdf_path = os.path.join(user_dir, "timetable.pdf")
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    
    return pdf_path
