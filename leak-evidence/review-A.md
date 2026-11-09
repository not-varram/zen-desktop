# Review A: 28be25f20 (fix) and d55c862ca (test), since squashed into 8cdddb81e with the fixes below; independent adversarial review (2026-11-09)

Hard rule (verbatim from the user): Hard rule, because it has crashed every session on this account twice tonight: never run `apt-get install`, `dpkg -i` or `systemd-tmpfiles`, and never change the ownership or mode of /root or anything under it. A systemd postinst re-owns the account's shared /root and kills all sessions; run-v27ssb3txh is fixing that in Aether. Put this rule word for word in every sub-session's and subagent's brief. If you truly need system packages, stop and tell Varsh which ones and why.

Nothing was built or run. Firefox sources were read from raw.githubusercontent.com/mozilla-firefox/firefox/main on 2026-11-09.

## Verdict: approve the fix; approve the test with changes

The fix (`src/zen/library/ZenLibrary.mjs:960-963`) is correct, minimal, and in the right place. The test
(`src/zen/tests/library/browser_library_window_close_leak.js`) has one gap that can make it pass before the
fix, and one risk that can make it fail after the fix. Neither has been checked at runtime.

## Fix: claims checked

| Claim | Result | How |
|---|---|---|
| `<zen-library>` is in every browser.xhtml | true | read `src/browser/base/content/browser-box-inc-xhtml.patch:10` |
| `Services.prefs.addObserver` (no `holdWeak`) holds the observer strongly | true | `Preferences.cpp` `nsPrefBranch::AddObserverImpl` builds `PrefCallback(prefName, aObserver, this)` (strong) |
| The arrow function keeps the element alive | true | `ZenLibrary.mjs:121-123`. It is a class-field arrow, so `this` is the element |
| `disconnectedCallback` does not run when a chrome window closes | true | `Document::Destroy` (`dom/base/Document.cpp`) calls `DestroyContent()` on each child and asserts `child->GetParentNode() == this`. Nothing is unbound, so no CE disconnected reaction runs |
| Removing an observer twice is safe | true | `RemoveObserverImpl` returns `NS_OK` when no entry matches. A strong re-add is deduplicated in `AddObserverImpl`, so a remove/re-add or a move is fine too |
| `unload` reaches `#teardown` | true for every element that ran `connectedCallback` | `ZenLibrary.mjs:201` (`once`), `:950-951`. Removal comes first in `#teardown`, so a throw in `#cleanup()` can no longer skip it (the order matters) |
| Nothing registers the observer again after teardown | true | the only `addObserver` is in `connectedCallback`. A later Lit render (from `#cleanup`'s `requestUpdate`) only renders `nothing` into `#zen-library-content`, because `#contentMounted` is false |
| Provenance: ba9ca6818, first shipped in 1.24b | true | `git log -S"addObserver(HIDDEN_TABS_PREF"` gives only ba9ca6818. `gh api compare 1.23.4b...ba9ca6818` = ahead, `ba9ca6818...1.24b` = ahead |
| Section observers are removed by `replaceChildren()` in `#teardown` | true | Media `:136/:186`, Downloads `:82/:94`, Boosts, History, Spaces each pair add with remove in dis/connectedCallback. `replaceChildren` is `[CEReactions]` |
| `ZenLibraryWidget` holds nothing past unload | true | `stacks` is a `WeakMap` keyed by document. The stack's `unload` calls `destroy()` -> `removeView` (`ZenLibraryWidget.sys.mjs:74-85`) |

### F1 (minor, wording): "every window" depends on the module being imported
`ZenLibrary.mjs` is not preloaded. It is a lazy `defineESModuleGetters(..., {global:"current"})` in
`src/zen/common/zen-sets.js:8-14`, `ZenCompactMode.mjs:64-68` and `ZenSpaceManager.mjs:20`.
`customElements.define("zen-library")` (`ZenLibrary.mjs:1204`) only runs on the first `lazy.ZenLibrary` access.
Until then the element is not upgraded and registers nothing. In practice it is imported at startup, most likely
through `ZenSpaceManager.mjs:3016-3019` (`onPinnedTabsResize`, from a ResizeObserver plus rAF) (inferred).
So the leak is real for almost every window, but the commit message and cause A overstate it
("connectedCallback runs once per window"). This does not change the fix.

## Test: findings

### F2 (should fix): the test can pass before the fix
`browser_library_window_close_leak.js:23`, `ok(win.document.querySelector("zen-library"))`, passes even when the
element was never upgraded. Scenario: the new window closes before anything touches `lazy.ZenLibrary`, for
example the essentials ResizeObserver's rAF has not run yet. Then no observer is registered, the weak reference
clears, and the test passes on the unfixed code. Fix: assert the upgrade, for example
`ok(win.customElements.get("zen-library"), ...)` and
`ok(lib instanceof win.customElements.get("zen-library"))`, or force the import inside `win` before closing it.

### F3 (risk, cannot settle without a run): the test can fail after the fix because of other retainers
The test asserts that *nothing* keeps the window alive, so it is a whole-browser leak test.
- REPORT.md says 24 of the 26 detached-window reports come from versions without cause A or C, and that they are
  **unexplained**. If that retainer still exists on base, this test fails permanently after the fix.
- Late registrations (window-retention.md #1-#3). `ZenMods.init()` awaits `SessionStore.promiseInitialized` and IOUtils
  reads before `Services.prefs.addObserver` plus its `unload` remover (`src/zen/mods/ZenMods.mjs:485-545`). The
  test only waits for `gZenWorkspaces.promiseInitialized` and delayed startup (`BrowserTestUtils.openNewBrowserWindow`
  waits for `browser-delayed-startup-finished`). If ZenMods' I/O is still pending at close, it leaks: intermittent.
- `src/zen/sessionstore/ZenWindowSync.sys.mjs` (process-lifetime) was excluded from window-retention.md. I only
  spot-read it: `#lastFocusedWindow` is a `WeakRef`. Not a full check.
- Recommendation: run it on a build without the fix and with it before landing. If it is flaky, wait for
  `gZenMods`, or narrow the assertion.

### F4 (nit): pref hygiene
`:31-32` `clearUserPref` wipes any user value an earlier test left behind, and briefly hides History in the main
window. Use `SpecialPowers.pushPrefEnv` / `popPrefEnv` or `registerCleanupFunction`. The pref poke is not needed
for retention, because the strong reference exists without it. The comment at `:29-30` suggests otherwise.

### Questions asked
- **Async condition with `waitForCondition`**: OK. `TestUtils.sys.mjs` `tryOnce` does `conditionPassed = await condition()`.
  It runs up to 50 tries 100 ms apart, each with 3x GC+CC, which fits the 45 s default (inferred, cost not measured).
- **`win = null`**: meaningful and needed. The async function's environment lives across the awaits, so `win`
  (the WindowProxy) would otherwise stay reachable from the test. `let` allows the reassignment.
  `waitForCondition` nulls `condition` on success.
- **Is the weak reference the right object?** Yes. `xpcJSWeakReference::Init` -> `ReflectorToISupportsDynamic`
  with `stopAtWindowProxy=false` resolves to the inner `nsGlobalWindowInner` (supports weak references). That is
  the object that leaks. It is not a throwaway wrapped-JS weak reference, which would clear at once.

## REPORT.md code claims

- "CustomizableUI `onDestroyed` does not run on window close": **true**. `unregisterBuildWindow`
  (CustomizableUI.sys.mjs ~2098-2139) only does `widget.instances.delete(document)` and notifies listeners.
  `widget.onDestroyed` is called only from `destroyWidget` (~4593). I did not check Zen's CustomizableUI patch for
  an added call (inferred absent). Cause C detail: 2ee1275f2 really called `getData(this.#window, true)`. Base now
  calls `getData(this.#window)`. Both kinds of data hold their views strongly, according to cause C. I did not re-read that.
- "disconnectedCallback does not run when a chrome window closes": **true**, see above.
- "Gecko still runs promise callbacks for a closed chrome window": **consistent with source**.
  `GetCheckedGlobalObject` -> `GetActiveGlobalObjectForCall` refuses only when `!HasActiveDocument()`, which is
  `IsCurrentInnerWindow()`. A discarded BrowsingContext counts as current if `WasCurrentInnerWindow()`. Then
  `CanRunJSMicroTask` for the system principal only checks `IsScriptForbidden` and does not check `IsDying`. I did not read
  whether `mOuterWindow` is cleared during teardown, which would flip the answer. So the claim is plausible but
  not fully proven.

## Aside (out of scope, not part of this fix)
`ZenWindowSync.sys.mjs:1613`: `this.#swapedTabsEntriesForWC.size === 0` reads a WeakMap, which has no `.size`, so the early return
never fires. It is harmless (the loop just looks up keys).
