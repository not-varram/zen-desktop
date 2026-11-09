# Does motion v13 leave `animate()` promises unsettled? (tab-close retention)

Vendored file: `src/zen/vendor/motion.min.mjs`, **motion v13.2.0** (`motion.dep`). Line numbers below are into a prettier-formatted copy
(`npx prettier --parser babel motion.min.mjs`, 7808 lines); the minified file is a handful of lines, so function names are the minified
identifiers (`Bl`=`animate`, `Mn`=controls, `Pn`=value animation wrapper, `fn`/`vn`=WAAPI animation, `ke`=JS-driven animation, `Pe`=base).
Harness: `harness.cjs` (jsdom + the real bundle), output in `harness-output.txt`. Run: `npm i && node harness.cjs`.

## 1. When does the promise settle? (code)

`animate(el, kf, opts)` = `Bl()` (l.6419) -> `Dl` -> `yi` (l.2380) starts one `MotionValue` animation per CSS property and returns
`new Mn(animations)` (l.6440). The thenable's settle point is:

```js
class Mn extends En { then(t,e){ return this.finished.finally(t).then(()=>{}) } }   // l.1998
class En { get finished(){ return Promise.all(this.animations.map(t=>t.finished)) } } // l.1944
class Pe { updateFinished(){ this._finished = new Promise(t=>{this.resolve=t}) }
           notifyFinished(){ this.resolve() } }                                       // l.1006-1017
```

`Pe` promises have **only a resolve side: nothing ever calls `reject`**, and `resolve` is called only from `notifyFinished()`:

| Path | Only caller of `notifyFinished()` |
|---|---|
| WAAPI (`fn`, opacity/transform, l.1582) | `animation.onfinish = () => { ...; l?.(); this.notifyFinished() }` |
| JS/rAF (`ke`, e.g. `marginBottom`, l.1213) | `finish(){ this.notifyFinished(); this.teardown(); ... }`, reached only from `tick()` when `S` (time >= duration) |
| `Pn` wrapper (l.1871) | `g.finished.then(()=>this.notifyFinished())` (inner promise) |

Every cancelling operation skips these:

```js
// fn (WAAPI)  l.1604, 1610
cancel(){ try{ this.animation.cancel() }catch(t){} }                 // no notifyFinished
stop(){ if(this.isStopped)return; this.isStopped=!0; ... this.cancel() }  // no notifyFinished
// ke (JS)     l.1030, 1226
this.stop = () => { ...tick(now)...; this.isStopped=!0; "idle"!==this.state && (this.teardown(), this.options.onStop?.()) }
cancel(){ this.holdTime=null; this.startTime=0; this.tick(0); this.teardown(); this.options.onCancel?.() }
// Mn/En   l.1995  cancel(){ this.runAll("cancel") }   stop = () => runAll("stop")
```

A WAAPI `cancel()` fires the DOM `cancel` event, never `finish`, and motion registers no `oncancel` handler (grep: none), so a cancelled
animation never resolves. `ke.stop()` only calls `tick(now)` first: if that tick happens to cross the end time it `finish()`es (resolves);
otherwise it tears down silently.

**Superseding** (second `animate()` on same element+property): `yi` -> `i.start(Xn(...))`; `MotionValue.start` (l.2118) begins with
`this.stop()` -> `animation.stop()` -> the old animation is stopped (`stop` row above), so **the first controls' promise stays pending
forever** (the second one resolves normally). The mini path does the same: `Ll` (l.6503) `c && c.stop()` on the existing animation for the key.

Settle table (verified by `harness.cjs`, the real bundle in jsdom with a fake WAAPI whose `cancel()` fires no `finish`, like the spec):

