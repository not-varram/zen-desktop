# Task: Find process-lifetime holders of closed browser windows in Zen code (detached browser.xhtml)

## Hard rule (verbatim from the user)
Hard rule, because it has crashed every session on this account twice tonight: never run `apt-get install`, `dpkg -i` or `systemd-tmpfiles`, and never change the ownership or mode of /root or anything under it. A systemd postinst re-owns the account's shared /root and kills all sessions; run-v27ssb3txh is fixing that in Aether. Put this rule word for word in every sub-session's and subagent's brief. If you truly need system packages, stop and tell Varsh which ones and why.

## Context
Meta issue zen-browser/desktop#8932 tracks memory leaks. `leak-evidence/meta/memreports.md` (pattern 2) shows 26 of 77 posted about:memory reports have `explicit/window-objects/top(none)/detached/window(chrome://browser/content/browser.xhtml)` entries in the Main Process: closed browser windows that stay alive (2..14 entries, ~5 MB each, up to 289 MB), from Zen 1.12 through 1.23.4. The lead (Opus) is reading `src/zen/sessionstore/ZenWindowSync.sys.mjs`, `ZenSessionManager.sys.mjs` and `src/zen/library/**` itself; do not duplicate those.

## Goal
Find code that keeps a closed browser window (its `window`, `document`, any chrome DOM element, `gBrowser`, tabs, or a closure over any of those) reachable after the window closes. Sweep:
1. All `src/**/*.patch` files: Zen-added hunks (lines starting with `+`) in Firefox modules (`*.sys.mjs` / `*.jsm` patches are process-lifetime) that store window/tab/element references into module-level state, or register listeners/observers from window scope without removal.
2. `src/zen/**/*.sys.mjs` except ZenWindowSync/ZenSessionManager/library: module-level Maps/Sets/arrays/fields that receive windows, tabs, browsers or elements; whether they are pruned on window close (`unload`, `domwindowclosed`, `TabClose`), are WeakMap/WeakRef, or not.
3. Window-scope code in `src/zen/**/*.mjs|*.js` that registers into process-lifetime registries without a matching removal on `unload`: `Services.obs.addObserver` (strong), `Services.prefs.addObserver` (strong unless weak=true), `CustomizableUI.addListener`, `PlacesUtils.observers.addListener`, `lazy.X.on(...)`/EventEmitter on a sys module, `Services.mm/ppmm addMessageListener`, `XPCOMUtils.defineLazyPreferenceGetter` with a callback (check what it holds), `Services.wm.addListener`, `Cc[...].getService` callbacks, `setInterval` without clear, JSWindowActor registration with per-window state stored in the parent module, `ChromeUtils.defineLazyGetter` on a shared object etc. A strong observer whose callback closes over `window`/`this` (a window global) and is never removed retains the whole window.
For every candidate give file:line, the holder, what is retained, the trigger (e.g. "open and close any window"), and whether removal exists. Verify each by reading both registration and teardown; mark what is inferred.

## Files
You own only `leak-evidence/window-retention.md` (new). Do not edit source under `src/`. Do not open PRs/issues/comments on any upstream repo. Commit the file early and update it as you go (commit evidence as you go so a crash doesn't lose it). Push your branch to origin if push works.

## Final report must contain
Ranked candidate list (confirmed by reading vs inferred), the coverage list of what was checked and fine, and your commit SHA.
