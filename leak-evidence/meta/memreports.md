# about:memory attachments of #8932: per-report table and patterns

Generated with `python3 analyze_memreports.py` (stdlib only, handles truncated gz) over the 81 downloaded attachments in `raw/files/` (gitignored; names are `<comment id>_<attachment id>_<name>`). 78 of these are memory reports (one is a Gecko profile, one is a verbose-html text dump, the 404s are gone). 77 contain a Main Process. 5 gz files are truncated at the source (marked in the notes column). Reproduce one report with `python3 analyze_memreports.py --main-only FILE`; all rows with `--table`. Comment context for each id is in `comments.md`.

Column notes: "Main explicit" = sum of `explicit/*` in the Main Process. "biggest process" = process with most explicit memory (IWC = Isolated Web Content/webIsolated). "ghost / detached win" counts Main Process window objects (one `dom/element-nodes` report per window) in the `ghost` and `detached` state under `explicit/window-objects/top(...)`; bytes are the detached total. The separate top-level `ghost-windows/` section was empty for Main in all reports (it lists only content-process ghosts). "orphan-nodes" and "element-nodes" are for the active `browser.xhtml` window(s) of the Main Process (summed over all browser windows). Event-listener total is the sum of `event-counts/.../dom/event-listeners` in Main. `Zen` is blank (`?`) where the comment has no pasted about:support.

## Table

