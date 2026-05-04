# T03 Summary - Backend Behavior

- Implemented no fake import/export/reload/report success.
- `DeferredFileDataService` is the default because no repo backend currently
  provides map merge/import policy, monster/NPC catalog import, minimap image
  export, tileset export, selected client-root reload, or version-manager
  missing item report behavior.
- Reload Data Files intentionally does not call client asset discovery yet:
  the shell has no selected client data root seam to pass into discovery.
- Injected services can return success, deferred, or failure messages; shell
  behavior maps those results to status text only and does not mutate document
  state or recents for deferred/failure results.
