# S01 Context - BRUSH-10-ACTIVATION-BACKEND-CONTRACT

## Scope

Add focused backend activation contract coverage around `EditorModel` and `EditorSessionState`.

## Boundaries

- Include `tests/python/test_editor_activation_backend.py`.
- Do not include the large dirty `pyrme/ui/main_window.py` UI-shell delta.
- Do not include untracked legacy menu parity tests.

## Gap Review

No product gap found in the backend contract covered by this slice. Pending UI command wiring remains separate follow-up work.
