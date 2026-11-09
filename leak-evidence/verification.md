# What could and could not be verified in this container (2026-11-09)

## Not feasible: build, run, about:memory
- **Build:** no Firefox engine checkout (`engine/` absent; `npm run init` downloads ~GBs of Firefox source and
  `mach bootstrap` installs system packages through apt, which is forbidden in this session). Host had about 2 GB
  of free RAM out of 29 GB (`free -g`), and a Firefox build needs far more.
- **Run the released build:** downloaded `zen.linux-x86_64.tar.xz` for 1.24.1b into `/tmp/zenrt` (outside the
  repo). `ldd libxul.so` reports missing system libraries: libgtk-3.so.0, libgdk-3.so.0, libX11.so.6,
  libX11-xcb.so.1, libxcb.so.1, libxcb-shm.so.0, libXcomposite/Xdamage/Xext/Xfixes/Xrandr/Xrender/Xcursor/Xi,
  libasound.so.2, libfreetype.so.6, libfontconfig.so.1, libpango/pangocairo, libatk-1.0, libcairo/cairo-gobject,
  libgdk_pixbuf-2.0, libglib/gobject/gio-2.0, libdbus-1.so.3. No docker/podman. Installing them is a system-package
  install, so this stopped here (Ubuntu 24.04 packages, roughly: libgtk-3-0t64 libasound2t64 libdbus-glib-1-2
  libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libxcursor1 libxi6 fonts-dejavu, plus xvfb if not headless).
- What a runtime check would be: with Zen 1.24.1b stock vs. the same build with `ZenLibrary.mjs` patched inside
  `browser/omni.ja`, open and close 5 windows, press "GC"+"CC" in about:memory, then "Measure": stock should show
  5 `top(none)/detached/window(chrome://browser/content/browser.xhtml)` entries, patched 0. The mochitest added in
  8cdddb81e encodes the same check (weak reference to a closed window must clear after GC/CC).

## Verified by reading code (both sides of every claim)
- Cause A chain: `browser-box-inc-xhtml.patch:10` (element in every window) -> `ZenLibrary.mjs` connectedCallback
  `Services.prefs.addObserver` -> Firefox `Preferences.cpp` `AddObserverImpl` strong `PrefCallback.mStrongRef`
  -> removal only in disconnectedCallback (not run at window close). `RemoveObserverImpl` returns NS_OK when the
  observer is absent (double removal is safe).
- Gecko still runs promise callbacks for a closed chrome window: `CallSetup::GetActiveGlobalObjectForCall` only
  refuses windows without an active document, and `nsPIDOMWindowInner::IsCurrentInnerWindow` treats a discarded
  BrowsingContext's last inner window as current (`dom/bindings/CallbackObject.cpp`, `dom/base/nsGlobalWindowInner.cpp`,
  fetched from mozilla-firefox/firefox main). This is why the late-registration candidates in
  `window-retention.md` are possible in principle.
- Library fix 3d7777adc is in base and in 1.23.2b but not in 1.23.1b (`gh api .../compare`); ba9ca6818 is in 1.24b
  but not 1.23.4b.
- Motion v13.2.0 settle semantics: verified with a jsdom harness over the real vendored bundle
  (`motion/harness.cjs`, `motion/harness-output.txt`).

## Lint / tests that ran
- `npx prettier --check --trailing-comma es5 --arrow-parens avoid` on the changed files: clean. (Run without
  `--trailing-comma/--arrow-parens`, prettier also flags the untouched base file, so the repo's real config lives in
  the engine; those two options reproduce the base file's style exactly.)
- `node --check` on the changed files: OK.
- ESLint: not runnable; `eslint.config.mjs` imports `./engine/eslint-*.config.mjs`.
- Mochitests (`npm test` -> `scripts/run_tests.py` -> `mach test`): not runnable without a build. The new test
  `src/zen/tests/library/browser_library_window_close_leak.js` has **never been run**.
