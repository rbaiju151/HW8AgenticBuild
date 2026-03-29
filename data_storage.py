"""
Shared data storage utilities.
Provides common functions for loading and saving pickle files with error handling.
"""

import pickle
import shutil
from pathlib import Path
from typing import Any, Dict


def load_pickle_file(filepath: Path) -> Dict:
    """
    Load data from a pickle file with error handling.
    
    Args:
        filepath: Path to the pickle file
        
    Returns:
        Loaded data dictionary, or empty dict if file doesn't exist or is corrupted
    """
    if filepath.exists():
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            return {}
        except (IOError, OSError):
            return {}
    return {}


def save_pickle_file(filepath: Path, data: Any) -> None:
    """
    Save data to a pickle file with atomic writes and error handling.
    
    Writes to a temporary file first, then replaces the original file
    to ensure data integrity in case of interruption.
    
    Args:
        filepath: Path to save the pickle file
        data: Data to serialize and save
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        # Write to temporary file first for atomicity
        temp_file = Path(str(filepath) + '.tmp')
        with open(temp_file, 'wb') as f:
            pickle.dump(data, f)
        # Replace original file
        shutil.move(str(temp_file), str(filepath))
    except (IOError, OSError) as e:
        raise IOError(f"Cannot save to {filepath.name}: {e}")
