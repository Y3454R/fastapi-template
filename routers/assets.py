import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from core.auth import get_current_active_user
from core.config import settings
from models.user import User

router = APIRouter(
    prefix="/api/v1/assets",
    tags=["assets"],
)

# Allowed MIME type groups
_ALLOWED_TYPES: dict[str, str] = {
    # Images
    "image/jpeg": "images",
    "image/png": "images",
    "image/gif": "images",
    "image/webp": "images",
    "image/svg+xml": "images",
    # Videos
    "video/mp4": "videos",
    "video/mpeg": "videos",
    "video/quicktime": "videos",
    "video/webm": "videos",
    # General files
    "application/pdf": "files",
    "text/plain": "files",
    "application/zip": "files",
}


def _get_ext(filename: str) -> str:
    """Return the file extension including the leading dot, lowercased."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a public asset",
    description=(
        "Upload an image, video, or file to the public static directory. "
        "The file is renamed to a UUID to prevent collisions and MIME type is validated. "
        "Returns the public URL path for the uploaded file. Requires authentication."
    ),
)
async def upload_asset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),  # noqa: ARG001
) -> dict:
    # Validate MIME type
    content_type = file.content_type or ""
    sub_dir = _ALLOWED_TYPES.get(content_type)
    if sub_dir is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: '{content_type}'. "
                   f"Allowed: {', '.join(_ALLOWED_TYPES.keys())}",
        )

    # Validate file size
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.max_upload_size_mb} MB.",
        )

    # Generate UUID filename to avoid collisions
    ext = _get_ext(file.filename or "")
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_dir = Path(settings.static_dir) / sub_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / unique_name

    async with aiofiles.open(dest_path, "wb") as out_file:
        await out_file.write(content)

    public_url = f"/static/{sub_dir}/{unique_name}"
    return {
        "filename": unique_name,
        "content_type": content_type,
        "url": public_url,
    }


@router.delete(
    "/{sub_dir}/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an uploaded asset",
    description=(
        "Permanently delete an uploaded file from the static directory given its sub-directory "
        "(`images`, `videos`, or `files`) and filename. Requires authentication."
    ),
)
async def delete_asset(
    sub_dir: str,
    filename: str,
    current_user: User = Depends(get_current_active_user),  # noqa: ARG001
) -> None:
    if sub_dir not in {"images", "videos", "files"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sub-directory. Must be one of: images, videos, files.",
        )

    file_path = Path(settings.static_dir) / sub_dir / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found.",
        )

    file_path.unlink()
    return None
