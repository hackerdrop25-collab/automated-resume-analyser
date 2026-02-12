"""
File storage utilities for managing uploaded resumes
"""
import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_path(user_id):
    """Get user-specific upload directory"""
    user_upload_dir = os.path.join(Config.UPLOAD_FOLDER, f'user_{user_id}')
    os.makedirs(user_upload_dir, exist_ok=True)
    return user_upload_dir


def save_resume_file(file, user_id):
    """
    Save uploaded resume file to user's upload directory
    
    Args:
        file: Flask file object
        user_id: User ID for organizing files
    
    Returns:
        tuple: (original_filename, saved_filepath, file_size)
    """
    if not file or file.filename == '':
        raise ValueError('No file selected')
    
    if not allowed_file(file.filename):
        raise ValueError(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')
    
    original_filename = secure_filename(file.filename)
    user_upload_dir = get_upload_path(user_id)
    
    # Add timestamp to avoid filename conflicts
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    saved_filename = timestamp + original_filename
    filepath = os.path.join(user_upload_dir, saved_filename)
    
    # Save file
    file.save(filepath)
    file_size = os.path.getsize(filepath)
    
    return original_filename, filepath, file_size


def delete_resume_file(filepath):
    """Delete a resume file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f'Error deleting file {filepath}: {e}')
    return False


def cleanup_user_uploads(user_id):
    """Delete all uploads for a user"""
    user_upload_dir = os.path.join(Config.UPLOAD_FOLDER, f'user_{user_id}')
    try:
        if os.path.exists(user_upload_dir):
            shutil.rmtree(user_upload_dir)
            return True
    except Exception as e:
        print(f'Error cleaning up user uploads: {e}')
    return False


def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else None