| Scenario | Result | Evidence |
|---|---|---|
| WAAPI anim runs to `finish` | resolves | harness |
| `ctrl.stop()` | **pending forever** | harness |
| `ctrl.cancel()` | **pending forever** | harness |
| underlying `Animation.cancel()` (external / style reset) | **pending forever** | harness |
| 2nd `animate()` same element+prop supersedes 1st | **1st pending forever**, 2nd resolves | harness (WAAPI props and JS-path `marginBottom`) |
| JS-path (`marginBottom`) `stop()` / `cancel()` | **pending forever** | harness |
| `animate(0,100,..)` value `stop()`/`cancel()` | **pending forever** | harness |
| `complete()` | resolves | harness |
| from == to / already at target | resolves (instant path, `W.update(()=>{onUpdate;onComplete})`, l.2268) | harness |
| rAF not firing (hidden/occluded/throttled), JS-path prop | pending while frozen, **resolves when frames resume** (delayed, not lost) | harness |
| WAAPI props while window not ticking | not testable in jsdom; Gecko defers `finish` to the refresh driver; expected delayed, not lost | inferred |
| element removed from DOM mid-animation | jsdom fake cannot model this. Per WAAPI spec a script animation on a disconnected element keeps running and still finishes; motion does not listen for removal either | inferred |
| promise rejection | cannot happen from `Pe`; and `Mn.then` uses `finally(t)` so the callback runs even on reject (it drops the `onRejected` arg) | read from code |
| `document.hidden` at start | Zen short-circuits with `Promise.resolve()` (`animateItemClose`) | read from Zen code |

Note `Mn.finished` is `Promise.all` over *every* property animation, so **one** stopped property (opacity, transform or marginBottom) keeps
the whole `animate()` pending.

## 2. Call sites where release/cleanup is gated on a motion promise

(`.then`/`await` after `gZenUIManager.motion.animate` or `animateItemClose`; "fallback" = timeout/catch that still runs the cleanup)

