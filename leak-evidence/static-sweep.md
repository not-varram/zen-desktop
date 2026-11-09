# Static sweep of Zen chrome code for retention bugs

Scope: `src/zen/**` (excluding tests/vendor/emoji data) plus Zen-added hunks in
`src/browser/components/{tabbrowser,sessionstore}/**.patch`.
Base: `bd97c6bb0`. Everything below is read from source only. Nothing was run or
measured. Items marked *(inferred)* are reasoning, not observation. I did not
read issue #8932 or any other GitHub thread, so no comment citations are included.

**Headline.** The sweep found no clear per-tab, per-hover or per-pref-change
unbounded leak in the Zen JS. The Zen code mostly follows the pattern "listener
on `window`, bound once per window, closure over `this` only". Window-lifetime
singletons like that are not leaks. Every candidate below is small, bounded, or
conditional. If memory growth is real, it more likely lives in native or
content-side retention (docshells kept alive by the tab/browser objects listed
in items 1-3) or in something this static pass cannot see (e.g. Firefox's own
tab code, the motion library internals).

## Ranked candidates

Ranking = (bytes retained x trigger frequency x confidence). All are low-to-medium.

### 1. Closed-tab removal is gated on a motion `animate()` promise with no timeout *(inferred, medium-low confidence, potentially high impact)*
- Retain: `src/browser/components/tabbrowser/Tabbrowser-sys-mjs.patch:803-806` (patched `_removeTab`):
  ```js
  if (animate && !gReduceMotion && !(testingEnabled && !profilingEnabled)) {
    gZenVerticalTabsManager.animateItemClose(aTab, ...).then(() => {
      this._endRemoveTab(aTab);
    });
  } else { this._endRemoveTab(aTab); }
  ```
- Same shape for tab groups: `tabgroup-mjs.patch:~134` `animateItemClose(this).then(() => { ...; this.remove(); })`.
- `animateItemClose` (`src/zen/common/modules/ZenVerticalTabsManager.mjs:214-243`) returns
  `gZenUIManager.motion.animate(...)`. It has no timeout, no catch, and no fallback timer.
  It only short-circuits for `document.hidden`/`gReduceMotion`.
- Holder: the pending promise closure holds `aTab`. Until `_endRemoveTab` runs, the tab is `closing`
  but still has its `linkedBrowser` and docshell. `_endRemoveTab` is what destroys the browser.
- Retains: the whole content window/docshell of the closed tab *(inferred, this is the biggest-byte item in the sweep)*.
- Trigger: every animated tab close. It leaks only if the motion promise never settles
  (cancelled animation, throttled/occluded window, element detached mid-animation).
  I did not verify motion's cancel semantics, so treat this as a hypothesis to test dynamically.
- Contrast: Zen's other animation waits use `Promise.race` with a timeout
  (`ZenSpaceManager.mjs:2514-2518`, referencing issue 9334). This one has none.
- Suggested check: close tabs while the window is occluded/minimized and look for `closing` tabs that persist.

### 2. `gZenWorkspaces.lastSelectedWorkspaceTabs[uuid]` keeps a closed tab alive per space
- Retain: `src/zen/spaces/ZenSpaceManager.mjs:2635-2636` (set to the selected tab on every space switch),
  also `:2569`, `:3112`, `space-routing/ZenSpaceRoutingNavigation.sys.mjs:105`, `ZenSpaceRoutingManager.sys.mjs:422`.
  ```js
  this.lastSelectedWorkspaceTabs[oldWorkspaceId] =
    gZenGlanceManager.getTabOrGlanceParent(currentSelectedTab);
  ```
- Release: only (a) when the tab is moved to another workspace (`ZenSpaceManager.mjs:1863-1866`,
  `ZenFolders.mjs:720-722`), (b) when the workspace is deleted (`ZenSpaceManager.mjs:1564`), or
  (c) overwritten by the next switch away from that space. There is no `TabClose` handler.
- Holder: plain-object field on the `gZenWorkspaces` singleton, one slot per space.
- Retains: the `<tab>` element plus its `linkedBrowser` after close. If the browser is not
  destroyed (see item 1) it retains the content docshell. Otherwise it retains a detached DOM subtree.
- Bound: at most one tab per space. Trigger: per space switch, then close the tab in a non-active space or from the strip.
- Fix would be a `TabClose` listener or a WeakRef.

### 3. `nsZenFolder._activeTabs` / `activeTabs` holds tab objects with no `TabClose` pruning *(inferred)*
- Retain: `src/zen/folders/ZenFolder.mjs:76,224-226,245`; written at `ZenFolders.mjs:333,383,1775,2187-2192`.
- Release: `ZenFolders.mjs:2025` filters the tab out inside `animateUnload`, which is only called from
  `on_TabUngrouped`/`on_FolderUngrouped` (`:399,455`) and the pinned-tab unload path
  (`ZenPinnedTabManager.mjs:413`). `ZenFolders.mjs` registers no `TabClose` listener.
  Whether closing a tab inside a folder fires `TabUngrouped` before the early-return in `animateUnload`
  (`tabToUnload.hasAttribute("folder-active")`) is defined in Firefox's tabgroup code that is not in this repo.
