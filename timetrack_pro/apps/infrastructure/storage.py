"""
Storage service abstraction.

Uses django-storages with environment-based backend selection:
- Development: FileSystemStorage (local files)
- Production: S3Boto3Storage (AWS S3)
"""
from django.core.files.storage import default_storage


def get_storage():
    """
    Get the configured storage backend.

    Returns the Django default_storage, which is configured
    in settings based on environment.
    """
    return default_storage


def save_file(name: str, content) -> str:
    """
    Save a file to storage and return the path.

    Args:
        name: Desired file name/path
        content: File content (file-like object or bytes)

    Returns:
        Actual saved path (may differ from name if file exists)
    """
    storage = get_storage()
    return storage.save(name, content)


def get_file_url(name: str) -> str:
    """
    Get URL for accessing a stored file.

    Args:
        name: File path in storage

    Returns:
        URL to access the file
    """
    storage = get_storage()
    return storage.url(name)


def delete_file(name: str) -> None:
    """
    Delete a file from storage.

    Args:
        name: File path in storage
    """
    storage = get_storage()
    storage.delete(name)


def file_exists(name: str) -> bool:
    """
    Check if a file exists in storage.

    Args:
        name: File path to check

    Returns:
        True if file exists
    """
    storage = get_storage()
    return storage.exists(name)
