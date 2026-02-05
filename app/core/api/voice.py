"""
Voice processing API endpoints for Bhashini STT/TTS integration.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.common import BaseSchema
from app.core.services.auth import get_current_user
from app.database import get_db

router = APIRouter()


# Tamil keyword mappings for domain-specific terms
TAMIL_KEYWORD_MAPPING = {
    # Locations
    "விருந்தினர் இல்லம்": {"en": "guest_house", "category": "location"},
    "அறை": {"en": "room", "category": "location"},
    "வயல்": {"en": "field", "category": "location"},
    "தோட்டம்": {"en": "garden", "category": "location"},
    # Plumbing
    "கசிவு": {"en": "leak", "category": "plumbing"},
    "குழாய்": {"en": "pipe", "category": "plumbing"},
    "ஷவர்": {"en": "shower", "category": "plumbing"},
    "கழிப்பறை": {"en": "toilet", "category": "plumbing"},
    "வாஷர்": {"en": "washer", "category": "plumbing"},
    "தண்ணீர்": {"en": "water", "category": "plumbing"},
    "பம்ப்": {"en": "pump", "category": "plumbing"},
    "கீசர்": {"en": "geyser", "category": "plumbing"},
    # Electrical
    "மின்விசிறி": {"en": "fan", "category": "electrical"},
    "விளக்கு": {"en": "light", "category": "electrical"},
    "சாக்கெட்": {"en": "socket", "category": "electrical"},
    "ஸ்விட்ச்": {"en": "switch", "category": "electrical"},
    "ஏசி": {"en": "ac", "category": "electrical"},
    "மின்சாரம்": {"en": "electricity", "category": "electrical"},
    # Farm
    "உரம்": {"en": "fertilizer", "category": "farm"},
    "அறுவடை": {"en": "harvest", "category": "farm"},
    "விதைப்பு": {"en": "sowing", "category": "farm"},
    "புல்": {"en": "grass", "category": "farm"},
    "பசுமாடு": {"en": "cow", "category": "farm"},
    "தீவனம்": {"en": "fodder", "category": "farm"},
    # Status
    "முடிந்தது": {"en": "completed", "category": "status"},
    "பிரச்சினை": {"en": "problem", "category": "status"},
    "சரி": {"en": "okay", "category": "status"},
    "உடனடி": {"en": "urgent", "category": "priority"},
    "அவசரம்": {"en": "emergency", "category": "priority"},
    # Actions
    "சரிசெய்": {"en": "fix", "category": "action"},
    "மாற்று": {"en": "replace", "category": "action"},
    "சரிபார்": {"en": "check", "category": "action"},
}


class TranscribeRequest(BaseSchema):
    """Request for audio transcription."""

    language: str = "ta"  # Tamil default


class TranscribeResponse(BaseSchema):
    """Response from audio transcription."""

    transcript_tamil: str
    transcript_english: Optional[str] = None
    confidence: float
    keywords: list[dict]
    audio_duration_seconds: Optional[float] = None


class SynthesizeRequest(BaseSchema):
    """Request for text-to-speech."""

    text: str
    language: str = "ta"
    voice_gender: str = "female"  # 'male' or 'female'


class SynthesizeResponse(BaseSchema):
    """Response from text-to-speech."""

    audio_url: str
    audio_format: str = "mp3"
    duration_seconds: Optional[float] = None


class KeywordMapping(BaseSchema):
    """Keyword mapping entry."""

    tamil: str
    english: str
    category: str


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    audio: UploadFile = File(...),
    language: str = "ta",
):
    """
    Transcribe Tamil audio to text using Bhashini API.

    - **audio**: Audio file (WAV, MP3, or OGG format)
    - **language**: Language code (default: 'ta' for Tamil)

    Returns:
    - Tamil transcript
    - English translation (if available)
    - Extracted keywords with categories
    """
    # Validate file type
    allowed_types = ["audio/wav", "audio/mpeg", "audio/ogg", "audio/x-wav"]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: {', '.join(allowed_types)}",
        )

    # Read audio content
    audio_content = await audio.read()

    # TODO: Implement actual Bhashini API call
    # For now, return a mock response
    # In production, this would call:
    # 1. Upload audio to storage
    # 2. Call Bhashini ASR API
    # 3. Extract keywords from transcript
    # 4. Translate if needed

    # Mock response for development
    mock_transcript = "ரூம் 102 ல் மின்விசிறி வேலை செய்யவில்லை"
    mock_keywords = extract_keywords(mock_transcript)

    return TranscribeResponse(
        transcript_tamil=mock_transcript,
        transcript_english="Fan not working in room 102",
        confidence=0.92,
        keywords=mock_keywords,
        audio_duration_seconds=3.5,
    )


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Convert text to Tamil speech using Bhashini TTS API.

    - **text**: Text to convert to speech
    - **language**: Language code (default: 'ta' for Tamil)
    - **voice_gender**: Voice gender ('male' or 'female')

    Returns:
    - URL to the generated audio file
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # TODO: Implement actual Bhashini TTS API call
    # For now, return a mock response
    # In production, this would:
    # 1. Call Bhashini TTS API
    # 2. Store generated audio
    # 3. Return audio URL

    # Mock response for development
    return SynthesizeResponse(
        audio_url="/api/v1/voice/audio/mock-audio-id.mp3",
        audio_format="mp3",
        duration_seconds=2.5,
    )


@router.get("/keywords", response_model=list[KeywordMapping])
async def get_keyword_mappings(
    current_user: Annotated[User, Depends(get_current_user)],
    category: Optional[str] = None,
):
    """
    Get Tamil keyword mappings for domain-specific terms.

    - **category**: Filter by category (location, plumbing, electrical, farm, status, action)

    Used for:
    - Training frontend keyword recognition
    - Displaying Tamil terms to users
    - Mapping voice input to system actions
    """
    mappings = [
        KeywordMapping(tamil=tamil, english=data["en"], category=data["category"])
        for tamil, data in TAMIL_KEYWORD_MAPPING.items()
    ]

    if category:
        mappings = [m for m in mappings if m.category == category]

    return mappings


def extract_keywords(transcript: str) -> list[dict]:
    """
    Extract domain-specific keywords from Tamil transcript.
    """
    keywords = []
    transcript_lower = transcript.lower()

    for tamil_word, data in TAMIL_KEYWORD_MAPPING.items():
        if tamil_word in transcript_lower:
            keywords.append(
                {
                    "tamil": tamil_word,
                    "english": data["en"],
                    "category": data["category"],
                }
            )

    # Extract numbers (room numbers, quantities, etc.)
    import re

    numbers = re.findall(r"\d+", transcript)
    for num in numbers:
        keywords.append(
            {
                "tamil": num,
                "english": num,
                "category": "number",
            }
        )

    return keywords
