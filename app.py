import logging
from typing import Any, Dict, List

from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path

from .logging_setup import setup_logging
from .api_client import ChatClient
from .utils import build_system_message

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/")

setup_logging()
logger = logging.getLogger(__name__)
client = ChatClient()

def ensure_system_message(
    messages: List[Dict[str, str]], format_style: str
) -> List[Dict[str, str]]:
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        messages.insert(
            0, {"role": "system", "content": build_system_message(format_style)}
        )
    return messages


@app.route("/")
def index() -> Any:
    return send_from_directory(app.static_folder, "index.html")

# Flask receives the POST request
@app.route("/api/chat", methods=["POST"]) # This means Flask is waiting for POST requests at /api/chat. 
def api_chat() -> Any:  # This function handles the POST request. Then Flask extracts: All messages, Formatting style (plain, bullets, numbered), Then it prepares them for the AI.
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    messages = data.get("messages", [])
    format_style = (data.get("format_style") or "plain").lower()

    if not isinstance(messages, list):
        return jsonify({"error": "messages must be a list"}), 400

    messages = ensure_system_message(messages, format_style)

    try:
        reply = client.send_chat(messages)
        messages.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply, "messages": messages})
    except RuntimeError as e:
        logger.error("Error in /api/chat: %s", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run as: python -m src.web_app
    app.run(host="127.0.0.1", port=5000, debug=True)
