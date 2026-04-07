# Feature parity: Settings and LLM

## Application settings page

Source: [`libs/ktem/ktem/pages/settings.py`](../../libs/ktem/ktem/pages/settings.py).

- [ ] Mirror `SettingGroup` / `BaseSettingGroup` structure: application + reasoning + per-index options
- [ ] Persist to same backing store as `settings_state` / flowsettings (respect `finalize()` ordering from [`BaseApp`](../../libs/ktem/ktem/app.py))
- [ ] Reasoning registry: entries from `KH_REASONINGS` and `register_reasonings`

## LLM resources

Source: [`libs/ktem/ktem/llms/ui.py`](../../libs/ktem/ktem/llms/ui.py), [`llms/manager.py`](../../libs/ktem/ktem/llms/manager.py).

- [ ] List/add/edit/delete LLM definitions (`btn_new`, delete with confirm, edit save)
- [ ] Test connection (`btn_test_connection`)

## Embeddings

Source: [`libs/ktem/ktem/embeddings/ui.py`](../../libs/ktem/ktem/embeddings/ui.py).

- [ ] Same CRUD + test patterns as LLMs

## Reranking

Source: [`libs/ktem/ktem/rerankings/ui.py`](../../libs/ktem/ktem/rerankings/ui.py).

- [ ] Same CRUD + test patterns

## MCP

Source: [`libs/ktem/ktem/mcp/ui.py`](../../libs/ktem/ktem/mcp/ui.py).

- [ ] If MCP enabled in settings, expose configuration UI consistent with Gradio

## Help / resources

- [ ] Static Help tab: [`pages/help.py`](../../libs/ktem/ktem/pages/help.py) — port content to Next page or MDX

## Ordering

Implement **after** chat + file flows are stable; settings drive pipeline behavior and are harder to regression-test manually.
