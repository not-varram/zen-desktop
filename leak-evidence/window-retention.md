# Process-lifetime holders of closed browser windows (detached browser.xhtml)

Scope: Zen-added code that could keep a closed `browser.xhtml` window, document, chrome element or `gBrowser`
reachable from something that lives for the whole process. Read from source at base `0a4e95809`.
Nothing was run or measured. Items marked *(inferred)* are reasoning about timing, not observation.
Excluded by assignment: `ZenWindowSync.sys.mjs`, `ZenSessionManager.sys.mjs`, `src/zen/library/**` (the lead reads those).

**Headline.** I found no unconditional leak: every strong registration made from window scope
(`Services.obs.addObserver`, `Services.prefs.addObserver`) has a matching removal on that window's `unload`.
The only holders that survive a window close are *late registrations*: observers added after an `await`
or deferred step, so the window can already be gone when the `unload` listener is attached or when the
removal condition is tested. Those are bounded (one registration per window that closed in the startup
window) and cannot by themselves explain windows accumulating in long-running sessions (2..14 entries,
up to 289 MB), unless windows are routinely closed during startup/restore. They are the only candidates
this sweep can support. The bulk of the 26/77 reports probably live in the excluded modules or in Firefox code.

Why a strong observer retains the whole window: the Observer Service / pref branch holds the observer
strongly (`weak` is false by default). Zen window-scope modules are loaded with
`ChromeUtils.importESModule(script, { global: "current" })` (`src/zen/common/ZenPreloadedScripts.js:27-33,
44-52`), so the observer's functions/classes belong to the *window's own global*. A reachable closure from
that global keeps the window global, its `document` and the chrome DOM alive.

## Ranked candidates

### 1. `ZenMods.init()` registers two pref observers after several awaits *(inferred, window-closed-during-startup)*
- Registration: `src/zen/mods/ZenMods.mjs:535-536` (`Services.prefs.addObserver(this.updatePref, rebuildObserver)`,
  `("zen.themes.disable-all", disableObserver)`). Both are `bind(this)` closures over the window's ZenMods.
- Removal: `ZenMods.mjs:537-545`, an `unload` listener attached *right after* the registration.
- Why it can leak: `init()` (`:485`) first does `await SessionStore.promiseInitialized` (`:487`),
  `await this.getMods()`, `#getEnabledMods()`, `Promise.all(getModPreferences...)` (`IOUtils` reads), and
  `await this.#insertStylesheet()` (`:514`). If the window closes during any of them, `unload` has already
  fired, the later `addEventListener("unload")` never runs, and the pref branch keeps both closures forever.
  The `window.closed` guard exists only for the update check (`:518-523`), not for the registration.
- Retains: `gZenMods` instance, therefore the whole window global (about 5 MB, matches the report size).
- Trigger: open a window and close it before ZenMods finishes loading (fast open/close, tab-drag windows
  closed again, closing during session restore).
- Verified by reading: registration, removal, awaits. Inferred: that `unload` has already been dispatched
  by then (event on a closing window is not replayed).

### 2. `ZenCompactMode.init()` registers a pref observer and an obs observer after three awaits *(inferred)*
- Registration: `src/zen/compact-mode/ZenCompactMode.mjs:97-108` (`zen.tabs.vertical.right-side` pref observer;
  `zen-mouse-tracker:exited` observer), both bound closures over `gZenCompactModeManager`.
- Removal: `:110-123`, `unload` listener attached in the same function.
- Why it can leak: `init()` is only called from `src/zen/common/modules/ZenStartup.mjs:99`, inside
  `gZenWorkspaces.promiseInitialized.then(async () => { await delayedStartupPromise; await
  SessionStore.promiseAllWindowsRestored; gZenCompactModeManager.init(); ...})` (`:95-100`).
  Nothing checks `window.closed` before `init()`. If the window is closed before those promises resolve,
  the observers are added to a window whose `unload` never fires again.
- Retains: the compact mode manager and the window global. Same trigger and caveats as #1.
- Note `promiseAllWindowsRestored` can take long at startup with many windows, which widens the window of time.

### 3. `ZenStartup` observer for `browser-delayed-startup-finished` is only removed on a match *(inferred)*
- Registration: `src/zen/common/modules/ZenStartup.mjs:82` `Services.obs.addObserver(this, "browser-delayed-startup-finished")`
  when `gBrowserInit.delayedStartupFinished` is still false.
- Removal: only in `observe` (`:87-91`) and only when `aSubject == window`. No `unload` fallback.
- If the window closes before its own delayed startup finishes, the notification never arrives for it,
  so the strong observer (`this`, a ZenStartup of that window) stays registered for the life of the process.
