# Feature parity: Files and indexing

Primary UI: [`libs/ktem/ktem/index/file/ui.py`](../../libs/ktem/ktem/index/file/ui.py) (`File` page class and `DirectoryUpload`).

## Layout

- [ ] Nested tabs when `len(indices) > 1` (parent "Files" in [`main.py`](../../libs/ktem/ktem/main.py)); single index may use index name as top-level tab
- [ ] Scrollable main area (`fill-main-area-height`, `scrollable`)

## Upload

- [ ] File upload (`File` subclass preserving original filenames)
- [ ] Directory upload accordion (`DirectoryUpload`) with supported types from index config `supported_file_types`
- [ ] Progress / close panel for uploads (`btn_close_upload_progress_panel` pattern)

## Listing and selection

- [ ] Filter (`filter.submit`)
- [ ] Dataframe or table of files with actions: delete, download single, download all, deselect
- [ ] Selection state driving chat (`chat_button` → focus chat / pass context)
- [ ] Group CRUD: add, save, delete, close (`group_*` buttons)

## Limits

- [ ] `MAX_FILE_COUNT`, `MAX_FILENAME_LENGTH` behavior and user messaging

## Integration with chat

- [ ] `update_file_list_js` equivalent: when file list changes, refresh `@` mention choices in chat input
- [ ] Quick URL submit to indexing (demo flows in chat page referencing file index)

## Graph / advanced indices

If graph indices enabled (`light_graph_index`, `nano_graph_index`, etc.):

- [ ] Surface any visualization or extra controls from `index/file/graph/` pipelines — track separately after baseline file index parity

## API alignment

See [endpoints-outline.md](../backend-api/endpoints-outline.md) (`/api/index/...`).
