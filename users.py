"""
User authentication management module.
Handles user registration, login, and password verification.
Uses pickle for storage obfuscation and hashlib for secure password hashing.
"""

import pickle
import hashlib
import os
from pathlib import Path


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
    users_file = get_users_file_path()
    if users_file.exists():
        try:
            with open(users_file, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            return {}
    return {}


def save_users(users: dict) -> None:
    """
    Save users to the pickle file.
    
    Args:
        users: Dictionary mapping usernames to hashed passwords
    """
    users_file = get_users_file_path()
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)


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


def register_user(username: str, password: str) -> bool:
    """
    Register a new user with username and password.
    
    Args:
        username: The username for the new account
        password: The plaintext password for the new account
        
    Returns:
        True if registration successful, False if user already exists
    """
    users = load_users()
    username_lower = username.lower()
    
    if username_lower in users:
        return False
    
    password_hash = hash_password(password)
    users[username_lower] = password_hash
    save_users(users)
    return True


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
