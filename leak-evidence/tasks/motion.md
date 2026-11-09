# Task: Does Zen's vendored motion v13 leave animate() promises unsettled (tab-close retention)?

## Hard rule (verbatim from the user)
Hard rule, because it has crashed every session on this account twice tonight: never run `apt-get install`, `dpkg -i` or `systemd-tmpfiles`, and never change the ownership or mode of /root or anything under it. A systemd postinst re-owns the account's shared /root and kills all sessions; run-v27ssb3txh is fixing that in Aether. Put this rule word for word in every sub-session's and subagent's brief. If you truly need system packages, stop and tell Varsh which ones and why.

## Context
Meta issue zen-browser/desktop#8932 tracks memory leaks. Evidence so far is in `leak-evidence/` (read `leak-evidence/static-sweep.md` item 1). Hypothesis: the patched `_removeTab` in `src/browser/components/tabbrowser/Tabbrowser-sys-mjs.patch` (search `animateItemClose`) only calls `this._endRemoveTab(aTab)` inside `.then()` of `gZenVerticalTabsManager.animateItemClose(...)` (`src/zen/common/modules/ZenVerticalTabsManager.mjs`), which returns `gZenUIManager.motion.animate(...)` (vendored `src/zen/vendor/motion.min.mjs`, v13; wired in `src/zen/common/modules/ZenUIManager.mjs`). If that promise never resolves (animation cancelled, element removed mid-animation, window occluded/hidden so no frames, animation interrupted by another animate() on the same element/property, rejection), the tab's browser/docshell is never destroyed. Same shape in `src/browser/components/tabbrowser/content/tabgroup-mjs.patch` and any other `motion.animate(...).then(() => cleanup)` call site in src/zen.

## Goal
1. From the motion v13 source (the minified vendor file; the unminified motion/framer-motion v13 source on npm/GitHub may help, read-only web is fine), determine exactly when the `animate()` controls' `.then`/`finished` promise resolves, rejects, or stays pending: on `stop()`, `cancel()`, on a second animate() of the same element+property, when the element is removed from the DOM, when `document.hidden` / no rAF, when the WAAPI animation `oncancel` fires, when the value is already at the target. Quote the relevant code (with line/offset references into motion.min.mjs).
2. If node is available (`node --version`), try to exercise the logic: e.g. a tiny harness with a fake/minimal DOM or with motion's JS-animation path (`animate(object, ...)` / `animate(value)`), showing whether cancel/stop leaves the promise pending. Commit the harness under `leak-evidence/motion/`. Do not install system packages. npm packages into a local dir under the repo are OK only if network works; do not commit node_modules.
3. List every call site in `src/zen/**` and `src/**/*.patch` where cleanup that releases tabs/browsers/DOM (`_endRemoveTab`, `.remove()`, `removeTab`, deleting from maps) happens only after a motion promise settles, with file:line, and whether a timeout/catch fallback exists.
4. Conclude: is a never-settling promise possible in real Zen use, and does it retain closed tabs (browser + content docshell) or windows? Confidence level, and what is verified vs inferred.

## Files
You own only `leak-evidence/motion/**` (new). Do not edit any source under `src/`. Do not open PRs/issues/comments on any upstream repo. Commit your notes as `leak-evidence/motion/README.md` early and often (commit evidence as you go). Push your branch to origin if push works.

## Final report must contain
The settle/pending table with code quotes, the call-site list, the harness result (or why it could not run), verdict + confidence, and your commit SHAs.
