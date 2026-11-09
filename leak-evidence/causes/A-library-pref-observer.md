# Cause A: `<zen-library>` hidden-tabs pref observer retains every closed window (1.24b+)

Status: **confirmed by code reading** (both registration and the missing teardown, plus the
Firefox pref-service semantics below). **Not confirmed at runtime**: Zen cannot be started in
this container (see `../verification.md`).

## Retention chain
1. `src/browser/base/content/browser-box-inc-xhtml.patch:10` puts `<html:zen-library hidden="true">`
   into every `browser.xhtml`, so every browser window creates one `ZenLibrary` element at load.
2. `src/zen/library/ZenLibrary.mjs` `connectedCallback()` (line ~202 on base bd97c6bb0):
   `Services.prefs.addObserver(HIDDEN_TABS_PREF, this.#tabsObserver)`.
   `#tabsObserver = { observe: () => this.requestUpdate() }`: the arrow function closes over
   `this` (the element), so the element's document, its window global and every node of that
   window's chrome DOM become reachable from the observer.
3. `nsPrefBranch::AddObserverImpl` with `aHoldWeak=false` stores
   `PrefCallback(prefName, aObserver, this)`, which keeps `nsCOMPtr<nsIObserver> mStrongRef`
   (Firefox `modules/libpref/Preferences.cpp`, `PrefCallback` constructor, fetched 2026-11-09 from
   mozilla-firefox/firefox main). The root pref branch is process-lifetime, so this is a GC root
   from C++ until removal.
4. The only removal was in `disconnectedCallback()`. Closing a window does not remove the nodes of
   its document from the document, so `disconnectedCallback` never runs for it. The
   element's `unload` handler (`#teardown`, added in 3d7777adc for gh-15823) did not remove the
   observer.
=> every closed browser window stays alive (shows as
`explicit/window-objects/top(none)/detached/window(chrome://browser/content/browser.xhtml)` in
about:memory of the Main Process) until quit.

## Since when
`git log -L199,208:src/zen/library/ZenLibrary.mjs`: the observer came in with ba9ca6818
(gh-16098/gh-16099, "Move space routing settings to the library", 2026-10-23). Releases (gh api):
1.23.4b 2026-10-21, 1.24b 2026-10-29, 1.24.1b 2026-11-06, so it ships in 1.24b and 1.24.1b.
The posted reports in #8932 stop at 1.23.4b (`../meta/memreports.md`), so **this cause explains
none of the posted reports**; it is a live regression on current dev with the same
symptom as pattern 2 there (detached browser.xhtml).

## Fix (commit 28be25f20)
Remove the observer in `#teardown()` (run on window `unload`). `nsPrefBranch::RemoveObserverImpl`
returns `NS_OK` when no matching callback exists (same file), so the existing removal in
`disconnectedCallback` stays harmless. XPConnect reuses one wrapped-JS per JS object, so passing
the same `#tabsObserver` object finds the same `PrefCallback` key.

## Other library registrations checked
Sections (`Boosts`, `Media`, `Downloads`, `History`, `Spaces`) register observers or download views
in `connectedCallback` and remove them in `disconnectedCallback`; they are children of
`#zen-library-content`, and `#teardown` calls `this._content?.replaceChildren()`, which is a
`[CEReactions]` DOM call, so their `disconnectedCallback`s do run on unload.
`ZenLibraryWidget.sys.mjs`: `stacks` is a `WeakMap` keyed by document; `ZenLibraryDownloadStack`
removes its `DownloadsData` view on unload (since 3d7777adc).
