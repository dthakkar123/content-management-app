import hashlib
import os
import aiofiles
from fastapi import UploadFile
from app.config import settings


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save an uploaded file to the upload directory.

    Args:
        upload_file: FastAPI UploadFile object

    Returns:
        str: Path to saved file

    Raises:
        ValueError: If file is too large or invalid type
    """
    # Check file size
    content = await upload_file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum of {settings.MAX_FILE_SIZE} bytes")

    # Reset file pointer
    await upload_file.seek(0)

    # Generate unique filename using hash
    file_hash = hashlib.md5(content).hexdigest()
    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{file_hash}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    return file_path


def generate_content_hash(content: str, metadata: dict = None) -> str:
    """
    Generate SHA-256 hash for content deduplication.

    Args:
        content: Text content
        metadata: Optional metadata to include in hash

    Returns:
        str: SHA-256 hash (64 characters)
    """
    # Normalize content: lowercase, remove extra whitespace
    normalized = ' '.join(content.lower().split())

    # Include key metadata to differentiate versions
    hash_input = normalized
    if metadata:
        url = metadata.get('url', '')
        title = metadata.get('title', '')
        hash_input = f"{normalized}|{url}|{title}"

    return hashlib.sha256(hash_input.encode()).hexdigest()


async def delete_file(file_path: str) -> bool:
    """
    Delete a file from the upload directory.

    Args:
        file_path: Path to file

    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: File name

    Returns:
        str: Extension (lowercase, with dot)
    """
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(filename: str, allowed_extensions: list = ['.pdf']) -> bool:
    """
    Check if file type is allowed.

    Args:
        filename: File name
        allowed_extensions: List of allowed extensions

    Returns:
        bool: True if allowed
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions
