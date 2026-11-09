# Issues linked from / cross-referencing meta #8932 (zen-browser/desktop)

Method: `gh api repos/zen-browser/desktop/issues/8932/timeline --paginate` (re-run 2026-11-08: same 35 cross-references as the brief, no new ones), then `gh issue view N --json ...` for each (read-only; scripts `fetch.sh`, `digest.py`, `closers.sh`, `memsum.py` in this dir; raw JSON is gitignored, re-fetch with `fetch.sh`). Comment ids are `cN` = 0-based index in `.comments` of `raw/N.json`. Anything marked *(inferred)* is my inference, not a quoted fact.
Fix pointers come from `git log --all` in this repo (HEAD bd97c6bb0) and the timeline API's `closed` / `referenced` events.

- 1058 and 1244 (named in #8932 comment bodies) do **not** resolve as issues/PRs in zen-browser/desktop (`GraphQL: Could not resolve ... 1058`); skipped.
- One-hop extras fetched: 15616, 11851, 6302, 4450, 2777, 13556, 5447, 7197, 5500, 7784, 5734/5588/5840/2206 (titles only), 14079.
- Closers: most "closed" states are triage actions by `mr-cheffy` ("move to #8932") or `dosubot[bot]` stale-closes, **not** fixes. Only the issues in the "Fixed" list below have a real code change.
- The `about:support` dumps were stripped by `digest.py`; version/OS lines are quoted per issue where present.

## Per-issue sections

### #504 Too much RAM Consumption — CLOSED/COMPLETED (2024-10-21, mr-cheffy; no fix)
- Reporter subhashhhhhh, Zen 1.0.0-a.28, macOS aarch64 (8 GB M1 Air): ~3 GB. 82 comments 2024-08 → 2026-06.
- Maintainer cause statements: mr-cheffy c37/c41 (2024-10-21) "some containers are known for doing memory leaks ... I meant extensions/addons ... I can't do much about it" (i.e. blamed Multi-Account Containers / add-ons; kahveciderin c35 raised it). Mil0dV c45: GPU mem is probably WebRender; "outside Zen's control".
- Evidence in thread: c15 lee-orr (2024-08-30) Main Process explicit 24,112 MB, 96.8% `js-non-window/zones` strings, one string `length=333802, copies=22926 "First Name,Last Name,..."` (a CSV tab; c17 says investigating, no follow-up). c11 niutech: WebExtensions process vsize 440 GB in thrzl's report. c18/c22/c21: YouTube/pinned tab/sidebar panels (Messenger ~300 MB) never unloaded; Auto Tab Discard helps. c32 chenasraf profile https://share.firefox.dev/4ertH72 (not fetchable offline). c34: `browser.cache.memory.enable=false` did nothing. c48 thrzl: Fastfox/Betterfox prefs "work great" (c56 niutech links them). c75: disabling GPU acceleration reduces mem. c74: Wappalyzer.
- about:memory attachments downloaded (`mem/504*.summary.txt`):
  - 504a (thrzl, 2024-08-28, 14 procs): Main Process explicit 332 MB: top `cert-storage/storage` 51.9, `startup-cache/data` 20, cld-worker.js translation worker 16, `window-objects/.../active/.../element-nodes` 15.7, **`ghost` window element-nodes 14.1 MB (2 ghost entries)**, 106 "detached" report entries (entries, not windows). Nothing leaky in parent; WebExtensions process dominated vsize.
  - 504b (everyoneexe, 2025-11-24, 9 tabs/5.5 GB, 22 procs): `webIsolated=youtube.com` 614 MB (`media/resources` 181 MB, 36 detached entries); Main 352 MB (about:memory page itself 50 MB element-nodes); extension process 348 MB. 0 ghost windows.
  - 504c (same user "after-disable" extension): Main 592 MB of which **`gfx/webrender/swgl` 149 MB** (software WebRender); youtube 551 MB (57 detached entries); chatgpt.com 333 MB. 0 ghost.
- Zen 1.0.1-a.12 fresh start ~600 MB with GPU process the biggest (niutech c44/c47); Firefox 131 less. Later c77 (Nov 2025): CleanMyMac 12 GB vs about:processes 5 GB for ~20 tabs (macOS footprint vs resident discrepancy). c79 (2026-06): "single RTC stream +400 MB/min".
- Pointers to Zen code: none. Prefs mentioned: `browser.cache.memory.enable`, Betterfox Fastfox set, GPU acceleration toggle.

### #3299 Memory Leaks in 1.0.1-a.22 ... — CLOSED/NOT_PLANNED (2025-02-19 by dosubot stale; no fix)
- Windows, 1.0.1-a.22 (48 GB RAM fills within an hour; regression vs a.19). c5 myamusashi: "solved in new beta" (1.0.2-b.x). c7 niutech: 1.7.6b startup 490 MB vs Firefox 135 380 MB. c10 eliliam (2025-04-25) Arch 1.11.5b htop 25 GB vs about:processes small (RSS/shared mismatch). No profiles, no repro. Cause: none stated.

### #7240 INSANE MEMORY LEAK ... — CLOSED/COMPLETED same day (2025-04-03, no content)
- Template-only angry issue listing #5447 #4450 #3299 #2777 #504 #7197; not actionable. c1 niutech later points to #8932.

### #8081 Zen has become unberably laggy — CLOSED/COMPLETED 2025-06-21 (mr-cheffy, redirect to #8932)
- 1.12.1b, Linux Flatpak (Fedora kernel 6.14.4). `data.json` about:support: Version 1.12.1b, Firefox 138 UA, add-ons: uBlock, TWP, enhanced-h264ify, Dark theme, animated cat theme.
- Cause found by reporter c4: **removing the workspace colour completely fixes the lag** (incognito has no colour). c5: not laggy in 1.12.5b. macOS user c6 says persists. UI-gradient render cost, not a leak. Pointer *(inferred)*: Zen space gradient/colour rendering, `src/zen/spaces/ZenGradientGenerator.mjs` (the recent HEAD commit bd97c6bb0 reduces its allocations).

### #8157 Zen RAM Consumption is too much — CLOSED/COMPLETED 2025-06-20 (mr-cheffy redirect)
- macOS aarch64; Zen 7.83 GB vs Chrome 3.3 GB with >10 tabs. Key maintainer-side statement: Propheticus c3 (2025-06-08, community mod) "Zen's buffering and caching preferences have been tweaked from the Firefox defaults ... more memory allowed ... the dev is looking at these settings again. Especially the (shared) GPU memory". c5 abb4-r053: 13-15 GB peak vs normal 2.5-3 GB.

### #8428 Zen laggy and consumes excessive energy — CLOSED/COMPLETED 2025-06-21 (redirect)
- macOS 15.5 M1 Air 8 GB, high CPU 50%+, even in private mode. No version. Not a leak (CPU/energy).

### #8742 Zen suddenly eats all available memory [Windows 11] — CLOSED/NOT_PLANNED 2025-08-07 (dosubot stale)
- Win 11, 1.12.6b (~1.5 GB → fills 64 GB; started 2025-04-26, random, no pattern; not in Firefox). c3 ElRaphik: regression between **1.12.8b (<1 GB for 100 tabs) and 1.12.10b (6 GB for ~20 tabs)**. c6 Propheticus (2025-06-28): "Quite a few changes in Zen's buffering/caching settings were made. Try 1.13.2b"; c7 ElRaphik: "somewhat better ... ~100 MB/tab". c0/c1/c5: YouTube/streaming sites keep growing (flatpak Mint too). c2: "Minimize memory usage" as workaround.
- Overlaps in time with the unloader replacement (see #8822, shipped 1.12.9b) *(inferred correlation)*.

### #8822 Tab auto unload not working with recent changes — CLOSED/NOT_PLANNED (first closed 2025-06-04 by Propheticus; marked duplicate 2026-01-14; final close by dosubot stale 2026-05-21)
- 1.12.10b, Windows (also Linux Arch/Ubuntu/Debian, macOS 14.5). 83 comments, "second most commented open issue" (c54).
- Cause (Propheticus c4, 2025-06-04): "Zen has changed to the Firefox native tab unloader in v1.12.9b". Behaviour: unloads only when memory is low and there is demand, LRU, `browser.tabs.min_inactive_duration_before_unload` (default 10 min), no fade unless `browser.tabs.fadeOutUnloadedTabs=true`; `about:unloads` shows candidates. mr-cheffy c16 "not enabled on linux" (Firefox's `browser.tabs.unloadOnLowMemory` is false on Linux, Propheticus c25); c20 "It is based on time, 60 minutes" (disputed c22). Linux workaround (c26): `browser.low_commit_space_threshold_percent=100`, `min_inactive_duration_before_unload=300000`, `unloadOnLowMemory=true`; Bugzilla 1780058 (mr-cheffy c27). Propheticus c14 asks whether Zen's copy of the memory-pressure detector is wired; c32 proposes UI options. Dev's stance relayed by users c52/c55 on Discord: not convinced unloading is a core feature; mr-cheffy never commented publicly in thread.
- Repo evidence: `ebfc88574` (2025-05-23) "feat: Replace zen's tab unloader with firefox's one. Also added more tests" removed the timer unloader. A dead pref registration remains: `src/browser/components/preferences/zen-settings.js:778` `zen.tab-unloader.timeout-minutes` (default 10) — no consumer found by grep *(inferred vestigial)*. `prefs/firefox/browser.yaml` sets `browser.sessionstore.restore_pinned_tabs_on_demand: true`, `browser.tabs.unloadTabInContextMenu`, `browser.tabs.fadeOutExplicitlyUnloadedTabs`. Side effect c47/c49: unloading one tab of a split view breaks the split.
- Classification: missing feature/regression → higher steady RAM, not a code leak.

### #8925 High CPU usage on Windows — CLOSED/DUPLICATE 2025-06-08 (of #8932)
- 1.12.10b Win11, Ryzen 7; after closing all tabs and waiting minutes, Zen eats 100% CPU (reddit thread linked). Not repro-ed. No fix.

### #8928 High CPU usage on MacOS — CLOSED/DUPLICATE 2025-06-08
- 1.12.10b macOS aarch64 M3; React dev server testing → CPU high, overheats. Propheticus c0 asks for troubleshoot mode + process monitor. No data.

### #9649 Memory leak in browser on MacOS 26 — CLOSED/COMPLETED 2026-08-16 (mr-cheffy, via PR #14978)
- 1.14.7b, macOS 26, Mac Studio M4 Max. **Repro: start Discord screen-share (window share, not full-screen) → Zen RAM climbs 500 MB → 90+ GB (96 GB seen); no leak in Firefox/Chrome (NepsyNep c4)**. Others: also macOS screen capture/Teams (c16), unrelated to sharing 16-105 GB on M4 (c19/c20/c21), Intel i9 (c15), Linux/Teams (c18), 500 GB virtual (c17).
- Attachment `mem/9649.summary.txt` (23 procs): Main Process explicit only **180 MB** (script-preloader 12.8, sqlite 11.4, startup-cache 10.6, `storage/prefix-set/goog-phish-proto` 9.1); WebExtensions 300 MB (89 MB single JS class); Isolated Web Content 248 MB (`media/resources` 43 MB). 0 ghost windows. Propheticus c3: Activity Monitor attributes the huge **physical footprint to the main process while resident-unique is 270 MB → memory reserved/not released outside the JS/Gecko heap**, "prime example of a leak".
- Maintainer line: Propheticus c22 (2026-01-05): "fixed in Firefox 3 years ago by changing the way they compile for Mac" (bug 1794647); mr-cheffy c23 posts Mozilla's nightly mozconfig and bug 1788837.
- **Fix history (this repo)**: `beb4f94fd` 2026-01-05 "Change compile flags for macos to fix potential memory leaks, b=bug #9649" — `configs/macos/mozconfig` (dropped global `CFLAGS/CPPFLAGS/CXXFLAGS/LDFLAGS/RUSTFLAGS` `-O3 -march=...`; aarch64 now `-O3 -mcpu=apple-m1` appended to `$CFLAGS`; `--enable-linker=ld64`), `configs/windows/mozconfig` (`$LDFLAGS`/`$RUSTFLAGS` appended not overwritten). Then `13edb480c` (PR #14978, 2026-08-16) "Start cross-compiling macos builds from linux": `.github/workflows/macos-*-build.yml`, `build.yml`, `configs/macos/mozconfig`, `prefs/firefox/browser.yaml`, `src/browser/base/content/aboutDialog-*.patch`, `src/zen/split-view/ZenViewSplitter.mjs`, `vertical-tabs.css`; and `816ec2d40` (#14988) bump surfer version (firefox.icns, package.json). Issue closed by the cross-compile PR; reporter said at 2026-04-10 (after Dosu stale) "no change. i still check here or there and same issue will happen". No post-fix confirmation in the thread (inferred: unverified whether fixed).

### #9727 "ZenCP Isolated Web Content" process pegs all cores after media playback on MacOS — OPEN (44 comments, 2025-08-02 → 2026-10)
- 1.14.9b macOS aarch64 M3 Max; multiple times/week after YouTube/X video, persists after video tabs closed until app restart. Memory variant c0/c4/c5/c6: ZenCP Isolated Web Content >18 GB total.
- Facts from thread: c2 rennokki (2025-08-14) trigger = pending update, many tabs, then "Restart to Update"; c3: after Mac standby 3+ days, only reboot (not restarting Zen) fixes → *OS-level*. c7 declanblanc: same with Firefox ("Firefox CP Isolated Web Content"). c8: killing process unloads "essential" pinned tabs → suspects background refresh of essentials; c23 illegalnumbers: number of "activity" processes == number of workspaces (11 workspaces, >100 tabs). c12-c17: all affected users have/had an external monitor (rennokki); mr-cheffy c18 "may be upstream Firefox". mr-cheffy c24 asks if `browser.sessionstore.restore_pinned_tabs_on_demand` is disabled (repo default true, `prefs/firefox/browser.yaml:8`). c27 Propheticus: Apple fixed video decoding in macOS 26.1; disable `gfx.webrender.layer-compositor` (Betterfox users); mr-cheffy c28: layer-compositor deliberately off on macOS. c30: M1 AV1 software decode (enhanced-h264ify). c39/c40/c43 (2026-10-01..05): profile https://share.firefox.dev/4yp6lZI showed **Ghostery** causing YouTube CPU 300%; confirmed fix by uninstalling. c33 Propheticus: bug 2021840 (Notion). No Zen-code root cause identified; open.

### #10695 Very low performance — CLOSED/DUPLICATE 2025-10-05 → #8932
- 1.16t Windows x64; Speedometer/JetStream 2x slower than Chrome. Pure perf; no leak.

### #10701 High Memory & Disk Consumption on Snapdragon X Plus — CLOSED/DUPLICATE (2025-11-17)
- 1.16.1b Windows aarch64 ASUS Vivobook S15, RAM + disk 99%. c0 Ezall2001 Linux Arch 6.17.8: RAM 10/16 GB in 30 min "never freed". Asked for profiler (mr-cheffy c1).

### #10797 Large Memory Leak (zen.exe not properly exiting) — CLOSED/DUPLICATE 2025-10-13 (→ #8932, then #10834)
- 1.16.4b Windows x64. RAMMap shows up to **1499 zen.exe instances** with kernel memory (page table 7.6 GB). Counts: start 0 → launch 15 → 3 tabs 22 → close Zen 22 → reopen 34 → ... → 91 after 10 cycles. New entries on opening/clicking unloaded tabs and on video. Not visible in Task Manager. Extensions off made no difference.

### #10834 Zombie processes — CLOSED/NOT_PLANNED 2026-01-25 (dosubot stale; no fix) — Zen twilight 1.18t, Windows x64
- Repro: browse, close Zen, RamMap shows leftover zen.exe with 0 private usage; Redex68: 530 zen.exe + 5341 svchost, 5180 netsh, 5450 conhost after 4 h; troubleshoot mode: 89 zen.exe/621 netsh/708 svchost/724 conhost after 30 min, 360 zen.exe after a day; rises while watching YouTube without new tabs.
- Cause statements: Propheticus c5 (2025-10-16) matches Mozilla bug **1754807** "RDD and Socket processes leak zombie processes on unexpected shutdown"; suspects "Unhook" YouTube extension that aborts connections (c3). Redex68 c7: Firefox gives similar counts (47 firefox.exe, 174 svchost, 168 conhost, 77 netsh after a few min). Conclusion: shared Firefox behaviour exacerbated by extensions; no Zen code.

### #11390 After 1.17.7b, zen browser is extremely slow — CLOSED/NOT_PLANNED 2026-03-29
- Windows x64 (+Linux). Cause: **HTTP/3 + AdGuard conflict in Firefox 145**; `network.http.http3.enable=false` fixes (c3, c8, c12); Firefox itself reproduces (c12); Propheticus filed Mozilla bug 1997372#c5; also 2001618/2002061. umarhamzy c6 memory 2.5→9 GB, Propheticus c7: different issue. Not a leak.

### #11569 performance issue — CLOSED/DUPLICATE (2025-12-09). 1.17.12b Windows; tab switching lag, blank render. No data.

### #11721 Memory leak on arch linux? — CLOSED/NOT_PLANNED 2026-04-20 (dosubot stale). Reporter `not-varram` (same login as this workspace's git user).
- Zen 1.17.15b-ish, Arch 6.18.2, Ryzen 9 7900X3D, RTX 4090, 62 GB, AUR zen-browser-bin. Grows over hours to ~40 GB with constant tabs; not on Windows (artrixdotdev c7 says Windows yes, Arch no, the opposite). Ubuntu (c3, Zen 1.17.15b, Firefox 146 UA), Gentoo, CachyOS, macOS reports. Extensions MetaMask/OneTab suspected (c1) and ruled out (c5). mr-cheffy c10: "main low hanging fruit for linux would be the lack of picture caching" (#6302, Bugzilla 1994267).
- about:memory `mem/11721.summary.txt` (64 procs): **no big parent leak** (Main ~350 MB: `gfx/heap-textures` 208 MB, `webrender/display-list` 43 MB, `js-non-window/gc-heap/unused-chunks` 22 MB, 40 detached-window report entries). Leak is in content: Isolated Web Content pid 3410 **2,317 MB** and pid 194566 **2,283 MB** (12 distinct detached windows each; repeated 22.6 MB `window-objects/.../classes/class(BoundFunctionObject)` per window → many JS realms retained), WebExtensions 1,727 MB (16 detached windows, 547 detached entries), 3 ghost windows in pid 25767. Origins anonymized. *(inferred)* page/extension JS retaining detached windows (classic detached-DOM leak), not parent chrome.

### #11724 [Twilight] Spaces are removed after updating to December 25 version — CLOSED/COMPLETED (2026-01-17). **Not a leak.** Session-restore migration regression; fixes `d74cf98f6` (`SessionStartup-sys-mjs.patch`, `SessionStore-sys-mjs.patch`, `src/zen/sessionstore/ZenSessionManager.sys.mjs`, "closes #11724"), `1338b43e10c` pinned/essential migration, `2a5bb0fb5`. Cross-ref'd because a user (c49) said troubleshoot mode (used for #8932) breaks spaces. Prefs: `zen.ui.migration.session-manager-restore`, `browser.sessionstore.loglevel`.

### #11997 Pinned tabs don't scale: hundreds of pins freeze browser — CLOSED/DUPLICATE 2026-01-25 (of #11851)
- Arc migrant with 200+ pinned tabs; freezes on startup and browsing. mr-cheffy c0: asks value of `browser.sessionstore.restore_pinned_tabs_on_demand` → reporter c1: **true** (the default in `prefs/firefox/browser.yaml:8`); asks for profiler (c2); moves it into #11851 (c3). No profile supplied.
- #11851 (one hop): "Workspace switching becomes laggy with 4+ workspaces and many pinned tabs" Windows GTX 1660 Ti, CLOSED/COMPLETED 2026-03-09, only on NVIDIA machine, same profile smooth on Intel iGPU; mr-cheffy asked for profiler. No fix reference found (no commit mentions 11851).

### #12496 Obscene memory leak on Mac — CLOSED/COMPLETED 2026-07-21 (mr-cheffy, clean-up of "me-too" comments; no fix)
- 1.18.10b macOS aarch64 8 GB: GPU Helper grows to 2 GB, each WebCP ~700 MB. Propheticus c1: one process = one tab/domain, "open fewer tabs". Triggers named: threads.com (c5, c8 Linux), YouTube freeze 4 GB on Arch (c10), Mozilla bug **2035904** (YouTube UI rendering bug, fixed upstream ~2026-05-04 per #13572 c1), Spotlight indexing of bookmark menu (Bugzilla 1990191, 2007363, 2028278, 1979283 – macOS indexing of nested bookmark folders; c13). macOS 27 beta virtual 30-60 GB (c19). Limit workaround `systemd-run --user --scope -p MemoryMax=5G` (c14).

### #12741 10gb for 5 tabs — CLOSED/DUPLICATE (2026-03-12). 1.19b Windows; YouTube x3 + articles.
### #13088 Meta Issues — CLOSED/COMPLETED 2026-06-11 by mr-cheffy, label Triage, body "Collection of meta issues to keep github more organized"; 0 comments. Not a bug.
### #13279 Searching sometimes crashes a tab on windows ARM64 — OPEN. 1.19.8b; search for "translucenttb" crashes content process; c3 also x64 with big pages; same error shown by clicking the about:support link in #8932. **Crash, not memory** (inferred: a #8932 hyperlink mention only).
### #13307 The browser takes up 99% RAM — CLOSED/DUPLICATE (2026-04-18). 1.19.8b Windows; no data.

### #13433 unusual behaviour when using clear feature in sidebar — OPEN (1.19.9b)
- Not a leak. "Clear" closes 100+ tabs without confirmation; undo history default 25 tabs (Propheticus c0); lag/GPU spike during restore. Mentions memory only as a symptom. Plan: confirmation dialog (contributor boobachad c3/c4).

### #13494 Memory leak: main Zen process grows from ~500MB to 3.7GB+ — CLOSED/COMPLETED 2026-04-30 (mr-cheffy; no PR linked)
- 1.19.10b, macOS aarch64 16 GB. Main process jumps from ~400-500 MB to 3.7 GB+ unpredictably (5 min after launch or hours in), total up to ~12 GB (main + WebExtensions + GPU helper + isolated content), macOS Jetsam kills; restart with the same session drops main back to ~500 MB; Mac shut down nightly (not accumulation). "Started after a recent update." ~20 tabs across workspaces (Coolify, Supabase, GitHub dashboards). Extensions ProtonVPN, ProtonPass, Deepl (c17). No about:memory attached.
- Same-day confirmations: Windows (c0), Arch (c2/c3 "after an update made around a week ago"), M2 (c4), yakusho (c9). c8 asks about CVE-2026-7324.
- Maintainer statement mr-cheffy c12/c14 (2026-04-30): "should now be fixed once 1.19.11b is out, thanks to Firefox 150.0.1 [typed '1.10.11b'/'140.0.1']... there have been some regressions from 140.0 related to memory"; Propheticus c13 asks "Which memory leak related fix?". Reporter c17 (05-02): "latest Zen update seems to significantly reduce the frequency"; c22 (2026-07-19) usumiq "still broken".
- Repo cross-check: `c0620a95e` 2026-04-28 "Sync upstream Firefox to version 150.0.1" is the only upstream sync around that date; Zen UI commits landed just before the report (2026-04-27 `92dfe0bab` gh-13439 **Boosts implementation**, 04-26 `6aafd8cb3` gh-13414 startup responsiveness, 04-29 `18c15ac0b` workspace search). Whether Boosts (`src/zen/boosts/`) contributed is *(inferred/untested)*; nothing in the issue says so. Propheticus c21 lists other candidates: macOS Spotlight bookmark-menu indexing (Bugzilla 2028278/2007363/1979283), 1Password/YouTube/Wappalyzer extension leaks.

### #13572 Bad Performence since last update and freezes — CLOSED/COMPLETED 2026-05-07 (by reporter)
- Windows 8 GB, 11 tabs, >5 GB, CPU 75%. Causes: **Wappalyzer add-on severe leak** (Propheticus c1, mr-cheffy c6 → #13556), YouTube rendering bug (Bugzilla 2035904), AV1/VP9 codecs (c7). Resolved by uninstalling Zen/reinstall (c9) and uninstalling Wappalyzer (fgilmet c10).
- #13556 (one hop) "[wappalyzer]: Memory usage huge increase": Arch KDE 6 GB for 5 tabs, mr-cheffy c0 "Wappalyzer is EXTREMELY resource-needy lately" — extension-caused, closed 2026-05-04.

### #14141 Lost all tabs, preferences ... after updating to macOS 26.5.1 — CLOSED/COMPLETED 2026-06-13. **Not a leak** (profile/session loss; recovered via docs.zen-browser.app window-sync "recovering lost window sessions"). Cross-ref only because the body mentions #8932.
### #14287 performance issue — CLOSED/DUPLICATE (1.21.3b Windows; YouTube miniplayer GPU stutter). Perf/GPU, not a leak.
### #14393 Severe performance issues: High RAM usage, laggy UI... — CLOSED/COMPLETED same day (2026-06-27) as redirect to #8932; Windows, no data.
### #14569 High Memory Usage — CLOSED/COMPLETED 2026-07-20 (Propheticus) — CachyOS 16 GB, 3-4.5 GB with 5 tabs. Propheticus c2: media-heavy sites ~500 MB each is normal; "Zen does not unload idle tabs (neither does Firefox), only when system RAM runs out"; use manual unload in context menu. sporocyst c0 same. Not a leak.

### #14873 Plex freezing whole system via Zen Browser under Arch Linux — OPEN (1.21.10b tarball)
- ~30 min of Plex playback → Xorg then OS freeze for 1-2 years, not in Firefox/Chromium. programmerlexi c1/c2 (NixOS unstable via zen-browser-flake): **main process (not content) RSS grows from ~1 GB at 0.25-2 GB/s up to 16-32 GB then drops back to 1 GB**, main thread pegs one core, **240 threads → 120 after restart** ("memory leak and thread leak"), starts "a while after a YouTube tab has been opened and lasts the whole process lifetime", 300+ tabs, 2 loaded. moheladwy c3/c4: any website freezes the system (Arch). ashvwinn c5 asks for a #8932-style report. No profile/memory report attached; open and unowned.

### #15050 Excessive activity tabs causing high system memory usage and freezing — CLOSED/DUPLICATE 2026-08-21
- Windows, 40 GB; "hundreds of tabs, dozens active". Propheticus c0: enhancement request not bug; Zen doesn't auto-sleep until memory low; manual unload tab/folder/space exists (context menu). Requested options: auto-sleep on open, auto-sleep inactive spaces on switch, sleep non-focused tabs. Related repo features: `7dbe5b414` "unload all other spaces" (2026-03-14, #12751), `813fc1698`, `5be2ffa41` (#9683).

### #15603 (PR) gh-15616: Fix split view node map leak — MERGED 2026-09-30 (merge commit e3542b349 in this repo)
- Author VictorGugug (contributor); issue #15616 (1.22.3b Windows): `gZenViewSplitter._tabToSplitNode` (Map tab→split node) is only ever `set`/`get`, so every tab ever split stays referenced until the window closes. Repro in Browser Console: `[...gZenViewSplitter._tabToSplitNode.keys()].filter(t => !t.isConnected).length` grows by 2 per split+close.
- Fix: `src/zen/split-view/ZenViewSplitter.mjs:80` `_tabToSplitNode = new WeakMap()` (only change landed: 1 line). The PR text also claims a `try/finally` for `#onTabSwitchOrWindowFocus` / `#docShellSwitchPromise` (never cleared on throw → later tab switches bail) and a `useCapture` fix in `on_SSWindowClosing`; the latter was dropped by its second commit and `grep -rn docShellSwitchPromise src` finds nothing in this tree, so that part did not land here *(or was in the window_sync module of the PR branch)*. Note `src/zen/split-view/ZenViewSplitter.mjs:1746 .set(splitNode.tab, …)` and `:1848 .get(tab)` are the only uses (WeakMap-compatible; no iteration).

### #15654 TOO MUCH LAG — CLOSED/COMPLETED same day (2026-10-02) redirect. 1.22.3b (Firefox 156.0.1), Windows; Instagram shows "this site is slowing down zen". No data.

### #15823 Memory leak when the library doesn't get opened on a window — CLOSED/COMPLETED 2026-10-09 by mr-cheffy via PR #15826 (commit `3d7777adc`)
- Empty body, no comments (author mr-cheffy, a maintainer-discovered Zen-UI leak). Fix `3d7777adc` "Prevent opening library on startup and other fixes": `src/zen/library/ZenLibrary.mjs` — `#contentMounted` default `true` → `false`; adds `connectedCallback()` registering a `window` `unload` listener (once) and a new `#teardown()` (`#cleanup()`, `#cancelIdleCleanup()`, `#contentMounted=false`, `#mounted=new Set([activeTab])`, `_content.replaceChildren()`); also `ZenLibraryUtils.sys.mjs` (+83), `ZenLibraryWidget.sys.mjs`, `ZenLibraryMediaPreview.mjs`, sections `ZenLibraryDownloadsSection.mjs`, `ZenLibraryMediaSection.mjs`; `ZenSessionManager.sys.mjs` (+36), `ZenSpaceManager.mjs` (+43), `ZenGradientGenerator.mjs`, `Tabbrowser-sys-mjs.patch` (32 lines), `ZenUBGlobalActions.sys.mjs`, tests `src/zen/tests/window_sync/browser_collect_tab_state.js`, `browser_move_unloaded_tabs.js`. Mechanism *(inferred from diff)*: library content was mounted eagerly in every window and never torn down at window close.

### Other one-hop issues (summary)
- #4450 "Severe memory leak" (Arch, twilight AUR zen-twilight-bin-25910c5, 2025-01): closed COMPLETED 2025-03-29 by mr-cheffy in a bulk clean-up, no data. #2777 "Ram usage" (Windows, all versions, 900 MB idle): closed same bulk clean-up. #5447, #7197: not read in depth (3 and 10 comments; closed COMPLETED).
- #6302 "Zen is not making use of picture-caching correctly" (nical, a WebRender developer, 2025-03-10; CLOSED/COMPLETED 2026-09-09): Zen's UI rounded-rect clip/mix-blend-mode stops WebRender picture caching → choppy scrolling and worse power use on all platforms. mr-cheffy c6: uses `mix-blend-mode` rather than `clip-path` (clip-path caused GPU/blur issues). Even with styles removed it stays griding (c3). Pref hint: `gfx.webrender.debug.picture-caching`; repo `prefs/firefox/performance.yaml` `gfx.webrender.compositor`. GPU/CPU cost, not a leak.
- #5500 (dup perf), #7784 (power saving lag, NOT_PLANNED), #5734/#5588/#5840/#2206 (scroll/GPU), #14079 (profile data loss, open): not leaks.

## Clusters (ranked by number of linked issues)

| # | Pattern | Count | Issues | Evidence strength | Code/pref pointers |
|---|---|---|---|---|---|
| 1 | "Me-too" high steady RAM with no data / just many loaded media tabs (RAM not a leak; Zen never unloads idle tabs; native unloader only under pressure) | 17 | 504, 3299, 7240, 8157, 8742, 10695, 10701, 11569, 12741, 13307, 14287, 14393, 14569, 15050, 15654, 8925, 8928 | weak (screenshots) | unloader swap `ebfc88574`; vestigial `zen.tab-unloader.timeout-minutes` (`zen-settings.js:778`); caching/buffering prefs changed between 1.12.8b↔1.13.2b (8742 c6) |
| 2 | Site/extension-caused content-process growth (Wappalyzer, Ghostery, Unhook, MetaMask/OneTab suspects, YouTube/threads.com/Notion/Plex, AV1 sw decode) | 9 | 504 (c74), 9727, 11721, 12496, 13494, 13572 (+13556), 14873, 10834 | strong for Wappalyzer (13556/13572) and Ghostery (9727 c43); 11721 report shows detached windows in content procs | none in Zen |
| 3 | Platform/upstream: macOS main-process footprint (screen-share, Spotlight bookmark indexing, build flags), macOS isolated-content CPU after standby/external monitor | 4 | 9649, 13494, 9727, 12496 | 9649: main process footprint 65 GB vs resident-unique 270 MB; fix `beb4f94fd`/`13edb480c` | `configs/macos/mozconfig`, `.github/workflows/macos-*-build.yml` |
| 4 | Zombie/leftover processes (Windows, RDD/Socket, 1499 zen.exe) | 2 | 10797, 10834 | strong, Firefox reproduces (bug 1754807) | none |
| 5 | Main-process abrupt growth (not content) with thread growth | 3 | 13494, 14873, 504 (c15 CSV string case) | mid: statements only; **no about:memory of the growth moment** | unknown; candidates *(inferred)*: ZenSessionManager/space sync, Boosts, library (cf. #15823), split view (cf. #15603) |
| 6 | Real Zen-code leaks found & fixed | 2 | 15603/15616 (`ZenViewSplitter._tabToSplitNode` → WeakMap), 15823 (`ZenLibrary` content never torn down) | confirmed in diff | `src/zen/split-view/ZenViewSplitter.mjs`, `src/zen/library/ZenLibrary.mjs` |
| 7 | Many-pins / many-spaces scaling (restore_pinned_tabs_on_demand, 1 process per workspace?) | 3 | 11997, 11851, 9727 (c23) | weak | `browser.sessionstore.restore_pinned_tabs_on_demand`, `src/zen/sessionstore/`, `src/zen/spaces/` |
| 8 | UI rendering/GPU cost (workspace colour, picture caching, WebRender swgl) | 3 | 8081, 6302, 504c (swgl 149 MB) | mid | `ZenGradientGenerator.mjs`, `gfx.webrender.*` |
| 9 | Cache/buffer prefs tuned above Firefox default | 2 (stated) | 8157, 8742 | statement by community mod only | prefs/ (not located by me) |

(Issues can appear in more than one row; row 1 is the largest because 17 are no-data reports, not because of a shared cause.)

## Already fixed upstream (in this repo)
- 15616/#15603 → `e3542b349` (WeakMap).
- 15823/#15826 → `3d7777adc` (ZenLibrary teardown).
- 9649 → `beb4f94fd` + `13edb480c` (#14978) + `816ec2d40` (#14988) (macOS build flags + cross-compile; effect unconfirmed by reporter).
- 11724 → `d74cf98f6`, `1338b43e10c` (session restore; not a leak).
- 13494 → no commit; maintainer attributes to FF 150.0.1 (`c0620a95e`), reporter later: fewer spikes, another user: "still broken" 2026-07-19.
- 8932-labeled `0a7e81f53` gh-8932 "Add more PGO instrumentation" (#13158): `src/external-patches/*` + `src/zen/common/sys/ZenActorsManager.sys.mjs` (perf, not a leak).

## Not leaks (perf, extension, hardware, other)
- 8081 (workspace colour render), 8428, 8925, 8928 (CPU), 10695 (Speedometer), 11390 (HTTP/3 + AdGuard), 11569, 11724 (session loss), 11851, 6302 (picture cache), 13088 (meta), 13279 (tab crash), 13307/14393/15654 (no data), 13433 (undo history), 13556/13572 (Wappalyzer), 14141 (profile loss), 14287 (GPU stutter), 9727 CPU part (Ghostery).
- Hardware/OS: 9727 (external monitor, standby; Apple video decode fixed in 26.1), 14287.

## Gaps
No linked issue contains a main-process about:memory taken while growth is happening (13494, 14873 have none), and none a profiler/memory report for #11997/#15050. 11721's report is the only content-process detached-window evidence. Memory reports attached directly in #8932 itself (~75 files) are out of scope for this file.