| comment | user | Zen | OS | file | Main explicit | biggest process (explicit) | Main ghost / detached win (bytes) | Main orphan-nodes in browser.xhtml | Main browser.xhtml element-nodes / event-listeners total | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2955646153 | cmvalma | 1.12.10b | macOS | memory-report.json.gz | 556.9MB | IWC https://tonepedia.com^userCont 787.3MB | 0 / 4 (13.3MB) | 1.5MB | 16.4MB / 34342 |  |
| 2969542012 | rvsmooth | 1.14t | Linux | memory-report.json.gz | 128.3MB | Isolated Web Content 333.6MB | 0 / 0 (0.0MB) | 0.3MB | 1.5MB / 2244 |  |
| 2980418049 | Illustar0 | ? | ? | memory-report.json.gz | 192.5MB | IWC https://github.com 925.7MB | 0 / 0 (0.0MB) | 0.5MB | 3.6MB / 6546 |  |
| 2982506074 | Beeditor04 | 1.13.2b | Win | memory-report.json.gz | 225.1MB | IWC https://github.com 1034.1MB | 0 / 0 (0.0MB) | 0.6MB | 3.1MB / 5200 |  |
| 2990400743 | muhmudrik | 1.13.2b | macOS | memory-report.json.gz | 363.6MB | IWC https://google.com 614.2MB | 0 / 4 (20.2MB) | 0.9MB | 4.2MB / 10146 |  |
| 2993777488 | mistycalpi | 1.13.2b | Win | memory-report.json.gz | 158.1MB | IWC https://twitch.tv 530.4MB | 0 / 0 (0.0MB) | 0.4MB | 2.0MB / 3133 |  |
| 2995758865 | MW-J97 | 1.13.2b | Linux | memory-report.json.gz | 202.7MB | IWC https://google.com 264.0MB | 0 / 2 (11.3MB) | 0.5MB | 4.0MB / 8679 |  |
| 2995758865 | MW-J97 | 1.13.2b | Linux | memory-report.json | 202.7MB | IWC https://google.com 264.0MB | 0 / 2 (11.3MB) | 0.5MB | 4.0MB / 8679 |  |
| 2999500694 | no main process in file |
| 3001248556 | Beeditor04 | 1.13.2b | Win | memory-report.json.gz | 181.2MB | IWC https://clickup.com 506.3MB | 0 / 0 (0.0MB) | 0.6MB | 4.3MB / 6747 |  |
| 3003495162 | rubiin | 1.13.2b | Linux | memory-report.json.gz | 139.4MB | IWC https://discord.com 411.1MB | 0 / 0 (0.0MB) | 0.4MB | 2.7MB / 4293 |  |
| 3007090321 | abb4-r053 | 1.13.2b | Win | memory-report.json.gz | 1205.6MB | GPU 1244.2MB | 0 / 2 (10.9MB) | 1.3MB | 11.0MB / 35252 | realm realm([System Principal], DevTools (Module loader) 117.0MB |
| 3036506537 | chaggui | 1.15t | macOS | memory-report.json.gz | 138.3MB | Main Process 138.3MB | 0 / 0 (0.0MB) | 0.4MB | 2.9MB / 4827 | file truncated |
| 3037618377 | ZN0N15 | 1.15t | Win | memory-report.json.gz | 125.3MB | IWC https://youtube.com 269.9MB | 0 / 0 (0.0MB) | 0.3MB | 1.7MB / 2533 |  |
| 3069652218 | giammabria | 1.14.4b | Win | memory-report.json | 195.9MB | IWC https://google.com 735.9MB | 0 / 0 (0.0MB) | 0.5MB | 2.9MB / 4799 |  |
| 3072983275 | treffendharm | 1.14.5b | macOS | memory-report.json.gz | 299.5MB | Isolated Web Content 306.7MB | 0 / 0 (0.0MB) | 0.4MB | 2.6MB / 9358 |  |
| 3074098682 | WhateverMO | 1.14.5b | macOS | memory-report.json.gz | 183.8MB | IWC https://duckduckgo.com 303.9MB | 0 / 0 (0.0MB) | 0.4MB | 3.4MB / 5609 |  |
| 3082861133 | shellheim | 1.14.5b | Linux | memory-report.json.gz | 127.2MB | Main Process 127.2MB | 0 / 0 (0.0MB) | 0.3MB | 2.0MB / 2906 |  |
| 3134139924 | TheRaigeki | 1.14.9b | macOS | memory-report.json.gz | 233.2MB | Isolated Web Content 405.2MB | 0 / 0 (0.0MB) | 0.5MB | 2.6MB / 3836 |  |
| 3146458438 | tht2005 | 1.14.9b | Linux | memory-report.json.gz | 200.3MB | IWC https://facebook.com 445.1MB | 0 / 4 (21.5MB) | 0.5MB | 2.5MB / 7774 |  |
| 3153524948 | enfinders | 1.14.9b | macOS | memory-report.json.gz | 254.6MB | Main Process 254.6MB | 0 / 2 (11.5MB) | 0.5MB | 2.8MB / 10727 |  |
| 3177090423 | Luka-J999 | ? | ? | memory-report.json.gz | 164.8MB | extension 169.7MB | 0 / 0 (0.0MB) | 0.5MB | 1.9MB / 3098 |  |
| 3189223763 | chaggui | 1.15t | macOS | 20250814.memory-report.json.gz | 279.0MB | Isolated Web Content 823.2MB | 0 / 4 (20.9MB) | 0.4MB | 4.0MB / 10025 |  |
| 3192572069 | chaggui | 1.15t | macOS | 20250815.memory-report.json.gz | 249.7MB | Main Process 249.7MB | 0 / 4 (26.9MB) | 0.7MB | 4.5MB / 13564 |  |
| 3200621722 | Mohamedsayhii | 1.14.11b | Linux | 20250815.memory-report.json.gz | 249.7MB | Main Process 249.7MB | 0 / 4 (26.9MB) | 0.7MB | 4.5MB / 13564 |  |
| 3235144733 | chaggui | 1.15t | macOS | 20250828.memory-report.json.gz | 272.6MB | Isolated Web Content 355.9MB | 0 / 6 (31.2MB) | 0.8MB | 6.5MB / 15234 | file truncated |
| 3237408703 | Holly-Chan | 1.15.2b | Win | memory-report.json.gz | 161.3MB | IWC https://aliexpress.com 230.4MB | 0 / 0 (0.0MB) | 0.8MB | 2.1MB / 2933 |  |
| 3254457436 | chaggui | 1.15t | macOS | 20250904.memory-report.json.gz | 194.6MB | Main Process 194.6MB | 0 / 0 (0.0MB) | 0.9MB | 4.9MB / 7655 |  |
| 3254457436 | chaggui | 1.15t | macOS | 20250904.1414.memory-report.json | 459.1MB | Isolated Web Content 477.1MB | 0 / 0 (0.0MB) | 3.7MB | 15.6MB / 23769 |  |
| 3267961461 | constantinemagnus | 1.15.5b | Win | memory-report.json.gz | 253.3MB | extension 2599.2MB | 0 / 0 (0.0MB) | 0.7MB | 3.1MB / 4678 |  |
| 3273285021 | Spaccce | 1.15.2b | macOS | memory-report.json.gz | 266.6MB | IWC https://slack.com 397.9MB | 0 / 0 (0.0MB) | 0.9MB | 3.3MB / 11729 |  |
| 3298676199 | enp-aszuszkiewicz | ? | ? | memory-report.json.gz | 286.6MB | Main Process 286.6MB | 0 / 6 (33.0MB) | 0.5MB | 2.5MB / 11127 |  |
| 3301958751 | enp-aszuszkiewicz | ? | ? | memory-report.json.gz | 252.4MB | IWC https://atlassian.net 513.0MB | 0 / 2 (11.7MB) | 0.4MB | 2.7MB / 8762 |  |
| 3303166387 | Geetr695 | 1.15.5b | Win | memory-report.json.gz | 124.2MB | IWC https://github.com 173.4MB | 0 / 0 (0.0MB) | 0.3MB | 2.4MB / 3136 |  |
| 3312694994 | hampoelz | 1.15.5b | macOS | memory-report.json.gz | 4447.9MB | Main Process 4447.9MB | 0 / 6 (34.5MB) | 1.0MB | 4.1MB / 221747 | realm realm([System Principal], DevTools (Module loader) 1315.0MB |
| 3316278377 | mcglk | 1.15.5b | macOS | memory-report.json.gz | 4360.1MB | Main Process 4360.1MB | 0 / 0 (0.0MB) | 0.6MB | 3.6MB / 5758 | large main (see text) |
| 3403204589 | Redex68 | 1.16.4b | Win | memory-report.json.gz | 219.1MB | Isolated Web Content 895.1MB | 0 / 0 (0.0MB) | 0.4MB | 4.0MB / 6159 |  |
| 3410950306 | Redex68 | 1.16.4b | Win | memory-report.json.gz | 200.4MB | IWC https://itch.zone 362.8MB | 0 / 2 (11.8MB) | 1.1MB | 3.0MB / 6702 |  |
| 3440257192 | dezren39 | 1.17.1b | macOS | memory-report.json.gz | 691.6MB | IWC https://youtube.com 1274.6MB | 0 / 0 (0.0MB) | 2.8MB | 211.2MB / 262542 | file truncated; **huge DOM** |
| 3448450519 | dezren39 | ? | ? | memory-report-verbose-2025-10-26 | 685.8MB | Main Process 685.8MB | 0 / 0 (0.0MB) | 2.6MB | 210.1MB / 262866 | **huge DOM** |
| 3448450519 | dezren39 | ? | ? | memory-report-2026-10-26.json | 307.5MB | Main Process 307.5MB | 0 / 0 (0.0MB) | 0.4MB | 2.1MB / 3038 |  |
| 3477425040 | aningdev | ? | ? | memory-report.json.gz | 469.8MB | IWC https://tanstack.com 4682.1MB | 0 / 8 (54.6MB) | 0.7MB | 4.9MB / 32402 |  |
| 3508174127 | kburnwall | 1.17.6b | Win | memory-report.json.gz | 181.6MB | IWC https://github.com 183.4MB | 0 / 0 (0.0MB) | 0.4MB | 2.4MB / 3681 |  |
| 3517395966 | daniel-kneip | 1.17.4b | macOS | memory-report.json.gz | 585.6MB | IWC https://amazon.com^userContext 632.4MB | 0 / 12 (78.9MB) | 1.7MB | 8.6MB / 30677 | file truncated |
| 3522009156 | onyvaxyz | 1.17.6b | ? | memory-report.json | 171.0MB | Main Process 171.0MB | 0 / 0 (0.0MB) | 0.4MB | 2.3MB / 4860 |  |
| 3572293490 | Ferrb9579 | 1.17.8b | Win | memory-report.json.gz | 506.8MB | Main Process 506.8MB | 3 / 0 (0.0MB) (chrome:\\devtools\content\webc, about:devtools-toolbox, chrome:\\devtools\content\netm) | 2.2MB | 13.8MB / 23302 |  |
| 3592171958 | chillcicada | 1.17.10b | Win | memory-report.json.gz | 186.9MB | IWC https://github.com 198.2MB | 0 / 0 (0.0MB) | 1.0MB | 2.0MB / 9392 |  |
| 3604088200 | Rydsmith | 1.17.12b | Linux | memory-report.json.gz | 249.9MB | IWC https://fandom.com 525.4MB | 0 / 4 (21.7MB) | 0.9MB | 5.0MB / 10932 |  |
| 3611177013 | RetroitKnife | 1.17.9b | Linux | memory-report.json.gz | 295.2MB | Main Process 295.2MB | 0 / 0 (0.0MB) | 1.3MB | 7.9MB / 12690 |  |
| 3620074672 | spookybytesyou | 1.17.12b | Linux | memory-report.json.gz | 265.1MB | Isolated Web Content 299.9MB | 0 / 2 (10.7MB) | 1.5MB | 6.6MB / 11156 |  |
| 3625661325 | benseddikmo | 1.17.12b | macOS | memory-report.json.gz | 210.7MB | IWC https://dune.com 777.7MB | 0 / 0 (0.0MB) | 0.5MB | 3.0MB / 4780 |  |
| 3773143435 | diegopluna | 1.17.15b | macOS | memory-report.json.gz | 175.4MB | IWC https://github.com^userContext 306.2MB | 0 / 0 (0.0MB) | 0.5MB | 3.3MB / 5071 |  |
| 3809580132 | AwesomesuperDan0927 | ? | ? | memory-report.json.gz | 243.4MB | IWC https://feishu.cn 426.3MB | 0 / 0 (0.0MB) | 1.5MB | 10.4MB / 14203 |  |
| 3835430673 | Matteoverzotti | 1.18.3b | macOS | memory-report.json.gz | 210.9MB | WebExtensions 749.7MB | 0 / 0 (0.0MB) | 0.4MB | 3.6MB / 4692 |  |
| 4060511625 | ElRaphik | 1.18.10b | Win | memory-report.json.gz | 465.4MB | Isolated Web Content 952.9MB | 0 / 14 (83.4MB) | 1.8MB | 20.3MB / 37880 |  |
| 4280517023 | noturenemy | ? | ? | memory-report.json.gz | 216.5MB | IWC https://vk.com 459.3MB | 0 / 0 (0.0MB) | 0.4MB | 3.6MB / 4765 |  |
| 4324642779 | boobachad | 1.19.9b | Linux | memory-report.json.gz | 714.0MB | Main Process 714.0MB | 0 / 0 (0.0MB) | 1.9MB | 22.4MB / 37966 |  |
| 4495005360 | igads3d | 1.19.13b | Linux | memory-report-9gb.json.gz | 700.1MB | Main Process 700.1MB | 1 / 0 (0.0MB) (about:preferences#zenMarketpla) | 5.7MB | 4.0MB / 21236 |  |
| 4495005360 | igads3d | 1.19.13b | Linux | memory-report-after-minimize.jso | 533.5MB | Main Process 533.5MB | 0 / 0 (0.0MB) | 0.8MB | 4.0MB / 4970 |  |
| 4495005360 | igads3d | 1.19.13b | Linux | memory-report-after-restart-trou | 293.4MB | Main Process 293.4MB | 0 / 0 (0.0MB) | 0.5MB | 3.4MB / 4300 |  |
| 4500740919 | igads3d | ? | ? | memory-report-weird-rdd.json.gz | 339.4MB | IWC https://youtube.com^userContex 733.5MB | 0 / 0 (0.0MB) | 0.7MB | 4.3MB / 11161 |  |
| 4500740919 | igads3d | ? | ? | memory-report-nowarns-troublesho | 399.6MB | IWC https://youtube.com^userContex 446.0MB | 0 / 0 (0.0MB) | 0.5MB | 3.5MB / 8381 |  |
| 4785775944 | Pendonym | 1.21.3b | Win | memory-report.json.gz | 243.0MB | Main Process 243.0MB | 0 / 4 (17.6MB) | 0.9MB | 2.7MB / 5716 | file truncated |
| 4988564893 | shivanshs9 | 1.21.4b | Linux | zen-memoryleak-160726-aws-consol | 283.7MB | Main Process 283.7MB | 0 / 0 (0.0MB) | 0.8MB | 4.8MB / 9053 |  |
| 5507908503 | Nirmal314 | 1.21.16b | Win | memory-report.json.gz | 215.4MB | IWC https://claude.ai^userContextI 282.5MB | 0 / 4 (26.3MB) | 0.9MB | 3.1MB / 8156 |  |
| 5709093579 | aki665 | 1.22.2b | Win | memory-report.json.gz | 367.6MB | Main Process 367.6MB | 0 / 0 (0.0MB) | 4.1MB | 25.8MB / 36957 |  |
| 5744743156 | codeforge11 | 1.22.2b | Win | memory-report.json.gz | 3046.3MB | WebExtensions 5723.6MB | 0 / 0 (0.0MB) | 0.6MB | 4.0MB / 4413 | large main (see text) |
| 5752693192 | emryll | 1.22.2b | Win | memory-report.json.gz | 215.0MB | Isolated Web Content 4520.9MB | 0 / 2 (14.2MB) | 0.6MB | 5.2MB / 9022 |  |
| 5973482637 | rexendevar | 1.22.3b | Linux | memory-report.json | 233.9MB | IWC https://youtube.com 343.1MB | 0 / 0 (0.0MB) | 0.9MB | 6.3MB / 7254 |  |
| 5981075145 | michaelhazan | 1.23b | macOS | memory-report.json.gz | 366.5MB | IWC https://github.com 793.3MB | 0 / 2 (15.5MB) | 0.9MB | 5.2MB / 9158 |  |
| 6060921916 | XeynQ4 | 1.23.1b | Win | memory-report.json.gz | 10549.5MB | Main Process 10549.5MB | 0 / 0 (0.0MB) | 8457.3MB | 7.4MB / 10367 | **orphan-nodes 8457.3MB** |
| 6063114915 | mennatawfiq | 1.23.1b | Linux | memory-report.json.gz | 3595.5MB | Main Process 3595.5MB | 0 / 0 (0.0MB) | 2808.8MB | 5.0MB / 9618 | **orphan-nodes 2808.8MB** |
| 6233774650 | rfeskov | 1.23.2b | macOS | memory-report.json.gz | 365.0MB | Isolated Web Content 663.9MB | 0 / 2 (15.2MB) | 1.6MB | 5.4MB / 9555 |  |
| 6320286920 | tr1kright | ? | ? | memory-report.json.gz | 255.2MB | IWC https://youtube.com 2284.1MB | 0 / 0 (0.0MB) | 0.8MB | 6.0MB / 7691 |  |
| 6460326976 | shivanshs9 | 1.23b | Linux | memory-report2.json.gz | 302.5MB | Isolated Web Content 49802.0MB | 0 / 0 (0.0MB) | 1.2MB | 8.3MB / 13363 |  |
| 6471626179 | blosny | ? | ? | memory-report.json | 225.8MB | Isolated Web Content 443.9MB | 0 / 0 (0.0MB) | 0.9MB | 8.6MB / 8487 |  |
| 6586890805 | tysaya123 | 1.23.4b | macOS | memory-report3.json.gz | 777.6MB | GPU 21554.8MB | 0 / 12 (289.1MB) | 7.0MB | 49.8MB / 155527 |  |
| 6619620912 | shivanshs9 | ? | ? | memory-report-20261103-aws.redac | 660.4MB | IWC <redacted-url> 9242.1MB | 0 / 0 (0.0MB) | 1.4MB | 6.7MB / 7186 | realm realm([System Principal], shared JSM global) 155.8MB |


## Patterns in the MAIN process (numbers from the table above)

Baseline: median Main explicit = 253 MB (p90 714 MB, n=77), median Main event-listeners = 8,679, median `shared JSM global` realm = 17 MB (max 156 MB), median `browser.xhtml` active element-nodes about 3-4 MB per window.
Only 6 of 77 reports have Main above 1 GB, and every one has a single explained dominant entry (below). In 71 of 77 reports Main is normal and the growth is in content, GPU, extension or RDD processes (see "biggest process" column).

### 1. One Zen-attributable Main leak: `dom/orphan-nodes` of `browser.xhtml` in Zen 1.23.1b
- 6060921916 (XeynQ4): `explicit/window-objects/top(chrome://browser/content/browser.xhtml, id=1)/active/window(browser.xhtml)/dom/orphan-nodes` = 8,457 MB (Main 10.5 GB total); `element-nodes` in the same window only 7.4 MB. Plus `js-realm([System Principal], about:blank)` classes under that window: Object 542 MB, XULElement 160 MB, Array 153 MB, HTMLElement 65 MB, Set 51 MB.
- 6063114915 (mennatawfiq): same path, 2,809 MB orphan-nodes (Main 3.6 GB).
- Both are Zen 1.23.1b, both opened a new session with nothing special ("just open the browser and wait", XeynQ4 #170; 10 minutes, same in safe mode, #166). XeynQ4 downgraded to 1.23b and the leak was gone. No other report in the set has more than 7 MB of orphan nodes in browser.xhtml (second place: 6586890805 with 7.0 MB).
- This matches issue #15823 ("ZenLibrary never torn down", fixed in PR #15826, commit 3d7777adc; see `../linked-issues.md`): mr-cheffy opened it from this very thread (#171). *(inferred: the orphans are the library's DOM built per window and never freed; the report cannot name the document, only that the nodes are detached from any tree and referenced by chrome JS.)*
- `orphan-nodes` is a plain "nodes not in a document, still alive" counter, so the useful lead for the main process hunt is: a Zen UI feature creating DOM (or `ChromeUtils.import`ed objects) that outlives its window. Not yet attributable to a specific field from the report alone.

### 2. Detached `browser.xhtml` windows in Main (closed windows that stay alive)
- 26 of 77 reports (34%) have detached `browser.xhtml` windows under `explicit/window-objects/top(none)/detached/window(chrome://browser/content/browser.xhtml)`.
- Counts are always even (2, 4, 6, 8, 12, 14), about 5-6 MB per entry (2 -> 10.7 MB, 4 -> 20.2 MB, 14 -> 83.4 MB, 6 -> 33.0 MB). Largest: 6586890805 (12 entries, 289 MB, one entry alone 77 MB `element-nodes`, 3 active windows), 4060511625 (14, 83.4 MB), 3517395966 (12, 78.9 MB), 3477425040 (8, 54.6 MB).
- Seen from Zen 1.12.10b (2025-06) through 1.23.4b (2026-11), i.e. not a regression of one version. Often in reports that also show multiple windows (the even count looks like two documents per closed window *(inferred; no way to tell from the report)*).
- Detached other: `bookmarkProperties.xhtml` x2 (2955646153), `about:support` x2 (4785775944). Ghost: DevTools windows (webconsole, netmonitor, toolbox, 3572293490), `about:preferences#zenMarketplace` 20.7 MB (4495005360, Zen 1.19.13b; a Zen-specific chrome page that stayed alive after closing: elements 6.8 MB, js-realm 3 MB, text/comment nodes).
- These are small (tens of MB) next to the multi-GB reports; they do show closed windows are retained. They are the same class as the "ghost chrome windows" hypothesis, but never above 289 MB total in this data set.

### 3. Main-process blow-ups caused by something else (not Zen code)
| report | Main | entry | cause |
|---|---|---|---|
| 3312694994 hampoelz 1.15.5b | 4.45 GB | 1,868 MB `orphan-nodes` of `top(about:devtools-toolbox)/window(chrome://devtools/content/inspector/index.xhtml)`, `realm(DevTools (Module loader))` 1.3 GB, 221,747 listeners / 198,122 event-targets | DevTools inspector open |
| 3007090321 abb4-r053 1.13.2b | 1.2 GB | 471 MB orphan-nodes of the devtools inspector window | DevTools open |
| 3316278377 mcglk 1.15.5b | 4.36 GB | 2,937 MB `dom/structured-clone-holder/ExtensionParent/tab-array@menhera.org/recvAddListener/storage.onChanged` + ~1 GB more structured-clone from the same add-on | add-on "tab-array" |
| 5744743156 codeforge11 1.22.2b | 3.05 GB | 2,817 MB `dom/structured-clone-holder/Messenger/{uuid}/sendRuntimeMessage` | an extension sending huge runtime messages (the thread says "buykers") |
Four of the six GB-class Main cases are extension messaging or DevTools, not Zen UI.

### 4. DOM / event listeners
- Event listeners and `dom/element-nodes` of the active `browser.xhtml` scale with number of tabs/windows, not time: 3440257192 (dezren39, 88 extensions, many tabs, Zen mods): browser.xhtml element-nodes 211 MB, 262,542 listeners, file truncated; the clean-profile file from the same user: 2.1 MB / 3,038 listeners. 6586890805: 155,527 listeners with 3 windows; 4060511625: 37,880; 4324642779: 37,966; 5709093579 (76 extensions, 8 browser windows): 36,957.
- `dom/event-targets` stays small (50-200) except for the DevTools case above (198,122).
- So the only browser.xhtml with abnormal element-nodes counts are these power-user profiles; I found nothing indicating a steadily growing listener count by itself (no time series in any report, all are single snapshots *(caveat)*).

### 5. JS realms in Main
- All Zen `.mjs` modules and `chrome://browser/content/zen-*` scripts run in the single `realm([System Principal], shared JSM global)`; it does not split by module, so the report cannot name a leaking Zen module. Its size: median 17 MB, above 60 MB in 5 reports (6619620912 156 MB, 3007090321 108 MB, 6586890805 83 MB, 4060511625 63 MB, 2982506074 58 MB), growing with uptime/windows is plausible but unprovable from the snapshots.
- `Namespace of ext-*.js scripts for main` realm: 0.8-13.5 MB (extension API).
- No `realm(...)` naming `resource:///modules/zen/...` or `chrome://browser/content/zen-...` exists in any Main process (checked all 77): the grep for those URLs finds only `window(about:preferences#zen*)` and image entries.

### 6. Zen-specific main-process entries (animations, motion, workspaces, glance, split view, library, boosts, gradients)
- Entries with "zen" in the path (2057 distinct): all of them are either images (`chrome://browser/skin/zen-icons/library/*-sprite.svg` 1-2 MB each, `zen-images/layouts/*.png` 0.7 MB decoded, `note-indicator.svg` 3 MB), a11y cache of pages (tabs about Zen), web pages (zen-browser.app/reddit), or `about:preferences#zen*` windows: `zenMarketplace` (ghost 20.7 MB, active 6.8 MB elements), `zenTabManagement` (12.6 MB), `zenCKS` (12.5 MB).
- None of the words "motion", "animation", "workspace", "glance", "split-view", "boost", "gradient" appears in a window URL or realm name of Main. Library appears only as sprite images and, indirectly, the 1.23.1b orphan-nodes (pattern 1). Boosts: sprite image only. So: **no Zen-specific main-process memory entry grows in the reports except (a) 1.23.1b orphan-nodes in browser.xhtml (library, fixed), (b) detached browser.xhtml windows and the zenMarketplace ghost page.**
- Fixed Zen leaks mentioned by maintainers inside the thread: folder-icon refresh tick every frame (#57, 1.15.x); library teardown (#15823).

### 7. Non-main patterns seen along the way (for completeness)
- Content processes: ghost windows only in `github.com` processes (5981075145: 5 ghost; 6619620912: 2+1; 6060921916: 1); the 18 ghosts in 6507688542 were reported as text only and fixed by Firefox 159 (bug 2079806) per the reporter.
- GPU process: 3007090321 GPU 1.24 GB; 6586890805 GPU 21.5 GB explicit (3 active windows, 12 detached); enp-aszuszkiewicz GPU leak fixed by disabling hardware acceleration.
- Extension/WebExtensions process: 3267961461 2.6 GB, 5744743156 5.7 GB.
- Content: 6460326976 chatgpt.com 49.8 GB (Mapbox worker, upstream), 5752693192 4.5 GB chatgpt.com, 3189223763 823 MB.
