# T03 Summary - File Lifecycle Wiring

- Wired File New/Open/Save/Save As/Close/Exit away from `_show_unavailable`.
- Added `MapDocumentState.path` and bridge capability wrappers for `load_otbm`/`save_otbm`.
- Close and Exit now share the dirty-document guard; Save uses the current path and Save As asks the service for a path.
- Correction: `MapDocumentState` now carries an optional persistence handle; Open binds the returned loaded context before path/dirty/recent updates, and Save leaves path/dirty/recent unchanged when persistence returns false or raises.
- Correction: `EditorShellCoreBridge.load_otbm` and `save_otbm` catch native exceptions and return `False`.
