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

## Notes

- In this environment, installing `kotaemon[all]` pulls `llama-cpp-python` and may fail to compile due to memory pressure.
- The command above uses the local editable packages and compatible pins to avoid that blocker.
