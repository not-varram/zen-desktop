# Task: Adversarial review of a memory-leak fix in Zen Browser (you did not write it)

## Hard rule (verbatim from the user)
Hard rule, because it has crashed every session on this account twice tonight: never run `apt-get install`, `dpkg -i` or `systemd-tmpfiles`, and never change the ownership or mode of /root or anything under it. A systemd postinst re-owns the account's shared /root and kills all sessions; run-v27ssb3txh is fixing that in Aether. Put this rule word for word in every sub-session's and subagent's brief. If you truly need system packages, stop and tell Varsh which ones and why.

## What to review
Commit 28be25f20 ("Remove the library's hidden-tabs pref observer on window unload"), `src/zen/library/ZenLibrary.mjs`, and its evidence `leak-evidence/causes/A-library-pref-observer.md`. Context for the hunt: `leak-evidence/meta/memreports.md`, `leak-evidence/window-retention.md`, `leak-evidence/motion/README.md`.

Try to break it. In particular:
1. Is the leak real? Is `<zen-library>` really in every browser window (`src/browser/base/content/browser-box-inc-xhtml.patch`), is the observer really strong (Firefox `modules/libpref/Preferences.cpp`, read-only web fetch of mozilla-firefox/firefox is OK), does the arrow closure really keep the window alive, and is it true that `disconnectedCallback` does not run when a chrome window closes?
2. Is the fix correct and complete? Does `unload` always reach `#teardown` (e.g. listener added in connectedCallback; what if the element is connected after unload, re-connected, moved, or created in non-browser windows/tests)? Can anything re-register the observer after teardown (Lit re-render after `replaceChildren()`, a pending `requestUpdate`, `connectedCallback` firing again)? Double-remove safety? Does the same element still behave when `disconnectedCallback` runs normally (tests that remove and re-add it, see `src/zen/tests/library/`)?
3. Anything else in `src/zen/library/**` that registers a process-lifetime observer/view/listener and is not removed on window unload (sections, media preview, widget, ZenLibraryUtils). Check also whether the provenance claim holds: `git log -L` on the lines, release dates via `gh api repos/zen-browser/desktop/releases` (read-only).
4. Code style: matches the surrounding code and comment density?

Do not edit `src/`. Write findings to `leak-evidence/review-A.md` and commit it. Do not open PRs/issues/comments on any upstream repo. Do not claim runtime verification; nothing can run Zen here.

## Final report must contain
Verdict (approve / approve with changes / reject), each finding with file:line and a concrete failure scenario, what you verified by reading vs inferred, and your commit SHA.