- Holder: the folder element (a DOM element that lives as long as the space). Retains closed `<tab>` elements.
- Bound: number of active tabs per folder at close time. Trigger: closing an active tab in an expanded folder.
- Confidence low. Cheap to verify dynamically (`gBrowser.tabGroups[n].activeTabs` after closing).

### 4. Glance blob URL created across an `await` can orphan if the glance is gone *(narrow race)*
- `src/zen/glance/ZenGlanceManager.mjs:608-615`:
  ```js
  data.elementData = await this.#getElementPreviewData(data);   // creates URL.createObjectURL blob (:1218)
  this.#glances.get(this.#currentGlanceID).elementData = data.elementData;
  ```
  Release is `#deleteGlance` (`:1221-1230`, called at `:1431` and `:1798`).
- If the glance is closed while the await is pending, the blob URL is never revoked. If the entry is
  missing at `:615`, the code throws instead of cleaning up.
- Retains: one PNG blob of the hovered element. Trigger: a glance closed within ~100 ms of opening.
  Rare, tens of KB each. Already partly fixed by 7ed7b63b0 (the `#deleteGlance` path).
- `onUnload` (`:327-333`) clears `#glances` without revoking, which is fine at shutdown.

### 5. `ZenUIManager` `mousemove {once:true}` collapse listeners stack up while the mouse is outside the window
- `src/zen/common/modules/ZenUIManager.mjs:421-431`: each popup-hidden event with the mouse outside the window does
  `document.addEventListener("mousemove", collapse, {once:true})` with a fresh closure over `element`
  (a static toolbox element). Only the last closure is stored in `#removeHasPopupAttribute`, so the others cannot be removed.
- Similar pattern in `ZenCompactMode.mjs:863-912` (`document.addEventListener("mousemove", ..., {once:true})` per window `mouseleave`).
- Retains: closures over static chrome elements only (no tab/browser). They drain at the next `mousemove`. Negligible bytes; listed for completeness.

### 6. `nsHasPolyfill.observers` is append-only
- `src/zen/common/modules/ZenHasPolyfill.mjs:7,53-71`: `observeSelectorExistence` pushes `{observer, element}` and
  `disconnectObserver` disconnects without splicing, so entries are never released.
- Currently no caller outside the file itself (`grep observeSelectorExistence` returns only the definition;
  `ZenCompactMode.mjs` just references the global). Dead code today. It becomes a leak the moment it is called per element.

### 7. Misc bounded caches keyed by workspace / domain
- `ZenGradientGenerator.mjs:178,2461,2467,2501`: `#gradientsCache` is declared as a `Map` but used as a plain object.
  Entries are deleted by `invalidateGradientCache(uuid)` (`:2460`). Is it called on workspace removal? Not verified. One small object per space.
- `ZenBoostStyles.sys.mjs:19,30-48,157`: `#stylesCache` keyed by domain, deleted on update. Bounded by user-created boosts.
- `ZenLiveFoldersManager.sys.mjs:44,180,413`: `dismissedItems` Set of string ids, pruned per folder on `deleteFolder`. Strings only.
- `ZenUBActionsProvider.sys.mjs:141,417,557`: `#seenCommands` cleared per query.

## Already fixed / verified as the task described
- `ZenViewSplitter.mjs:80` `_tabToSplitNode` is a `WeakMap` (e3542b349).
- `_splitNodeToSplitters` (`:79`, a strong `Map` keyed by split node; nodes reference `node.tab`):
  entries added in `getSplitters` (`:1832`), deleted in `_removeNodeSplitters` (`:686`) and `removeSplitters` (`:1840 .clear()`).
  Splitters only exist for the currently active view, so a closed-tab node is dropped when the view is torn down.
  I could not find a path that leaves entries behind. If a group is removed while active, `removeGroup` (`:1156-1172`) calls
  `deactivateCurrentSplitView`, which I did not trace to `removeSplitters`. Worth a quick dynamic check. Bounded by node count.
- `_data` (`:75`) group entries are spliced in `removeGroup` (`:1171`) and `handleTabClose` (`:155-`).
  `_lastOpenedTab` is nulled on close (`:150`).
- `fakeBrowser` created at `:453`, removed and deleted at `:2132-2136`.
- 7ed7b63b0 already addressed Glance/Mods retention; e3542b349 the split node map.

