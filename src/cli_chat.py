import logging
import textwrap
from typing import List, Dict

from .logging_setup import setup_logging
from .api_client import ChatClient
from .utils import build_system_message


def run_cli() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    client = ChatClient()

    print("==========================================")
    print("   MISTRAL CLI Chat")
    print("   Type 'exit' or 'quit' to stop.")
    print("==========================================\n")

    format_style = input(
        "Choose response format (plain/bullets/numbered) [plain]: "
    ).strip().lower() or "plain"

    if format_style not in ("plain", "bullets", "numbered"):
        print("Unknown format, defaulting to 'plain'.")
        format_style = "plain"

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": build_system_message(format_style)}
    ]

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("\nGoodbye 👋")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            reply = client.send_chat(messages)
        except RuntimeError as e:
            logger.error("Error during chat: %s", e)
            print(f"\n[Error] {e}")
            continue

        messages.append({"role": "assistant", "content": reply})

        print("\nAssistant:\n")
        print(textwrap.fill(reply, width=100))


if __name__ == "__main__":
    run_cli()
