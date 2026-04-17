from google import genai
from app.config import GEMINI_API_KEY, CHAT_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Transcribe Telegram voice audio using Gemini.
    """
    prompt = "Transcribe this audio exactly. Return only the transcript text."

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[
            prompt,
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_bytes,
                }
            },
        ],
    )

    return response.text.strip()