## Checked and FINE (coverage list)
Listeners on `window`/`document`, bound once per window, closure over `this` only (not per-tab):
`ZenViewSplitter.mjs:113-135`, `ZenGlanceManager.mjs:55-64,220`, `ZenSpaceManager.mjs:162,619-626,666,952-962,1124,1309-1328,1488`,
`ZenFolders.mjs:225-245`, `ZenUIManager.mjs:58-61`, `ZenCompactMode.mjs:97-139,730,855-919,1069`, `ZenDragAndDrop.js:131-140,1141`
(`handle_windowDragEnter` is a stable bound ref, so repeated adds dedupe), `ZenMediaController.sys.mjs:496-516`,
`ZenVerticalTabsManager.mjs:34-100`, `ZenSiteDataPanel.sys.mjs:77-110`.
Observers with paired `removeObserver` on `unload`:
`ZenSpaceManager.mjs:177-201`, `ZenGlanceManager.mjs:219-220` (+`onUnload` `:316`), `zenThemeModifier.js:62-95`
(capture flag matches), `ZenMods.mjs:535-548`, `ZenGradientGenerator.mjs:2232-2243`, `ZenSiteDataPanel.sys.mjs:102-117`,
`ZenDownloadAnimation.mjs:34` (`removeView`).
Process-lifetime singletons: `ZenUBGlobalActions.sys.mjs:346-348` (`labels` Map is keyed by l10n id, cleared on locale change),
`ZenWindowSync.sys.mjs` observers (init/uninit paired, `#lastFocusedWindow` is a WeakRef, `#inflightSwapTabs` add/delete in `finally`,
`#swapedTabsEntriesForWC` is a WeakMap), `ZenLiveFoldersManager` (`uninit` removes the observer and sync handler and clears maps).
ZenUIComponent subclasses (`ZenMediaController`, `ZenProgressBar`): listeners go through `addEventListener` and are removed on `unload`.
Per-tab listener: `ZenPinnedTabManager.mjs:150-158` adds and removes `tab._zenClickEventListener` (same reference, shared bound fn).
`_onAccelKeyChange` (`:182-196`) re-arms a `{once:true}` window listener only while `_tabWithResetPinButtonHovered` is set.
It closes over `this` only.
Media cards: `ZenMediaController.sys.mjs` `teardown()` (`:422-441`) removes controller listeners and clears the interval and timeout;
`onTabDiscardedOrClosed` (`:633-641`) destroys by `browserId`; `#cards.delete` in `onCardDestroyed`.
Observers with proper disconnect: `ZenSpace.mjs:441-461` (IntersectionObserver + AbortController in `disconnectedCallback`),
`ZenKeyboardShortcuts.sys.mjs:342-352`, Library sections (`disconnect` in teardown).
`ZenSpaceManager.mjs:102,387` ResizeObserver observes only the essentials container (static).
`MutationObserver` in `tabgroup-mjs.patch:~134` is per group and observes a child of the group, so it dies with the group.
Timers: no `setInterval` outside `ZenMediaController.sys.mjs:273` (cleared in `teardown`). Live folder refresh uses `DeferredTask`
with `stop()` on delete/uninit/wake. Toast timeouts (`ZenToasts.mjs:12`) are deleted on fire and on hover. No per-tab rAF loops found.
`ZenZapDissolve` rAF is cancelled in cleanup (`:585-588,621`). `ZenZapOverlayChild` pool is capped at 5.
Per-tab expandos (`_zenContentsVisible`, `_zenPinnedInitialState`, `_zenChangeLabelFlag`, `zenStaticLabel/Icon`) die with the tab.
`browser._zenShareOverlay` (`ZenShareManager.mjs:374-377,525`) is removed on navigate/close.
Boost editor progress listeners are removed on editor `unload` (`ZenBoostsManager.sys.mjs:679-720`).
Drag and drop: drag-image wrapper is removed and deleted on drag end (`ZenDragAndDrop.js:1514-1525`).
Session data: `restoreInitialTabData` (`ZenSessionStore.mjs`) sets attributes only. No `gZen*` per-tab maps found beyond items 2-3.
Zen-patched SessionStore hunks add no caches (`SessionStore-sys-mjs.patch`: only pass-through `storeDataForSessionStore`).
Tabbrowser patch: `#tabListeners`/`#tabFilters`/`#closeTime*TimerIds` are upstream tab-keyed statics.
I did not verify that they are WeakMaps, and the patch only adds a `zenSetTabProgressListener` setter.

## Not covered
`src/zen/library/**` (only the grep-level listener/observer check; the Library is opened on demand and has `unload` handling),
`src/zen/welcome`, `src/zen/about`, `src/zen/boosts` editor UI and `src/zen/migration`.
Firefox-side (non-Zen) code and C++ were out of scope. The motion library's cancel behaviour (item 1) is unverified.
