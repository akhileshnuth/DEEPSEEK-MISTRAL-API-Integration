# Hiringhood Intelligent Workspace

A clean, modern, customizable AI chat application with selectable formatting, scroll‑to‑bottom UI behavior, a Flask backend, and a Mistral-powered API integration.

##  Overview
Hiringhood Intelligent Workspace is a full-stack AI chat system built with:
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **LLM Provider:** Mistral
- **Features:** formatting styles, scroll-to-bottom button, auto-resizing input, CLI support, logging, secure .env config.

## Live App
**Frontend:** https://deepseek-mistral-api-integration.onrender.com/

## Project Structure
```
project-root/
├── web/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── src/
│   ├── web_app.py
│   ├── cli_chat.py
│   ├── api_client.py
│   ├── config.py
│   ├── utils.py
│   └── logging_setup.py
├── .env
├── requirements.txt
└── logs/
```

## Running the Project
### Start Backend
```
python -m src.web_app
```
Visit: http://127.0.0.1:5000/

### Start CLI Chat
```
python -m src.cli_chat
```

## Install Dependencies
```
pip install -r requirements.txt
```

## Environment (.env)
```
MISTRAL_API_KEY=your-key
LLM_MODEL=mistral-small-latest
API_TIMEOUT=30
LOG_FILE=logs/app.log
```
