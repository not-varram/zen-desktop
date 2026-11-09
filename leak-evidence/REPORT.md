# Memory leaks tracked in zen-browser/desktop#8932: findings (2026-11-09)

Branch `aether/run-find-and-fix-the-memory-leak-s-t-wc37286tt8` on not-varram/zen-desktop, base = upstream `dev`
bd97c6bb0 (2026-11-08, checked equal to upstream dev head). Nothing was sent upstream.

Sources: `meta/comments.md` (body + 198 comments, every report with version, OS, trigger, attachments, triage
reply), `meta/memreports.md` (78 about:memory files parsed by `meta/analyze_memreports.py`), `linked-issues.md`
(39 linked + 12 one-hop issues), `static-sweep.md`, `window-retention.md`, `motion/README.md`, `causes/`,
`verification.md`.

## 1. What the reports say

- Distinct reports with data: 38 rows in `meta/comments.md` section A (Zen 1.12.10b .. 1.23.4b; macOS, Windows,
  Linux incl. Flatpak). Me-too reports without data: section B.
- **In 71 of 77 reports with a Main Process, the Main Process is normal** (median 253 MB explicit). The growth is
  in content processes (YouTube, ChatGPT/Mapbox, AWS, GitHub, AliExpress), the GPU process, extension processes,
  or DevTools. Triage replies in the thread attribute those to upstream Firefox bugs (1956680, 2079806 fixed in FF
  159, 2076013, 1931717, 2027413), to extensions (tab-array, vidIQ, "buykers", Allow CORS, Bitwarden?), to
  hardware acceleration, or to themes with `will-change: transform`. None of that is Zen code.
- Zen-owned paths that dominate the Main Process when it is abnormal:
  1. `explicit/window-objects/top(chrome://browser/content/browser.xhtml, id=1)/active/window(browser.xhtml)/dom/orphan-nodes`:
     8,457 MB (6060921916, XeynQ4) and 2,809 MB (6063114915, mennatawfiq), both **1.23.1b**, "open the browser and
     wait 10 minutes", gone after a downgrade to 1.23b. No other report exceeds 7 MB there.
  2. `explicit/window-objects/top(none)/detached/window(chrome://browser/content/browser.xhtml)`: closed browser
     windows still alive, in **26 of 77** reports, 2..14 entries, ~5 MB each, max 289 MB (6586890805, 1.23.4b),
     seen from 1.12.10b to 1.23.4b.
  3. Ghost `about:preferences#zenMarketplace` (20.7 MB, 4495005360, 1.19.13b), one report.
  No realm, window or memory path names a Zen module (motion, workspaces, glance, split view, boosts, gradients). All Zen
  window code shares the window's realm, so a report cannot point at a module.

## 2. Ranked causes

| # | Cause | Reports explained | Confidence | Status |
|---|---|---|---|---|
| 1 | Library built at startup and never torn down: browser.xhtml orphan nodes, 1.23.1b (#15823) | 2 posted (the only multi-GB Zen-attributable Main leaks) + #15823 | high (path, version window, downgrade fix, maintainer linked it) | **already fixed upstream**: 3d7777adc (gh-15826), in 1.23.2b and in base. No change made |
| 2 | Library download stack never removed its `DownloadList` view on window close, so every closed window stayed alive, 1.23b..1.23.1b | detached windows in 1.23b reports (5981075145: 2 detached) | high by reading: `addView` -> `DownloadList._views` is a strong `Set` (Firefox `DownloadList.sys.mjs`), the stack holds `#window`, and CustomizableUI `onDestroyed` does not run on window close | **already fixed upstream**: same 3d7777adc added an `unload` -> `destroy()`. No change made |
| 3 | **Cause A**: `<zen-library>` hidden-tabs pref observer is strong and removed only in `disconnectedCallback`, so every closed window stays alive, 1.24b+ | **0 posted** (it shipped after the last report, 1.23.4b); same symptom as pattern 2 for anyone on 1.24b/1.24.1b | high by reading (`causes/A-library-pref-observer.md`); runtime **not** verified | **fixed here**: 28be25f20 (+ test d55c862ca) |
| 4 | Late registrations: ZenMods / ZenCompactMode / ZenStartup add strong observers after awaits; a window closed before they run keeps them forever | could add 1 detached window per window closed during startup/restore; cannot explain 14 | low-medium (code verified; Gecko still runs promise callbacks for a closed chrome window, verified in source; timing inferred) | not fixed (not confirmed) |
| 5 | Tab close waits on a motion promise with no timeout (`_removeTab` -> `animateItemClose().then(_endRemoveTab)`); motion 13.2.0 never settles a stopped/cancelled/superseded animation | none identified; no in-tree trigger found | ~20% (settle semantics harness-verified; trigger not found) | not fixed (latent) |
| - | Detached browser.xhtml windows in 1.12..1.22 and in 1.23.2b..1.23.4b | 24 of the 26 detached-window reports | **unexplained** | open |

Earlier Zen leaks fixed upstream and mentioned in the thread or in git: folder-icon refresh tick every frame
(f77db8cb2, 1.15.x, #57 in the thread), split-view node map (e3542b349), glance blob URLs (7ed7b63b0).

## 3. Commits on this branch (source changes)

- `28be25f20` Remove the library's hidden-tabs pref observer on window unload (cause A).
- `d55c862ca` Add a test that a closed window is not kept alive by the library (never run, see below).
- All other commits only add files under `leak-evidence/`.

## 4. Verified vs inferred

See `verification.md`. Short version: no build, no run, no about:memory in this container (no engine checkout,
Zen's GTK/X11 runtime libraries are missing, installing system packages is forbidden here). Everything about cause A
is verified **by reading both sides** (Zen code + Firefox C++), not at runtime. Prettier and `node --check` pass;
ESLint and mochitests cannot run.

## 5. Not covered by the fixes

- All content-process, GPU, extension, DevTools and upstream-Firefox reports (71/77 Main-normal reports).
- Detached browser.xhtml windows before 1.23b and in 1.23.2b..1.23.4b (24 reports): no confirmed Zen cause.
  Candidates 4-5 above, extensions (many of those profiles have tab-manager/session add-ons), and Firefox itself.
  The cheapest next step is a runtime check: open/close windows on 1.23.4b in a clean profile, GC/CC, Measure.
- The zenMarketplace ghost page (one report, 1.19.13b).
- Freezes/OOM reports without data (section B of `meta/comments.md`).
