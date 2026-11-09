# Cause C (already fixed upstream): library download stack view kept closed windows alive, 1.23b..1.23.1b

- 2ee1275f2 (gh-15282, 2026-09-17) added `ZenLibraryDownloadStack` (`src/zen/library/ZenLibraryWidget.sys.mjs`).
  Its constructor does `this.#data = DownloadsCommon.getData(this.#window, true); this.#data.addView(this);`.
- `getData(window, true)` returns the history `DownloadsHistoryData`, whose `addView` forwards to
  `DownloadList.addView`, and `DownloadList._views` is a strong `Set` (Firefox `toolkit/components/downloads/DownloadList.sys.mjs`
  lines ~149/248, fetched 2026-11-09). The list is process-lifetime, the stack holds `#window`/`#button`/`#list`.
- `destroy()` (removeView) ran only from the CustomizableUI widget's `onDestroyed`, which is not called on window
  close, so every browser window with the library button stayed alive after close.
- `zen.library.enabled` became `true` on release in 06e65df70 (2026-09-27), so 1.23b and 1.23.1b release users had it.
- Fixed by 3d7777adc (gh-15826): `this.#window.addEventListener("unload", this, { once: true })` -> `destroy()`.
  `gh api compare`: 3d7777adc is in 1.23.2b, not in 1.23.1b.
- Posted reports in that version window with detached browser.xhtml: 5981075145 (1.23b, 2 entries, 15.5 MB).
Confidence: high by reading (registration + strong holder + missing teardown); not runtime-verified.