- Retains: the window global. Narrowest of the three (delayed startup is quick), but the same pattern as #1/#2.
- Trigger: open and close a window faster than Firefox's delayed startup (idle-dispatched).

### 4. Known-fine pattern that depends on `unload` firing: everything below
Not leaks as written, listed so nobody re-checks them. All were read at both registration and teardown.

### 5. `ZenBoostsEditor` (separate window) keeps `openerWindow` *(low, bounded)*
- `src/zen/boosts/ZenBoostsEditor.mjs:32-52` stores `openerWindow` (a browser.xhtml) and registers strong observers
  (`OBSERVERS`, plus `selector-picker-picked` at `:658`). Removal: `uninit()` at `:175-181` via `handleClose()`
  (`:1692`) from the editor's `unload` listener (`:84`).
- The listener is attached in `init()` (`:84`), after the observers are added in the constructor (`:51-53`).
  If anything between throws (`killOtherEditorInstances`, `init`), the editor leaks along with `openerWindow`.
  I did not find a throw path; listed because the retained object is a full browser window.
- `selector-picker-picked` add/remove is toggled by `onUpdatePickerObserver` (`:650-662`) without a guard against
  double-add; an unmatched `addObserver` on teardown would be removed once only. Inferred, small.

## Checked and fine (registration and teardown both read)

| Where | Holder | Teardown |
| --- | --- | --- |
| `src/zen/spaces/ZenSpaceManager.mjs:176-203` | `obs` `workspace-bookmarks-updated`, `contextual-identity-deleted` (closures over `gZenWorkspaces`) | `unload` (`:191-200`). Registered synchronously in the non-private branch (awaits at `:166-168` only in the private branch) |
| `src/zen/spaces/ZenGradientGenerator.mjs:2228-2241` | `look-and-feel-changed` obs + `zen.theme.accent-color` pref | `unload`, `once`, attached in the same function; called from the constructor |
| `src/zen/common/zenThemeModifier.js:58-92` | pref observers and capture listeners | `unload` (`:82-94`), synchronous registration |
| `src/zen/glance/ZenGlanceManager.mjs:218-221, 315-330` | `quit-application-requested` (strong, `this`) | `unload` removes it; the quit-request path intentionally keeps it |
| `src/zen/urlbar/ZenSiteDataPanel.sys.mjs:101-120` | `zen-boosts-update` obs; `gBrowser.addProgressListener` | obs removed on `unload`; progress listener lives on the window's own `gBrowser` |
| `src/zen/boosts/ZenBoostReceiveDialog.mjs:35-45`, `ZenBoostShareDialog.mjs:48-56` | `zen-boosts-kill-share` (strong, `this` holds `openerWindow`) | `unload` of the dialog window (`once`) |
| `src/zen/boosts/actors/ZenBoostsParent.sys.mjs:38-52` | 4+ strong observers per actor | `didDestroy` removes them; zap bar element nulled |
| `src/zen/boosts/ZenBoostsManager.sys.mjs:637-745` (`openBoostWindow`) | progress listener + `TabSelect` listener on the opener's `gBrowser` | editor `unload` removes both; editor holds `openerWindow` only while open |
| `src/zen/common/sys/ui/ZenUIComponent.sys.mjs` (+ `ZenMediaController`, `ZenSpaceRoutingNavigation`, `ZenLiveFoldersUI`, `ZenProgressBar`) | per-window components; `gBrowser.addTabsProgressListener(this)`, DOM listeners | created per window by the `browser-window-delayed-startup` category; owner is the window itself. Module-level state: none |
| `src/zen/media/ZenMediaController.sys.mjs:273, 202-209` | `window.setInterval` / `setTimeout` | cleared on stop; timers belong to the window, die with it |
| `src/zen/kbs/ZenKeyboardShortcuts.sys.mjs:266-355` | `#legacyMigration` promise (module singleton) closing over `window`; `MutationObserver` on that window's body | promise reference is cleared in `.finally` (`:272-274`); observer is `disconnect`ed on `unload`. Runs once per profile |
| `src/zen/urlbar/ZenUBGlobalActions.sys.mjs:346-348` | module `labels` Map of l10n strings and a never-removed `intl:app-locales-changed` observer | holds strings and the Map only, no window |
| `src/zen/sync/ZenSpacesSync.sys.mjs:92-105` | tracker obs topics | `onStop` removes; holds no window |
| `src/zen/live-folders/ZenLiveFoldersManager.sys.mjs` | `wake_notification` obs, `ZenWindowSync.addSyncHandler`, DeferredTask providers | `uninit()` removes; `window` is a getter over `firstSyncedWindow`, no stored window. The sync-handler registry itself is in the lead's module |
| `src/zen/common/sys/ZenUIMigration.sys.mjs:63-90` | `CustomizableUI.addListener(listener)` | removed on first matching area; listener holds no window |
| `src/zen/space-routing/ZenSpaceRoutingManager.sys.mjs:33-50` | per-window DOM listeners with `.bind(this)` on the singleton | listeners live on that window's own elements; the singleton does not store the window |
| `src/zen/urlbar/*Provider*.sys.mjs`, `ZenUBActionsProvider.sys.mjs` | `getTopWindow()` used transiently | no stored window; `#seenCommands` Set holds strings |
| `src/zen/window-drag/actors/*`, `src/zen/glance/actors/*`, `src/zen/mods/actors/*`, `src/zen/boosts/actors/ZenBoostsChild`, `ZenZap*`, `ZenSelectorComponent` | JSWindowActors / content-side | content-scope refs to `window`, nulled on teardown; no parent-module registry of windows |
| `src/zen/common/sys/ZenCustomizableUI.sys.mjs`, `ZenActorsManager.sys.mjs`, `ZenPGOTraining`, `share/ZenShareClient`, `migration/*`, `urlbar/ZenUBResultsLearner` | no module-level collections of windows/tabs/elements | `ZenMigrationUtils.browserWindow` picks a window on demand and does not cache it |
| `src/zen/zen.globals.mjs`, `ZenPreloadedScripts.js` | all window `.mjs` loaded with `global: "current"` | per-window module instances, so module-level `DOMParser`/`static` fields (e.g. `ZenFolder.rawIcon`) are window-scoped |

