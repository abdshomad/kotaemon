#!/bin/bash
cd "$(cd "$(dirname "$0")" && pwd)" || exit 1; fuser -k 7861/tcp 2>/dev/null || true; sleep 1; exec env GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7861 .venv/bin/python app.py
