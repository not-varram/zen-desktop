/* Any copyright is dedicated to the Public Domain.
   https://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// Every browser window has a <zen-library>, and anything it leaves registered
// with a process-wide service after the window closes keeps that whole window
// alive. See zen-browser/desktop#8932.

async function collectGarbage() {
  for (let i = 0; i < 3; i++) {
    Cu.forceGC();
    Cu.forceCC();
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}

// The element only registers anything once its class is defined, so make sure
// the window's library really is one. This runs in its own function so that the
// class, which belongs to that window, is not left in the test's frame.
async function assertUpgradedLibrary(win) {
  const Library = await win.customElements.whenDefined("zen-library");
  ok(
    win.document.querySelector("zen-library") instanceof Library,
    "The window has an upgraded library"
  );
}

add_task(async function test_closed_window_is_released() {
  let win = await BrowserTestUtils.openNewBrowserWindow();
  await win.gZenWorkspaces.promiseInitialized;
  await assertUpgradedLibrary(win);

  const weakWindow = Cu.getWeakReference(win);
  await BrowserTestUtils.closeWindow(win);
  win = null;

  await TestUtils.waitForCondition(async () => {
    await collectGarbage();
    return !weakWindow.get();
  }, "The closed window should be collected");
  ok(!weakWindow.get(), "Nothing keeps the closed window alive");
});
