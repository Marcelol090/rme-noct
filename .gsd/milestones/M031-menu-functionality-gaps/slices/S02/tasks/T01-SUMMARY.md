# T01 Summary - File Data RED

- Added RED coverage for all six S02 File data actions:
  Import Map, Import Monsters/NPC, Export Minimap, Export Tilesets,
  Reload Data Files, and Missing Items Report.
- Added assertions that injected file data operations are called and that
  success/failure/deferred result messages reach the status bar.
- Added non-mutation coverage for deferred/failure results preserving document
  path, dirty state, settings recents, and the Recent Files menu.
- RED command: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short`
- RED result: 3 failed, 12 passed. Intended failures: `MainWindow.__init__()`
  did not accept `file_data_service`, and default actions still returned generic
  unavailable text.
