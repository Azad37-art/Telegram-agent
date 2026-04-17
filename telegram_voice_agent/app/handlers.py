import os
from telegram import Update
from telegram.ext import ContextTypes

from app.gemini_audio import transcribe_audio
from app.rag_pipeline import ask_pdf
from app.utils import ensure_dir


TEMP_DIR = "temp"

GREETINGS = {
    "hi", "hello", "hey", "assalamualaikum", "salam",
    "how are you", "good morning", "good evening"
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send me a text question or a voice note. I will answer from the indexed PDF."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/reindex - Rebuild the PDF knowledge base\n\n"
        "Ask questions by text or voice."
    )


def is_greeting(text: str) -> bool:
    cleaned = text.strip().lower()
    return cleaned in GREETINGS


async def normal_chat_reply(update: Update, text: str) -> None:
    lowered = text.strip().lower()

    if lowered in {"hi", "hello", "hey", "salam", "assalamualaikum"}:
        await update.message.reply_text("Hello! Ask me anything from the PDF.")
    elif lowered == "how are you":
        await update.message.reply_text("I'm doing well. Ask me something from the PDF.")
    else:
        await update.message.reply_text(
            "I answer questions from the PDF. Ask me a topic from the document."
        )


async def answer_question(update: Update, question: str) -> None:
    if is_greeting(question):
        await normal_chat_reply(update, question)
        return

    await update.message.reply_text("Searching PDF...")

    try:
        answer, pages = ask_pdf(question)

        if pages:
            await update.message.reply_text(f"{answer}\n\nSources: {pages}")
        else:
            await update.message.reply_text(answer)

    except FileNotFoundError:
        await update.message.reply_text(
            "Knowledge base not found. Put your PDF in data/docs and run ingest.py first."
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    question = update.message.text.strip()
    if not question:
        return

    await answer_question(update, question)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.voice:
        return

    ensure_dir(TEMP_DIR)
    voice = update.message.voice

    await update.message.reply_text("Voice received. Transcribing...")

    telegram_file = await context.bot.get_file(voice.file_id)
    local_path = os.path.join(TEMP_DIR, f"{voice.file_unique_id}.ogg")

    try:
        await telegram_file.download_to_drive(local_path)

        with open(local_path, "rb") as f:
            audio_bytes = f.read()

        transcript = transcribe_audio(audio_bytes, mime_type="audio/ogg")
        await update.message.reply_text(f"Transcript:\n{transcript}")

        await answer_question(update, transcript)

    except Exception as e:
        await update.message.reply_text(f"Voice processing failed: {e}")

    finally:
        if os.path.exists(local_path):
            os.remove(local_path)