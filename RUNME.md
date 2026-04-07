# RUNME

This project can be started on port `7861` with the commands below.

## 1) Create/use local venv and install

```bash
cd /home/aiserver/LABS/OCR/kotaemon-abdshomad-github
uv pip install --python .venv/bin/python -e libs/kotaemon -e libs/ktem
```

## 2) Pin compatible package versions (first run fixups)

```bash
uv pip install --python .venv/bin/python "huggingface_hub<1.0"
uv pip install --python .venv/bin/python "langchain==0.2.15" "langchain-community==0.2.11" "langchain-core==0.2.43" "langchain-openai==0.1.25" "langchain-text-splitters==0.2.4" "langchain-anthropic==0.1.23" "langchain-ollama==0.1.3"
uv pip install --python .venv/bin/python "langchain-google-genai==1.0.10"
uv pip install --python .venv/bin/python "langchain-cohere==0.2.4" "langchain-experimental==0.0.64" "langchain-mistralai==0.1.13"
uv pip install --python .venv/bin/python cachetools
```

## 3) Run on port 7861

```bash
GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7861 .venv/bin/python app.py
```

Open:

- http://127.0.0.1:7861
- http://localhost:7861

## Restart after changes

Edits to Python, `flowsettings.py`, or other app code do not apply until you restart the Gradio process.

1. Stop whatever is listening on the port (same machine as the app):

   ```bash
   fuser -k 7861/tcp 2>/dev/null || true
   ```

   If you started the app in a terminal in the foreground, use **Ctrl+C** there instead.

2. Start again with the same command as in **3) Run on port 7861** (from the project root):

   ```bash
   cd /home/aiserver/LABS/OCR/kotaemon-abdshomad-github
   GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7861 .venv/bin/python app.py
   ```

   To run in the background and append logs:

   ```bash
   nohup env GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7861 .venv/bin/python app.py >> /tmp/kotaemon-app.log 2>&1 &
   ```

3. Reload the page in your browser (or open the URL again).

## Notes

- In this environment, installing `kotaemon[all]` pulls `llama-cpp-python` and may fail to compile due to memory pressure.
- The command above uses the local editable packages and compatible pins to avoid that blocker.
