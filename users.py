"""
User authentication management module.
Handles user registration, login, and password verification.
Uses pickle for storage obfuscation and hashlib for secure password hashing.
"""

import hashlib
from pathlib import Path

from data_storage import load_pickle_file, save_pickle_file


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        The hashed password as a hex string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_users_file_path() -> Path:
    """Get the path to the users file."""
    return Path(__file__).parent / "users_data.pkl"


def load_users() -> dict:
    """
    Load users from the pickle file.
    
    Returns:
        Dictionary mapping usernames to hashed passwords.
        Returns empty dict if file doesn't exist.
    """
    return load_pickle_file(get_users_file_path())


def save_users(users: dict) -> None:
    """
    Save users to the pickle file.
    
    Args:
        users: Dictionary mapping usernames to hashed passwords
        
    Raises:
        IOError: If file cannot be written
    """
    save_pickle_file(get_users_file_path(), users)


def user_exists(username: str) -> bool:
    """
    Check if a user exists.
    
    Args:
        username: The username to check
        
    Returns:
        True if user exists, False otherwise
    """
    users = load_users()
    return username.lower() in users


def authenticate(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username to authenticate
        password: The plaintext password to verify
        
    Returns:
        True if authentication successful, False otherwise
    """
    users = load_users()
    username_lower = username.lower()
    
    if username_lower not in users:
        return False
    
    password_hash = hash_password(password)
    return users[username_lower] == password_hash


def validate_password(password: str) -> tuple:
    """
    Validate password meets security requirements.
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    return True, ""


def register_user(username: str, password: str) -> tuple:
    """
    Register a new user with username and password.
    
    Args:
        username: The username for the new account
        password: The plaintext password for the new account
        
    Returns:
        Tuple of (success, message). success=True if registration successful
    """
    # Validate password
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
    
    users = load_users()
    username_lower = username.lower()
    
    if username_lower in users:
        return False, "Username already exists"
    
    password_hash = hash_password(password)
    users[username_lower] = password_hash
    
    try:
        save_users(users)
        return True, "Registration successful"
    except (IOError, OSError) as e:
        return False, f"Failed to save user data: {e}"
    except Exception as e:
        return False, f"Unexpected error during registration: {e}"


def get_display_username(username: str) -> str:
    """
    Get the display version of a username (preserves original casing).
    
    Args:
        username: The username to look up
        
    Returns:
        The username if it exists, None otherwise
    """
    users = load_users()
    # Find the original casing
    for stored_user in users.keys():
        if stored_user == username.lower():
            return stored_user
    return None