### Zen-added hunks in process-lifetime Firefox modules (`*-sys-mjs.patch`)
Read every `+` line in all 60+ `*-sys-mjs.patch` files for stored state or listeners. Findings:
- No Zen hunk adds a module-level Map/Set/array/WeakRef or an observer/listener registration to a Firefox `.sys.mjs`.
  The adds are gating logic and calls into `gZen*` objects on the window passed in.
- `SessionStore-sys-mjs.patch:151-204`: `let browsers = aWindow.gZenWorkspaces.allUsedBrowsers` (was
  `Array.from(tabbrowser.browsers)`) is captured by the `flushWindow(...).then` closure and passed to
  `ZenWindowSync.on_WindowCloseAndBrowserFlushed(browsers)` (`:193`). The closure lives only as long as the
  flush promise; what `ZenWindowSync` does with `browsers` is in the lead's module. **Worth the lead checking
  that the browser array is not stored.**
- `Tabbrowser-sys-mjs.patch`: `#tabsWithInitialTitle` / `#endRemoveArgs` are upstream statics keyed by tab
  (not Zen-added). I did not verify they are WeakMap/WeakSet in this Firefox version; `#endRemoveArgs` is
  upstream and entries are deleted in `_endRemoveTab`.
- `CustomizableUI-sys-mjs.patch:107,118` call `ZenCustomizableUI.init(aWindow)` / `registerToolbarNodes(aWindow)`;
  these build DOM on the window and do not store it.
- `TabState`, `TabStateFlusher`, `SessionSaver`, `SessionFile`, `BrowserWindowTracker`, `URILoadingHelper`,
  `BrowserContentHandler`, `SubDialog`, `PopupNotifications`, `UrlbarValueFormatter` hunks: no retained
  references (timers on `this._window` / `anchorElement.documentGlobal`, which are window-owned).

## Not covered
- `ZenWindowSync`, `ZenSessionManager`, `library/**` (lead).
- Firefox's own code (e.g. `TabStateFlusher` requests, `BrowserWindowTracker` ordered list). I did not read upstream behavior.
- Non-`sys-mjs` patches (window-scope `.mjs`/`.js`): their registrations die with the window unless they hit a
  process-lifetime registry; I grepped the Zen `.mjs/.js` (not the patches) for such registries and found only
  the items above.
- Anything dynamic: no profiling, heap snapshot, or CC logs were run.

## Suggested verification (cheap)
1. Open a window, close it within ~100 ms, repeat 10x. In `about:memory`, look for `detached/window(chrome://browser/content/browser.xhtml)`.
   Candidates #1-#3 predict one retained window per iteration when the close beats delayed startup/ZenMods init.
2. Add `console.log` inside the `unload` handlers at `ZenMods.mjs:537`, `ZenCompactMode.mjs:110` to see whether
   `init()` runs after `unload` for such windows.
3. Minimal fix for #1-#3 (not applied here): check `window.closed` before registering and bail, or register the
   `unload` listener *before* the awaits and remove through a flag; for #3 add an `unload` fallback.
