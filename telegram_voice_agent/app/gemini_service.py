from google import genai
from app.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Send audio bytes to Gemini and ask for a plain-text transcription.
    """
    prompt = "Transcribe this audio exactly. Return only the transcript text."

    response = client.models.generate_content(
        model=GEMINI_MODEL,
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


def ask_gemini(user_text: str) -> str:
    """
    Ask Gemini to answer the user's transcribed message.
    """
    system_prompt = (
        "You are a helpful Telegram voice assistant. "
        "Reply clearly, naturally, and briefly. "
        "If the user asks a factual question and the answer is uncertain, say so."
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"{system_prompt}\n\nUser message:\n{user_text}",
    )
    return response.text.strip()