| Site | Gated cleanup | Releases tab/browser/DOM? | Fallback |
|---|---|---|---|
| `src/browser/components/tabbrowser/Tabbrowser-sys-mjs.patch:804-806` `_removeTab` | `this._endRemoveTab(aTab)` (destroys linkedBrowser/docshell, removes tab) | **YES, the tab + content docshell** | **none** (no timeout, no catch) |
| `src/browser/components/tabbrowser/content/tabgroup-mjs.patch:118-123` | `TabGroupRemovedFromDOM` event + `this.remove()` | group element only (observer fires when group has no tabs, so no browser) | none |
| `src/zen/common/modules/ZenToasts.mjs:48-58` | `toast.remove()` | toast DOM | none (also `#scheduleHide` timer) |
| `src/zen/common/modules/ZenStartup.mjs:147-162` | removes inline `opacity` | style only | none |
| `src/zen/spaces/ZenSpaceCreation.mjs:432-446` | removes inline `opacity` | style only | none |
| `src/zen/compact-mode/ZenCompactMode.mjs:471-505, 520+` | style cleanup + `resolve()` of the surrounding promise | a stuck `resolve()` blocks whoever awaits the sidebar hide/show | none |
| `src/zen/split-view/ZenViewSplitter.mjs:516-530, 616-626` | `docShellIsActive=false`, `_canDrop=true`, `_maybeRemoveFakeBrowser()` | fake browser DOM; docShell active flag of dragged tab | none |
| `src/zen/split-view/ZenViewSplitter.mjs:2339-2353` `animateBrowserDrop` | caller-supplied callback | depends on callback | none |
| `src/zen/media/ZenMediaController.sys.mjs:760+` | hides media bar / `#revealBar()` | DOM visibility | none |
| `src/zen/live-folders/ZenLiveFoldersManager.sys.mjs:321-334` | style/attr cleanup | style | none |
| `src/zen/spaces/ZenSpace.mjs:590-606` | `button.hidden = true` | DOM visibility | none |
| `src/zen/urlbar/ZenUrlbarController.mjs:315-319` | `#animatingSearchMode = false` | flag; stuck flag blocks later animations | none |
| `src/zen/downloads/ZenDownloadAnimation.mjs:260,410,423,473,484` (`await`) | removes animation elements after await | transient DOM | none |
| `src/zen/spaces/ZenSpaceManager.mjs:2518-2522` | `await Promise.race([Promise.all(animations), timeout])` | space switch state | **YES, timeout** (added for issue #9334 because the promise got stuck) |
| `src/zen/common/modules/ZenVerticalTabsManager.mjs:187-200` `_startItemOpenAnimation` | `.finally(...)` removes inline margin/opacity | style | uses `.catch`/`.finally` (finally also never fires if pending) |
| `src/zen/library/sections/ZenLibrarySpacesSection.mjs:654` | calls `animateItemClose(tab)` and discards it, then `removeTab({animate:true})` (calls it again) | no gating (see below) | n/a |

Only the first row retains something heavy. `ZenFolders.mjs` uses its own `Element.animate` (not motion), and the one place that already hit a stuck motion promise
(`ZenSpaceManager`, issue 9334) was patched with a timeout race, which shows the problem class is real in Zen, but nobody patched the tab close path.

## 3. Verdict

* **Verified (harness + code):** an `animate()` promise from motion 13.2.0 is settled only by natural completion (WAAPI `finish`, or JS tick past duration)
  or `complete()`. `stop()`, `cancel()`, an external WAAPI cancel, or a **second `animate()` on the same element+property** leave the *first* promise
  pending forever. No `oncancel`, no reject, no timeout in the library.
* **Verified (code):** `_removeTab` calls `_endRemoveTab(aTab)` only inside that `.then`, with no timeout/catch.
  `_endRemoveTab` is what destroys the browser and docshell, so a never-settling promise means a closed tab keeps its `linkedBrowser`/content docshell
  (tab is already `closing`, maybe invisible), retained by the unresolved promise's closure and by the DOM element.
* **Reachability in real Zen (inferred, not reproduced in Firefox):**
  * Another motion `animate()` on the closing tab element touching `opacity`/`transform`/`marginBottom` during the 100 ms window. The only in-tree animator of tab items is
    `animateItemOpen` (opening) and `animateItemClose` itself. A close right after an open (<120 ms) supersedes the *open* promise, which is harmless. A repeated
    close on the same tab is blocked by `aTab.closing`. The library section's double call (`ZenLibrarySpacesSection.mjs:654` then `removeTab`) supersedes the *first* (discarded) promise, and the one
    `_removeTab` waits on survives. So I found **no in-tree path that supersedes the promise `_removeTab` waits on**.
  * Frozen frames after the guard: `document.hidden` is checked only at the start. If the window becomes occluded/minimised during the 100 ms, rAF-driven props
    (`marginBottom` for any non-last tab) wait until frames resume (harness: resolves on resume). A permanent leak needs the window to be destroyed while hidden, in
    which case teardown frees the docshells anyway. So this is a delay, not a leak.
  * Something else cancelling the WAAPI animation or the element disappearing mid-animation: nothing in Zen does `getAnimations().forEach(cancel)` on tabs
    (not exhaustively checked in Firefox's own code).
* **Conclusion:** the pending-forever semantics are real (high confidence, verified), and the `_removeTab` gating without a timeout is real (verified), but I could **not
  identify a concrete trigger** in current Zen that supersedes/cancels the specific close animation. Confidence that this explains the #8932 leaks: **low-to-medium (~20%)**.
  It is a latent fragility (any future or extension-driven `animate()`/`getAnimations().cancel()` on a closing tab, or a motion bug, silently leaks a whole docshell).
  Cheap robust fix (not applied, out of scope): race the promise with `setTimeout(~250ms)` or use `.finally`-with-timeout before `_endRemoveTab`, as already done
  for `ZenSpaceManager` (#9334). A runtime check in Firefox (about:memory / `gBrowser.tabs` still containing `closing` tabs after a close with the animation interrupted) is the missing verification.
