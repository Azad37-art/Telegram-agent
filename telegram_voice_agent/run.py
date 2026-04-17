import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from app.bot import create_app


def main() -> None:
    app = create_app()
    print("Telegram PDF RAG bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()